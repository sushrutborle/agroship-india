-- ============================================================
--  AgroShip India — Full Database Schema
--  Run this file in MySQL Workbench or via: mysql -u root -p < agroship.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS agroship_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE agroship_db;

-- ------------------------------------------------------------
-- USERS (Admin accounts)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100)        NOT NULL,
    email       VARCHAR(150)        NOT NULL UNIQUE,
    password    VARCHAR(255)        NOT NULL,
    role        ENUM('admin','staff') DEFAULT 'admin',
    is_active   BOOLEAN             DEFAULT TRUE,
    created_at  DATETIME            DEFAULT CURRENT_TIMESTAMP
);

-- Default admin  (password: admin123 — change after first login)
INSERT INTO users (name, email, password, role) VALUES (
  'Admin',
  'admin@agroshipindia.com',
  '$2b$12$KIXoFbPMCfIx9DtUiNLpYuXNwWdEgz1r5zN3mU8e3FhJkLm2MtPZS',
  'admin'
);

-- ------------------------------------------------------------
-- PRODUCTS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(150)        NOT NULL,
    category    VARCHAR(50)         NOT NULL,
    origin      VARCHAR(150)        NOT NULL,
    description TEXT,
    price       VARCHAR(100),
    markets     VARCHAR(255),
    emoji       VARCHAR(10)         DEFAULT '🌿',
    status      ENUM('active','draft') DEFAULT 'active',
    created_at  DATETIME            DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME            DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Seed default products
INSERT INTO products (name, category, origin, description, price, markets, emoji, status) VALUES
('Fresh Red Onion',  'Vegetable', 'Lasalgaon, Nashik',   'Premium export grade red onions sourced directly from Asia\'s largest onion market. Sizes 40–60mm, 60–80mm available.', 'USD 200–250/MT', 'UAE, Malaysia, Sri Lanka', '🧅', 'active'),
('Fresh Lemon',      'Vegetable', 'Vidarbha, Maharashtra','Thin-skinned, high-juice content lemons. Phytosanitary certified and cold chain handled.',                              'USD 300–380/MT', 'UAE, Saudi Arabia, UK',   '🍋', 'active'),
('Cavendish Banana', 'Fruit',     'Jalgaon, Maharashtra', 'Premium Cavendish bananas from the banana capital of India. Consistent sizing, excellent shelf life.',                   'USD 350–420/MT', 'UAE, Qatar, Kuwait',       '🍌', 'active'),
('Raw Turmeric',     'Spice',     'Sangli, Maharashtra',  'High curcumin content turmeric from the world\'s largest turmeric trading hub. Organic grades available.',               'USD 500–650/MT', 'USA, Germany, Japan',      '🌿', 'active');

-- ------------------------------------------------------------
-- ORDERS  (Place Order form)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    customer_name   VARCHAR(150)    NOT NULL,
    company         VARCHAR(150),
    email           VARCHAR(150)    NOT NULL,
    phone           VARCHAR(30),
    country         VARCHAR(100)    NOT NULL,
    product_id      INT,
    product_name    VARCHAR(150)    NOT NULL,
    quantity_mt     DECIMAL(10,2)   NOT NULL,
    delivery_date   DATE,
    special_notes   TEXT,
    status          ENUM('NEW','PROCESSING','CONFIRMED','SHIPPED','COMPLETED','CANCELLED') DEFAULT 'NEW',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- INQUIRIES  (Contact form)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inquiries (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(150)    NOT NULL,
    company         VARCHAR(150),
    email           VARCHAR(150)    NOT NULL,
    country         VARCHAR(100),
    products_interest VARCHAR(255),
    message         TEXT,
    status          ENUM('NEW','CONTACTED','QUOTATION_SENT','CLOSED') DEFAULT 'NEW',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- SETTINGS  (Website settings managed from admin panel)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS settings (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100)    NOT NULL UNIQUE,
    value       TEXT,
    updated_at  DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO settings (setting_key, value) VALUES
('company_name',  'AgroShip India'),
('email',         'exports@agroshipindia.com'),
('phone',         '+91 98765 43210'),
('location',      'Pune, Maharashtra, India'),
('tagline',       'From India\'s Fields to the World\'s Tables');
