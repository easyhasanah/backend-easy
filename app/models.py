from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class Submissions(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_bpp = db.Column(db.String(255))
    house_category = db.Column(db.String(255))
    income_type = db.Column(db.String(255))
    family_status = db.Column(db.String(255))
    total_children = db.Column(db.Integer)
    income = db.Column(db.Integer)
    tnc = db.Column(db.Boolean)
    status_pengajuan = db.Column(db.String(20))
    total_bad_debt = db.Column(db.Integer)
    total_good_debt = db.Column(db.Integer)
    years_of_working = db.Column(db.Integer)
    applicant_age = db.Column(db.Integer)
    nik = db.Column(db.String(255))

    user = db.relationship('Users', backref='submissions')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class HasanahCards(db.Model):
    __tablename__ = 'hasanah_cards'

    id = db.Column(db.Integer, primary_key=True)
    card_no = db.Column(db.String(255))
    expired_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pin = db.Column(db.String(6))
    card_category_id = db.Column(db.Integer, db.ForeignKey('card_categories.id'), nullable=True)

    user = db.relationship('Users', backref='hasanah_cards')
    card_category = db.relationship('CardCategories', backref='card_categories')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class CardCategories(db.Model):
    __tablename__ = 'card_categories'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255))
    category = db.Column(db.Integer)
    limit = db.Column(db.Integer)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
