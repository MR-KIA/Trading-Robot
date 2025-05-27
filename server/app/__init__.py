from flask import Flask

def create_app():
    app = Flask(__name__)

    from .routes import main_bp
    from .auto_routes import bp1
    from .normal_routes import bp2
    app.config['CONNECTIONS'] = {}

    app.register_blueprint(main_bp)
    app.register_blueprint(bp1, url_prefix='/api/v1/auto')
    app.register_blueprint(bp2, url_prefix='/api/v1')

    return app
