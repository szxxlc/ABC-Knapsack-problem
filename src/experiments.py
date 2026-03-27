from dataclasses import asdict, dataclass, field
from pathlib import Path
import csv
import statistics
import time

from src.abc_algorithm import ArtificialBeeColony
from src.neighborhood import RandomNeighborMode
from src.evaluator import (
    are_shopping_requirements_fully_satisfied,
    calculate_actual_cost,
    calculate_regular_cost,
    calculate_savings,
    calculate_score,
    calculate_shopping_penalty,
    calculate_total_volume,
    is_feasible,
)
from src.problem import ProblemInstance, Solution


@dataclass
class SingleRunResult:
    run_index: int
    seed: int
    instance_seed: int | None
    random_neighbor_mode: RandomNeighborMode
    num_food_sources: int
    best_solution: Solution
    best_score: float
    regular_cost: float
    actual_cost: float
    savings: float
    shopping_penalty: float
    total_volume: float
    hard_constraints_feasible: bool
    shopping_requirements_fully_satisfied: bool
    iterations_completed: int
    stopped_early: bool
    iterations_without_improvement: int
    execution_time_seconds: float
    best_score_history: list[float] = field(default_factory=list)


@dataclass
class ExperimentSummary:
    run_results: list[SingleRunResult] = field(default_factory=list)
    random_neighbor_mode: RandomNeighborMode = "all"
    num_food_sources: int = 0

    instance_num_products: int = 0
    instance_cart_volume_limit: float = 0.0
    instance_budget_limit: float | None = None
    instance_num_requirements: int = 0
    instance_num_products_with_sale: int = 0
    instance_num_products_without_sale: int = 0

    best_score_min: float = 0.0
    best_score_max: float = 0.0
    best_score_avg: float = 0.0
    best_score_median: float = 0.0
    best_score_std: float = 0.0

    savings_min: float = 0.0
    savings_max: float = 0.0
    savings_avg: float = 0.0
    savings_median: float = 0.0
    savings_std: float = 0.0

    penalty_min: float = 0.0
    penalty_max: float = 0.0
    penalty_avg: float = 0.0
    penalty_median: float = 0.0
    penalty_std: float = 0.0

    execution_time_min: float = 0.0
    execution_time_max: float = 0.0
    execution_time_avg: float = 0.0
    execution_time_median: float = 0.0
    execution_time_std: float = 0.0

    fully_satisfied_count: int = 0
    feasible_count: int = 0

    best_run_index: int = -1
    best_run_seed: int = -1
    best_run_score: float = 0.0


def _safe_mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return statistics.mean(values)


def _safe_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values)


def extract_instance_metadata(instance: ProblemInstance) -> dict:
    num_products = len(instance.products)
    num_products_with_sale = sum(
        product.sale is not None for product in instance.products
    )

    return {
        "instance_num_products": num_products,
        "instance_cart_volume_limit": instance.cart_volume_limit,
        "instance_budget_limit": instance.budget_limit,
        "instance_num_requirements": len(instance.shopping_requirements),
        "instance_num_products_with_sale": num_products_with_sale,
        "instance_num_products_without_sale": num_products - num_products_with_sale,
    }


def run_single_experiment(
    instance: ProblemInstance,
    run_index: int,
    seed: int,
    instance_seed: int | None,
    num_food_sources: int,
    num_onlooker_bees: int,
    trial_limit: int,
    max_iterations: int,
    max_iterations_without_improvement: int | None = None,
    random_neighbor_mode: RandomNeighborMode = "all",
) -> SingleRunResult:
    abc = ArtificialBeeColony(
        instance=instance,
        num_food_sources=num_food_sources,
        num_onlooker_bees=num_onlooker_bees,
        trial_limit=trial_limit,
        max_iterations=max_iterations,
        max_iterations_without_improvement=max_iterations_without_improvement,
        seed=seed,
        random_neighbor_mode=random_neighbor_mode,
    )

    start_time = time.perf_counter()
    result = abc.optimize()
    end_time = time.perf_counter()

    best_solution = result.best_solution

    regular_cost = calculate_regular_cost(instance, best_solution)
    actual_cost = calculate_actual_cost(instance, best_solution)
    savings = calculate_savings(instance, best_solution)
    shopping_penalty = calculate_shopping_penalty(instance, best_solution)
    total_volume = calculate_total_volume(instance, best_solution)
    best_score = calculate_score(instance, best_solution)
    hard_constraints_feasible = is_feasible(instance, best_solution)
    shopping_requirements_fully_satisfied = (
        are_shopping_requirements_fully_satisfied(instance, best_solution)
    )

    return SingleRunResult(
        run_index=run_index,
        seed=seed,
        instance_seed=instance_seed,
        random_neighbor_mode=random_neighbor_mode,
        num_food_sources=num_food_sources,
        best_solution=best_solution,
        best_score=best_score,
        regular_cost=regular_cost,
        actual_cost=actual_cost,
        savings=savings,
        shopping_penalty=shopping_penalty,
        total_volume=total_volume,
        hard_constraints_feasible=hard_constraints_feasible,
        shopping_requirements_fully_satisfied=shopping_requirements_fully_satisfied,
        iterations_completed=result.iterations_completed,
        stopped_early=result.stopped_early,
        iterations_without_improvement=result.iterations_without_improvement,
        execution_time_seconds=end_time - start_time,
        best_score_history=result.best_score_history.copy(),
    )


def summarize_results(
    instance: ProblemInstance,
    run_results: list[SingleRunResult],
    random_neighbor_mode: RandomNeighborMode = "all",
    num_food_sources: int = 0,
) -> ExperimentSummary:
    if not run_results:
        metadata = extract_instance_metadata(instance)
        return ExperimentSummary(
            random_neighbor_mode=random_neighbor_mode,
            num_food_sources=num_food_sources,
            **metadata,
        )

    best_scores = [result.best_score for result in run_results]
    savings_values = [result.savings for result in run_results]
    penalty_values = [result.shopping_penalty for result in run_results]
    execution_times = [result.execution_time_seconds for result in run_results]

    fully_satisfied_count = sum(
        result.shopping_requirements_fully_satisfied
        for result in run_results
    )

    feasible_count = sum(
        result.hard_constraints_feasible
        for result in run_results
    )

    best_run = max(run_results, key=lambda result: result.best_score)
    metadata = extract_instance_metadata(instance)

    return ExperimentSummary(
        run_results=run_results,
        random_neighbor_mode=random_neighbor_mode,
        num_food_sources=num_food_sources,
        instance_num_products=metadata["instance_num_products"],
        instance_cart_volume_limit=metadata["instance_cart_volume_limit"],
        instance_budget_limit=metadata["instance_budget_limit"],
        instance_num_requirements=metadata["instance_num_requirements"],
        instance_num_products_with_sale=metadata["instance_num_products_with_sale"],
        instance_num_products_without_sale=metadata["instance_num_products_without_sale"],
        best_score_min=min(best_scores),
        best_score_max=max(best_scores),
        best_score_avg=_safe_mean(best_scores),
        best_score_median=statistics.median(best_scores),
        best_score_std=_safe_std(best_scores),
        savings_min=min(savings_values),
        savings_max=max(savings_values),
        savings_avg=_safe_mean(savings_values),
        savings_median=statistics.median(savings_values),
        savings_std=_safe_std(savings_values),
        penalty_min=min(penalty_values),
        penalty_max=max(penalty_values),
        penalty_avg=_safe_mean(penalty_values),
        penalty_median=statistics.median(penalty_values),
        penalty_std=_safe_std(penalty_values),
        execution_time_min=min(execution_times),
        execution_time_max=max(execution_times),
        execution_time_avg=_safe_mean(execution_times),
        execution_time_median=statistics.median(execution_times),
        execution_time_std=_safe_std(execution_times),
        fully_satisfied_count=fully_satisfied_count,
        feasible_count=feasible_count,
        best_run_index=best_run.run_index,
        best_run_seed=best_run.seed,
        best_run_score=best_run.best_score,
    )


def run_multiple_experiments(
    instance: ProblemInstance,
    num_runs: int,
    base_seed: int,
    instance_seed: int | None,
    num_food_sources: int,
    num_onlooker_bees: int,
    trial_limit: int,
    max_iterations: int,
    max_iterations_without_improvement: int | None = None,
    random_neighbor_mode: RandomNeighborMode = "all",
) -> ExperimentSummary:
    run_results: list[SingleRunResult] = []

    for run_index in range(num_runs):
        seed = base_seed + run_index

        run_result = run_single_experiment(
            instance=instance,
            run_index=run_index,
            seed=seed,
            instance_seed=instance_seed,
            num_food_sources=num_food_sources,
            num_onlooker_bees=num_onlooker_bees,
            trial_limit=trial_limit,
            max_iterations=max_iterations,
            max_iterations_without_improvement=max_iterations_without_improvement,
            random_neighbor_mode=random_neighbor_mode,
        )
        run_results.append(run_result)

    return summarize_results(
        instance,
        run_results,
        random_neighbor_mode=random_neighbor_mode,
        num_food_sources=num_food_sources,
    )


def _single_run_result_to_row(
    result: SingleRunResult,
    instance: ProblemInstance,
) -> dict:
    metadata = extract_instance_metadata(instance)

    return {
        **metadata,
        "run_index": result.run_index,
        "seed": result.seed,
        "instance_seed": result.instance_seed,
        "random_neighbor_mode": result.random_neighbor_mode,
        "num_food_sources": result.num_food_sources,
        "best_solution_quantities": result.best_solution.quantities,
        "best_score": result.best_score,
        "regular_cost": result.regular_cost,
        "actual_cost": result.actual_cost,
        "savings": result.savings,
        "shopping_penalty": result.shopping_penalty,
        "total_volume": result.total_volume,
        "hard_constraints_feasible": result.hard_constraints_feasible,
        "shopping_requirements_fully_satisfied": (
            result.shopping_requirements_fully_satisfied
        ),
        "iterations_completed": result.iterations_completed,
        "stopped_early": result.stopped_early,
        "iterations_without_improvement": result.iterations_without_improvement,
        "execution_time_seconds": result.execution_time_seconds,
        "best_score_history": result.best_score_history,
    }


def save_run_results_to_csv(
    instance: ProblemInstance,
    run_results: list[SingleRunResult],
    file_path: str | Path,
) -> None:
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if not run_results:
        return

    rows = [_single_run_result_to_row(result, instance) for result in run_results]
    fieldnames = list(rows[0].keys())

    with file_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_summary_to_csv(
    summary: ExperimentSummary,
    file_path: str | Path,
) -> None:
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    summary_dict = asdict(summary)
    summary_dict.pop("run_results", None)

    with file_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["metric", "value"])

        for key, value in summary_dict.items():
            writer.writerow([key, value])


def save_score_plot_data_to_csv(
    summaries: list[ExperimentSummary],
    file_path: str | Path,
) -> None:
    """Save compact, plotting-ready score data in long format."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    sorted_summaries = sorted(
        summaries,
        key=lambda summary: (summary.num_food_sources, summary.random_neighbor_mode),
    )

    rows: list[dict] = []
    for summary in sorted_summaries:
        run_count = len(summary.run_results)
        feasible_rate = (
            summary.feasible_count / run_count if run_count > 0 else 0.0
        )
        fully_satisfied_rate = (
            summary.fully_satisfied_count / run_count if run_count > 0 else 0.0
        )

        rows.append(
            {
                "num_food_sources": summary.num_food_sources,
                "random_neighbor_mode": summary.random_neighbor_mode,
                "num_runs": run_count,
                "best_score_avg": summary.best_score_avg,
                "best_score_median": summary.best_score_median,
                "best_score_min": summary.best_score_min,
                "best_score_max": summary.best_score_max,
                "best_score_std": summary.best_score_std,
                "feasible_rate": feasible_rate,
                "fully_satisfied_rate": fully_satisfied_rate,
                "execution_time_avg": summary.execution_time_avg,
            }
        )

    fieldnames = [
        "num_food_sources",
        "random_neighbor_mode",
        "num_runs",
        "best_score_avg",
        "best_score_median",
        "best_score_min",
        "best_score_max",
        "best_score_std",
        "feasible_rate",
        "fully_satisfied_rate",
        "execution_time_avg",
    ]

    with file_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_score_plot_pivot_to_csv(
    summaries: list[ExperimentSummary],
    file_path: str | Path,
) -> None:
    """Save score averages in wide format: one column per mode."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    modes_in_order: list[RandomNeighborMode] = []
    seen_modes: set[RandomNeighborMode] = set()
    for summary in summaries:
        mode = summary.random_neighbor_mode
        if mode not in seen_modes:
            seen_modes.add(mode)
            modes_in_order.append(mode)

    food_source_sizes = sorted(
        {summary.num_food_sources for summary in summaries}
    )

    score_lookup = {
        (summary.num_food_sources, summary.random_neighbor_mode): summary.best_score_avg
        for summary in summaries
    }

    fieldnames = ["num_food_sources", *[f"score_avg_{mode}" for mode in modes_in_order]]

    with file_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for num_food_sources in food_source_sizes:
            row = {"num_food_sources": num_food_sources}
            for mode in modes_in_order:
                row[f"score_avg_{mode}"] = score_lookup.get(
                    (num_food_sources, mode),
                    "",
                )
            writer.writerow(row)