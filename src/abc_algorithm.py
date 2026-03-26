from dataclasses import dataclass, field
import random

from src.problem import ProblemInstance, Solution
from src.evaluator import (
    calculate_score,
    get_unsatisfied_requirements,
    is_feasible,
    repair_hard_constraints,
)
from src.neighborhood import (
    RandomNeighborMode,
    add_product_for_requirement,
    copy_solution,
    generate_random_neighbor,
    increase_quantity,
    move_towards_sale_threshold,
)


@dataclass
class FoodSource:
    solution: Solution
    score: float
    trials: int = 0


@dataclass
class ABCResult:
    best_solution: Solution
    best_score: float
    iterations_completed: int
    stopped_early: bool
    iterations_without_improvement: int
    best_score_history: list[float] = field(default_factory=list)


class ArtificialBeeColony:
    def __init__(
        self,
        instance: ProblemInstance,
        num_food_sources: int = 10,
        num_onlooker_bees: int = 10,
        trial_limit: int = 20,
        max_iterations: int = 100,
        max_iterations_without_improvement: int | None = None,
        seed: int | None = None,
        random_neighbor_mode: RandomNeighborMode = "all",
    ) -> None:
        self.instance = instance
        self.num_food_sources = num_food_sources
        self.num_onlooker_bees = num_onlooker_bees
        self.trial_limit = trial_limit
        self.max_iterations = max_iterations
        self.max_iterations_without_improvement = max_iterations_without_improvement
        self.rng = random.Random(seed)
        self.random_neighbor_mode = random_neighbor_mode

        self.food_sources: list[FoodSource] = []
        self.best_solution: Solution | None = None
        self.best_score: float = float("-inf")
        self.best_score_history: list[float] = []

    def optimize(self) -> ABCResult:
        self._initialize_food_sources()
        improved = self._update_best_solution()

        self.best_score_history = [self.best_score]
        iterations_without_improvement = 0
        iterations_completed = 0
        stopped_early = False

        if not improved:
            iterations_without_improvement = 0

        for _iteration in range(self.max_iterations):
            self._employed_bee_phase()
            self._onlooker_bee_phase()
            self._scout_bee_phase()

            improved = self._update_best_solution()
            iterations_completed += 1
            self.best_score_history.append(self.best_score)

            if improved:
                iterations_without_improvement = 0
            else:
                iterations_without_improvement += 1

            if (
                self.max_iterations_without_improvement is not None
                and iterations_without_improvement
                >= self.max_iterations_without_improvement
            ):
                stopped_early = True
                break

        return ABCResult(
            best_solution=copy_solution(self.best_solution),
            best_score=self.best_score,
            iterations_completed=iterations_completed,
            stopped_early=stopped_early,
            iterations_without_improvement=iterations_without_improvement,
            best_score_history=self.best_score_history.copy(),
        )

    def _initialize_food_sources(self) -> None:
        self.food_sources = []

        for _ in range(self.num_food_sources):
            source = self._create_random_food_source()
            self.food_sources.append(source)

    def _create_random_food_source(self) -> FoodSource:
        solution = self._generate_random_feasible_solution()
        score = calculate_score(self.instance, solution)
        return FoodSource(solution=solution, score=score, trials=0)

    def _generate_random_feasible_solution(self) -> Solution:
        solution = Solution(quantities=[0] * len(self.instance.products))

        max_steps = max(10, len(self.instance.products) * 4)

        for _ in range(max_steps):
            if len(self.instance.products) == 0:
                break

            product_index = self.rng.randrange(len(self.instance.products))
            candidate = increase_quantity(solution, product_index, step=1)
            candidate = repair_hard_constraints(self.instance, candidate)

            if is_feasible(self.instance, candidate):
                solution = candidate

            if self.rng.random() < 0.15:
                break

        return solution 
    

    def _generate_candidate_neighbor(self, solution: Solution) -> Solution:
        move_type = self.rng.choice(["random", "sale", "category"])

        if move_type == "random":
            return generate_random_neighbor(
                self.instance,
                solution,
                self.rng,
                mode=self.random_neighbor_mode,
            )

        if move_type == "sale":
            return move_towards_sale_threshold(self.instance, solution, self.rng)

        unsatisfied_requirements = get_unsatisfied_requirements(
            self.instance,
            solution,
        )

        if unsatisfied_requirements:
            requirement = self.rng.choice(unsatisfied_requirements)
            return add_product_for_requirement(
                self.instance,
                solution,
                requirement=requirement,
                rng=self.rng,
            )

        if self.instance.shopping_requirements:
            requirement = self.rng.choice(self.instance.shopping_requirements)
            return add_product_for_requirement(
                self.instance,
                solution,
                requirement=requirement,
                rng=self.rng,
            )

        return generate_random_neighbor(
            self.instance,
            solution,
            self.rng,
            mode=self.random_neighbor_mode,
        )

    def _try_to_improve_food_source(self, source_index: int) -> None:
        current_source = self.food_sources[source_index]
        candidate_solution = self._generate_candidate_neighbor(current_source.solution)
        candidate_solution = repair_hard_constraints(self.instance, candidate_solution)

        if not is_feasible(self.instance, candidate_solution):
            current_source.trials += 1
            return

        candidate_score = calculate_score(self.instance, candidate_solution)

        if candidate_score > current_source.score:
            self.food_sources[source_index] = FoodSource(
                solution=candidate_solution,
                score=candidate_score,
                trials=0,
            )
        else:
            current_source.trials += 1

    def _employed_bee_phase(self) -> None:
        for source_index in range(len(self.food_sources)):
            self._try_to_improve_food_source(source_index)

    def _onlooker_bee_phase(self) -> None:
        for _ in range(self.num_onlooker_bees):
            selected_index = self._select_food_source_index()
            self._try_to_improve_food_source(selected_index)

    def _scout_bee_phase(self) -> None:
        for source_index, source in enumerate(self.food_sources):
            if source.trials >= self.trial_limit:
                self.food_sources[source_index] = self._create_random_food_source()

    def _select_food_source_index(self) -> int:
        scores = [source.score for source in self.food_sources]

        min_score = min(scores)
        weights = [(score - min_score) + 1.0 for score in scores]

        return self.rng.choices(
            population=range(len(self.food_sources)),
            weights=weights,
            k=1,
        )[0]

    def _update_best_solution(self) -> bool:
        improved = False

        for source in self.food_sources:
            if source.score > self.best_score:
                self.best_score = source.score
                self.best_solution = copy_solution(source.solution)
                improved = True

        return improved