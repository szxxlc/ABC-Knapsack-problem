from src.problem import Product, Sale, ShoppingRequirement, ProblemInstance, Solution
from src.evaluator import (
    calculate_savings,
    calculate_shopping_penalty,
    calculate_score,
    are_shopping_requirements_fully_satisfied,
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
            ShoppingRequirement(
                category="Fruit",
                minimum=2,
                distinct_required=True,
                penalty_per_missing=3.0,
            ),
            ShoppingRequirement(
                category="Dairy",
                minimum=2,
                distinct_required=False,
                penalty_per_missing=1.5,
            ),
        ],
    )

    solution = Solution(quantities=[1, 0, 1])

    print("Savings:", calculate_savings(instance, solution))
    print("Shopping penalty:", calculate_shopping_penalty(instance, solution))
    print("Score:", calculate_score(instance, solution))
    print("Shopping list fully satisfied:", are_shopping_requirements_fully_satisfied(instance, solution))
    print("Hard constraints feasible:", is_feasible(instance, solution))


if __name__ == "__main__":
    main()