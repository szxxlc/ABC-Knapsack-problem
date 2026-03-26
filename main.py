from src.experiments import (
    run_multiple_experiments,
    save_run_results_to_csv,
    save_summary_to_csv,
)
from src.instance_generator import generate_problem_instance
from src.evaluator import (
    calculate_score,
    calculate_total_volume,
    calculate_actual_cost,
    is_feasible,
    repair_hard_constraints,
)


def main():
    instance = generate_problem_instance(
        num_products=10,
        cart_volume_limit=18.0,
        budget_limit=40.0,
        sale_probability=0.6,
        seed=42,
    )

    summary = run_multiple_experiments(
        instance=instance,
        num_runs=10,
        base_seed=100,
        num_food_sources=8,
        num_onlooker_bees=8,
        trial_limit=10,
        max_iterations=50,
        max_iterations_without_improvement=12,
    )

    print("=== INSTANCE METADATA ===")
    print(f"Number of products: {summary.instance_num_products}")
    print(f"Cart volume limit: {summary.instance_cart_volume_limit:.2f}")
    print(f"Budget limit: {summary.instance_budget_limit}")
    print(f"Number of requirements: {summary.instance_num_requirements}")
    print(f"Products with sale: {summary.instance_num_products_with_sale}")
    print(f"Products without sale: {summary.instance_num_products_without_sale}")
    print()

    print("=== BEST SCORE STATISTICS ===")
    print(f"Min: {summary.best_score_min:.2f}")
    print(f"Max: {summary.best_score_max:.2f}")
    print(f"Avg: {summary.best_score_avg:.2f}")
    print(f"Median: {summary.best_score_median:.2f}")
    print(f"Std: {summary.best_score_std:.2f}")
    print()

    print("=== SAVINGS STATISTICS ===")
    print(f"Min: {summary.savings_min:.2f}")
    print(f"Max: {summary.savings_max:.2f}")
    print(f"Avg: {summary.savings_avg:.2f}")
    print(f"Median: {summary.savings_median:.2f}")
    print(f"Std: {summary.savings_std:.2f}")
    print()

    print("=== PENALTY STATISTICS ===")
    print(f"Min: {summary.penalty_min:.2f}")
    print(f"Max: {summary.penalty_max:.2f}")
    print(f"Avg: {summary.penalty_avg:.2f}")
    print(f"Median: {summary.penalty_median:.2f}")
    print(f"Std: {summary.penalty_std:.2f}")
    print()

    print("=== EXECUTION TIME STATISTICS ===")
    print(f"Min: {summary.execution_time_min:.4f} s")
    print(f"Max: {summary.execution_time_max:.4f} s")
    print(f"Avg: {summary.execution_time_avg:.4f} s")
    print(f"Median: {summary.execution_time_median:.4f} s")
    print(f"Std: {summary.execution_time_std:.4f} s")
    print()

    print(f"Feasible count: {summary.feasible_count}/{len(summary.run_results)}")
    print(
        "Fully satisfied shopping list count: "
        f"{summary.fully_satisfied_count}/{len(summary.run_results)}"
    )
    print()

    print("=== BEST RUN ===")
    print(f"Best run index: {summary.best_run_index}")
    print(f"Best run seed: {summary.best_run_seed}")
    print(f"Best run score: {summary.best_run_score:.2f}")
    print()

    print("=== SINGLE RUN RESULTS ===")
    for result in summary.run_results:
        print(
            f"Run {result.run_index} | "
            f"Seed={result.seed} | "
            f"Score={result.best_score:.2f} | "
            f"Savings={result.savings:.2f} | "
            f"Penalty={result.shopping_penalty:.2f} | "
            f"Feasible={result.hard_constraints_feasible} | "
            f"Full list satisfied={result.shopping_requirements_fully_satisfied} | "
            f"Iterations={result.iterations_completed} | "
            f"Stopped early={result.stopped_early} | "
            f"Time={result.execution_time_seconds:.4f}s"
        )

    save_run_results_to_csv(
        instance,
        summary.run_results,
        "data/results/run_results.csv",
    )

    save_summary_to_csv(
        summary,
        "data/results/summary.csv",
    )

    print()
    print("Results saved to data/results/run_results.csv")
    print("Summary saved to data/results/summary.csv")


if __name__ == "__main__":
    main()