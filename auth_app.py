from flask import Flask, Response
from flask import request
from flask import jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from auth_models import auth_db
from auth_models import User
from auth_models import Role
from auth_config import Configuration

auth_app = Flask(__name__)
auth_app.config.from_object(Configuration)

auth_db.init_app(auth_app)
jwt = JWTManager(auth_app)

'''with auth_app.app_context():
    auth_db.create_all()

    ownerRole = Role.query.filter(Role.name == 'owner').first()
    customerRole = Role.query.filter(Role.name == 'customer').first()
    courierRole = Role.query.filter(Role.name == 'courier').first()

    if not ownerRole:
        auth_db.session.add(Role(name='owner'))
    if not customerRole:
        auth_db.session.add(Role(name='customer'))
    if not courierRole:
        auth_db.session.add(Role(name='courier'))

    auth_db.session.commit()'''

@auth_app.route('/register_customer', methods=['POST'])
def register_customer():
    if 'forename' not in request.json:
        return jsonify({'message': 'Field forename is missing'}), 400
    if 'surname' not in request.json:
        return jsonify({'message': 'Field Surname is missing'}), 400
    if 'email' not in request.json:
        return jsonify({'message': 'Field email is missing'}), 400
    if 'password' not in request.json:
        return jsonify({'message': 'Field password is missing'}), 400
    forename = str(request.json['forename'])
    surname = str(request.json['surname'])
    email = str(request.json['email'])
    password = str(request.json['password'])
    role = Role.query.filter(Role.name == 'customer').first()

    if email.find('@') == -1:
        return jsonify({'message': 'Invalid email'})

    if len(password) < 8:
        return jsonify({'message': 'Invalid password'})

    email_occupied = User.query.filter(User.email == email).all()
    if len(email_occupied) > 0:
        return jsonify({'message': 'Email already exists'}), 400

    user = User(forename=forename, surname=surname, email=email, password=password, role=role.id)
    auth_db.session.add(user)
    auth_db.session.commit()
    return Response(status=200)

@auth_app.route('/register_courier', methods=['POST'])
def register_courier():
    if 'forename' not in request.json:
        return jsonify({'message': 'Field forename is missing'}), 400
    if 'surname' not in request.json:
        return jsonify({'message': 'Field Surname is missing'}), 400
    if 'email' not in request.json:
        return jsonify({'message': 'Field email is missing'}), 400
    if 'password' not in request.json:
        return jsonify({'message': 'Field password is missing'}), 400
    forename = str(request.json['forename'])
    surname = str(request.json['surname'])
    email = str(request.json['email'])
    password = str(request.json['password'])
    role = Role.query.filter(Role.name == 'courier').first()

    if email.find('@') == -1:
        return jsonify({'message': 'Invalid email'}), 400

    if len(password) < 8:
        return jsonify({'message': 'Invalid password'}), 400

    email_occupied = User.query.filter(User.email == email).all()
    if len(email_occupied) > 0:
        return jsonify({'message': 'Email already exists'}),400

    user = User(forename=forename, surname=surname, email=email, password=password, role=role.id)
    auth_db.session.add(user)
    auth_db.session.commit()
    return Response(status=200)


@auth_app.route('/login', methods=['POST'])
def login_user():
    if 'email' not in request.json:
        return jsonify({'message': 'Field email is missing'}), 400
    if 'password' not in request.json:
        return jsonify({'message': 'Field password is missing'}), 400
    email = str(request.json['email'])
    password = str(request.json['password'])
    if email.find('@') == -1:
        return jsonify({'message': 'Invalid email'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or user.password != password:
        return jsonify({'message': 'Invalid credentials'}), 400

    claims = {
        'role': user.user_role.name,
        'forename': user.forename,
        'surname': user.surname
    }

    access_token = create_access_token(identity=user.email, additional_claims=claims)
    return jsonify(access_token=access_token), 200

@auth_app.route('/delete', methods=['POST'])
@jwt_required()
def delete():
    identity = get_jwt_identity()
    user = User.query.filter_by(email=identity).first()
    if not user:
        return jsonify({'message': 'Unknown user'}), 400
    auth_db.session.delete(user)
    auth_db.session.commit()
    return Response(status=200)

if __name__ == '__main__':
    auth_app.run(debug=True)
