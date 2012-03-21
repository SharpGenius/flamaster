from flamaster.app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(20), nullable=True)
    addresses = db.relationship('Address', lazy='dynamic',
                                backref=db.backref('user', lazy='joined'),
                                cascade="all, delete, delete-orphan")

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return "<User: %r>" % self.email

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    @classmethod
    def authenticate(cls, email, password):
        return cls.query.filter_by(email=email,
                password=password).first()


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    users = db.relationship('User', lazy='dynamic',
                            backref=db.backref('role', lazy='joined'))
