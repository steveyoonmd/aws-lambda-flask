import os
from datetime import datetime

import boto3
from flask import Blueprint, g, current_app, session, request
from werkzeug.utils import secure_filename

from libs.dict_as_obj import DictAsObj
from libs.enums import Error
from libs.utils import respond_if_options, connect_database, is_access_allowed_ip_addr, is_user_logged_in, make_resp

tests2 = Blueprint('tests2', __name__, url_prefix='/tests2')


@tests2.before_request
def before_request():
    g.cfg = current_app.config['G_CFG']
    g.sess = session
    g.req = request
    g.res = DictAsObj({
        'err': Error.UNKNOWN,
        'url': '',
        'dat': None,
    })

    g.db = {}
    g.cursor = {}

    g.sess['domain'] = g.req.headers.get('Host', g.cfg['session']['domain'])
    connect_database('test1')


@tests2.teardown_request
def teardown_request(ex=None):
    for key in g.cursor.keys():
        g.cursor[key].close()

    for key in g.db.keys():
        g.db[key].close()


@tests2.route('/test_json', methods=['OPTIONS', 'POST'])
@respond_if_options()
def test_json():
    if not is_access_allowed_ip_addr() or not is_user_logged_in():
        return make_resp()

    req_json = request.get_json()

    g.cursor['test1'].execute('SELECT VERSION() AS version')
    rows = g.cursor['test1'].fetchall()

    g.res.err = Error.NONE
    g.res.dat = {'test_json': 'OK', 'a': req_json.get('a'), 'b': req_json.get('b'), 'rows': rows}
    return make_resp()


@tests2.route('/test_upload', methods=['OPTIONS', 'POST'])
@respond_if_options()
def test_upload():
    if not is_access_allowed_ip_addr() or not is_user_logged_in():
        return make_resp()

    if 'file' not in request.files:
        g.res.err = Error.UNKNOWN
        g.res.dat = {'test_upload': 'not uploaded'}
        return make_resp()

    file = request.files['file']
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'gif']:
        file_name = secure_filename(file.filename)
        file_path = os.path.join(g.cfg['upload']['directory'], file_name)
        file.save(file_path)

        g.res.err = Error.NONE
        g.res.dat = {'test_upload': 'file saved', 'name': request.form.get('name')}
        return make_resp()

        s3 = boto3.client('s3')
        s3.upload_file(file_path, g.cfg['aws_s3']['bucket'],
                       os.path.join('{0:%Y-%m-%d}'.format(datetime.now()), file_name))

        g.res.err = Error.NONE
        g.res.dat = {'test_upload': 'uploaded to s3', 'name': request.form.get('name')}
        return make_resp()

    g.res.err = Error.NONE
    g.res.dat = {'test_upload': 'not an image file'}
    return make_resp()
