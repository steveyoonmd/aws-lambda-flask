
from flask import Blueprint, session, request
from libs.utils import respond_if_options, make_resp, request

test1 = Blueprint('test1', __name__, url_prefix='/test1')

@test1.before_request
def before_request():
    session['domain'] = request.headers.get('Host', 'localhost')

@test1.route('/test_get', methods=['OPTIONS', 'GET'])
@respond_if_options()
def test_get():
    session['userid'] = 'steve'

    return make_resp(request, {'test_get': 'OK', 'a': request.args.get('a'), 'b': request.args.get('b')})

@test1.route('/test_post', methods=['OPTIONS', 'POST'])
@respond_if_options()
def test_post():
    return make_resp(request, {'test_post': 'OK', 'a': request.form.get('a'), 'b': request.form.get('b')})
