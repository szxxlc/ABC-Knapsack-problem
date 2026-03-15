from src.problem import ProblemInstance, ShoppingRequirement, Product, Solution


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


def count_total_items_in_category(
    instance: ProblemInstance,
    solution: Solution,
    category: str,
) -> int:
    validate_solution(instance, solution)

    total = 0
    for product, quantity in zip(instance.products, solution.quantities):
        if product.category == category:
            total += quantity

    return total


def count_distinct_products_in_category(
    instance: ProblemInstance,
    solution: Solution,
    category: str,
) -> int:
    validate_solution(instance, solution)

    count = 0
    for product, quantity in zip(instance.products, solution.quantities):
        if product.category == category and quantity > 0:
            count += 1

    return count


def is_volume_feasible(instance: ProblemInstance, solution: Solution) -> bool:
    total_volume = calculate_total_volume(instance, solution)
    return total_volume <= instance.cart_volume_limit


def is_budget_feasible(instance: ProblemInstance, solution: Solution) -> bool:
    if instance.budget_limit is None:
        return True

    actual_cost = calculate_actual_cost(instance, solution)
    return actual_cost <= instance.budget_limit


def get_requirement_shortage(
    instance: ProblemInstance,
    solution: Solution,
    requirement: ShoppingRequirement,
) -> int:
    validate_solution(instance, solution)

    if requirement.distinct_required:
        current_value = count_distinct_products_in_category(
            instance,
            solution,
            requirement.category,
        )
    else:
        current_value = count_total_items_in_category(
            instance,
            solution,
            requirement.category,
        )

    return max(0, requirement.minimum - current_value)


def calculate_requirement_penalty(
    instance: ProblemInstance,
    solution: Solution,
    requirement: ShoppingRequirement,
) -> float:
    shortage = get_requirement_shortage(instance, solution, requirement)
    return shortage * requirement.penalty_per_missing


def calculate_shopping_penalty(
    instance: ProblemInstance,
    solution: Solution,
) -> float:
    validate_solution(instance, solution)

    total_penalty = 0.0

    for requirement in instance.shopping_requirements:
        total_penalty += calculate_requirement_penalty(
            instance,
            solution,
            requirement,
        )

    return total_penalty


def calculate_score(instance: ProblemInstance, solution: Solution) -> float:
    savings = calculate_savings(instance, solution)
    shopping_penalty = calculate_shopping_penalty(instance, solution)

    return savings - shopping_penalty


def are_shopping_requirements_fully_satisfied(
    instance: ProblemInstance,
    solution: Solution,
) -> bool:
    validate_solution(instance, solution)

    for requirement in instance.shopping_requirements:
        if get_requirement_shortage(instance, solution, requirement) > 0:
            return False

    return True


def is_feasible(instance: ProblemInstance, solution: Solution) -> bool:
    return (
        is_volume_feasible(instance, solution)
        and is_budget_feasible(instance, solution)
    )
    
def get_unsatisfied_requirements(
    instance: ProblemInstance,
    solution: Solution,
) -> list[ShoppingRequirement]:
    validate_solution(instance, solution)

    unsatisfied = []

    for requirement in instance.shopping_requirements:
        if get_requirement_shortage(instance, solution, requirement) > 0:
            unsatisfied.append(requirement)

    return unsatisfied

from src.problem import ProblemInstance, Product, ShoppingRequirement, Solution


def copy_solution(solution: Solution) -> Solution:
    return Solution(quantities=solution.quantities.copy())


def remove_one_unit(solution: Solution, product_index: int) -> Solution:
    if product_index < 0 or product_index >= len(solution.quantities):
        raise IndexError("Product index is out of range.")

    new_solution = copy_solution(solution)
    new_solution.quantities[product_index] = max(
        0,
        new_solution.quantities[product_index] - 1,
    )
    return new_solution


def calculate_score_loss_after_removal(
    instance: ProblemInstance,
    solution: Solution,
    product_index: int,
) -> float:
    if solution.quantities[product_index] <= 0:
        return float("inf")

    current_score = calculate_score(instance, solution)
    candidate_solution = remove_one_unit(solution, product_index)
    candidate_score = calculate_score(instance, candidate_solution)

    return current_score - candidate_score


def select_best_product_to_remove(
    instance: ProblemInstance,
    solution: Solution,
) -> int | None:
    best_index = None
    best_loss = float("inf")

    for product_index, quantity in enumerate(solution.quantities):
        if quantity <= 0:
            continue

        loss = calculate_score_loss_after_removal(
            instance,
            solution,
            product_index,
        )

        if loss < best_loss:
            best_loss = loss
            best_index = product_index

    return best_index


def repair_hard_constraints(
    instance: ProblemInstance,
    solution: Solution,
) -> Solution:
    validate_solution(instance, solution)

    repaired = copy_solution(solution)

    while not is_feasible(instance, repaired):
        product_index = select_best_product_to_remove(instance, repaired)

        if product_index is None:
            break

        repaired = remove_one_unit(repaired, product_index)

    return repaired