# view.py
import customtkinter as ctk
from controller import Controller
from inserting import ProductForm
from datavisualization import SalesChart
from receipts import save_and_print_receipt
from tkinter import messagebox, simpledialog
import threading
import webbrowser
import os

ctk.set_appearance_mode("System")  # "Dark", "Light", or "System"
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Enhanced E-Commerce System")
        self.geometry("1000x640")
        self.controller = Controller()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.create_widgets()
        self.refresh_products()

    def create_widgets(self):
        # left navigation frame
        self.nav_frame = ctk.CTkFrame(self, width=220)
        self.nav_frame.pack(side="left", fill="y", padx=12, pady=12)

        self.logo = ctk.CTkLabel(self.nav_frame, text="E-COMMERCE", font=ctk.CTkFont(size=18, weight="bold"))
        self.logo.pack(pady=(8,12))

        self.btn_dashboard = ctk.CTkButton(self.nav_frame, text="Dashboard", command=self.show_dashboard)
        self.btn_products = ctk.CTkButton(self.nav_frame, text="Products", command=self.show_products)
        self.btn_cart = ctk.CTkButton(self.nav_frame, text="Cart", command=self.show_cart)
        self.btn_analytics = ctk.CTkButton(self.nav_frame, text="Analytics", command=self.show_analytics)
        self.btn_logout = ctk.CTkButton(self.nav_frame, text="Logout", command=self.logout)

        self.btn_dashboard.pack(pady=6, fill="x")
        self.btn_products.pack(pady=6, fill="x")
        self.btn_cart.pack(pady=6, fill="x")
        self.btn_analytics.pack(pady=6, fill="x")
        self.btn_logout.pack(side="bottom", pady=12, fill="x")

        # top frame (user info + search)
        self.top_frame = ctk.CTkFrame(self, height=80)
        self.top_frame.pack(side="top", fill="x", padx=12, pady=(12,0))

        self.user_label = ctk.CTkLabel(self.top_frame, text="Not logged in")
        self.user_label.pack(side="right", padx=12)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.top_frame, placeholder_text="Search products...", textvariable=self.search_var)
        self.search_entry.pack(side="left", padx=12, pady=12, fill="x", expand=True)
        self.search_entry.bind("<Return>", lambda e: self.search_products())

        self.search_btn = ctk.CTkButton(self.top_frame, text="Search", command=self.search_products)
        self.search_btn.pack(side="left", padx=(0,12))

        # main content frame
        self.content = ctk.CTkFrame(self)
        self.content.pack(side="right", fill="both", expand=True, padx=12, pady=12)

        # Start with login screen overlay
        self.show_login()

    # ---------- screens ----------
    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_login(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.pack(expand=True)

        ctk.CTkLabel(frame, text="Login", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(8,20))
        username = ctk.CTkEntry(frame, placeholder_text="Username")
        username.pack(pady=8, padx=12, fill="x")
        password = ctk.CTkEntry(frame, placeholder_text="Password", show="*")
        password.pack(pady=8, padx=12, fill="x")

        def attempt_login():
            user = username.get().strip()
            pwd = password.get().strip()
            ok, msg = self.controller.login(user, pwd)
            if ok:
                self.user_label.configure(text=f"{self.controller.current_user['username']} ({self.controller.current_user['role']})")
                messagebox.showinfo("Login", msg)
                self.show_dashboard()
            else:
                messagebox.showerror("Login failed", msg)

        login_btn = ctk.CTkButton(frame, text="Login", command=attempt_login)
        login_btn.pack(pady=8, padx=12, fill="x")

        def open_register():
            dlg = RegisterDialog(self, self.controller)
            self.wait_window(dlg)
        reg_btn = ctk.CTkButton(frame, text="Register", fg_color="#2E8B57", command=open_register)
        reg_btn.pack(pady=6, padx=12, fill="x")

    def show_dashboard(self):
        if not self.controller.current_user:
            self.show_login(); return
        self.clear_content()
        header = ctk.CTkLabel(self.content, text="Dashboard", font=ctk.CTkFont(size=22, weight="bold"))
        header.pack(pady=(6,12))

        stats_frame = ctk.CTkFrame(self.content)
        stats_frame.pack(fill="x", padx=12, pady=(0,12))

        # summary cards
        products = self.controller.list_products()
        total_products = len(products)
        total_stock = sum(p[4] for p in products)
        orders = self.controller.list_orders()
        total_sales = sum(o[2] for o in orders)

        ctk.CTkLabel(stats_frame, text=f"Products: {total_products}", corner_radius=8).grid(row=0, column=0, padx=12, pady=8, sticky="w")
        ctk.CTkLabel(stats_frame, text=f"Total Stock: {total_stock}", corner_radius=8).grid(row=0, column=1, padx=12, pady=8, sticky="w")
        ctk.CTkLabel(stats_frame, text=f"Total Sales: ₱{total_sales:.2f}", corner_radius=8).grid(row=0, column=2, padx=12, pady=8, sticky="w")

        # quick actions
        actions = ctk.CTkFrame(self.content)
        actions.pack(fill="x", padx=12, pady=6)
        ctk.CTkButton(actions, text="Open Products", command=self.show_products).pack(side="left", padx=8, pady=8)
        ctk.CTkButton(actions, text="Open Cart", command=self.show_cart).pack(side="left", padx=8, pady=8)
        ctk.CTkButton(actions, text="View Analytics", command=self.show_analytics).pack(side="left", padx=8, pady=8)

        # if admin show management shortcuts
        if self.controller.current_user['role'] == "admin":
            admin_frame = ctk.CTkFrame(self.content)
            admin_frame.pack(fill="x", padx=12, pady=12)
            ctk.CTkLabel(admin_frame, text="Admin Actions", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=8)
            ctk.CTkButton(admin_frame, text="Add Product", command=lambda: self.open_product_form(mode="add")).pack(anchor="w", padx=8, pady=6)

    def show_products(self):
        if not self.controller.current_user:
            self.show_login(); return
        self.clear_content()
        header = ctk.CTkLabel(self.content, text="Products", font=ctk.CTkFont(size=20, weight="bold"))
        header.pack(pady=(6,10), anchor="w", padx=12)

        toolbar = ctk.CTkFrame(self.content)
        toolbar.pack(fill="x", padx=12, pady=(0,8))
        add_btn = ctk.CTkButton(toolbar, text="Add Product", command=lambda: self.open_product_form(mode="add"))
        add_btn.pack(side="left", padx=8)
        refresh_btn = ctk.CTkButton(toolbar, text="Refresh", command=self.refresh_products)
        refresh_btn.pack(side="left", padx=8)

        # products list
        self.products_box = ctk.CTkScrollableFrame(self.content)
        self.products_box.pack(fill="both", expand=True, padx=12, pady=6)

        self.populate_products(self.controller.list_products())

    def populate_products(self, products):
        # clear
        for w in self.products_box.winfo_children():
            w.destroy()
        for p in products:
            card = ctk.CTkFrame(self.products_box, corner_radius=8)
            card.pack(fill="x", padx=8, pady=8)
            ctk.CTkLabel(card, text=f"{p[1]}  —  ₱{p[3]:.2f}", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=12, pady=6)
            ctk.CTkLabel(card, text=f"Stock: {p[4]}   |   ID: {p[0]}").grid(row=1, column=0, sticky="w", padx=12)
            ctk.CTkLabel(card, text=p[2] or "", wraplength=600).grid(row=2, column=0, sticky="w", padx=12, pady=(4,8))

            btn_frame = ctk.CTkFrame(card)
            btn_frame.grid(row=0, column=1, rowspan=3, padx=12, pady=8, sticky="n")

            ctk.CTkButton(btn_frame, text="Add to Cart", command=lambda pid=p[0]: self.add_to_cart_prompt(pid)).pack(pady=4)
            if self.controller.current_user['role'] == "admin":
                ctk.CTkButton(btn_frame, text="Edit", command=lambda prod=p: self.open_product_form(mode="edit", product=prod)).pack(pady=4)
                ctk.CTkButton(btn_frame, text="Delete", fg_color="transparent", text_color="red",
                              command=lambda pid=p[0]: self.delete_product_confirm(pid)).pack(pady=4)

    def refresh_products(self):
        if hasattr(self, "products_box") and self.products_box:
            prods = self.controller.list_products()
            self.populate_products(prods)

    def open_product_form(self, mode="add", product=None):
        def on_save():
            self.refresh_products()
        form = ProductForm(self, self.controller, mode=mode, product=product, on_save=on_save)
        form.grab_set()

    def delete_product_confirm(self, pid):
        if messagebox.askyesno("Confirm", "Delete this product?"):
            self.controller.remove_product(pid)
            self.refresh_products()

    def add_to_cart_prompt(self, product_id):
        prod = self.controller.get_product(product_id)
        if not prod:
            messagebox.showerror("Error", "Product not found.")
            return
        qty = simpledialog.askinteger("Quantity", f"Enter quantity for {prod[1]} (Available: {prod[4]})", minvalue=1, maxvalue=prod[4])
        if qty is None:
            return
        ok, msg = self.controller.add_to_cart(product_id, qty)
        if ok:
            messagebox.showinfo("Added", msg)
        else:
            messagebox.showerror("Failed", msg)

    def show_cart(self):
        if not self.controller.current_user:
            self.show_login(); return
        self.clear_content()
        header = ctk.CTkLabel(self.content, text="Shopping Cart", font=ctk.CTkFont(size=20, weight="bold"))
        header.pack(pady=(6,10), anchor="w", padx=12)

        cart_frame = ctk.CTkFrame(self.content)
        cart_frame.pack(fill="both", expand=True, padx=12, pady=6)

        items = self.controller.get_cart()
        if not items:
            ctk.CTkLabel(cart_frame, text="Cart is empty.").pack(padx=12, pady=12)
            return

        for it in items:
            row = ctk.CTkFrame(cart_frame)
            row.pack(fill="x", padx=8, pady=6)
            ctk.CTkLabel(row, text=f"{it['name']} (₱{it['price']:.2f})").pack(side="left", padx=8)
            qty_entry = ctk.CTkEntry(row, width=80, justify="center")
            qty_entry.insert(0, str(it['qty']))
            qty_entry.pack(side="left", padx=8)
            def make_update(pid, entry):
                def update_action():
                    try:
                        new_q = int(entry.get())
                    except ValueError:
                        messagebox.showerror("Invalid", "Quantity must be integer.")
                        return
                    ok, msg = self.controller.update_cart_qty(pid, new_q)
                    if ok:
                        messagebox.showinfo("Updated", msg)
                        self.show_cart()
                    else:
                        messagebox.showerror("Failed", msg)
                return update_action
            ctk.CTkButton(row, text="Update", command=make_update(it['id'], qty_entry)).pack(side="left", padx=6)
            ctk.CTkButton(row, text="Remove", fg_color="transparent", text_color="red",
                          command=lambda pid=it['id']: [self.controller.remove_from_cart(pid), self.show_cart()]).pack(side="left", padx=6)

        total = sum(it['price']*it['qty'] for it in items)
        ctk.CTkLabel(cart_frame, text=f"Total: ₱{total:.2f}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=12)
        ctk.CTkButton(cart_frame, text="Checkout", command=self.checkout_action).pack()

    def checkout_action(self):
        ok, res = self.controller.checkout()
        if not ok:
            messagebox.showerror("Checkout failed", res)
            return
        # save receipt
        fname = save_and_print_receipt(self.controller, res)
        messagebox.showinfo("Order placed", f"Order {res['order_id']} placed. Receipt saved to {fname}")

    def show_analytics(self):
        if not self.controller.current_user:
            self.show_login(); return
        SalesChart(self)

    # --- misc ---
    def search_products(self):
        q = self.search_var.get().strip()
        if not q:
            self.refresh_products()
        else:
            results = self.controller.search_products(q)
            self.clear_content()
            header = ctk.CTkLabel(self.content, text=f"Search results for '{q}'", font=ctk.CTkFont(size=18))
            header.pack(pady=8)
            self.products_box = ctk.CTkScrollableFrame(self.content)
            self.products_box.pack(fill="both", expand=True, padx=12, pady=6)
            self.populate_products(results)

    def logout(self):
        self.controller.logout()
        self.user_label.configure(text="Not logged in")
        self.show_login()

    def on_close(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.destroy()

# small register dialog
class RegisterDialog(ctk.CTkToplevel):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.title("Register")
        self.geometry("420x260")
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="Register", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(12,8))
        self.username = ctk.CTkEntry(self, placeholder_text="Username")
        self.username.pack(pady=8, padx=12, fill="x")
        self.password = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password.pack(pady=8, padx=12, fill="x")
        ctk.CTkButton(self, text="Register", command=self.do_register).pack(pady=12, padx=12, fill="x")

    def do_register(self):
        u = self.username.get().strip()
        p = self.password.get().strip()
        if not u or not p:
            messagebox.showerror("Invalid", "Provide username and password.")
            return
        ok, msg = self.controller.register(u, p, "customer")
        if ok:
            messagebox.showinfo("Registered", "You can now login.")
            self.destroy()
        else:
            messagebox.showerror("Failed", msg)
