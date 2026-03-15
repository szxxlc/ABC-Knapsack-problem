from dataclasses import asdict, dataclass, field
from pathlib import Path
import csv
import time

from src.abc_algorithm import ArtificialBeeColony
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
    best_score_min: float = 0.0
    best_score_max: float = 0.0
    best_score_avg: float = 0.0
    savings_min: float = 0.0
    savings_max: float = 0.0
    savings_avg: float = 0.0
    penalty_min: float = 0.0
    penalty_max: float = 0.0
    penalty_avg: float = 0.0
    execution_time_min: float = 0.0
    execution_time_max: float = 0.0
    execution_time_avg: float = 0.0
    fully_satisfied_count: int = 0
    feasible_count: int = 0


def run_single_experiment(
    instance: ProblemInstance,
    run_index: int,
    seed: int,
    num_food_sources: int,
    num_onlooker_bees: int,
    trial_limit: int,
    max_iterations: int,
    max_iterations_without_improvement: int | None = None,
) -> SingleRunResult:
    abc = ArtificialBeeColony(
        instance=instance,
        num_food_sources=num_food_sources,
        num_onlooker_bees=num_onlooker_bees,
        trial_limit=trial_limit,
        max_iterations=max_iterations,
        max_iterations_without_improvement=max_iterations_without_improvement,
        seed=seed,
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


def summarize_results(run_results: list[SingleRunResult]) -> ExperimentSummary:
    if not run_results:
        return ExperimentSummary()

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

    return ExperimentSummary(
        run_results=run_results,
        best_score_min=min(best_scores),
        best_score_max=max(best_scores),
        best_score_avg=sum(best_scores) / len(best_scores),
        savings_min=min(savings_values),
        savings_max=max(savings_values),
        savings_avg=sum(savings_values) / len(savings_values),
        penalty_min=min(penalty_values),
        penalty_max=max(penalty_values),
        penalty_avg=sum(penalty_values) / len(penalty_values),
        execution_time_min=min(execution_times),
        execution_time_max=max(execution_times),
        execution_time_avg=sum(execution_times) / len(execution_times),
        fully_satisfied_count=fully_satisfied_count,
        feasible_count=feasible_count,
    )


def run_multiple_experiments(
    instance: ProblemInstance,
    num_runs: int,
    base_seed: int,
    num_food_sources: int,
    num_onlooker_bees: int,
    trial_limit: int,
    max_iterations: int,
    max_iterations_without_improvement: int | None = None,
) -> ExperimentSummary:
    run_results: list[SingleRunResult] = []

    for run_index in range(num_runs):
        seed = base_seed + run_index

        run_result = run_single_experiment(
            instance=instance,
            run_index=run_index,
            seed=seed,
            num_food_sources=num_food_sources,
            num_onlooker_bees=num_onlooker_bees,
            trial_limit=trial_limit,
            max_iterations=max_iterations,
            max_iterations_without_improvement=max_iterations_without_improvement,
        )
        run_results.append(run_result)

    return summarize_results(run_results)


def _single_run_result_to_row(result: SingleRunResult) -> dict:
    return {
        "run_index": result.run_index,
        "seed": result.seed,
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
    run_results: list[SingleRunResult],
    file_path: str | Path,
) -> None:
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if not run_results:
        return

    rows = [_single_run_result_to_row(result) for result in run_results]
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