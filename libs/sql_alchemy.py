from sqlalchemy.sql import func
from sqlalchemy.types import Integer, BigInteger, Float, String, DateTime, Text, Binary

from app import db


def select_count_without_sub_query(query):
    select_count = query.statement.with_only_columns([func.count()])
    # print(select_count)
    return db.session.execute(select_count).scalar()


def json_serializable(rows):
    if rows is None:
        return None

    if isinstance(rows, list):
        serializable = []
        for row in rows:
            tmp = {}
            for column in row.__table__.columns:
                if isinstance(column.type, Integer):
                    tmp[column.name] = getattr(row, column.name, 0)
                elif isinstance(column.type, BigInteger):
                    tmp[column.name] = getattr(row, column.name, 0)
                elif isinstance(column.type, Float):
                    tmp[column.name] = getattr(row, column.name, 0)
                elif isinstance(column.type, String):
                    tmp[column.name] = getattr(row, column.name, '')
                elif isinstance(column.type, Text):
                    tmp[column.name] = getattr(row, column.name, '')
                elif isinstance(column.type, Binary):
                    tmp[column.name] = getattr(row, column.name, '').decode('utf-8')
                elif isinstance(column.type, DateTime):
                    tmp[column.name] = '{0:%Y-%m-%d %H:%M:%S}'.format(getattr(row, column.name, 0))
                else:
                    tmp[column.name] = getattr(row, column.name)

            serializable.append(tmp)
    else:
        serializable = {}
        for column in rows.__table__.columns:
            if isinstance(column.type, Integer):
                serializable[column.name] = getattr(rows, column.name, 0)
            elif isinstance(column.type, BigInteger):
                serializable[column.name] = getattr(rows, column.name, 0)
            elif isinstance(column.type, Float):
                serializable[column.name] = getattr(rows, column.name, 0)
            elif isinstance(column.type, String):
                serializable[column.name] = getattr(rows, column.name, '')
            elif isinstance(column.type, Text):
                serializable[column.name] = getattr(rows, column.name, '')
            elif isinstance(column.type, Binary):
                serializable[column.name] = getattr(rows, column.name, '').decode('utf-8')
            elif isinstance(column.type, DateTime):
                serializable[column.name] = '{0:%Y-%m-%d %H:%M:%S}'.format(getattr(rows, column.name, 0))
            else:
                serializable[column.name] = getattr(rows, column.name)

            serializable[column.name] = getattr(rows, column.name)

    return serializable
