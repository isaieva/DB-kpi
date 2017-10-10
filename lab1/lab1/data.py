class Product:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price

    def __str__(self):
        return "'{1}' #{0:d}, {2:d}$".format(self.id, self.name, self.price)

class Order:
    def __init__(self, id, client_name, client_address):
        self.id=id
        self.client_name = client_name
        self.client_address = client_address

    def __str__(self):
        return  "Order #{:d} for {}, deliver to {}".format(self.id, self.client_name, self.client_address)

class ProductOrder:
    def __init__(self, product_id, order_id, quantity):
        self.product_id = product_id
        self.order_id = order_id
        self.quantity = quantity

    def __str__(self):
        return str((self.product_id, self.order_id, self.quantity))
