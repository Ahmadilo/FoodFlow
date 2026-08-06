from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from models.database import db
from models.models import Order, OrderItem, MenuItem

order_bp = Blueprint("order", __name__, url_prefix="/order")

def recalc_order_total(order_id):
    total = db.session.query(db.func.sum(OrderItem.subtotal)).filter_by(order_id=order_id).scalar()
    if total is None:
        total = 0
    order = Order.query.get(order_id)
    order.total_amount = total
    db.session.commit()

@order_bp.route("/create", methods=["POST"])
def create_order():
    if "user_id" not in session:
        flash("You must be logged in to place an order.")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    item_id = request.form.get("item_id")
    quantity = int(request.form.get("quantity", 1))

    item = MenuItem.query.get(item_id)
    if not item:
        flash("Item not found!")
        return redirect(url_for("menu.view_menu"))

    # ---------------------------------------------------
    # 1) هل يوجد طلب سابق في حالة pending للمستخدم هذا؟
    # ---------------------------------------------------
    pending_order = Order.query.filter_by(
        user_id=user_id, 
        order_status="pending"
    ).first()

    if not pending_order:
        # إذا لا يوجد → نعمل واحد جديد
        pending_order = Order(
            user_id=user_id,
            total_amount=0,
            order_status="pending",
            payment_status="pending"
        )
        db.session.add(pending_order)
        db.session.flush()  # create order.id

    # ---------------------------------------------------
    # 2) هل العنصر موجود مسبقًا داخل نفس الطلب؟
    # ---------------------------------------------------
    order_item = OrderItem.query.filter_by(
        order_id=pending_order.id,
        menu_item_id=item.id
    ).first()

    if order_item:
        # لو موجود → نزيد الكمية فقط
        order_item.quantity += quantity
        order_item.subtotal = order_item.quantity * order_item.unit_price
    else:
        # لو مو موجود → نضيفه
        order_item = OrderItem(
            order_id=pending_order.id,
            menu_item_id=item.id,
            quantity=quantity,
            unit_price=item.price,
            subtotal=item.price * quantity
        )
        db.session.add(order_item)

    # ---------------------------------------------------
    # 3) تحديث total_amount في order
    # ---------------------------------------------------
    total = db.session.query(db.func.sum(OrderItem.subtotal)).filter_by(order_id=pending_order.id).scalar()
    pending_order.total_amount = total

    db.session.commit()

    flash("Item added to your order!")
    return redirect(url_for("menu.view_menu"))

    if "user_id" not in session:
        flash("You must be logged in to place an order.")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    item_id = request.form.get("item_id")
    quantity = int(request.form.get("quantity", 1))

    item = MenuItem.query.get(item_id)
    if not item:
        flash("Item not found!")
        return redirect(url_for("menu.view_menu"))

    total = item.price * quantity

    # create new order
    order = Order(
        user_id=user_id,
        total_amount=total,
        order_status="pending",
        payment_status="pending"
    )
    db.session.add(order)
    db.session.flush()

    # add order item
    order_item = OrderItem(
        order_id=order.id,
        menu_item_id=item.id,
        quantity=quantity,
        unit_price=item.price,
        subtotal=total
    )

    db.session.add(order_item)
    db.session.commit()

    flash("Order created successfully!")
    return redirect(url_for("menu.view_menu"))


@order_bp.route("/my")
def my_orders():
    if "user_id" not in session:
        flash("Login required.")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    # get all orders for this user
    orders = Order.query.filter_by(user_id=user_id).all()

    return render_template("my_orders.html", orders=orders)

@order_bp.route("/view/<int:order_id>")
def view_order(order_id):
    if "user_id" not in session:
        flash("Login required.")
        return redirect(url_for("auth.login"))

    order = Order.query.get(order_id)

    if not order or order.user_id != session["user_id"]:
        flash("Order not found.")
        return redirect(url_for("order.my_orders"))

    items = OrderItem.query.filter_by(order_id=order_id).all()
    return render_template("order_details.html", order=order, items=items)

@order_bp.route("/delete/<int:order_id>")
def delete_order(order_id):
    if "user_id" not in session:
        flash("Login required.")
        return redirect(url_for("auth.login"))

    order = Order.query.get(order_id)

    if not order or order.user_id != session["user_id"]:
        flash("Order not found.")
        return redirect(url_for("order.my_orders"))

    # delete all order items first
    OrderItem.query.filter_by(order_id=order_id).delete()

    # delete order
    db.session.delete(order)
    db.session.commit()

    flash("Order deleted successfully.")
    return redirect(url_for("order.my_orders"))

@order_bp.route("/item/update/<int:item_id>", methods=["POST"])
def update_order_item(item_id):
    quantity = int(request.form.get("quantity", 1))

    item = OrderItem.query.get(item_id)
    if not item:
        flash("Item not found.")
        return redirect(url_for("order.my_orders"))

    # update subtotal of this item
    item.quantity = quantity
    item.subtotal = item.unit_price * quantity
    db.session.commit()

    # recalc total of the entire order
    recalc_order_total(item.order_id)

    flash("Item updated.")
    return redirect(url_for("order.view_order", order_id=item.order_id))

@order_bp.route("/item/delete/<int:item_id>")
def delete_order_item(item_id):
    item = OrderItem.query.get(item_id)
    if not item:
        flash("Item not found.")
        return redirect(url_for("order.my_orders"))

    order_id = item.order_id

    # delete item
    db.session.delete(item)
    db.session.commit()

    # recalc total
    recalc_order_total(order_id)

    flash("Item removed from order.")
    return redirect(url_for("order.view_order", order_id=order_id))


@order_bp.route("/confirm/<int:order_id>")
def confirm_order(order_id):
    if "user_id" not in session:
        flash("Login required.")
        return redirect(url_for("auth.login"))

    order = Order.query.get(order_id)

    if not order or order.user_id != session["user_id"]:
        flash("Order not found.")
        return redirect(url_for("order.my_orders"))

    # Only allow confirm if pending
    if order.order_status != "pending":
        flash("Order already confirmed or processed.")
        return redirect(url_for("order.view_order", order_id=order_id))

    # Change state
    order.order_status = "preparing"
    db.session.commit()

    flash("Order confirmed! Now preparing your food.")
    return redirect(url_for("order.view_order", order_id=order_id))

@order_bp.route("/pay/<int:order_id>")
def pay_order(order_id):
    if "user_id" not in session:
        flash("Login required.")
        return redirect(url_for("auth.login"))

    order = Order.query.get(order_id)

    if not order or order.user_id != session["user_id"]:
        flash("Order not found.")
        return redirect(url_for("order.my_orders"))

    if order.order_status != "delivered":
        flash("Order not delivered yet.")
        return redirect(url_for("order.view_order", order_id=order_id))

    if order.payment_status == "paid":
        flash("Order already paid.")
        return redirect(url_for("order.view_order", order_id=order_id))

    return render_template("payment_page.html", order=order)

@order_bp.route("/pay/confirm/<int:order_id>")
def confirm_payment(order_id):
    if "user_id" not in session:
        flash("Login required.")
        return redirect(url_for("auth.login"))

    order = Order.query.get(order_id)

    if not order or order.user_id != session["user_id"]:
        flash("Order not found.")
        return redirect(url_for("order.my_orders"))

    order.payment_status = "paid"
    db.session.commit()

    flash("Payment successful! Thank you.")
    return redirect(url_for("order.my_orders"))

@order_bp.route("/cart")
def cart():
    if "user_id" not in session:
        flash("Login required.")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    # 1) order المفتوح (pending) = cart
    order = Order.query.filter_by(
        user_id=user_id,
        order_status="pending"
    ).order_by(Order.id.desc()).first()

    # 2) لو ما فيه pending → خذ آخر طلب (للعرض فقط)
    if not order:
        order = Order.query.filter_by(user_id=user_id).order_by(Order.id.desc()).first()

        if not order:
            # ما عنده ولا طلب
            return render_template("cart.html", order=None, items=[])

    items = OrderItem.query.filter_by(order_id=order.id).all()
    return render_template("cart.html", order=order, items=items)
