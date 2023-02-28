-- Create the database
CREATE
DATABASE IF NOT EXISTS crm;

-- Use the database
USE crm;

-- Create the Properties table
CREATE TABLE IF NOT EXISTS Properties
(
    id            INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL,
    address       TEXT    NOT NULL,
    city          TEXT    NOT NULL,
    state         TEXT    NOT NULL,
    value         INTEGER NOT NULL,
    property_type TEXT    NOT NULL,
    price         INTEGER NOT NULL,
    bedrooms      INTEGER NOT NULL,
    bathrooms     INTEGER NOT NULL,
    area          INTEGER NOT NULL,
    garage        TEXT    NOT NULL,
    description   TEXT    NOT NULL,
    photo         BLOB,
    client_id     INTEGER NOT NULL,
    FOREIGN KEY (client_id) REFERENCES Client (id)
);

-- Create the Client table
CREATE TABLE IF NOT EXISTS Client
(
    id       INTEGER PRIMARY KEY,
    email    TEXT UNIQUE NOT NULL,
    password TEXT        NOT NULL,
    username TEXT        NOT NULL,
    is_admin INTEGER DEFAULT 0,
    FOREIGN KEY (id) REFERENCES Properties (client_id)
);

-- Create the Users table
CREATE TABLE IF NOT EXISTS Users
(
    id       INTEGER PRIMARY KEY,
    email    TEXT UNIQUE NOT NULL,
    password TEXT        NOT NULL,
    username TEXT        NOT NULL,
    is_admin INTEGER DEFAULT 0,
    FOREIGN KEY (id) REFERENCES Properties (owner_id)
);

-- Create the Sale table
CREATE TABLE IF NOT EXISTS Sale
(
    id           INTEGER PRIMARY KEY,
    date         DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    value        INTEGER                            NOT NULL,
    commission   INTEGER                            NOT NULL,
    closing_date DATETIME,
    details      TEXT,
    client_id    INTEGER                            NOT NULL,
    FOREIGN KEY (client_id) REFERENCES Client (id)
);

-- Create the Lead table
CREATE TABLE IF NOT EXISTS Lead
(
    id              INTEGER PRIMARY KEY,
    date            DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    source          TEXT                               NOT NULL,
    status          TEXT,
    additional_info TEXT
);

-- Create the Interaction table
CREATE TABLE IF NOT EXISTS Interaction
(
    id          INTEGER PRIMARY KEY,
    date        DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    notes       TEXT,
    next_action TEXT,
    client_id   INTEGER                            NOT NULL,
    FOREIGN KEY (client_id) REFERENCES Client (id)
);
