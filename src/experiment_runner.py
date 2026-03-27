import time
from src.experiments import (
    ExperimentSummary,
    run_multiple_experiments,
    save_run_results_to_csv,
    save_summary_to_csv,
    save_score_plot_data_to_csv,
    save_score_plot_pivot_to_csv,
)
from src.neighborhood import RandomNeighborMode
from src.problem import ProblemInstance


class ExperimentRunner:
    """Orchestrates running multiple ABC experiments with different configurations."""

    def __init__(
        self,
        num_runs: int = 10,
        base_seed: int = 100,
        num_onlooker_bees: int = 8,
        trial_limit: int = 10,
        max_iterations: int = 50,
        max_iterations_without_improvement: int = 12,
    ):
        self.num_runs = num_runs
        self.base_seed = base_seed
        self.num_onlooker_bees = num_onlooker_bees
        self.trial_limit = trial_limit
        self.max_iterations = max_iterations
        self.max_iterations_without_improvement = max_iterations_without_improvement

    def run_all_experiments(
        self,
        instance: ProblemInstance,
        food_source_sizes: list[int],
        random_neighbor_modes: list[RandomNeighborMode],
    ) -> None:
        """Run all experiment combinations and log progress."""
        program_start_time = time.time()
        total_combinations = len(food_source_sizes) * len(random_neighbor_modes)
        current_combination = 0
        combination_times: list[float] = []
        all_summaries: list[ExperimentSummary] = []

        print(f"Starting experiments: {total_combinations} combinations")
        print(f"Food source sizes: {food_source_sizes}")
        print(f"Random neighbor modes: {random_neighbor_modes}")
        print()

        for num_food_sources in food_source_sizes:
            for mode in random_neighbor_modes:
                current_combination += 1
                combination_start_time = time.time()

                summary = self._run_experiment(
                    instance,
                    num_food_sources,
                    mode,
                )
                all_summaries.append(summary)
                self._save_detailed_results(summary, num_food_sources, mode, instance)

                combination_duration = time.time() - combination_start_time
                combination_times.append(combination_duration)

                self._print_progress(
                    current_combination,
                    total_combinations,
                    combination_duration,
                    combination_times,
                    num_food_sources,
                    mode,
                )

        self._save_aggregated_results(all_summaries)

        program_end_time = time.time()
        total_time = program_end_time - program_start_time
        self._print_final_summary(total_time, combination_times, total_combinations)

    def _run_experiment(
        self,
        instance: ProblemInstance,
        num_food_sources: int,
        mode: RandomNeighborMode,
    ) -> ExperimentSummary:
        """Run a single experiment configuration and return summary."""
        summary = run_multiple_experiments(
            instance=instance,
            num_runs=self.num_runs,
            base_seed=self.base_seed,
            num_food_sources=num_food_sources,
            num_onlooker_bees=self.num_onlooker_bees,
            trial_limit=self.trial_limit,
            max_iterations=self.max_iterations,
            max_iterations_without_improvement=self.max_iterations_without_improvement,
            random_neighbor_mode=mode,
        )

        # self._print_detailed_results(summary, num_food_sources, mode)
        return summary

    def _print_progress(
        self,
        current: int,
        total: int,
        duration: float,
        all_durations: list[float],
        num_food_sources: int,
        mode: str,
    ) -> None:
        """Print progress information."""
        avg_time = sum(all_durations) / len(all_durations)
        remaining = total - current
        estimated_remaining = avg_time * remaining

        progress_percent = (current / total) * 100

        print(f"\n[{current}/{total}] ({progress_percent:.1f}%)")
        print(f"Current: num_food_sources={num_food_sources}, mode={mode}")
        print(f"Combination time: {duration:.2f}s | Avg time: {avg_time:.2f}s")
        print(f"Estimated remaining time: {estimated_remaining:.1f}s (~{estimated_remaining/60:.1f} min)")

    def _print_detailed_results(
        self,
        summary,
        num_food_sources: int,
        mode: str,
    ) -> None:
        """Print detailed experiment results."""
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
        print()

    def _save_aggregated_results(
        self,
        summaries: list[ExperimentSummary],
    ) -> None:
        """Save compact experiment data to a small number of CSV files."""
        long_format_path = "data/aggregated_results/score_by_mode_food_source.csv"
        pivot_format_path = "data/aggregated_results/score_by_mode_food_source_pivot.csv"

        save_score_plot_data_to_csv(
            summaries,
            long_format_path,
        )

        save_score_plot_pivot_to_csv(
            summaries,
            pivot_format_path,
        )

        print(f"Aggregated plotting data saved to {long_format_path}")
        print(f"Pivot plotting data saved to {pivot_format_path}")

    def _save_detailed_results(
        self,
        summary,
        num_food_sources: int,
        mode: str,
        instance: ProblemInstance,
    ) -> None:
        """Save detailed per-combination files as backup data."""
        mode_run_results_path = (
            f"data/detailed_results/run_results/run_results_{num_food_sources}_{mode}.csv"
        )
        mode_summary_path = (
            f"data/detailed_results/summary/summary_{num_food_sources}_{mode}.csv"
        )

        save_run_results_to_csv(
            instance,
            summary.run_results,
            mode_run_results_path,
        )

        save_summary_to_csv(
            summary,
            mode_summary_path,
        )

        print(f"Detailed results saved to {mode_run_results_path}")
        print(f"Detailed summary saved to {mode_summary_path}")

    def _print_final_summary(
        self,
        total_time: float,
        combination_times: list[float],
        total_combinations: int,
    ) -> None:
        """Print final experiment summary."""
        print("\n" + "=" * 80)
        print("ALL EXPERIMENTS COMPLETED")
        print("=" * 80)
        print(f"Total time: {total_time:.2f}s (~{total_time/60:.2f} min)")
        print(f"Average time per combination: {sum(combination_times) / len(combination_times):.2f}s")
        print(f"Combinations executed: {total_combinations}")
        print("=" * 80 + "\n")
