from app import db


class Test1(db.Model):
    test1_id = db.Column('test1_id', db.BigInteger, primary_key=True, nullable=False)
    col01 = db.Column('col01', db.Integer, nullable=False)
    col02 = db.Column('col02', db.Integer, nullable=False)
    col03 = db.Column('col03', db.Integer, nullable=True)
    col04 = db.Column('col04', db.BigInteger, nullable=False)
    col05 = db.Column('col05', db.Float, nullable=False)
    col06 = db.Column('col06', db.Float, nullable=False)
    col07 = db.Column('col07', db.String(10), nullable=False)
    col08 = db.Column('col08', db.Text, nullable=False)
    col09 = db.Column('col09', db.Binary, nullable=False)
    col10 = db.Column('col10', db.DateTime, nullable=False)
    col11 = db.Column('col11', db.Integer, nullable=True)
    col12 = db.Column('col12', db.DateTime, nullable=False)
