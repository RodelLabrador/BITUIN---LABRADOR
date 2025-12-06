# controller.py
from model import Model

class Controller:
    def __init__(self):
        self.model = Model()
        self.current_user = None  # dict {id, username, role}
        self.cart = []  # list of dicts {id, name, price, qty}

    # --- Auth ---
    def login(self, username, password):
        row = self.model.authenticate(username, password)
        if row:
            self.current_user = {"id": row[0], "username": row[1], "role": row[2]}
            return True, f"Welcome {row[1]}!"
        return False, "Invalid credentials."

    def register(self, username, password, role="customer"):
        try:
            self.model.create_user(username, password, role)
            return True, "Registration successful."
        except Exception as e:
            return False, str(e)

    def logout(self):
        self.current_user = None
        self.cart = []

    # --- Products ---
    def list_products(self):
        return self.model.get_products()

    def get_product(self, pid):
        return self.model.get_product(pid)

    def search_products(self, q):
        return self.model.search_products(q)

    def add_product(self, name, description, price, stock):
        self.model.insert_product(name, description, price, stock)

    def edit_product(self, product_id, name, description, price, stock):
        self.model.update_product(product_id, name, description, price, stock)

    def remove_product(self, product_id):
        self.model.delete_product(product_id)

    # --- Cart ---
    def add_to_cart(self, product_id, qty):
        prod = self.get_product(product_id)
        if not prod:
            return False, "Product not found."
        if qty <= 0:
            return False, "Quantity must be at least 1."
        # check stock
        if prod[4] < qty:
            return False, f"Not enough stock. Available: {prod[4]}"
        # if exists in cart, update
        for it in self.cart:
            if it["id"] == product_id:
                if prod[4] < it["qty"] + qty:
                    return False, f"Not enough stock for combined quantity. Available: {prod[4]}"
                it["qty"] += qty
                return True, "Quantity updated in cart."
        self.cart.append({"id": prod[0], "name": prod[1], "price": prod[3], "qty": qty})
        return True, "Added to cart."

    def remove_from_cart(self, product_id):
        self.cart = [it for it in self.cart if it["id"] != product_id]

    def update_cart_qty(self, product_id, new_qty):
        prod = self.get_product(product_id)
        if not prod:
            return False, "Product not found."
        if new_qty <= 0:
            return False, "Quantity must be >= 1."
        if prod[4] < new_qty:
            return False, f"Not enough stock. Available: {prod[4]}"
        for it in self.cart:
            if it["id"] == product_id:
                it["qty"] = new_qty
                return True, "Quantity updated."
        return False, "Item not in cart."

    def get_cart(self):
        return self.cart

    # --- Checkout ---
    def checkout(self):
        if not self.current_user:
            return False, "User not logged in."
        if not self.cart:
            return False, "Cart is empty."
        # verify stock again
        for it in self.cart:
            prod = self.get_product(it["id"])
            if not prod or prod[4] < it["qty"]:
                return False, f"Insufficient stock for {it['name']}. Available: {prod[4] if prod else 0}"
        order_id, total = self.model.save_order(self.current_user["id"], self.cart)
        self.cart = []
        return True, {"order_id": order_id, "total": total}

    # --- Orders ---
    def list_orders(self):
        return self.model.get_orders()

    def get_order_items(self, order_id):
        return self.model.get_order_items(order_id)
