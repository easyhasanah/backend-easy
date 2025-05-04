from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from app.config import Config
from sqlalchemy import create_engine

Base = declarative_base()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)

    submissions = relationship("Submissions", back_populates="user")
    hasanah_cards = relationship("HasanahCards", back_populates="user")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Submissions(Base):
    __tablename__ = 'submissions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_bpp = Column(String(255))
    house_category = Column(String(255))
    income_type = Column(String(255))
    family_status = Column(String(255))
    total_children = Column(Integer)
    total_income = Column(Integer)
    tnc = Column(Boolean)
    status_pengajuan = Column(String(255))
    total_bad_debt = Column(Integer)
    total_good_debt = Column(Integer)
    years_of_working = Column(Integer)
    applicant_age = Column(Integer)
    nik = Column(String(255))

    user = relationship("Users", back_populates="submissions")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class HasanahCards(Base):
    __tablename__ = 'hasanah_cards'

    id = Column(Integer, primary_key=True)
    card_no = Column(String(255))
    expired_date = Column(Date)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    pin = Column(String(255))
    card_category_id = Column(Integer, ForeignKey('card_categories.id'))

    user = relationship("Users", back_populates="hasanah_cards")
    card_category = relationship("CardCategories", back_populates="cards")

    def to_dict(self):
        data = {c.name: getattr(self, c.name) for c in self._table_.columns}
        if self.expired_date:
            data["expired_date"] = self.expired_date.strftime("%m/%y")  # misal: "09/24"
        return data


class CardCategories(Base):
    __tablename__ = 'card_categories'

    id = Column(Integer, primary_key=True)
    type = Column(String(255))
    category = Column(Integer)
    limit = Column(Integer)

    cards = relationship("HasanahCards", back_populates="card_category")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
