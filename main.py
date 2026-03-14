from src.problem import Sale, Product, ShoppingRequirement, ProblemInstance, Solution


def main():
    milk_sale = Sale(buy_qty=2, free_qty=2)

    milk = Product(
        id=1,
        name="Milk",
        category="Dairy",
        base_price=4.0,
        unit_volume=1.0,
        sale=milk_sale,
    )

    bread = Product(
        id=2,
        name="Bread",
        category="Bakery",
        base_price=3.5,
        unit_volume=0.8,
        sale=None,
    )

    requirement = ShoppingRequirement(
        category="Dairy",
        minimum=1,
        distinct_required=False,
    )

    instance = ProblemInstance(
        products=[milk, bread],
        cart_volume_limit=10.0,
        budget_limit=30.0,
        shopping_requirements=[requirement],
    )

    solution = Solution(quantities=[4, 1])

    print(milk)
    print(instance)
    print(solution)


if __name__ == "__main__":
    main()