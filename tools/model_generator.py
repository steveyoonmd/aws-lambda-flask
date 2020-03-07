import json
import os
import sys

import pymysql


def camel_case(table_name):
    table_name_split = table_name.split('_')

    table_name_split_new = []
    for s in table_name_split:
        table_name_split_new.append(s[0].upper() + s[1:])

    return ''.join(table_name_split_new)


def tab():
    return '    '


def sql_alchemy_name(n):
    return n


def sql_alchemy_type(t):
    if t == 'bigint' or 'bigint(' in t:
        return 'db.BigInteger'
    elif t == 'int' or 'int(' in t:
        return 'db.Integer'
    elif 'varchar(' in t:
        return 'db.' + t.replace('varchar', 'String')
    elif 'char(' in t:
        return 'db.' + t.replace('char', 'String')
    elif t == 'date':
        return 'db.Date'
    elif t == 'datetime' or 'datetime(' in t:
        return 'db.DateTime'
    elif t == 'float' or 'float(' in t or t == 'double' or 'double(' in t:
        return 'db.Float'
    elif 'decimal(' in t:
        return 'db.' + t.replace('decimal', 'Numeric')
    elif 'text' in t:
        return 'db.Text'
    elif 'blob' in t:
        return 'db.Binary'
    else:
        print(t)

    return ''


def sql_alchemy_key(k):
    if k == 'PRI':
        return 'primary_key=True'
    elif k == 'UNI':
        return 'unique=True'

    return ''


def sql_alchemy_nullable(n):
    if n == 'YES':
        return 'nullable=True'

    return 'nullable=False'


def sql_alchemy_default(t, d):
    if d is not None:
        if 'db.BigInteger' in t:
            return 'default=' + str(d)
        elif 'db.Integer' in t:
            return 'default=' + str(d)
        elif 'db.String' in t:
            return "default='" + str(d) + "'"
        elif 'db.Date' in t:
            return "default='" + str(d) + "'"
        elif 'db.Float' in t:
            return 'default=' + str(d)
        elif 'db.Decimal' in t:
            return 'default=' + str(d)
        elif 'db.Text' in t:
            return "default='" + str(d) + "'"
        else:
            print(t)

    return ''


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 ./model_generator.py localhost')
        sys.exit()
    k = sys.argv[1]

    # mkdir
    data_dir = './generated_models/'
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    # remove all files
    files = os.listdir(data_dir)
    for f in files:
        os.remove(os.path.join(data_dir, f))

    with open('./tools.json', encoding='utf-8') as cfg_json:
        cfg = json.loads(cfg_json.read())

    conn = pymysql.connect(host=cfg[k]['host'], user=cfg[k]['user'],
                           password=cfg[k]['password'],
                           database=cfg[k]['database'], port=cfg[k]['port'], cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    cursor.execute('SHOW TABLES')
    show_tables = cursor.fetchall()

    tables = []
    for show_table in show_tables:
        tables.append(show_table['Tables_in_' + cfg[k]['database']])

    for table in tables:
        # print('alter table ' + table + ' convert to character set utf8mb4;')
        # continue

        cursor.execute('DESC ' + table)
        desc_table = cursor.fetchall()

        lines = ['from app import db', '', '', 'class ' + camel_case(table) + '(db.Model):']
        for row in desc_table:
            column_type = sql_alchemy_type(row['Type'])
            db_column = [column_type]

            column_key = sql_alchemy_key(row['Key'])
            if column_key != '':
                db_column.append(column_key)

            column_null = sql_alchemy_nullable(row['Null'])
            if column_null != '':
                db_column.append(column_null)

            column_default = sql_alchemy_default(column_type, row['Default'])
            if column_default != '':
                db_column.append(column_default)

            lines.append(tab() + sql_alchemy_name(row['Field']) + " = db.Column('" + row['Field'] + "', " + ', '.join(
                db_column) + ')')

        with open(os.path.join(data_dir, table + '.py'), 'a') as f:
            f.write('\n'.join(lines) + '\n')

    cursor.close()
    conn.close()


main()
