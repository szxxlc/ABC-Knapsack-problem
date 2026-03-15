from src.problem import Solution
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
        num_products=8,
        cart_volume_limit=15.0,
        budget_limit=100.0,
        sale_probability=0.6,
        seed=42,
    )

    solution = Solution(quantities=[2, 1, 2, 1, 2, 1, 2, 1])

    print("=== BEFORE REPAIR ===")
    print("Quantities:", solution.quantities)
    print(f"Actual cost: {calculate_actual_cost(instance, solution):.2f}")
    print(f"Total volume: {calculate_total_volume(instance, solution):.2f}")
    print(f"Score: {calculate_score(instance, solution):.2f}")
    print("Feasible:", is_feasible(instance, solution))
    print()

    repaired = repair_hard_constraints(instance, solution)

    print("=== AFTER REPAIR ===")
    print("Quantities:", repaired.quantities)
    print(f"Actual cost: {calculate_actual_cost(instance, repaired):.2f}")
    print(f"Total volume: {calculate_total_volume(instance, repaired):.2f}")
    print(f"Score: {calculate_score(instance, repaired):.2f}")
    print("Feasible:", is_feasible(instance, repaired))


if __name__ == "__main__":
    main()