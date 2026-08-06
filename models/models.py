# models/models.py

from datetime import datetime
from .database import db

class User(db.Model):
    __tablename__ = "users"   # اسم الجدول في MySQL

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default="customer")  # customer, admin, delivery
    address = db.Column(db.String(255))

    def __repr__(self):
        return f"<User {self.email}>"

class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    is_available = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(255))  # 👈 هذا مهم

    def __repr__(self):
        return f"<MenuItem {self.name}>"

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    payment_status = db.Column(db.String(20), default="pending")   # pending, paid, failed
    order_status = db.Column(db.String(20), default="pending")     # pending, preparing, on_the_way, delivered, cancelled

    # relationship (not required yet but helpful)
    items = db.relationship("OrderItem", backref="order", lazy=True)
    payment = db.relationship("Payment", backref="order", uselist=False)
    delivery = db.relationship("Delivery", backref="order", uselist=False)
    user = db.relationship(
        "User",
        backref=db.backref("orders", lazy=True)
    )

    def __repr__(self):
        return f"<Order {self.id}>"

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
     # FIX: relationship to MenuItem
    menu_item = db.relationship("MenuItem", backref="order_items")

    def __repr__(self):
        return f"<OrderItem order={self.order_id} item={self.menu_item_id}>"

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), default="simulation")
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="pending")  # pending, paid, failed

    def __repr__(self):
        return f"<Payment order={self.order_id} status={self.status}>"

class Delivery(db.Model):
    __tablename__ = "deliveries"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    delivery_agent_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    assigned_time = db.Column(db.DateTime)
    delivered_time = db.Column(db.DateTime)
    delivery_status = db.Column(db.String(20), default="assigned")  
    # assigned, on_the_way, delivered, failed

    def __repr__(self):
        return f"<Delivery order={self.order_id} status={self.delivery_status}>"
    
class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)

    # FK → users.id
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)

    # relationship
    user = db.relationship(
        "User",
        backref=db.backref("customer", uselist=False)
    )

    def __repr__(self):
        return f"<Customer user_id={self.user_id} phone={self.phone}>"
