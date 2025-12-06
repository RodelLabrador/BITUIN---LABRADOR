# inserting.py
# Helper popups / small UI helpers for product add/edit (used by view.py)
import customtkinter as ctk
from tkinter import messagebox

class ProductForm(ctk.CTkToplevel):
    def __init__(self, master, controller, mode="add", product=None, on_save=None):
        super().__init__(master)
        self.controller = controller
        self.mode = mode
        self.product = product
        self.on_save = on_save
        self.title("Add Product" if mode=="add" else "Edit Product")
        self.geometry("420x320")
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Product Name").grid(row=0, column=0, sticky="w", padx=16, pady=(16,4))
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.grid(row=1, column=0, padx=16, pady=4, sticky="ew")

        ctk.CTkLabel(self, text="Description").grid(row=2, column=0, sticky="w", padx=16, pady=(8,4))
        self.desc_entry = ctk.CTkTextbox(self, height=80)
        self.desc_entry.grid(row=3, column=0, padx=16, pady=4, sticky="ew")

        ctk.CTkLabel(self, text="Price").grid(row=4, column=0, sticky="w", padx=16, pady=(8,4))
        self.price_entry = ctk.CTkEntry(self)
        self.price_entry.grid(row=5, column=0, padx=16, pady=4, sticky="ew")

        ctk.CTkLabel(self, text="Stock").grid(row=6, column=0, sticky="w", padx=16, pady=(8,4))
        self.stock_entry = ctk.CTkEntry(self)
        self.stock_entry.grid(row=7, column=0, padx=16, pady=4, sticky="ew")

        btn_text = "Add Product" if self.mode=="add" else "Save Changes"
        self.save_btn = ctk.CTkButton(self, text=btn_text, command=self.save)
        self.save_btn.grid(row=8, column=0, padx=16, pady=12, sticky="ew")

        if self.mode == "edit" and self.product:
            self.name_entry.insert(0, self.product[1])
            self.desc_entry.insert("0.0", self.product[2] or "")
            self.price_entry.insert(0, str(self.product[3]))
            self.stock_entry.insert(0, str(self.product[4]))

    def save(self):
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get("0.0", "end").strip()
        try:
            price = float(self.price_entry.get().strip())
            stock = int(self.stock_entry.get().strip())
        except ValueError:
            messagebox.showerror("Invalid", "Price must be a number and stock must be an integer.")
            return

        if not name:
            messagebox.showerror("Invalid", "Name required.")
            return

        if self.mode == "add":
            self.controller.add_product(name, desc, price, stock)
        else:
            self.controller.edit_product(self.product[0], name, desc, price, stock)

        if callable(self.on_save):
            self.on_save()
        self.destroy()
