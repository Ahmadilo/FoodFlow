from flask import Blueprint, render_template, session, redirect, url_for, flash
from models.models import Order, User
from models.database import db

delivery_bp = Blueprint("delivery", __name__, url_prefix="/delivery")

def delivery_required():
    if "user_id" not in session:
        return False
    user = User.query.get(session["user_id"])
    return user and user.role == "delivery"

@delivery_bp.route("/orders")
def delivery_orders():

    if not delivery_required():
        flash("Delivery access only")
        return redirect(url_for("index"))

    orders = Order.query.filter(
        Order.order_status.in_(["awaiting_driver", "on_the_way", "delivered"])
    ).all()

    return render_template("delivery_orders.html", orders=orders)

@delivery_bp.route("/orders/next/<int:order_id>")
def next_status(order_id):

    if not delivery_required():
        flash("Delivery access only")
        return redirect(url_for("index"))

    order = Order.query.get(order_id)

    if not order:
        flash("Order not found")
        return redirect(url_for("delivery.delivery_orders"))

    if order.order_status == "awaiting_driver":
        order.order_status = "on_the_way"
    elif order.order_status == "on_the_way":
        order.order_status = "delivered"

    db.session.commit()
    return redirect(url_for("delivery.delivery_orders"))
