from src.problem import Sale, Product, ShoppingRequirement, ProblemInstance, Solution
from src.evaluator import (
    calculate_product_actual_cost,
    calculate_regular_cost,
    calculate_actual_cost,
    calculate_savings,
    calculate_total_volume,
)


def main():
    milk = Product(
        id=1,
        name="Milk",
        category="Dairy",
        base_price=4.0,
        unit_volume=1.0,
        sale=Sale(buy_qty=2, free_qty=2),
    )

    bread = Product(
        id=2,
        name="Bread",
        category="Bakery",
        base_price=3.5,
        unit_volume=0.8,
        sale=None,
    )

    instance = ProblemInstance(
        products=[milk, bread],
        cart_volume_limit=20.0,
        budget_limit=30.0,
        shopping_requirements=[
            ShoppingRequirement(category="Dairy", minimum=1, distinct_required=False)
        ],
    )

    solution = Solution(quantities=[6, 1])
    
    print("Milk actual cost:", calculate_product_actual_cost(milk, 6))
    print("\nRegular cost:", calculate_regular_cost(instance, solution))
    print("Actual cost:", calculate_actual_cost(instance, solution))
    print("Savings:", calculate_savings(instance, solution))
    print("Total volume:", calculate_total_volume(instance, solution))


if __name__ == "__main__":
    main()