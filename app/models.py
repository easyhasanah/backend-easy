from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nik = db.Column(db.Integer, nullable=False)
    nama_lengkap = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    

    
class Submissions(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_bpp = db.Column(db.String(255))
    kategori_rumah = db.Column(db.String(255))
    kategori_pemasukan = db.Column(db.String(255))
    status_keluarga = db.Column(db.String(255))
    jumlah_anak = db.Column(db.String(255))
    income = db.Column(db.Integer)
    tnc = db.Column(db.Boolean)
    status_pengajuan = db.Column(db.String(20))

    user = db.relationship('Users', backref='submissions')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    

class HasanahCards(db.Model):
    __tablename__ = 'hasanahcards'

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

class Rumah(db.Model):
    __tablename__ = 'rumah'

    id = db.Column(db.Integer, primary_key=True)
    nama_kategori_rumah = db.Column(db.String(255), nullable=False)

class Pemasukan(db.Model):
    __tablename__ = 'pemasukan'

    id = db.Column(db.Integer, primary_key=True)
    nama_kategori_pemasukan = db.Column(db.String(255), nullable=False)

class Keluarga(db.Model):
    __tablename__ = 'keluarga'

    id = db.Column(db.Integer, primary_key=True)
    nama_status_keluarga = db.Column(db.String(255), nullable=False)

class Pendidikan(db.Model):
    __tablename__ = 'pendidikan'

    id = db.Column(db.Integer, primary_key=True)
    nama_pendidikan = db.Column(db.String(255), nullable=False)
