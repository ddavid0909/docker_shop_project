CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    price DECIMAL(10,3) NOT NULL
);

CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256) NOT NULL
);

CREATE TABLE product_category (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    category_id INT NOT NULL,

    CONSTRAINT fk_to_product
                         FOREIGN KEY(product_id) REFERENCES product(id),
    CONSTRAINT fk_to_category
                         FOREIGN KEY(category_id) REFERENCES category(id)
);

CREATE TABLE "order" (
    id SERIAL PRIMARY KEY,
    creation_time TIMESTAMP NOT NULL,
    to_pay DECIMAL(10,3) NOT NULL,
    user_email VARCHAR(256) NOT NULL,
    status VARCHAR(10) NOT NULL
);

CREATE TABLE element (
    id SERIAL PRIMARY KEY,
    quantity INT NOT NULL,
    product_id INT NOT NULL,
    order_id INT NOT NULL,

    CONSTRAINT fk_element_to_product
                          FOREIGN KEY(product_id) REFERENCES product(id),
    CONSTRAINT fk_element_to_order
                          FOREIGN KEY(order_id) REFERENCES "order"(id)
)
