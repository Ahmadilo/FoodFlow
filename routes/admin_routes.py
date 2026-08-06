from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.models import User
from models.database import db
from models.models import MenuItem, Order
import os
from werkzeug.utils import secure_filename
import uuid



admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required():
    if "user_id" not in session:
        return False
    user = User.query.get(session["user_id"])
    return user and user.role == "admin"


# ---------------------------
# SHOW + ADD MENU ITEMS
# ---------------------------
@admin_bp.route("/menu", methods=["GET", "POST"])
def manage_menu():

    if not admin_required():
        flash("Admins only.")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        category = request.form.get("category")

        image = request.files.get("image")
        image_url = None

        if image and image.filename:
            filename = secure_filename(image.filename)
            upload_path = os.path.join("static/images", filename)
            image.save(upload_path)
            image_url = f"/static/images/{filename}"

        new_item = MenuItem(
            name=name,
            description=description,
            price=float(price),
            category=category,
            image_url=image_url
        )


        db.session.add(new_item)
        db.session.commit()

        flash("Menu item added successfully!")
        return redirect(url_for("admin.manage_menu"))

    items = MenuItem.query.all()
    return render_template("admin_menu.html", items=items)

# ---------------------------
# DELETE ITEM
# ---------------------------
@admin_bp.route("/menu/delete/<int:item_id>")
def delete_item(item_id):

    if not admin_required():
        flash("Admins only.")
        return redirect(url_for("index"))

    item = MenuItem.query.get(item_id)
    if not item:
        flash("Item not found!")
        return redirect(url_for("admin.manage_menu"))

    db.session.delete(item)
    db.session.commit()

    flash("Item deleted successfully!")
    return redirect(url_for("admin.manage_menu"))

# ---------------------------
# EDIT ITEM (FORM PAGE)
# ---------------------------
@admin_bp.route("/menu/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):

    if not admin_required():
        flash("Admins only.")
        return redirect(url_for("index"))

    item = MenuItem.query.get(item_id)

    if not item:
        flash("Item not found!")
        return redirect(url_for("admin.manage_menu"))

    if request.method == "POST":
        item.name = request.form.get("name")
        item.description = request.form.get("description")
        item.price = float(request.form.get("price"))
        item.category = request.form.get("category")

        image = request.files.get("image")

        if image and image.filename:
            ext = os.path.splitext(image.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            upload_path = os.path.join("static/images", filename)
            image.save(upload_path)

            item.image_url = f"/static/images/{filename}"

        db.session.commit()
        flash("Item updated successfully!")
        return redirect(url_for("admin.manage_menu"))


    return render_template("admin_edit_menu.html", item=item)

@admin_bp.route("/orders/next/<int:order_id>")
def next_order_status(order_id):
    if "user_id" not in session:
        flash("Login required.")
        return redirect(url_for("auth.login"))

    admin = User.query.get(session["user_id"])
    if not admin or admin.role != "admin":
        flash("Admins only.")
        return redirect(url_for("index"))

    order = Order.query.get(order_id)
    if not order:
        flash("Order not found.")
        return redirect(url_for("admin.list_orders"))

    # الحالات الممكنة
    flow = ["pending", "preparing", "awaiting_driver", "on_the_way", "delivered"]

    current = order.order_status
    if current in flow:
        idx = flow.index(current)
        if idx < len(flow) - 1:
            order.order_status = flow[idx + 1]
            db.session.commit()
            flash(f"Order moved to: {order.order_status}")
        else:
            flash("Order already delivered.")
    else:
        flash("Invalid order status.")

    return redirect(url_for("admin.list_orders"))

from models.models import Order, User

@admin_bp.route("/orders")
def list_orders():
    # فقط الأدمن يدخل
    if "user_id" not in session:
        flash("Login required.")
        return redirect(url_for("auth.login"))

    admin = User.query.get(session["user_id"])
    if not admin or admin.role != "admin":
        flash("Admins only.")
        return redirect(url_for("index"))

    # جيب كل الطلبات من كل المستخدمين
    orders = Order.query.order_by(Order.order_date.desc()).all()

    return render_template("admin_orders.html", orders=orders)

@admin_bp.route("/users")
def admin_users():

    if not admin_required():
        flash("Admins only.")
        return redirect(url_for("index"))

    users = User.query.order_by(User.id.asc()).all()
    return render_template("admin_users.html", users=users)

@admin_bp.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):

    if not admin_required():
        flash("Admins only.")
        return redirect(url_for("index"))

    user = User.query.get(user_id)

    if not user:
        flash("User not found.")
        return redirect(url_for("admin.admin_users"))

    if request.method == "POST":
        role = request.form.get("role")

        if role not in ["admin", "customer", "delivery"]:
            flash("Invalid role.")
            return redirect(url_for("admin.edit_user", user_id=user.id))

        user.role = role
        db.session.commit()

        flash("User role updated successfully.")
        return redirect(url_for("admin.admin_users"))

    return render_template("admin_edit_user.html", user=user)

