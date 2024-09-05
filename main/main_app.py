import datetime
import os

from flask import Flask, jsonify, request, Response
from flask_jwt_extended import jwt_required, JWTManager, get_jwt, get_jwt_identity
from flask_migrate import Migrate
from sqlalchemy import String, func
from sqlalchemy.dialects.postgresql import ARRAY
from web3.exceptions import ContractLogicError

from main_config import Configuration

from role_check import role_check

from main_models import main_db
from main_models import ProductCategory
from main_models import Product
from main_models import Category
from main_models import Order
from main_models import Element

from main_solidity import create_contract
from main_solidity import add_courier
from main_solidity import confirm_delivery
from main_solidity import money_to_owner

main_app = Flask(__name__)
main_app.config.from_object(Configuration)
main_db.init_app(main_app)
migrate = Migrate(app=main_app, db=main_db)

jwt = JWTManager(main_app)



@main_app.route('/update', methods=['POST'])
@role_check('owner')
def add_product():
    if 'file' not in request.files:
        return jsonify({'message': 'Field file missing.'}), 400
    line_num = 0

    content_stream = request.files['file'].stream
    contents = []
    while (line := content_stream.readline()) != b'':
        line = line.decode('utf-8')
        line_contents = line.split(',')
        if len(line_contents) != 3:
            return jsonify({'message': f'Incorrect number of values on line {line_num}'}), 400

        categories, product_name, price = line_contents

        price = float(price)
        if price <= 0:
            return jsonify({'message': f'Incorrect price on line {line_num}'}), 400

        existing_product = Product.query.filter_by(name=product_name).first()
        if existing_product:
            return jsonify({'message': f'Product {product_name} already exists'}), 400
        contents.append(line)
        line_num += 1

    for line in contents:
        categories, product_name, price = line.split(',')
        price = float(price)

        product = Product(name=product_name, price=price)
        main_db.session.add(product)

        categories = categories.split('|')
        for category in categories:
            existing_category = Category.query.filter_by(name=category).first()
            if not existing_category:
                new_category = Category(name=category)
                main_db.session.add(new_category)
        main_db.session.commit()

        for category in categories:
            existing_category = Category.query.filter_by(name=category).first()
            product_category = ProductCategory(product_id=product.id, category_id=existing_category.id)
            main_db.session.add(product_category)
    main_db.session.commit()
    return Response(status=200)


@main_app.route('/product_statistics', methods=['GET'])
@role_check('owner')
def product_statistics():
    pass


@main_app.route('/category_statistics', methods=['GET'])
@role_check('owner')
def category_statistics():
    pass


@main_app.route('/search', methods=['GET'])
@role_check('customer')
def search():
    viable_product_category = ProductCategory.query.with_entities(ProductCategory.product_id, ProductCategory.category_id).join(Product, ProductCategory.product_id == Product.id).join(Category, ProductCategory.category_id == Category.id)
    if 'category' in request.args:
        viable_product_category = viable_product_category.filter(Category.name.ilike('%' + request.args['category'] + '%'))
    if 'name' in request.args:
        viable_product_category = viable_product_category.filter(Product.name.ilike('%' + request.args['name'] + '%'))

    viable_product_category = viable_product_category.all()
    viable_products = set([elem[0] for elem in viable_product_category])
    viable_categories = set([elem[1] for elem in viable_product_category])

    categories = main_db.session.query(Category.name).filter(Category.id.in_(viable_categories)).all()

    products = (main_db.session.query(Product.id, Product.name, Product.price, func.array_agg(Category.name, type_=ARRAY(String)))
                .join(ProductCategory, Product.id == ProductCategory.product_id).join(Category, ProductCategory.category_id==Category.id).filter(Product.id.in_(viable_products)).group_by(Product.id, Product.name, Product.price)).all()

    ret = {'categories' : [category[0] for category in categories], 'products' : [{'id' : product[0], 'name' : product[1], 'price': product[2], 'categories' : product[3]} for product in products]}

    return jsonify(ret), 200


@main_app.route('/order', methods=['POST'])
@role_check('customer')
def create_order():
    req_num = 0
    to_pay = 0
    email = get_jwt_identity()
    if 'requests' not in request.json:
        return jsonify({'message': 'Field requests is missing'}), 400
    requests = request.json['requests']

    for req in requests:
        if 'id' not in req:
            return jsonify({'message': f'Product id is missing for request number {req_num}'}), 400
        if 'quantity' not in req:
            return jsonify({'message': f'Product quantity is missing for request number {req_num}'}), 400
        # check if int at all
        if req['id'] <= 0:
            return jsonify({'message': f'Invalid product id for request number {req_num}'}), 400
        if req['quantity'] <= 0:
            return jsonify({'message': f'Invalid product quantity for request number {req_num}'}), 400
        product = Product.query.filter_by(id=req['id']).first()
        if not product:
            return jsonify({'message': 'Product id is missing '})
        to_pay += req['quantity'] * product.price
        req_num += 1

    if 'address' not in request.json:
        return jsonify({'message': 'Field address is missing'}), 400
    if request.json['address'].find('0x') != 0 or len(request.json['address']) != 42:
        return jsonify({'message': 'Invalid address'}), 400

    contract = create_contract(request.json['address'], to_pay)

    # timezone sensitivity
    order = Order(creation_time=datetime.datetime.now(), to_pay=to_pay, user_email=email, contract_address=contract)
    main_db.session.add(order)
    main_db.session.commit()

    for req in requests:
        element = Element(product_id=req['id'], quantity=req['quantity'], order_id=order.id)
        main_db.session.add(element)
    main_db.session.commit()
    return jsonify({'id': order.id}), 200


@main_app.route('/status', methods=['GET'])
@role_check('customer')
def get_status():
    email = get_jwt_identity()
    return_list = []
    orders = Order.query.filter_by(user_email=email).all()
    for order in orders:
        order_dict = {'products': [], 'price': order.to_pay, 'status': order.status, 'timestamp': order.creation_time, 'address': order.contract_address}
        products_list = ((main_db.session.query(Product.name, Product.price, Element.quantity,
                                                func.array_agg(Category.name, type_=ARRAY(String)))
                          .join(Element, Product.id == Element.product_id).join(ProductCategory,
                                                                                Product.id == ProductCategory.product_id)
                          .join(Category, ProductCategory.category_id == Category.id)).filter(
            order.id == Element.order_id).
                         group_by(Product.name, Product.price, Element.quantity).all())

        for product in products_list:
            order_dict['products'].append(
                {'name': product[0], 'price': product[1], 'quantity': product[2], 'categories': product[3]})
        return_list.append(order_dict)
    return jsonify({'orders': return_list}), 200





@main_app.route('/delivered', methods=['POST'])
@role_check('customer')
def delivered():
    email = get_jwt_identity()
    if 'id' not in request.json:
        return jsonify({'message': 'Missing order id'}), 400
    order = Order.query.filter_by(id=request.json['id']).first()
    if not order or order.status != 'PENDING' or order.user_email != email:
        return jsonify({'message': 'Invalid order id'}), 400

    try:
        confirm_delivery(order.contract_address)
        order.status = 'COMPLETE'
        main_db.session.add(order)
        main_db.session.commit()
        return Response(status=200)
    except ContractLogicError as cle:
        return jsonify({'message': cle.message}), 400


@main_app.route('/orders_to_deliver', methods=['GET'])
@role_check('courier')
def orders_to_deliver():
    orders = Order.query.with_entities(Order.id, Order.user_email).filter(Order.status == 'CREATED').all()
    return jsonify({'orders': [{'id': order[0], 'user_email': order[1]} for order in orders]}), 200


@main_app.route('/pick_up_order', methods=['POST'])
@role_check('courier')
def pick_up_order():
    if 'id' not in request.json:
        return jsonify({'message': 'Missing order id'}), 400
    order_id = request.json['id']
    if order_id <= 0:
        return jsonify({'message': 'Invalid order id'}), 400
    order = Order.query.filter_by(id=order_id).first()
    if not order or order.status != 'CREATED':
        return jsonify({'message': 'Invalid order status'}), 400
    if 'address' not in request.json:
        return jsonify({'message': 'Missing address'}), 400
    if request.json['address'].find('0x') != 0 or len(request.json['address']) != 42:
        return jsonify({'message': 'Invalid address'}), 400

    try:
        add_courier(order.contract_address, request.json['address'])
        order.status = 'PENDING'
        main_db.session.add(order)
        main_db.session.commit()
        return Response(status=200)
    except ContractLogicError as cle:
        return jsonify({'message': cle.message.split('revert ')[-1]}), 400


if __name__ == '__main__':
    money_to_owner()
    main_app.run(debug=False, host='localhost' if 'PRODUCTION' not in os.environ else '0.0.0.0', port=5001 if 'PRODCUTION' not in os.environ else 5000)
