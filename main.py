from src.problem import Sale, Product, ShoppingRequirement, ProblemInstance, Solution
from src.evaluator import (
    calculate_regular_cost,
    calculate_actual_cost,
    calculate_savings,
    calculate_total_volume,
    is_volume_feasible,
    is_budget_feasible,
    is_shopping_requirements_feasible,
    is_feasible,
)


def main():
    apple = Product(
        id=1,
        name="Apple",
        category="Fruit",
        base_price=2.0,
        unit_volume=0.3,
        sale=None,
    )

    banana = Product(
        id=2,
        name="Banana",
        category="Fruit",
        base_price=2.5,
        unit_volume=0.25,
        sale=None,
    )

    milk = Product(
        id=3,
        name="Milk",
        category="Dairy",
        base_price=4.0,
        unit_volume=1.0,
        sale=Sale(buy_qty=2, free_qty=2),
    )

    instance = ProblemInstance(
        products=[apple, banana, milk],
        cart_volume_limit=10.0,
        budget_limit=20.0,
        shopping_requirements=[
            ShoppingRequirement(category="Fruit", minimum=2, distinct_required=True),
            ShoppingRequirement(category="Dairy", minimum=1, distinct_required=False),
        ],
    )

    solution = Solution(quantities=[1, 1, 4])

    print("Regular cost:", calculate_regular_cost(instance, solution))
    print("Actual cost:", calculate_actual_cost(instance, solution))
    print("Savings:", calculate_savings(instance, solution))
    print("Total volume:", calculate_total_volume(instance, solution))

    print("\nVolume feasible:", is_volume_feasible(instance, solution))
    print("Budget feasible:", is_budget_feasible(instance, solution))
    print("Shopping requirements feasible:", is_shopping_requirements_feasible(instance, solution))
    print("Overall feasible:", is_feasible(instance, solution))


if __name__ == "__main__":
    main()