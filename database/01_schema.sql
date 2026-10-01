-- ============================================================
-- Campus Mart | 01_schema.sql
-- Database: MySQL 8 (InnoDB + utf8mb4)
-- Beginner guide: read top to bottom, run one block at a time.
-- ============================================================
-- WHAT IS HAPPENING HERE?
-- We create ONE database (campus_mart) with 7 tables.
-- Think of it as a story:
--   Users (WHO) -> Categories (WHAT shelf) -> Listings (WHAT item)
--   -> Listing_Images (PHOTOS) + Rentals (RENT terms)
--   -> Conversations (WHO talks about WHAT) -> Messages (WHAT they say)
--
-- RULE: create PARENTS before CHILDREN.
-- Order: Users, Categories -> Listings -> Images, Rentals, Conversations -> Messages
-- ============================================================

CREATE DATABASE IF NOT EXISTS campus_mart
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE campus_mart;

-- ------------------------------------------------------------
-- TABLE 1: Users | WHO is in the market?
-- One row = one student / faculty / staff member.
-- ------------------------------------------------------------
-- user_id        : ID number, auto-increases (1,2,3...). PRIMARY KEY = unique + never NULL.
-- name           : person name, must be filled (NOT NULL).
-- university_email: college mail, UNIQUE so nobody registers twice. Example: asha@bmsce.ac.in
-- password_hash  : NEVER store plain password, only its hash.
-- role           : only 3 allowed values (ENUM).
-- is_verified    : FALSE until they verify email, then TRUE.
CREATE TABLE IF NOT EXISTS Users (
  user_id          INT AUTO_INCREMENT PRIMARY KEY,
  name             VARCHAR(50) NOT NULL,
  university_email VARCHAR(100) NOT NULL UNIQUE,
  password_hash    VARCHAR(255) NOT NULL,
  phone            VARCHAR(15),
  role             ENUM('student','faculty','staff') DEFAULT 'student',
  department       VARCHAR(50),
  is_verified      BOOLEAN DEFAULT FALSE,
  created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CHECK (university_email LIKE '%@%.%')
);

-- ------------------------------------------------------------
-- TABLE 2: Categories | WHAT shelf does the item go on?
-- One row = one shelf. Keeps spelling consistent.
-- Beginner idea: without this table we would type 'Electronics'
-- 1000 times and someone would type 'electronic' -> mess.
-- This is called 2NF: keep repeated facts in one place.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Categories (
  category_id INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(50) NOT NULL UNIQUE,
  description VARCHAR(255)
);

-- ------------------------------------------------------------
-- TABLE 3: Listings | WHAT is being sold / rented / offered?
-- One row = one item or service ad. This is the CENTER table.
-- seller_id   : WHO sells? Must match a user_id in Users.
-- category_id : WHICH shelf? Must match a category_id in Categories.
-- FOREIGN KEY = "this value must already exist in the parent table".
-- ON DELETE CASCADE : if a User is deleted, delete their listings too.
-- ON DELETE RESTRICT: you CANNOT delete a Category that still has listings.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Listings (
  listing_id  INT AUTO_INCREMENT PRIMARY KEY,
  seller_id   INT NOT NULL,
  category_id INT NOT NULL,
  title       VARCHAR(100) NOT NULL,
  description TEXT,
  price       DECIMAL(10,2) NOT NULL,
  type        ENUM('sale','rent','service') DEFAULT 'sale',
  `condition` ENUM('new','like-new','used') DEFAULT 'used',
  status      ENUM('active','sold','rented','inactive') DEFAULT 'active',
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (seller_id)   REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CHECK (price >= 0),
  INDEX idx_listings_category_status (category_id, status),
  INDEX idx_listings_price (price),
  FULLTEXT INDEX ft_listings_title_desc (title, description)
);

-- ------------------------------------------------------------
-- TABLE 4: Listing_Images | PHOTOS of the item
-- One listing has MANY photos -> 1:N relationship.
-- Beginner idea: we do NOT make columns photo1, photo2 in Listings.
-- That would break 1NF (one cell = one value). So separate table.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Listing_Images (
  image_id   INT AUTO_INCREMENT PRIMARY KEY,
  listing_id INT NOT NULL,
  image_url  VARCHAR(255) NOT NULL,
  sort_order INT DEFAULT 0,
  FOREIGN KEY (listing_id) REFERENCES Listings(listing_id) ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_images_listing (listing_id)
);

-- ------------------------------------------------------------
-- TABLE 5: Rentals | IF it is for rent, what are the terms?
-- One rentable listing has ONE rent rule -> 1:1 relationship.
-- Beginner idea: only rent items get a row here. Sale items get none.
-- This is 3NF: don't fill Listings with empty rent columns for everyone.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Rentals (
  rental_id         INT AUTO_INCREMENT PRIMARY KEY,
  listing_id        INT NOT NULL UNIQUE,
  price_per_day     DECIMAL(10,2) NOT NULL,
  deposit           DECIMAL(10,2) DEFAULT 0,
  max_duration_days INT,
  FOREIGN KEY (listing_id) REFERENCES Listings(listing_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CHECK (price_per_day >= 0),
  CHECK (deposit >= 0)
);

-- ------------------------------------------------------------
-- TABLE 6: Conversations | WHO wants to talk about WHICH listing?
-- One row = one buyer asking about one listing ("I want this laptop").
-- UNIQUE(listing_id, buyer_id): same buyer cannot open 10 chats
-- for the same item. One chat per buyer per item.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Conversations (
  conversation_id INT AUTO_INCREMENT PRIMARY KEY,
  listing_id      INT NOT NULL,
  buyer_id        INT NOT NULL,
  seller_id       INT NOT NULL,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (listing_id) REFERENCES Listings(listing_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (buyer_id)   REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (seller_id)  REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  UNIQUE KEY uq_conversation (listing_id, buyer_id),
  INDEX idx_conv_listing (listing_id)
);

-- ------------------------------------------------------------
-- TABLE 7: Messages | WHAT did they say in the chat?
-- One conversation has MANY messages -> 1:N.
-- Newest message = ORDER BY sent_at.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Messages (
  message_id      INT AUTO_INCREMENT PRIMARY KEY,
  conversation_id INT NOT NULL,
  sender_id       INT NOT NULL,
  body            TEXT NOT NULL,
  sent_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_read         BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (conversation_id) REFERENCES Conversations(conversation_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (sender_id)       REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_messages_conv_time (conversation_id, sent_at)
);

-- ------------------------------------------------------------
-- EXTRA FOR MARKS: View + Trigger
-- View = saved SELECT that looks like a table. Good for security
-- (show only active items, hide seller phone etc).
-- ------------------------------------------------------------
CREATE OR REPLACE SQL SECURITY INVOKER VIEW Active_Listings AS
SELECT listing_id, title, price, type, status
FROM Listings
WHERE status = 'active';

-- Trigger = automatic check before INSERT. Blocks negative price
-- with a clear error even if CHECK is bypassed.
DELIMITER //
CREATE TRIGGER IF NOT EXISTS trg_listings_check_price
BEFORE INSERT ON Listings
FOR EACH ROW
BEGIN
  IF NEW.price < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Price cannot be negative';
  END IF;
END //
DELIMITER ;
