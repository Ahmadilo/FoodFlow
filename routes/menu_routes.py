from flask import Blueprint, render_template
from models.models import MenuItem

menu_bp = Blueprint("menu", __name__, url_prefix="/menu")

@menu_bp.route("/")
def view_menu():
    items = MenuItem.query.all()   # fetch all items from DB
    return render_template("menu.html", items=items)
