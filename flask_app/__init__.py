# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

from flask_talisman import Talisman

# stdlib
from datetime import datetime
import os




db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()



from .users.routes import users
from .store.routes import store


def page_not_found(e):
    return render_template("404.html"), 404




def create_app(test_config=None):
    app = Flask(__name__)
    

    app.config["SECRET_KEY"] = b'\x020;yr\x91\x11\xbe"\x9d\xc1\x14\x91\xadf\xec'
    app.config["MONGODB_HOST"] = os.getenv("MONGODB_HOST")

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(users)
    app.register_error_handler(404, page_not_found)

    app.register_blueprint(store)
    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"


    csp = {
        'default-src': '\'self\'',
        'img-src': ['*.fakestoreapi.com', '*.pngimage.net'],
        'script-src': ['*', "'unsafe-inline'"],
        'style-src': ['*', "'unsafe-inline'"]
    }
    
    Talisman(app, content_security_policy=csp)


    return app
