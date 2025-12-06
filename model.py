# model.py
from database import get_connection
import datetime

class Model:
    # ========== User ==========
    def create_user(self, username, password, role="customer"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
                    (username, password, role))
        conn.commit()
        conn.close()

    def authenticate(self, username, password):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, role FROM users WHERE username=? AND password=?",
                    (username, password))
        row = cur.fetchone()
        conn.close()
        return row

    # ========== Products ==========
    def get_products(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, description, price, stock FROM products ORDER BY id")
        rows = cur.fetchall()
        conn.close()
        return rows

    def get_product(self, product_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, description, price, stock FROM products WHERE id=?", (product_id,))
        row = cur.fetchone()
        conn.close()
        return row

    def search_products(self, q):
        conn = get_connection()
        cur = conn.cursor()
        pattern = f"%{q}%"
        cur.execute("SELECT id, name, description, price, stock FROM products WHERE name LIKE ? OR description LIKE ? ORDER BY id",
                    (pattern, pattern))
        rows = cur.fetchall()
        conn.close()
        return rows

    def insert_product(self, name, description, price, stock):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO products (name, description, price, stock) VALUES (?,?,?,?)",
                    (name, description, price, stock))
        conn.commit()
        conn.close()

    def update_product(self, product_id, name, description, price, stock):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET name=?, description=?, price=?, stock=? WHERE id=?",
                    (name, description, price, stock, product_id))
        conn.commit()
        conn.close()

    def delete_product(self, product_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()
        conn.close()

    # ========== Orders ==========
    def save_order(self, user_id, cart_items):
        """
        cart_items: list of dicts {id, name, price, qty}
        """
        conn = get_connection()
        cur = conn.cursor()

        total = sum(item["price"] * item["qty"] for item in cart_items)
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO orders (user_id, total, date) VALUES (?,?,?)",
                    (user_id, total, date))
        order_id = cur.lastrowid

        for item in cart_items:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase)
                VALUES (?,?,?,?)
            """, (order_id, item["id"], item["qty"], item["price"]))
            # reduce stock
            cur.execute("UPDATE products SET stock = stock - ? WHERE id=?", (item["qty"], item["id"]))

        conn.commit()
        conn.close()
        return order_id, total

    def get_orders(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, user_id, total, date FROM orders ORDER BY date")
        rows = cur.fetchall()
        conn.close()
        return rows

    def get_order_items(self, order_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT product_id, quantity, price_at_purchase FROM order_items WHERE order_id=?", (order_id,))
        rows = cur.fetchall()
        conn.close()
        return rows
