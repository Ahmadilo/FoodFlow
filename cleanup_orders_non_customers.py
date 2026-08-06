# cleanup_orders_non_customers.py

from flask_app import create_app
from models.database import db
from models import Order, OrderItem, Payment


def cleanup_orders():
    app = create_app()

    with app.app_context():
        orders = Order.query.all()
        print("Total orders found:", len(orders))

        deleted_orders = 0
        deleted_items = 0
        deleted_payments = 0

        for order in orders:
            user = order.user

            # إذا المستخدم ما عنده Customer
            if not user or not user.customer:
                print(f"\n🗑 Deleting Order {order.id} (User {user.id if user else 'None'})")

                # ---- Payment ----
                if order.payment:
                    db.session.delete(order.payment)
                    deleted_payments += 1
                    print("  - Payment deleted")

                # ---- Order Items ----
                for item in order.items:
                    db.session.delete(item)
                    deleted_items += 1
                print(f"  - {len(order.items)} OrderItem(s) deleted")

                # ---- Order ----
                db.session.delete(order)
                deleted_orders += 1

        db.session.commit()

        print("\n✅ CLEANUP DONE")
        print("Orders deleted:", deleted_orders)
        print("OrderItems deleted:", deleted_items)
        print("Payments deleted:", deleted_payments)


if __name__ == "__main__":
    cleanup_orders()
