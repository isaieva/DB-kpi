from lab1.data import *
from lab1.error import *

from pickle import dump, load

class DB:
    def __init__(self):
        self.product_counter = 0
        self.order_counter = 0

        self.product = []
        self.order = []
        self.product_order = []

    def find_costly(self):
        return [
            (p, o, po.quantity)
            for po in self.product_order
            for p  in self.product if p.id == po.product_id
            for o  in self.order   if o.id == po.order_id
            if po.quantity * p.price >= 100
        ]

    def add_product(self, name, price):
        p = Product(self.product_counter, name, price)
        self.product_counter += 1
        self.product.append(p)
        return p

    def get_product(self, product_id):
        p = [r for r in self.product if r.id is product_id]
        if not p:
            raise NoRowException()
        elif len(p) is not 1:
            raise Exception("Non-unique product id in base!")
        else:
            return p[0]

    def update_product(self, product):
        p = self.get_product(product.id)
        p.name = product.name
        p.price = product.price

    def add_order(self, client_name, client_address):
        o = Order(self.order_counter, client_name, client_address)
        self.order_counter += 1
        self.order.append(o)
        return o

    def remove_order(self, order_id):
        o = self.get_order(order_id)
        if [r for r in self.product_order if r.order_id is order_id]:
            raise ReferenceException("order_id")
        self.order = [r for r in self.order if r is not o]

    def remove_product(self, product_id):
        p = self.get_product(product_id)
        if [r for r in self.product_order if r.product_id is product_id]:
            raise ReferenceException("product_id")
        self.product = [r for r in self.product if r is not p]

    def get_order(self, order_id):
        o = [r for r in self.order if r.id is order_id]
        if not o:
            raise NoRowException()
        elif len(o) is not 1:
            raise Exception("Non-unique order id in base!")
        else:
            return o[0]

    def update_order(self, order):
        o = self.get_order(order.id)
        o.client_name = order.client_name
        o.client_address = order.client_address

    def add_product_to_order(self, product_id, order_id):
        self.get_product(product_id)
        self.get_order(order_id)

        po = [r for r in self.product_order
              if r.product_id is product_id and r.order_id is order_id]
        if not po:
            po = ProductOrder(product_id, order_id, 1)
            self.product_order.append(po)
        elif len(po) is not 1:
            raise Exception("Non-unique product-order in base!")
        else:
            po = po[0]
            po.quantity += 1

    def remove_product_from_order(self, product_id, order_id):
        po = [r for r in self.product_order
              if r.product_id is product_id and r.order_id is order_id]
        if not po:
            raise NoRowException()
        elif len(po) is not 1:
            raise Exception("Non-unique product-order in base")
        else:
            po = po[0]
            po.quantity -= 1
            if po.quantity is 0:
                self.product_order = [r for r in self.product_order if r is not po]


db = DB()
while True:
    try:
        userInput = input("$ ").strip().split(" ")
        if not userInput:
            print("Enter the command")
        else:
            cmd = userInput[0]

            if cmd == "exit":
                break
            elif cmd == "costly":
                for (p, o, q) in db.find_costly():
                    print("{} ordered {:d} {}({:d}$) for {:d}$".format(o.client_name, q, p.name, p.price, p.price*q))
            elif cmd == "save":
                with open("db.pkl", "wb") as f:
                    dump(db, f)
            elif cmd == "load":
                with open("db.pkl", "rb") as f:
                    db = load(f)
            elif cmd == "add":
                if len(userInput) == 2:
                    if userInput[1] == "product":
                        product_name = input("Enter product name: ")
                        product_price = int(input("Enter product price: "))
                        p = db.add_product(product_name, product_price)
                        print("Added product: {!s}".format(p))
                    elif userInput[1] == "order":
                        name = input("Enter client name: ")
                        address = input("Enter client address: ")
                        o = db.add_order(name, address)
                        print("Added {!s}".format(o))
                    elif userInput[1] == "item":
                        product_id = int(input("Enter product id: "))
                        order_id = int(input("Enter order id: "))
                        db.add_product_to_order(product_id, order_id)
                    else:
                        print("Only adding order, item and product is available")
            elif cmd == "delete":
                if len(userInput) == 4 and userInput[1] == "item":
                    product_id = int(userInput[2])
                    order_id = int(userInput[3])
                    db.remove_product_from_order(product_id, order_id)
                elif len(userInput) == 3:
                    id = int(userInput[2])
                    if userInput[1] == "product":
                        db.remove_product(id)
                    elif userInput[1] == "order":
                        db.remove_order(id)
                    else:
                        print("Only deleting order and product is available")
                else:
                    print("To delete, enter: delete product id or delete order id or delete item product_id order_id")
            elif cmd == "update":
                if len(userInput) == 3:
                    id = int(userInput[2])
                    if userInput[1] == "product":
                        p = db.get_product(id)
                        name = input("Update name({}): ".format(p.name))
                        price = input("Update price({:d}$): ".format(p.price))
                        if name is not "":
                            p.name = name
                        if price is not "":
                            p.price = int(price)
                    elif userInput[1] == "order":
                        o = db.get_order(id)
                        name = input("Update client name({}): ".format(o.client_name))
                        addr = input("Update client address({}): ".format(o.client_address))
                        if name is not "":
                            o.client_name = name
                        if addr is not "":
                            o.client_address = addr
                    else:
                        print("Only updating order and product is supported")
                else:
                    print("To update, enter: update product id or update order id")
            elif cmd=="list":
                if len(userInput) == 2:
                    if userInput[1] == "product":
                        print([str(p) for p in db.product])
                    elif userInput[1] == "order":
                        print([str(o) for o in db.order])
                    elif userInput[1] == "item":
                        print(["{} ordered {:d} {}(for {:d}$) to {}".format(o.client_name, po.quantity, p.name, p.price, o.client_address)
                               for po in db.product_order
                               for p in db.product if p.id == po.product_id
                               for o in db.order   if o.id == po.order_id])
                else:
                    print("Use list product, list order, or list item")
            else:
                print("Commands: add, update, delete, list")

    except Exception as e:
        print(e)
