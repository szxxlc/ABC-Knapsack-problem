from src.experiments import (
    run_multiple_experiments,
    save_run_results_to_csv,
    save_summary_to_csv,
)
from src.neighborhood import RandomNeighborMode
from src.instance_generator import generate_problem_instance
from src.evaluator import (
    calculate_score,
    calculate_total_volume,
    calculate_actual_cost,
    is_feasible,
    repair_hard_constraints,
)
import time


def main():
    program_start_time = time.time()
    
    instance = generate_problem_instance(
        num_products=10,
        cart_volume_limit=18.0,
        budget_limit=40.0,
        sale_probability=0.6,
        seed=42,
    )

    random_neighbor_modes: list[RandomNeighborMode] = [
        "increase",
        "decrease",
        "swap",
        "all",
    ]

    food_source_sizes: list[int] = [2, 4, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60, 80, 100]

    total_combinations = len(food_source_sizes) * len(random_neighbor_modes)
    current_combination = 0
    combination_times: list[float] = []

    print(f"Starting experiments: {total_combinations} combinations")
    print(f"Food source sizes: {food_source_sizes}")
    print(f"Random neighbor modes: {random_neighbor_modes}")
    print()

    for num_food_sources in food_source_sizes:
        for mode in random_neighbor_modes:
            current_combination += 1
            combination_start_time = time.time()

            summary = run_multiple_experiments(
                instance=instance,
                num_runs=10,
                base_seed=100,
                num_food_sources=num_food_sources,
                num_onlooker_bees=8,
                trial_limit=10,
                max_iterations=50,
                max_iterations_without_improvement=12,
                random_neighbor_mode=mode,
            )

            combination_duration = time.time() - combination_start_time
            combination_times.append(combination_duration)
            
            avg_time_per_combination = sum(combination_times) / len(combination_times)
            remaining_combinations = total_combinations - current_combination
            estimated_remaining_time = avg_time_per_combination * remaining_combinations
            
            progress_percent = (current_combination / total_combinations) * 100
            
            print(f"\n[{current_combination}/{total_combinations}] ({progress_percent:.1f}%)")
            print(f"Current: num_food_sources={num_food_sources}, mode={mode}")
            print(f"Combination time: {combination_duration:.2f}s | Avg time: {avg_time_per_combination:.2f}s")
            print(f"Estimated remaining time: {estimated_remaining_time:.1f}s (~{estimated_remaining_time/60:.1f} min)")

            print(f"=== NUM_FOOD_SOURCES: {num_food_sources} | RANDOM NEIGHBOR MODE: {mode.upper()} ===")
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
                    f"Random mode={result.random_neighbor_mode} | "
                    f"Num food sources={result.num_food_sources} | "
                    f"Score={result.best_score:.2f} | "
                    f"Savings={result.savings:.2f} | "
                    f"Penalty={result.shopping_penalty:.2f} | "
                    f"Feasible={result.hard_constraints_feasible} | "
                    f"Full list satisfied={result.shopping_requirements_fully_satisfied} | "
                    f"Iterations={result.iterations_completed} | "
                    f"Stopped early={result.stopped_early} | "
                    f"Time={result.execution_time_seconds:.4f}s"
                )

            mode_run_results_path = f"data/results/run_results_{num_food_sources}_{mode}.csv"
            mode_summary_path = f"data/results/summary_{num_food_sources}_{mode}.csv"

            save_run_results_to_csv(
                instance,
                summary.run_results,
                mode_run_results_path,
            )

            save_summary_to_csv(
                summary,
                mode_summary_path,
            )

            print()
            print(f"Results saved to {mode_run_results_path}")
            print(f"Summary saved to {mode_summary_path}")
            print()

    program_end_time = time.time()
    total_time = program_end_time - program_start_time
    
    print("\n" + "="*80)
    print("ALL EXPERIMENTS COMPLETED")
    print("="*80)
    print(f"Total time: {total_time:.2f}s (~{total_time/60:.2f} min)")
    print(f"Average time per combination: {sum(combination_times) / len(combination_times):.2f}s")
    print(f"Combinations executed: {total_combinations}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()