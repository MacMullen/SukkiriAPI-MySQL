# models.py
import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60))
    last_name = db.Column(db.String(60))
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(60))


class DistributionCompany(db.Model):
    __tablename__ = 'dist_companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    email = db.Column(db.String(60))
    address = db.Column(db.String(200))
    hours = db.Column(db.String(13))
    contact_name = db.Column(db.String(60))
    phone = db.Column(db.String(60))


class Product(db.Model):
    __tablename__ = 'products'
    __table_args__ = (
        db.UniqueConstraint('brand', 'model'),
    )

    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(120), index=True)
    model = db.Column(db.String(120), index=True)
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    stock_under_control = db.Column(db.Boolean)
    distribution_company = db.Column(db.String(120))
    ean = db.Column(db.String(20))


class RMACase(db.Model):
    __tablename__ = 'rma_products'

    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(60))
    model = db.Column(db.String(60))
    problem = db.Column(db.Text)
    serial_number = db.Column(db.String(120))
    distribution_company = db.Column(db.String(60), index=True)
    status = db.Column(db.String(60), default="to_be_revised")
    to_be_revised_date = db.Column(db.DateTime, default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
    to_be_revised_by = db.Column(db.String(60))
    to_be_sent_date = db.Column(db.String(18))
    to_be_sent_by = db.Column(db.String(60))
    sent_date = db.Column(db.String(18))
    sent_by = db.Column(db.String(60))
    returned_date = db.Column(db.String(18))
    returned_by = db.Column(db.String(60))
    resolved_date = db.Column(db.String(18))
    resolved_by = db.Column(db.String(60))
    unresolved_date = db.Column(db.String(18))
    unresolved_by = db.Column(db.String(60))
