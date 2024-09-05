from flask_sqlalchemy import SQLAlchemy

main_db = SQLAlchemy()


class ProductCategory(main_db.Model):
    __tablename__ = 'product_category'
    id = main_db.Column(main_db.Integer, primary_key=True)
    product_id = main_db.Column(main_db.Integer, main_db.ForeignKey('product.id'), nullable=False)
    category_id = main_db.Column(main_db.Integer, main_db.ForeignKey('category.id'), nullable=False)


class Product(main_db.Model):
    __tablename__ = 'product'
    id = main_db.Column(main_db.Integer, primary_key=True)
    name = main_db.Column(main_db.String(256), nullable=False, unique=True)
    price = main_db.Column(main_db.Double, nullable=False)

    categories = main_db.relationship('Category', secondary=ProductCategory.__table__, back_populates='products')
    elements = main_db.relationship('Element', back_populates='product')


class Category(main_db.Model):
    __tablename__ = 'category'
    id = main_db.Column(main_db.Integer, primary_key=True)
    name = main_db.Column(main_db.String(256), nullable=False, unique=True)

    products = main_db.relationship('Product', secondary=ProductCategory.__table__, back_populates='categories')


class Order(main_db.Model):
    __tablename__ = 'order'
    id = main_db.Column(main_db.Integer, primary_key=True)
    creation_time = main_db.Column(main_db.DateTime, nullable=False)
    contract_address = main_db.Column(main_db.String(256), nullable=True)
    # customer_address is not a field, but must be put in the contract as customer address immediately
    # courier_address is not a field either, but must be put in the contract upon pick-up.
    to_pay = main_db.Column(main_db.Float, nullable=False)
    status = main_db.Column(main_db.String(16), nullable=False, default='CREATED')
    user_email = main_db.Column(main_db.String(256), nullable=False)
    elements = main_db.relationship('Element', back_populates='order')


class Element(main_db.Model):
    __tablename__ = 'element'
    id = main_db.Column(main_db.Integer, primary_key=True)
    product_id = main_db.Column(main_db.Integer, main_db.ForeignKey('product.id'), nullable=False)
    order_id = main_db.Column(main_db.Integer, main_db.ForeignKey('order.id'), nullable=False)
    quantity = main_db.Column(main_db.Integer, nullable=False)

    order = main_db.relationship('Order', back_populates='elements')
    product = main_db.relationship('Product', back_populates='elements')



