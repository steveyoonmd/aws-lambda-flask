
import os

from flask import Blueprint, session, request, current_app
from werkzeug.utils import secure_filename

from libs.utils import respond_if_options, make_resp

test2 = Blueprint('test2', __name__, url_prefix='/test2')

@test2.before_request
def before_request():
    session['domain'] = request.headers.get('Host', 'localhost')

@test2.route('/test_json', methods=['OPTIONS', 'POST'])
@respond_if_options()
def test_json():
    req_json = request.get_json()

    return make_resp(request, {'test_json': 'OK', 'a': req_json.get('a'), 'b': req_json.get('b')})

@test2.route('/test_upload', methods=['OPTIONS', 'POST'])
@respond_if_options()
def test_upload():
    if 'file' not in request.files:
        return make_resp(request, {'test_upload': 'no files'})

    file = request.files['file']
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'gif']:
        file.save(os.path.join(current_app.config.get('UPLOAD_FOLDER'), secure_filename(file.filename)))
        return make_resp(request, {'test_upload': 'saved', 'name': request.form.get('name')})

    return make_resp(request, {'test_upload': 'OK'})
