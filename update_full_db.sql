-- Create tables
CREATE TABLE IF NOT EXISTS client (
    id             INTEGER PRIMARY KEY,
    email          VARCHAR(255) NOT NULL UNIQUE,
    phone          TEXT,
    name           TEXT,
    address        TEXT,
    birthdate      TEXT,
    marital_status TEXT,
    profession     TEXT,
    income         INTEGER
);

CREATE TABLE IF NOT EXISTS comment (
    id        INTEGER PRIMARY KEY,
    author    VARCHAR(100) NOT NULL,
    text      TEXT NOT NULL,
    timestamp DATETIME
);

CREATE TABLE IF NOT EXISTS interaction (
    id          INTEGER PRIMARY KEY,
    date        DATETIME NOT NULL,
    notes       VARCHAR(500),
    next_action VARCHAR(50),
    client_id   INTEGER NOT NULL REFERENCES client(id)
);

CREATE TABLE IF NOT EXISTS lead (
    id              INTEGER PRIMARY KEY,
    date            DATETIME NOT NULL,
    source          VARCHAR(50) NOT NULL,
    status          VARCHAR(20),
    additional_info VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS properties (
    id            INTEGER PRIMARY KEY,
    name          VARCHAR(200) NOT NULL,
    address       VARCHAR(200) NOT NULL,
    city          VARCHAR(50) NOT NULL,
    state         VARCHAR(50) NOT NULL,
    value         INTEGER NOT NULL,
    property_type VARCHAR(50) NOT NULL,
    price         INTEGER NOT NULL,
    bedrooms      INTEGER NOT NULL,
    bathrooms     INTEGER NOT NULL,
    area          INTEGER NOT NULL,
    garage        VARCHAR(50) NOT NULL,
    description   VARCHAR(500) NOT NULL,
    photo         BLOB,
    client_id     INTEGER NOT NULL REFERENCES client(id)
);

CREATE TABLE IF NOT EXISTS sale (
    id            INTEGER PRIMARY KEY,
    date          DATETIME NOT NULL,
    value         INTEGER NOT NULL,
    commission    INTEGER NOT NULL,
    closing_date  DATETIME,
    details       VARCHAR(500),
    client_id     INTEGER NOT NULL REFERENCES client(id),
    properties_id INTEGER REFERENCES properties(id)
);

CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY,
    email    VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    username VARCHAR(255) NOT NULL,
    is_admin BOOLEAN
);

-- Create indexes
CREATE INDEX IF NOT EXISTS ix_comment_timestamp ON comment (timestamp);
CREATE INDEX IF NOT EXISTS idx_interaction_client_id ON interaction (client_id);
CREATE INDEX IF NOT EXISTS idx_interactions_client_id ON interaction (client_id);
CREATE INDEX IF NOT EXISTS ix_interaction_client_id ON interaction (client_id);
CREATE INDEX IF NOT EXISTS idx_properties_client_id ON properties (client_id);
CREATE INDEX IF NOT EXISTS ix_properties_client_id ON properties (client_id);
CREATE INDEX IF NOT EXISTS idx_sale_client_id ON sale (client_id);
CREATE INDEX IF NOT EXISTS idx_sale_property_id ON sale (properties_id);
CREATE INDEX IF NOT EXISTS idx_sales_client_id ON sale (client_id);
CREATE INDEX IF NOT EXISTS ix_sale_client_id ON sale (client_id);
CREATE INDEX IF NOT EXISTS ix_sale_property_id ON sale (properties_id);

