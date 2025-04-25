from abc import ABC, abstractmethod

class CheckoutProcess(ABC):
    def __init__(self, conn, user_id):
        self.conn = conn
        self.user_id = user_id

    @abstractmethod
    def fetch_cart_items(self, form_data):
        pass

    @abstractmethod
    def process_items(self, items):
        pass

    def calculate_totals(self, items):
        total = sum(item['subtotal'] for item in items)
        return total

    def apply_discount(self, total):
        if total >= 100:
            discount = round(total * 0.10, 2)
            total -= discount
            return total, discount
        return total, 0
