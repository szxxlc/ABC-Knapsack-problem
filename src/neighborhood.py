import random

from src.problem import ProblemInstance, ShoppingRequirement, Solution


def copy_solution(solution: Solution) -> Solution:
    return Solution(quantities=solution.quantities.copy())


def increase_quantity(
    solution: Solution,
    product_index: int,
    step: int = 1,
) -> Solution:
    if product_index < 0 or product_index >= len(solution.quantities):
        raise IndexError("Product index is out of range.")

    if step < 0:
        raise ValueError("Step must be non-negative.")

    new_solution = copy_solution(solution)
    new_solution.quantities[product_index] += step
    return new_solution


def decrease_quantity(
    solution: Solution,
    product_index: int,
    step: int = 1,
) -> Solution:
    if product_index < 0 or product_index >= len(solution.quantities):
        raise IndexError("Product index is out of range.")

    if step < 0:
        raise ValueError("Step must be non-negative.")

    new_solution = copy_solution(solution)
    new_quantity = new_solution.quantities[product_index] - step
    new_solution.quantities[product_index] = max(0, new_quantity)
    return new_solution


def swap_quantity_change(
    solution: Solution,
    increase_index: int,
    decrease_index: int,
    step: int = 1,
) -> Solution:
    if increase_index < 0 or increase_index >= len(solution.quantities):
        raise IndexError("Increase index is out of range.")

    if decrease_index < 0 or decrease_index >= len(solution.quantities):
        raise IndexError("Decrease index is out of range.")

    if increase_index == decrease_index:
        raise ValueError("Increase index and decrease index must be different.")

    if step < 0:
        raise ValueError("Step must be non-negative.")

    new_solution = copy_solution(solution)
    new_solution.quantities[increase_index] += step
    new_solution.quantities[decrease_index] = max(
        0,
        new_solution.quantities[decrease_index] - step,
    )
    return new_solution


def move_towards_sale_threshold(
    instance: ProblemInstance,
    solution: Solution,
    rng: random.Random,
) -> Solution:
    sale_product_indices = [
        index
        for index, product in enumerate(instance.products)
        if product.sale is not None
    ]

    if not sale_product_indices:
        return copy_solution(solution)

    product_index = rng.choice(sale_product_indices)
    product = instance.products[product_index]
    current_quantity = solution.quantities[product_index]

    bundle_size = product.sale.bundle_size
    sale_limit = product.sale.sale_limit

    if current_quantity >= sale_limit:
        return copy_solution(solution)

    remainder = current_quantity % bundle_size

    if remainder == 0:
        step = 1
    else:
        step = bundle_size - remainder

    max_possible_step = sale_limit - current_quantity
    step = min(step, max_possible_step)

    return increase_quantity(solution, product_index, step=step)


def add_product_from_category(
    instance: ProblemInstance,
    solution: Solution,
    category: str,
    rng: random.Random,
) -> Solution:
    matching_indices = [
        index
        for index, product in enumerate(instance.products)
        if product.category == category
    ]

    if not matching_indices:
        return copy_solution(solution)

    product_index = rng.choice(matching_indices)
    return increase_quantity(solution, product_index, step=1)


def add_product_for_requirement(
    instance: ProblemInstance,
    solution: Solution,
    requirement: ShoppingRequirement,
    rng: random.Random,
) -> Solution:
    matching_indices = [
        index
        for index, product in enumerate(instance.products)
        if product.category == requirement.category
    ]

    if not matching_indices:
        return copy_solution(solution)

    if requirement.distinct_required:
        not_yet_selected_indices = [
            index
            for index in matching_indices
            if solution.quantities[index] == 0
        ]

        if not_yet_selected_indices:
            product_index = rng.choice(not_yet_selected_indices)
            return increase_quantity(solution, product_index, step=1)

    product_index = rng.choice(matching_indices)
    return increase_quantity(solution, product_index, step=1)


def generate_random_neighbor(
    instance: ProblemInstance,
    solution: Solution,
    rng: random.Random,
) -> Solution:
    num_products = len(instance.products)

    if num_products == 0:
        return copy_solution(solution)

    move_type = rng.choice(["increase", "decrease", "swap"])

    if move_type == "increase":
        product_index = rng.randrange(num_products)
        return increase_quantity(solution, product_index, step=1)

    if move_type == "decrease":
        product_index = rng.randrange(num_products)
        return decrease_quantity(solution, product_index, step=1)

    if num_products == 1:
        product_index = 0
        return increase_quantity(solution, product_index, step=1)

    increase_index, decrease_index = rng.sample(range(num_products), 2)
    return swap_quantity_change(
        solution,
        increase_index=increase_index,
        decrease_index=decrease_index,
        step=1,
    )