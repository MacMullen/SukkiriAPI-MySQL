import datetime
import os
import uuid
from functools import wraps

import jwt
from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

from lib.models import *

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SUKKIRI_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SUKKIRI_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

migrate = Migrate(app, db)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = db.session.query(User).filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/api/rma_cases', methods=['GET'])
@token_required
def get_all_rma_cases(current_user):
    rma_cases = db.session.query(RMACase).all()

    output = []

    for rma_case in rma_cases:
        rma_case_data = {'id': rma_case.id, 'brand': rma_case.brand, 'model': rma_case.model,
                         'problem': rma_case.problem, 'serial_number': rma_case.serial_number,
                         'distribution_company': rma_case.distribution_company,
                         'sent_date': rma_case.sent_date, 'returned_date': rma_case.sent_date,
                         'resolved_date': rma_case.resolved_date, 'status': rma_case.status,
                         'to_be_revised_date': rma_case.to_be_revised_date,
                         'unresolved_date': rma_case.unresolved_date,
                         'to_be_sent_date': rma_case.to_be_sent_date,
                         'to_be_revised_by': rma_case.to_be_revised_by,
                         'to_be_sent_by': rma_case.to_be_sent_by, 'sent_by': rma_case.sent_by,
                         'returned_by': rma_case.returned_by,
                         'resolved_by': rma_case.resolved_by, 'unresolved_by': rma_case.unresolved_by}
        output.append(rma_case_data)
    return jsonify({'rma_cases': output})


@app.route('/api/rma_cases', methods=['POST'])
@token_required
def create_new_rma_case(current_user):
    data = request.get_json()

    if 'brand' not in data:
        return jsonify({'message': 'You must specify a brand!'})
    if 'model' not in data:
        return jsonify({'message': 'You must specify a model!'})
    if 'problem' not in data:
        return jsonify({'message': 'You must specify a problem!'})
    if 'serial_number' not in data:
        data['serial_number'] = 'N/A'
    if 'distribution_company' not in data:
        data['distribution_company'] = 'N/A'

    new_rma_case = RMACase(brand=data['brand'], model=data['model'], problem=data['problem'],
                           serial_number=data['serial_number'], distribution_company=data['distribution_company'],
                           to_be_revised_date=datetime.datetime.now().strftime('%d-%m-%Y %H:%M'),
                           to_be_revised_by=current_user.first_name + ' ' + current_user.last_name)

    try:
        db.session.add(new_rma_case)
        db.session.commit()
        return jsonify({'message': 'New RMA case created!', 'case': new_rma_case.id})
    except:
        return jsonify({'message': 'Could not create the RMA case'})


@app.route('/api/rma_cases/<rma_case_id>', methods=['GET'])
@token_required
def get_rma_case(current_user, rma_case_id):
    rma_case = db.session.query(RMACase).filter_by(id=rma_case_id).first()

    if not rma_case:
        return jsonify({'message': 'No RMA case found!'})

    rma_case_data = {'id': rma_case.id, 'brand': rma_case.brand, 'model': rma_case.model,
                     'problem': rma_case.problem, 'serial_number': rma_case.serial_number,
                     'distribution_company': rma_case.distribution_company,
                     'sent_date': rma_case.sent_date, 'returned_date': rma_case.sent_date,
                     'resolved_date': rma_case.resolved_date, 'status': rma_case.status,
                     'to_be_revised_date': rma_case.to_be_revised_date,
                     'unresolved_date': rma_case.unresolved_date,
                     'to_be_sent_date': rma_case.to_be_sent_date,
                     'to_be_revised_by': rma_case.to_be_revised_by,
                     'to_be_sent_by': rma_case.to_be_sent_by, 'sent_by': rma_case.sent_by,
                     'returned_by': rma_case.returned_by,
                     'resolved_by': rma_case.resolved_by, 'unresolved_by': rma_case.unresolved_by}

    return jsonify({'rma_case': rma_case_data})


@app.route('/api/rma_cases/<rma_case_id>', methods=['PUT'])
@token_required
def modify_rma_case(current_user, rma_case_id):
    rma_case = db.session.query(RMACase).filter_by(id=rma_case_id).first()

    if not rma_case:
        return jsonify({'message': 'No RMA case found!'})

    data = request.get_json()

    if 'problem' in data:
        rma_case.problem = data['problem']
    if 'serial_number' in data:
        rma_case.serial_number = data['serial_number']
    if 'distribution_company' in data:
        rma_case.distribution_company = data['distribution_company']

    db.session.commit()

    return jsonify({'message': 'RMA case modified successfully!'})


@app.route('/api/rma_cases/<rma_case_id>/status/<new_status>', methods=['POST'])
@token_required
def modify_rma_case_status(current_user, rma_case_id, new_status):
    rma_case = db.session.query(RMACase).filter_by(id=rma_case_id).first()

    if not rma_case:
        return jsonify({'message': 'No RMA case found!'})

    if new_status == 'to_be_sent' and rma_case.status == 'to_be_revised':
        rma_case.status = new_status
        rma_case.sent_date = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')
        rma_case.sent_by = current_user.first_name + ' ' + current_user.last_name
    elif new_status == 'sent' and rma_case.status == 'to_be_sent':
        rma_case.status = new_status
        rma_case.returned_date = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')
        rma_case.returned_by = current_user.first_name + ' ' + current_user.last_name
    elif new_status == 'returned' and rma_case.status == 'sent':
        rma_case.status = new_status
        rma_case.returned_date = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')
        rma_case.returned_by = current_user.first_name + ' ' + current_user.last_name
    elif new_status == 'resolved':
        rma_case.status = new_status
        rma_case.returned_date = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')
        rma_case.returned_by = current_user.first_name + ' ' + current_user.last_name
    elif new_status == 'unresolved':
        rma_case.status = new_status
        rma_case.returned_date = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')
        rma_case.returned_by = current_user.first_name + ' ' + current_user.last_name

    db.session.commit()

    return jsonify({'message': 'RMA case modified successfully!'})


@app.route('/api/dist_companies', methods=['GET'])
@token_required
def get_all_dist_companies(current_user):
    dist_companies = db.session.query(DistributionCompany).all()

    output = []

    for dist_company in dist_companies:
        dist_company_data = {'id': dist_company.id, 'name': dist_company.name, 'email': dist_company.email,
                             'address': dist_company.address, 'hours': dist_company.hours,
                             'contact_name': dist_company.contact_name,
                             'phone': dist_company.phone}
        output.append(dist_company_data)
    return jsonify({'dist_companies': output})


@app.route('/api/dist_companies', methods=['POST'])
@token_required
def create_new_dist_company(current_user):
    data = request.get_json()

    new_dist_company = DistributionCompany(name=data['name'], email=data['email'], address=data['address'],
                                           hours=data['hours'], contact_name=data['contact_name'],
                                           phone=data['phone'])

    try:
        db.session.add(new_dist_company)
        db.session.commit()
        return jsonify({'message': 'New distribution company created!'})
    except:
        return jsonify({'message': 'Distribution company already exists!'})


@app.route('/api/dist_companies/<dist_company_id>', methods=['GET'])
@token_required
def get_dist_company(current_user, dist_company_id):
    dist_company = db.session.query(DistributionCompany).filter_by(id=dist_company_id).first()

    if not dist_company:
        return jsonify({'message': 'No distribution company found!'})

    dist_company_data = {'name': dist_company.name, 'email': dist_company.email, 'address': dist_company.address,
                         'hours': dist_company.hours, 'contact_name': dist_company.contact_name,
                         'phone': dist_company.phone}

    return jsonify({'dist_company': dist_company_data})


@app.route('/api/dist_companies/<dist_company_id>', methods=['PUT'])
@token_required
def modify_dist_company(current_user, dist_company_id):
    dist_company = db.session.query(DistributionCompany).filter_by(id=dist_company_id).first()

    if not dist_company:
        return jsonify({'message': 'No product found!'})

    data = request.get_json()

    dist_company.name = data['name']
    dist_company.email = data['email']
    dist_company.address = data['address']
    dist_company.hours = data['hours']
    dist_company.contact_name = data['contact_name']
    dist_company.phone = data['phone']

    db.session.commit()

    return jsonify({'message': 'Distribution company modified successfully!'})


@app.route('/api/dist_companies/<dist_company_id>', methods=['DELETE'])
@token_required
def delete_dist_company(current_user, dist_company_id):
    dist_company = db.session.query(DistributionCompany).filter_by(id=dist_company_id).first()

    if not dist_company:
        return jsonify({'message': 'No distribution company found!'})

    db.session.delete(dist_company)
    db.session.commit()

    return jsonify({'message': 'Distribution company deleted successfully!'})


@app.route('/api/products', methods=['GET'])
@token_required
def get_all_products(current_user):
    products = db.session.query(Product).all()

    output = []

    for product in products:
        product_data = {'id': product.id, 'brand': product.brand, 'model': product.model,
                        'description': product.description, 'stock': product.stock,
                        'stock_under_control': product.stock_under_control,
                        'distribution_company': product.distribution_company, 'ean': product.ean}
        output.append(product_data)
    return jsonify({'products': output})


@app.route('/api/products', methods=['POST'])
@token_required
def create_new_product(current_user):
    data = request.get_json()

    new_product = Product(brand=data['brand'], model=data['model'], description=data['description'],
                          stock=int(data['stock']), stock_under_control=bool(data['stock_under_control']),
                          distribution_company=data['distribution_company'], ean=data['ean'])

    try:
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'New product created!'})
    except:
        return jsonify({'message': 'Product already exists!'})


@app.route('/api/products/<product_id>', methods=['GET'])
@token_required
def get_product(current_user, product_id):
    product = db.session.query(Product).filter_by(id=product_id).first()

    if not product:
        return jsonify({'message': 'No product found!'})

    product_data = {'id': product.id, 'brand': product.brand, 'model': product.model,
                    'description': product.description, 'stock': product.stock,
                    'stock_under_control': product.stock_under_control,
                    'distribution_company': product.distribution_company, 'ean': product.ean}

    return jsonify({'product': product_data})


@app.route('/api/products/ean/<ean>', methods=['GET'])
@token_required
def get_product_with_ean(current_user, ean):
    products = db.session.query(Product).filter_by(ean=ean).all()

    if len(products) == 0:
        return jsonify({'message': 'No product found with that EAN!'})
    elif len(products) == 1:
        product_data = {'id': products[0].id, 'brand': products[0].brand, 'model': products[0].model,
                        'description': products[0].description, 'stock': products[0].stock,
                        'stock_under_control': products[0].stock_under_control,
                        'distribution_company': products[0].distribution_company, 'ean': products[0].ean}

        return jsonify({'product': product_data})
    else:
        output = []
        for product in products:
            product_data = {'id': product.id, 'brand': product.brand, 'model': product.model,
                            'description': product.description, 'stock': product.stock,
                            'stock_under_control': product.stock_under_control,
                            'distribution_company': product.distribution_company, 'ean': product.ean}
            output.append(product_data)
        return jsonify({'products': output})


@app.route('/api/products/<product_id>', methods=['PUT'])
@token_required
def modify_product(current_user, product_id):
    product = db.session.query(Product).filter_by(id=product_id).first()

    if not product:
        return jsonify({'message': 'No product found!'})

    data = request.get_json()

    product.brand = data['brand']
    product.model = data['model']
    product.description = data['description']
    product.stock = int(data['stock'])
    product.stock_under_control = bool(data['stock_under_control'])
    product.distribution_company = data['distribution_company']
    product.ean = data['ean']

    db.session.commit()

    return jsonify({'message': 'Product modified successfully!'})


@app.route('/api/products/<product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    product = db.session.query(Product).filter_by(id=product_id).first()

    if not product:
        return jsonify({'message': 'No product found!'})

    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted successfully!'})


@app.route('/api/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user.role == 'admin':
        return jsonify({'message': 'Invalid permissions'})

    users = db.session.query(User).all()

    output = []

    for user in users:
        user_data = {'public_id': user.public_id, 'username': user.username, 'first_name': user.first_name,
                     'last_name': user.last_name, 'email': user.email, 'role': user.role}
        output.append(user_data)
    return jsonify({'users': output})


@app.route('/api/users', methods=['POST'])
@token_required
def create_new_user(current_user):
    if not current_user.role == 'admin':
        return jsonify({'message': 'Invalid permissions'})

    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id=str(uuid.uuid4()), email=data['email'], username=data['username'],
                    first_name=data['first_name'], last_name=data['last_name'], password_hash=hashed_password,
                    role=data['role'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created!'})


@app.route('/api/users/<user_public_id>', methods=['GET'])
@token_required
def get_user(current_user, user_public_id):
    if not current_user.role == 'admin':
        return jsonify({'message': 'Invalid permissions'})

    user = db.session.query(User).filter_by(public_id=user_public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    user_data = {'public_id': user.public_id, 'username': user.username, 'first_name': user.first_name,
                 'last_name': user.last_name, 'email': user.email, 'role': user.role}

    return jsonify({'user': user_data})


@app.route('/api/users/<user_public_id>', methods=['PUT'])
@token_required
def modify_user(current_user, user_public_id):
    if not current_user.role == 'admin':
        return jsonify({'message': 'Invalid permissions'})

    data = request.get_json()
    user = db.session.query(User).filter_by(public_id=user_public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'email' in data:
        user.email = data['email']
    if 'role' in data:
        user.role = data['role']
    if 'password' in data:
        hashed_password = generate_password_hash(data['password'], method='sha256')
        user.password = hashed_password

    db.session.commit()

    return jsonify({'message': 'User modified successfully!'})


@app.route('/api/users/<user_public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_public_id):
    if not current_user.role == 'admin':
        return jsonify({'message': 'Invalid permissions'})

    user = db.session.query(User).filter_by(public_id=user_public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully!'})


@app.route('/api/auth')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})

    user = db.session.query(User).filter_by(username=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})

    if check_password_hash(user.password_hash, auth.password):
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
            app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
