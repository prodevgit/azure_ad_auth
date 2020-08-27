from flask import Flask
import app_config
from flask_session import Session
from resources import user


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    from app import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    # app.register_blueprint(user.bp,url_prefix='/auth')
    #MSAI CONF
    app.config.from_object(app_config)
    Session(app)
    # This section is needed for url_for("foo", _external=True) to automatically
    # generate http scheme when this sample is running on localhost,
    # and to generate https scheme when it is deployed behind reversed proxy.
    # See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    #MSAI CONF
    from model import db
    db.init_app(app)

    return app


if __name__ == "__main__":
    app = create_app("config")
    app.run(host="localhost",port=7000,debug=True)