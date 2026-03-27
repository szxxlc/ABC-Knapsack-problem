from src.experiment_runner import ExperimentRunner
from src.neighborhood import RandomNeighborMode
from src.instance_generator import generate_problem_instance


def main():
    # Generate problem instance
    instance = generate_problem_instance(
        num_products=10,
        cart_volume_limit=18.0,
        budget_limit=40.0,
        sale_probability=0.6,
        seed=42,
    )

    # Define experiment parameters
    random_neighbor_modes: list[RandomNeighborMode] = [
        "increase",
        "decrease",
        "swap",
        "all",
    ]

    # food_source_sizes: list[int] = [2, 4, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60, 80, 100]
    food_source_sizes: list[int] = [2, 4, 6, 8, 10, 12, 15]
    NUMBER_OF_RUNS = 50

    # Initialize and run experiments
    runner = ExperimentRunner(
        num_runs=NUMBER_OF_RUNS,
        base_seed=100,
        num_onlooker_bees=8,
        trial_limit=10,
        max_iterations=50,
        max_iterations_without_improvement=12,
    )

    runner.run_all_experiments(
        instance=instance,
        food_source_sizes=food_source_sizes,
        random_neighbor_modes=random_neighbor_modes,
    )


if __name__ == "__main__":
    main()