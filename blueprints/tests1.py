from datetime import datetime

from flask import Blueprint, g, current_app, session, request

from libs.dict_as_obj import DictAsObj
from libs.enums import Error
from libs.utils import respond_if_options, connect_database, is_access_allowed_ip_addr, is_user_logged_in, make_resp

tests1 = Blueprint('tests1', __name__, url_prefix='/tests1')


@tests1.before_request
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


@tests1.teardown_request
def teardown_request(ex=None):
    for key in g.cursor.keys():
        g.cursor[key].close()

    for key in g.db.keys():
        g.db[key].close()


@tests1.route('/test_get', methods=['OPTIONS', 'GET'])
@respond_if_options()
def test_get():
    if not is_access_allowed_ip_addr() or not is_user_logged_in():
        return make_resp()

    query = 'INSERT INTO test1(col01, col02, col03, col04, col05, col06, col07, col08, col09, col10, col11, ' \
            'col12) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()) '
    params = (255, 65535, 429496729, 1844674407370955161, 5.01, 6.01, 'param7', 'param8', 'param9',
              '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.now()), None)
    g.cursor['test1'].execute(query, params)
    g.db['test1'].commit()
    last_row_id = g.cursor['test1'].lastrowid

    query = 'UPDATE test1 SET col01 = %s WHERE test1_id = %s'
    params = (254, last_row_id)

    g.cursor['test1'].execute(query, params);
    g.db['test1'].commit()
    row_count = g.cursor['test1'].rowcount

    g.res.err = Error.NONE
    g.res.dat = {'test_get': 'OK', 'a': request.args.get('a'), 'b': request.args.get('b'), 'last_row_id': last_row_id,
                 'row_count': row_count}
    return make_resp()


@tests1.route('/test_post', methods=['OPTIONS', 'POST'])
@respond_if_options()
def test_post():
    if not is_access_allowed_ip_addr() or not is_user_logged_in():
        return make_resp()

    query = 'SELECT * FROM test1 ORDER BY test1_id DESC LIMIT %s OFFSET %s '
    params = (1, 0)

    g.cursor['test1'].execute(query, params)
    row = g.cursor['test1'].fetchone()

    row['col09'] = row['col09'].decode('utf-8')

    g.res.err = Error.NONE
    g.res.dat = {'test_post': 'OK', 'a': request.form.get('a'), 'b': request.form.get('b'), 'row': row}
    return make_resp()
