# datavisualization.py
import customtkinter as ctk
from database import get_connection
import matplotlib
matplotlib.use("Agg")  # avoid issues if no display; we will render AGG then embed via FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import messagebox
import os

def fetch_sales():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT date, total FROM orders ORDER BY date")
    data = cur.fetchall()
    conn.close()
    return data

class SalesChart(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Sales Analytics")
        self.geometry("800x520")
        self.setup_ui()

    def setup_ui(self):
        data = fetch_sales()
        if not data:
            messagebox.showinfo("No data", "No sales data yet.")
            return

        dates = [d[0].split()[0] for d in data]
        totals = [d[1] for d in data]

        fig, ax = plt.subplots(figsize=(8,4))
        ax.bar(dates, totals)
        ax.set_title("Sales Over Time")
        ax.set_ylabel("Total (₱)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)

        # Save button
        save_btn = ctk.CTkButton(self, text="Save Chart PNG", command=lambda: self.save_png(fig))
        save_btn.pack(pady=8)

    def save_png(self, fig):
        os.makedirs("charts", exist_ok=True)
        fname = os.path.join("charts", "sales_chart.png")
        fig.savefig(fname)
        messagebox.showinfo("Saved", f"Chart saved to {fname}")
