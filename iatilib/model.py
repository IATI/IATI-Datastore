from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,DateTime,Date,BigInteger,Float,ForeignKey,Boolean,UnicodeText
from . import engine

Base = declarative_base(bind=engine)


class IndexedResource(Base):
    __tablename__ = 'indexed_resource'
    id = Column(UnicodeText, primary_key=True)
    url = Column(UnicodeText)
    last_modified = Column(DateTime)
    def apply_update(self,other):
        self.url = other.url
        self.last_modified = other.last_modified

class Sector(Base):
    __tablename__ = 'sector'
    id = Column(Integer, primary_key=True)   
    activity_iati_identifier = Column(UnicodeText, index=True)
    name = Column(UnicodeText)
    vocabulary = Column(UnicodeText)
    code = Column(UnicodeText)
    percentage = Column(Integer)



Base.metadata.create_all()
