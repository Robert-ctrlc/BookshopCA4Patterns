class Order:
    def __init__(self):
        self.user_id = None
        self.items = []
        self.total = 0
        self.discount_applied = False
        self.discount_amount = 0
        self.loyalty_discount = 0

class OrderBuilder:
    def __init__(self):
        self.order = Order()

    def set_user(self, user_id):
        self.order.user_id = user_id
        return self

    def add_item(self, book, quantity):
        subtotal = book.price * quantity
        self.order.items.append({'book': book, 'quantity': quantity, 'subtotal': subtotal})
        self.order.total += subtotal
        return self

    def apply_discount(self):
        if self.order.total >= 100:
            self.order.discount_applied = True
            self.order.discount_amount = round(self.order.total * 0.10, 2)
            self.order.total -= self.order.discount_amount
        return self

    def apply_loyalty_discount(self, order_count):
        if order_count % 3 == 0:
            self.order.loyalty_discount = 5
            self.order.total -= 5
        return self

    def build(self):
        return self.order
