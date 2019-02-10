from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Currency(Base):
    __tablename__ = 'currency'

    code = Column(String, primary_key=True)
    num = Column(Integer)
    name = Column(String)
    minor_unit = Column(Integer)

    def __init__(self, code, num=None, name=None, minor_unit=None):
        self.code = code
        self.num = num
        self.name = name
        self.minor_unit = minor_unit

    def __str__(self):

        out = [
            str(self.code),
            str(self.num),
            str(self.name),
            str(self.minor_unit),
        ]
        return ",".join(out)

    def __eq__(self, other):
        if isinstance(other, Currency):
            return (self.code == other.code) and (self.num == other.num)
        return False
