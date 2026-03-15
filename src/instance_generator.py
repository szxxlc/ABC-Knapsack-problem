import random
from typing import Optional

from src.problem import ProblemInstance, Product, Sale, ShoppingRequirement


CATEGORY_PRODUCT_NAMES = {
    "Fruit": ["Apple", "Banana", "Pear", "Orange", "Grapes", "Kiwi", "Watermelon", "Dragonfruit"],
    "Vegetables": ["Tomato", "Cucumber", "Carrot", "Pepper", "Onion", "Lettuce", "Cauliflower", "Potato"],
    "Dairy": ["Milk", "Yogurt", "Cheese", "Butter", "Cream", "Kefir", "Cottage Cheese"],
    "Bakery": ["Bread", "Roll", "Baguette", "Toast", "Croissant", "Bagel"],
    "Beverages": ["Water", "Juice", "Tea", "Coffee", "Cola", "Lemonade", "Beer"],
}

AVAILABLE_SALES = [
    (1, 1),
    (2, 1),
    (2, 2),
    (3, 1),
]


def generate_random_sale(
    rng: random.Random,
    sale_probability: float = 0.5,
) -> Optional[Sale]:
    if rng.random() > sale_probability:
        return None

    buy_qty, free_qty = rng.choice(AVAILABLE_SALES)
    return Sale(buy_qty=buy_qty, free_qty=free_qty)


def generate_random_product(
    product_id: int,
    name: str,
    category: str,
    rng: random.Random,
    sale_probability: float = 0.5,
) -> Product:
    base_price = round(rng.uniform(2.0, 15.0), 2)
    unit_volume = round(rng.uniform(0.2, 2.5), 2)
    sale = generate_random_sale(rng, sale_probability)

    return Product(
        id=product_id,
        name=name,
        category=category,
        base_price=base_price,
        unit_volume=unit_volume,
        sale=sale,
    )


def generate_products(
    num_products: int,
    rng: random.Random,
    sale_probability: float = 0.5,
) -> list[Product]:
    all_product_candidates: list[tuple[str, str]] = []

    for category, names in CATEGORY_PRODUCT_NAMES.items():
        for name in names:
            all_product_candidates.append((name, category))

    if num_products > len(all_product_candidates):
        raise ValueError(
            "Requested number of products exceeds available unique product names."
        )

    selected_candidates = rng.sample(all_product_candidates, num_products)

    products = []
    for product_id, (name, category) in enumerate(selected_candidates, start=1):
        product = generate_random_product(
            product_id=product_id,
            name=name,
            category=category,
            rng=rng,
            sale_probability=sale_probability,
        )
        products.append(product)

    return products


def generate_shopping_requirements(
    products: list[Product],
    rng: random.Random,
    min_requirements: int = 2,
    max_requirements: int = 4,
    max_minimum: int = 3,
) -> list[ShoppingRequirement]:
    available_categories = sorted({product.category for product in products})

    if not available_categories:
        return []

    requirement_count = rng.randint(
        min(min_requirements, len(available_categories)),
        min(max_requirements, len(available_categories)),
    )

    selected_categories = rng.sample(available_categories, requirement_count)

    requirements = []
    for category in selected_categories:
        minimum = rng.randint(1, max_minimum)
        distinct_required = rng.choice([True, False])
        penalty_per_missing = round(rng.uniform(1.0, 5.0), 2)

        requirement = ShoppingRequirement(
            category=category,
            minimum=minimum,
            distinct_required=distinct_required,
            penalty_per_missing=penalty_per_missing,
        )
        requirements.append(requirement)

    return requirements


def generate_problem_instance(
    num_products: int,
    cart_volume_limit: float,
    budget_limit: Optional[float] = None,
    sale_probability: float = 0.5,
    seed: Optional[int] = None,
) -> ProblemInstance:
    rng = random.Random(seed)

    products = generate_products(
        num_products=num_products,
        rng=rng,
        sale_probability=sale_probability,
    )

    shopping_requirements = generate_shopping_requirements(
        products=products,
        rng=rng,
    )

    return ProblemInstance(
        products=products,
        cart_volume_limit=cart_volume_limit,
        budget_limit=budget_limit,
        shopping_requirements=shopping_requirements,
    )