
import os
from functools import update_wrapper

from flask import current_app, make_response, request, session, send_from_directory
from werkzeug.utils import secure_filename

from aws_lambda import AwsLambdaFlask


origins = [
    'http://ec2-52-79-228-44.ap-northeast-2.compute.amazonaws.com:5000',
]


def with_origin(req):
    origin = req.headers.get('Origin', '')

    if origin not in origins:
        origin = origins[0]

    return {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'DELTE, GET, HEAD, OPTIONS, PATCH, POST, PUT',
        'Access-Control-Allow-Headers': 'Authorization, Content-Type, Cookie, Origin, X-Amz-Date, X-Amz-Security-Token, X-Api-Key, x-forced-preflight',
        'Access-Control-Allow-Credentials': 'true',
    }


def make_resp(req, body):
    resp = make_response(body)

    headers = with_origin(req)
    for key, value in headers.items():
        resp.headers[key] = value

    return resp


def create_app():
    app = AwsLambdaFlask(__name__)
    app.secret_key = 'this_is_my_secret_key'
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        # A future release of Chrome will only deliver cookies with cross-site requests
        # if they are set with `SameSite=None` and `Secure`.
        SESSION_COOKIE_SAMESITE=None,
        SESSION_COOKIE_SECURE=True,
    )
    app.config['UPLOAD_FOLDER'] = './upload/'
    
    @app.before_request
    def before_request():
        session['domain'] = request.headers.get('Host', 'localhost')

    # https://stackoverflow.com/questions/26980713/solve-cross-origin-resource-sharing-with-flask
    def respond_if_options():
        def decorator(f):
            def wrapped_function(*args, **kwargs):
                if request.method == 'OPTIONS':
                    opts_resp = current_app.make_default_options_response()
                else:
                    opts_resp = make_response(f(*args, **kwargs))

                headers = with_origin(request)
                for key, value in headers.items():
                    opts_resp.headers[key] = value

                return opts_resp

            f.provide_automatic_options = False
            return update_wrapper(wrapped_function, f)

        return decorator

    @app.route('/', methods=['OPTIONS', 'GET'])
    @respond_if_options()
    def index():
        return make_resp(request, {'index': 'OK'})

    @app.route('/doc/<path:path>', methods=['GET'])
    def doc(path):
        return send_from_directory('doc', path)

    @app.route('/test_get', methods=['OPTIONS', 'GET'])
    @respond_if_options()
    def test_get():
        session['userid'] = 'steve'

        return make_resp(request, {'test_get': 'OK', 'a': request.args.get('a'), 'b': request.args.get('b')})
        
    @app.route('/test_post', methods=['OPTIONS', 'POST'])
    @respond_if_options()
    def test_post():
        return make_resp(request, {'test_post': 'OK', 'a': request.form.get('a'), 'b': request.form.get('b')})

    @app.route('/test_json', methods=['OPTIONS', 'POST'])
    @respond_if_options()
    def test_json():
        req_json = request.get_json()

        return make_resp(request, {'test_json': 'OK', 'a': req_json.get('a'), 'b': req_json.get('b')})

    @app.route('/test_upload', methods=['OPTIONS', 'POST'])
    @respond_if_options()
    def test_upload():
        if 'file' not in request.files:
            return make_resp(request, {'test_upload': 'no files'})

        file = request.files['file']
        if file.filename == '':
            return make_resp(request, {'test_upload': 'no filename'})

        if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'gif']:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
            return make_resp(request, {'test_upload': 'saved', 'name': request.form.get('name')})

        return make_resp(request, {'test_upload': 'OK'})

    return app


run = create_app()
