-- ============================================================
-- Campus Mart | 04_innovative.sql
-- New tables: Requests (want-to-buy), Reviews (trust), Notifications
-- Run once: mysql -u root < 04_innovative.sql
-- Beginner: each table = one new idea, all link back to Users/Listings.
-- ============================================================
USE campus_mart;

-- 1. Requests: "I need X" board. Opposite of Listings.
CREATE TABLE IF NOT EXISTS Requests (
  request_id  INT AUTO_INCREMENT PRIMARY KEY,
  buyer_id    INT NOT NULL,
  category_id INT,
  title       VARCHAR(100) NOT NULL,
  max_price   DECIMAL(10,2),
  status      ENUM('open','matched','closed') DEFAULT 'open',
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (buyer_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE SET NULL,
  INDEX idx_requests_status (status)
);

-- 2. Reviews: trust score after pickup. 1 row per completed deal.
CREATE TABLE IF NOT EXISTS Reviews (
  review_id   INT AUTO_INCREMENT PRIMARY KEY,
  listing_id  INT NOT NULL,
  reviewer_id INT NOT NULL,
  seller_id   INT NOT NULL,
  rating      INT NOT NULL,
  comment     VARCHAR(255),
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (listing_id) REFERENCES Listings(listing_id) ON DELETE CASCADE,
  FOREIGN KEY (reviewer_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (seller_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  CHECK (rating BETWEEN 1 AND 5),
  UNIQUE KEY uq_review_once (listing_id, reviewer_id)
);

-- 3. Notifications: "your request matched!" inbox.
CREATE TABLE IF NOT EXISTS Notifications (
  notification_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL,
  body        VARCHAR(255) NOT NULL,
  is_read     BOOLEAN DEFAULT FALSE,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  INDEX idx_notif_user (user_id, is_read)
);

-- Trust-score view: avg rating + completed sales per seller.
-- SQL SECURITY INVOKER avoids 1449 definer errors on re-import.
CREATE OR REPLACE SQL SECURITY INVOKER VIEW Seller_Trust AS
SELECT U.user_id, U.name,
  COUNT(DISTINCT R.review_id) AS total_reviews,
  ROUND(AVG(R.rating), 2) AS avg_rating,
  COUNT(DISTINCT CASE WHEN L.status IN ('sold','rented') THEN L.listing_id END) AS completed_sales
FROM Users U
LEFT JOIN Reviews R ON R.seller_id = U.user_id
LEFT JOIN Listings L ON L.seller_id = U.user_id
GROUP BY U.user_id, U.name;

-- Seed: 2 requests, 2 reviews, 2 notifications
INSERT IGNORE INTO Requests (buyer_id, category_id, title, max_price) VALUES
(2, 1, 'Need DBMS Navathe 7th edition urgently', 600),
(4, 2, 'Need scientific calculator under 700', 700);

INSERT IGNORE INTO Reviews (listing_id, reviewer_id, seller_id, rating, comment) VALUES
(11, 2, 1, 5, 'Keyboard as described, quick handover at library'),
(3, 1, 2, 4, 'Lamp works, slightly late pickup');

INSERT IGNORE INTO Notifications (user_id, body) VALUES
(2, 'New match: DBMS Textbook Navathe (Rs.500) fits your request!'),
(4, 'New match: Casio Calculator fx-991ES (Rs.800) near your budget.');
