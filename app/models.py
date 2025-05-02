from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nik = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    

    
class Submissions(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_bpp = db.Column(db.String(255))
    house_category_id = db.Column(db.Integer, db.ForeignKey('house_category.id'), nullable=False)
    income_category_id = db.Column(db.Integer, db.ForeignKey('income_category.id'), nullable=False)
    family_status_id = db.Column(db.Integer, db.ForeignKey('family_status.id'), nullable=False)
    total_children = db.Column(db.Integer)
    income = db.Column(db.Integer)
    tnc = db.Column(db.Boolean)
    status_pengajuan = db.Column(db.String(20))
    total_bad_debt = db.Column(db.Integer)
    total_good_debt = db.Column(db.Integer)
    years_of_working = db.Column(db.Integer)
    applicant_age = db.Column(db.Integer)
    credit_card_category_id = db.Column(db.Integer, db.ForeignKey('card_category.id'), nullable=False)

    user = db.relationship('Users', backref='submissions')
    HouseCategory = db.relationship('HouseCategory', backref='house_category')
    IncomeCategory = db.relationship('IncomeCategory', backref='income_category')
    FamilyStatus = db.relationship('FamilyStatus', backref='family_status')
    CardCategory = db.relationship('CardCategory', backref='card_category')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    

class HasanahCards(db.Model):
    __tablename__ = 'hasanah_cards'

    id = db.Column(db.Integer, primary_key=True)
    nomor_hasanah = db.Column(db.Integer)
    tanggal_exp = db.Column(db.Date)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pin = db.Column(db.Integer)
    jenis_kartu = db.Column(db.String(255))
    limit_kartu = db.Column(db.Integer)

    user = db.relationship('Users', backref='hasanah_cards')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class HouseCategory(db.Model):
    __tablename__ = 'house_category'

    id = db.Column(db.Integer, primary_key=True)
    house_category_desc = db.Column(db.String(255), nullable=False)

class IncomeCategory(db.Model):
    __tablename__ = 'income_category'

    id = db.Column(db.Integer, primary_key=True)
    income_category_desc = db.Column(db.String(255), nullable=False)

class FamilyStatus(db.Model):
    __tablename__ = 'family_status'

    id = db.Column(db.Integer, primary_key=True)
    family_status_desc = db.Column(db.String(255), nullable=False)

class CardCategory(db.Model):
    __tablename__ = 'card_category'

    id = db.Column(db.Integer, primary_key=True)
    card_category_desc = db.Column(db.String(255), nullable=False)
