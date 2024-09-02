CREATE TABLE Role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(16) NOT NULL
);

INSERT INTO Role (name) VALUES ('owner');
INSERT INTO Role (name) VALUES ('customer');
INSERT INTO Role (name) VALUES ('courier');

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    forename VARCHAR(256) NOT NULL,
    surname VARCHAR(256) NOT NULL,
    email VARCHAR(256) UNIQUE NOT NULL,
    password VARCHAR(256) NOT NULL,
    role INT NOT NULL,
    CONSTRAINT fk_user_role
                         FOREIGN KEY(role) REFERENCES Role(id)

);

INSERT INTO "user"(forename, surname, email, password, role) VALUES('Scrooge', 'McDuck', 'onlymoney@gmail.com', 'evenmoremoney', 1);
