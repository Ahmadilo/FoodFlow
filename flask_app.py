from flask import Flask
from config import Config
from models.database import db
from models import User   # استيراد الموديل
from flask import render_template
from flask import session



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.menu_routes import menu_bp
    from routes.admin_routes import admin_bp
    from routes.order_routes import order_bp
    from routes.delivery_routes import delivery_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(delivery_bp)

    app.secret_key = "ANY_RANDOM_SECRET"

    @app.context_processor
    def inject_user_info():
        is_admin = False
        is_delivery = False
        if session.get("user_id"):
            user = User.query.get(session["user_id"])
            if user and user.role == "admin":
                is_admin = True
            if user and user.role == 'delivery':
                is_delivery = True

        return dict(
            session=session,
            is_admin=is_admin,
            is_delivery=is_delivery
        )

    @app.route("/")
    def index():
        return render_template("index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()   # هنا تنشأ الجداول في قاعدة البيانات

    app.run(debug=True)
