from src.experiment_runner import ExperimentRunner
from src.neighborhood import RandomNeighborMode
from src.instance_generator import generate_problem_instance


def main():
    instance_seeds: list[int] = list(range(42, 42+50))
    instances_with_seeds = [
        (
            instance_seed,
            generate_problem_instance(
                num_products=50,
                cart_volume_limit=25.0,
                budget_limit=75.0,
                sale_probability=0.75,
                min_requirements=4,
                max_requirements=5,
                max_requirement_minimum=4,
                min_penalty_per_missing=5.0,
                max_penalty_per_missing=20.0,
                seed=instance_seed,
            ),
        )
        for instance_seed in instance_seeds
    ]

    random_neighbor_modes: list[RandomNeighborMode] = [
        "increase",
        "decrease",
        "swap",
        "all",
    ]

    food_source_sizes: list[int] = [2, 4, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60, 80, 100]
    NUMBER_OF_RUNS = 25

    runner = ExperimentRunner(
        num_runs=NUMBER_OF_RUNS,
        base_seed=100,
        num_onlooker_bees=12,
        trial_limit=15,
        max_iterations=80,
        max_iterations_without_improvement=20,
    )

    runner.run_all_experiments(
        instances_with_seeds=instances_with_seeds,
        food_source_sizes=food_source_sizes,
        random_neighbor_modes=random_neighbor_modes,
    )


if __name__ == "__main__":
    main()