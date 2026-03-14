from src.problem import ProblemInstance, Product, Solution


def validate_solution(instance: ProblemInstance, solution: Solution) -> None:
    if len(solution.quantities) != len(instance.products):
        raise ValueError(
            "Solution length does not match number of products in the instance."
        )

    for quantity in solution.quantities:
        if quantity < 0:
            raise ValueError("Product quantity cannot be negative.")


def calculate_product_regular_cost(product: Product, quantity: int) -> float:
    if quantity < 0:
        raise ValueError("Product quantity cannot be negative.")

    return product.base_price * quantity


def calculate_product_actual_cost(product: Product, quantity: int) -> float:
    if quantity < 0:
        raise ValueError("Product quantity cannot be negative.")

    if product.sale is None:
        return product.base_price * quantity

    sale = product.sale
    bundle_size = sale.bundle_size
    sale_limit = sale.sale_limit

    promo_quantity = min(quantity, sale_limit)
    non_promo_quantity = quantity - promo_quantity

    full_bundles = promo_quantity // bundle_size
    remainder = promo_quantity % bundle_size

    promo_cost = full_bundles * sale.buy_qty * product.base_price
    remainder_cost = remainder * product.base_price
    non_promo_cost = non_promo_quantity * product.base_price

    return promo_cost + remainder_cost + non_promo_cost


def calculate_regular_cost(instance: ProblemInstance, solution: Solution) -> float:
    validate_solution(instance, solution)

    total = 0.0
    for product, quantity in zip(instance.products, solution.quantities):
        total += calculate_product_regular_cost(product, quantity)

    return total


def calculate_actual_cost(instance: ProblemInstance, solution: Solution) -> float:
    validate_solution(instance, solution)

    total = 0.0
    for product, quantity in zip(instance.products, solution.quantities):
        total += calculate_product_actual_cost(product, quantity)

    return total


def calculate_savings(instance: ProblemInstance, solution: Solution) -> float:
    regular_cost = calculate_regular_cost(instance, solution)
    actual_cost = calculate_actual_cost(instance, solution)

    return regular_cost - actual_cost


def calculate_total_volume(instance: ProblemInstance, solution: Solution) -> float:
    validate_solution(instance, solution)

    total = 0.0
    for product, quantity in zip(instance.products, solution.quantities):
        total += product.unit_volume * quantity

    return total