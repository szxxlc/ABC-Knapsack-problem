from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Sale:
    buy_qty: int
    free_qty: int

    @property
    def bundle_size(self) -> int:
        return self.buy_qty + self.free_qty

    @property
    def sale_limit(self) -> int:
        return 2 * self.bundle_size


@dataclass
class Product:
    id: int
    name: str
    category: str
    base_price: float
    unit_volume: float
    sale: Optional[Sale] = None


@dataclass
class ShoppingRequirement:
    category: str
    minimum: int = 1
    distinct_required: bool = False
    
@dataclass
class ProblemInstance:
    products: list[Product]
    cart_volume_limit: float
    budget_limit: Optional[float] = None
    shopping_requirements: list[ShoppingRequirement] = field(default_factory=list)
    
@dataclass
class Solution:
    quantities: list[int]