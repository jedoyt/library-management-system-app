import os
from flask import Flask


def create_app(test_config=None):
    """
    Run app on command line:
    $ flask --app app run --debug
    """
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app_db.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    from . import db
    db.init_app(app=app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import book_log
    app.register_blueprint(book_log.bp)

    from . import book
    app.register_blueprint(book.bp)

    from . import error_handlers
    app.register_blueprint(error_handlers.bp)

    return app