from flask import Flask
from flask_talisman import Talisman  # Added
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_mobility import Mobility
from .config import Config

''' Extensions '''
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mobility = Mobility()

mail = Mail()

# talisman = Talisman()  # Added
# csp = {
#     'default-src': [
#         '\'self\'',
#         '\'unsafe-inline\'',
#         'stackpath.bootstrapcdn.com',
#         'code.jquery.com',
#         'cdnjs.cloudflare.com',
#         'cdn.jsdelivr.net'
#     ],
#     'script-src': ["'sha384-(JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM)'",
#                         'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js',
#                         'https://code.jquery.com/jquery-3.3.1.slim.min.js',
#                         'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js'
#                    ],
#     'style-src': ["'self'", 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css']
# }


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    mobility.init_app(app)
    # talisman.init_app(app, content_security_policy=csp)  # Added

    from .users.routes import users
    from .posts.routes import posts
    from .main.routes import main
    from .admin.routes import admin
    from .errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(errors)

    return app
