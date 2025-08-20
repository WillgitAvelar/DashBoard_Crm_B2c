from flask import Flask, render_template
from src.extensions import db

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # importa e registra as rotas só depois de inicializar db
    from src.routes.lead import leads_bp
    from src.routes.b2c import b2c_bp

    app.register_blueprint(leads_bp)
    app.register_blueprint(b2c_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


