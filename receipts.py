# receipts.py
import os
from datetime import datetime
from database import get_connection

RECEIPTS_DIR = "receipts"

def save_and_print_receipt(controller, order_resp):
    """
    order_resp: {"order_id": ..., "total": ...}
    """
    if not order_resp or "order_id" not in order_resp:
        print("No order info.")
        return

    order_id = order_resp["order_id"]
    total = order_resp["total"]
    items = controller.get_order_items(order_id)
    username = controller.current_user["username"] if controller.current_user else "unknown"

    lines = []
    lines.append("=== RECEIPT ===")
    lines.append(f"Order ID: {order_id}")
    lines.append(f"User: {username}")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("Items:")
    for pid, qty, price in items:
        lines.append(f" - Product ID {pid} | Qty: {qty} | Unit: ₱{price:.2f} | Subtotal: ₱{price*qty:.2f}")
    lines.append("")
    lines.append(f"TOTAL: ₱{total:.2f}")
    lines.append("================")

    text = "\n".join(lines)
    # console print
    print(text)

    # save file
    os.makedirs(RECEIPTS_DIR, exist_ok=True)
    fname = os.path.join(RECEIPTS_DIR, f"receipt_{order_id}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write(text)

    return fname
