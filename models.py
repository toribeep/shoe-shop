from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: int
    role: str
    full_name: str
    login: str
    password: str

@dataclass
class Product:
    article: str
    name: str
    unit: str
    price: float
    supplier: str
    manufacturer: str
    category: str
    discount: float
    quantity: int
    description: str
    photo: Optional[str] = None

@dataclass
class Order:
    order_number: int
    order_articles: str
    order_date: datetime
    delivery_date: datetime
    pickup_address: int
    client_name: str
    pickup_code: str
    status: str

@dataclass
class PickupPoint:
    id : int
    address: str