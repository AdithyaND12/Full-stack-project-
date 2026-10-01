-- ============================================================
-- Campus Mart | 03_queries.sql
-- WHAT: 10 demo queries for viva + FastAPI backend.
-- HOW: run after seed. Copy-paste one query at a time into mysql.
--   mysql -u root -p campus_mart < 03_queries.sql
-- Beginner tip: SELECT ... FROM ... WHERE ... = "show me WHAT from WHERE with FILTER".
-- JOIN = "connect two tables using their link (FK)".
-- ============================================================

USE campus_mart;

-- ------------------------------------------------------------
-- Q1: Show all active listings, cheapest first.
-- Learn: WHERE filters rows, ORDER BY sorts.
-- ------------------------------------------------------------
SELECT listing_id, title, price, status
FROM Listings
WHERE status = 'active'
ORDER BY price ASC;

-- ------------------------------------------------------------
-- Q2: Search for "laptop" in title or description.
-- Learn: LIKE '%word%' = contains. FULLTEXT version is faster.
-- ------------------------------------------------------------
SELECT listing_id, title, price
FROM Listings
WHERE title LIKE '%Laptop%' OR description LIKE '%Laptop%';

-- FULLTEXT version (uses the index from schema):
-- SELECT listing_id, title, price FROM Listings
-- WHERE MATCH(title, description) AGAINST('laptop' IN NATURAL LANGUAGE MODE);

-- ------------------------------------------------------------
-- Q3: Filter by category + price range (shop page in FastAPI).
-- Learn: JOIN connects Listings -> Categories to show shelf name.
-- ------------------------------------------------------------
SELECT L.listing_id, L.title, L.price, C.name AS category, U.name AS seller
FROM Listings L
JOIN Categories C ON L.category_id = C.category_id
JOIN Users U ON L.seller_id = U.user_id
WHERE C.name = 'Electronics' AND L.price BETWEEN 500 AND 30000 AND L.status = 'active'
ORDER BY L.price;

-- ------------------------------------------------------------
-- Q4: Seller profile + their active listings.
-- Learn: one seller (Asha, id=1) has MANY listings = 1:N.
-- ------------------------------------------------------------
SELECT U.name AS seller, U.university_email, L.title, L.price, L.status
FROM Users U
JOIN Listings L ON L.seller_id = U.user_id
WHERE U.user_id = 1;

-- ------------------------------------------------------------
-- Q5: Chat history for laptop (conversation 1), oldest first.
-- Learn: 3-table JOIN: Messages -> Users (who said it).
-- ------------------------------------------------------------
SELECT M.sent_at, U.name AS sender, M.body
FROM Messages M
JOIN Users U ON M.sender_id = U.user_id
WHERE M.conversation_id = 1
ORDER BY M.sent_at ASC;

-- ------------------------------------------------------------
-- Q6: All conversations for a listing, with buyer names.
-- Learn: Conversations links Listing + Buyer + Seller.
-- ------------------------------------------------------------
SELECT C.conversation_id, L.title, B.name AS buyer, S.name AS seller
FROM Conversations C
JOIN Listings L ON C.listing_id = L.listing_id
JOIN Users B ON C.buyer_id = B.user_id
JOIN Users S ON C.seller_id = S.user_id
WHERE C.listing_id = 1;

-- ------------------------------------------------------------
-- Q7: Count of active listings per category (homepage stats).
-- Learn: GROUP BY groups rows, COUNT(*) counts, HAVING filters groups.
-- ------------------------------------------------------------
SELECT C.name AS category, COUNT(*) AS total
FROM Listings L
JOIN Categories C ON L.category_id = C.category_id
WHERE L.status = 'active'
GROUP BY C.name
ORDER BY total DESC;

-- ------------------------------------------------------------
-- Q8: Rentable items with per-day price (JOIN Listings + Rentals).
-- Learn: 1:1 JOIN, only rent items appear.
-- ------------------------------------------------------------
SELECT L.title, L.price AS total_price, R.price_per_day, R.deposit
FROM Listings L
JOIN Rentals R ON R.listing_id = L.listing_id
WHERE L.status = 'active';

-- ------------------------------------------------------------
-- Q9: Mark an item as sold SAFELY (transaction).
-- Learn: START TRANSACTION + COMMIT = all-or-nothing (ACID).
-- Run this when buyer picks up the item.
-- ------------------------------------------------------------
START TRANSACTION;
UPDATE Listings SET status = 'sold' WHERE listing_id = 3;
-- Check: SELECT listing_id, title, status FROM Listings WHERE listing_id = 3;
COMMIT;

-- ------------------------------------------------------------
-- Q10: Use the View (short form of Q1).
-- Learn: View = saved query, looks like a table.
-- ------------------------------------------------------------
SELECT * FROM Active_Listings ORDER BY price ASC LIMIT 5;
