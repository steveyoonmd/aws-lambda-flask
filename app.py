
from flask import request, session, request

from libs.aws_lambda import AwsLambdaFlask
from libs.utils import respond_if_options, make_resp

def create_app():
    app = AwsLambdaFlask(__name__, static_folder='static', static_url_path='/static')

    app.secret_key = 'this_is_my_secret_key'
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        # A future release of Chrome will only deliver cookies with cross-site requests
        # if they are set with `SameSite=None` and `Secure`.
        SESSION_COOKIE_SAMESITE=None,
        SESSION_COOKIE_SECURE=True,
    )
    app.config['UPLOAD_FOLDER'] = '/tmp/'
    

    from blueprints.test1 import test1
    from blueprints.test2 import test2

    app.register_blueprint(test1)
    app.register_blueprint(test2)
    
    @app.before_request
    def before_request():
        session['domain'] = request.headers.get('Host', 'localhost')

    @app.route('/', methods=['OPTIONS', 'GET'])
    @respond_if_options()
    def index():
        return make_resp(request, {'index': 'OK'})

    return app


run = create_app()
