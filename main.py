# main.py
from database import init_db
from view import App
from controller import Controller

def seed_demo(controller):
    # seed demo products only if none exist
    if len(controller.list_products()) == 0:
        controller.add_product("T-Shirt", "Comfortable cotton tee", 350.00, 20)
        controller.add_product("Cap", "Baseball cap", 120.00, 50)
        controller.add_product("Mug", "Ceramic mug 350ml", 180.00, 30)
        controller.add_product("Notebook", "A5 notebook 100 pages", 75.00, 100)

if __name__ == "__main__":
    init_db()
    # seed (safe)
    ctrl = Controller()
    seed_demo(ctrl)
    app = App()
    app.mainloop()
