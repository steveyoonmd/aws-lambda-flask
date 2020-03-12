from datetime import timedelta
import json

from flask import g, request, session, redirect
from flask_sqlalchemy import SQLAlchemy

from libs.aws_lambda import AwsLambdaFlask
from libs.dict_as_obj import DictAsObj
from libs.enums import Error
from libs.utils import md5hex, is_user_logged_in

db = SQLAlchemy()


def app_config(app, file):
    cfg = {}
    with open(file, encoding='utf-8') as cfg_json:
        cfg = json.loads(cfg_json.read())

    app.config.update(
        SECRET_KEY=md5hex(cfg['application']['secret_key']),
        SESSION_COOKIE_HTTPONLY=True,
        # A future release of Chrome will only deliver cookies with cross-site requests
        # if they are set with `SameSite=None` and `Secure`.
        SESSION_COOKIE_SAMESITE=None,
        # SESSION_COOKIE_SECURE=True,
        SESSION_PERMANENT=cfg['session']['permanent'],
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=cfg['session']['lifetime_minutes']),
        SESSION_COOKIE_DOMAIN=cfg['session']['domain'],
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_DATABASE_URI='mysql+pymysql://{}:{}@{}/{}?charset={}'.format(cfg['database_test1']['user'],
                                                                                cfg['database_test1']['password'],
                                                                                cfg['database_test1']['host'],
                                                                                cfg['database_test1']['database'],
                                                                                cfg['database_test1']['charset']),
    )

    app.config['G_CFG'] = {}
    for key1 in cfg.keys():
        if key1 == 'application':
            continue

        if isinstance(cfg[key1], list):
            app.config['G_CFG'][key1] = []
            for value2 in cfg[key1]:
                app.config['G_CFG'][key1].append(value2)
        elif isinstance(cfg[key1], dict):
            app.config['G_CFG'][key1] = {}
            for key2, value2 in cfg[key1].items():
                app.config['G_CFG'][key1][key2] = value2
        else:
            app.config['G_CFG'][key1] = cfg[key1]


def create_app():
    app = AwsLambdaFlask(__name__, static_folder='static', static_url_path='/static')
    app.url_map.strict_slashes = False
    app_config(app, './cfg.json')

    db.init_app(app)
    with app.app_context():
        db.create_all()

    from blueprints.tests1 import tests1
    from blueprints.tests2 import tests2
    from blueprints.tests3 import tests3
    from blueprints.users import users

    app.register_blueprint(tests1)
    app.register_blueprint(tests2)
    app.register_blueprint(tests3)
    app.register_blueprint(users)

    @app.before_request
    def before_request():
        g.cfg = app.config['G_CFG']
        g.sess = session
        g.req = request
        g.res = DictAsObj({
            'err': Error.UNKNOWN,
            'url': '',
            'dat': None,
        })

    @app.route('/')
    def index():
        if is_user_logged_in():
            return redirect('./static/main_index.html')

        return redirect('./static/users_login.html?return_url=main_index.html')

    return app


run = create_app()
