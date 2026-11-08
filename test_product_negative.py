import time
from datetime import datetime, timedelta

from database import Database
from models import Order


def test_add_order_negative():
    print("Запуск негативного теста создания заказа...")

    db = Database()

    order_number = db.get_max_order_number() + 1

    order = Order(
        order_number=order_number,
        order_articles="F635R4, 2, H782T5",
        order_date=datetime.now(),
        delivery_date=datetime.now() + timedelta(days=3),
        pickup_address=3,
        client_name="Test Client",
        pickup_code=f"TEST-{int(time.time())}",
        status="Новый"
    )

    try:
        db.add_order(order)

        created = db.fetch_one(
            "SELECT order_number FROM orders WHERE order_number = %s",
            (order_number,)
        )

        if created is not None:
            raise Exception(
                "ДЕФЕКТ: заказ был создан при некорректном формате поля order_articles"
            )

        print("Негативный тест пройден: заказ не был создан при некорректных данных.")

    finally:
        db.delete_order(order_number)
        print("Очистка тестовых данных выполнена.")


if __name__ == "__main__":
    test_add_order_negative()
