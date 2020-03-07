import json
import os
import sys
from datetime import datetime

import pymysql


def main():
    if len(sys.argv) < 3:
        print('Usage: python3 ./mysqldiff.py localhost dev')
        sys.exit()

    # mkdir
    data_dir = './mysqldiff/'
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    # remove all files
    files = os.listdir(data_dir)
    for f in files:
        os.remove(os.path.join(data_dir, f))

    with open('./tools.json', encoding='utf-8') as cfg_json:
        cfg = json.loads(cfg_json.read())

    for k in [sys.argv[1], sys.argv[2]]:
        conn = pymysql.connect(host=cfg[k]['host'], user=cfg[k]['user'], password=cfg[k]['password'],
                               database=cfg[k]['database'], port=cfg[k]['port'], cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        cursor.execute('SHOW TABLES')
        show_tables = cursor.fetchall()

        tables = []
        for show_table in show_tables:
            tables.append(show_table['Tables_in_' + cfg[k]['database']])

        select_counts = []
        create_tables = []
        for table in tables:
            # cursor.execute('SELECT COUNT(*) AS cnt FROM ' + table)
            # select_counts.append(cursor.fetchone()['cnt'])

            cursor.execute('SHOW CREATE TABLE ' + table)
            create_table = cursor.fetchone()['Create Table']

            create_table_split = create_table.split(' ')
            create_table_split_new = []
            for s in create_table_split:
                if 'AUTO_INCREMENT=' in s:
                    continue
                create_table_split_new.append(s)
            create_tables.append(' '.join(create_table_split_new))

        now = '{0:%Y%m%d%H%M%S}'.format(datetime.now())
        with open(os.path.join(data_dir, '{}_{}_{}{}{}'.format('create', 'tbl', k, now, '.sql')), 'a') as tbl:
            tbl.write(';\n\n'.join(create_tables))
            tbl.write(';')

        # with open(os.path.join(data_dir, '{}_{}_{}{}{}'.format('select', 'cnt', k, now, '.csv')), 'a') as cnt:
        #     for i in range(len(tables)):
        #         cnt.write(tables[i] + ',' + str(select_counts[i]) + '\n')

        cursor.close()
        conn.close()


main()
