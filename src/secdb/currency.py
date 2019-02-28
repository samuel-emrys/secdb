from sqlalchemy import Column, Integer, String
from secdb.database import Base
from sqlalchemy.orm import relationship
# from secdb.symbol import Symbol


class Currency(Base):
    __tablename__ = 'currency'

    code = Column(String, primary_key=True)
    num = Column(Integer)
    name = Column(String)
    minor_unit = Column(Integer)

    # Relationship management
    # Currency has many symbols
    symbols = relationship('Symbol', back_populates='currency')

    def __str__(self):

        out = [
            str(self.code),
            str(self.num),
            str(self.name),
            str(self.minor_unit),
        ]
        return ",".join(out)

    # Overload equality operator for list comparisons
    def __eq__(self, other):
        if isinstance(other, Currency):
            return (self.code == other.code)
        elif isinstance(other, str):
            return (self.code == other)
        return False
