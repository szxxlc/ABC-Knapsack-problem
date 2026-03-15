from src.instance_generator import generate_problem_instance


def main():
    instance = generate_problem_instance(
        num_products=8,
        cart_volume_limit=20.0,
        budget_limit=50.0,
        sale_probability=0.5,
        seed=42,
    )

    print("Products:")
    for product in instance.products:
        print(product)

    print("\nShopping requirements:")
    for requirement in instance.shopping_requirements:
        print(requirement)

    print("\nCart volume limit:", instance.cart_volume_limit)
    print("Budget limit:", instance.budget_limit)


if __name__ == "__main__":
    main()