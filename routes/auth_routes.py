from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import db
from models.models import User, Customer, Delivery
from flask import session

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")
        address = request.form.get("address")
        isDeliver = request.form.get("is_delivery")

        # check existing email
        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("auth.register"))
        role = "customer"
        if isDeliver:
            role = "delivery"

        # 1️⃣ Create User
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone,
            address=address,
            role=role
        )

        db.session.add(user)
        db.session.flush()  # 👈 مهم جدًا عشان user.id

        # 2️⃣ Create Customer (because phone + address exist)
        
        customer = Customer(
            user_id=user.id,
            phone=phone,
            address=address
        )

        db.session.add(customer)
        db.session.commit()

        flash("Account created successfully. Please login.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password!")
            return redirect(url_for("auth.login"))

        # store user id in session
        session["user_id"] = user.id
        flash(f"Welcome {user.name}!")
        return redirect(url_for("menu.view_menu"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.pop("user_id", None)   # حذف جلسة المستخدم
    flash("You have been logged out.")
    return redirect(url_for("index"))

