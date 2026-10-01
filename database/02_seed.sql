-- ============================================================
-- Campus Mart | 02_seed.sql
-- WHAT: sample data so you can SEE how tables connect.
-- HOW TO RUN: after 01_schema.sql, run this file once.
--   mysql -u root -p < 01_schema.sql
--   mysql -u root -p < 02_seed.sql
-- RULE: insert PARENTS before CHILDREN (Users first, Messages last).
-- ============================================================

USE campus_mart;

-- ------------------------------------------------------------
-- 1. Users (WHO) : 5 campus members
-- password_hash is fake here. Real app uses bcrypt in FastAPI.
-- ------------------------------------------------------------
INSERT INTO Users (name, university_email, password_hash, phone, role, department, is_verified) VALUES
('Asha Sharma',  'asha@bmsce.ac.in',  'hash_asha_123',  '9811111111', 'student', 'CSE', TRUE),
('Ravi Kumar',   'ravi@bmsce.ac.in',  'hash_ravi_123',  '9822222222', 'student', 'ME',  TRUE),
('Prof. Rao',    'rao@bmsce.ac.in',   'hash_rao_123',   '9833333333', 'faculty', 'CSE', TRUE),
('Priya Nair',   'priya@bmsce.ac.in', 'hash_priya_123', '9844444444', 'student', 'ECE', TRUE),
('Kiran Store',  'kiran@bmsce.ac.in', 'hash_kiran_123', '9855555555', 'staff',   'Stores', FALSE);

-- ------------------------------------------------------------
-- 2. Categories (WHAT shelf) : 5 shelves
-- IDs will be 1=Academic, 2=Electronics, 3=Dorm, 4=Vehicle, 5=Skill Services
-- ------------------------------------------------------------
INSERT INTO Categories (name, description) VALUES
('Academic',       'Textbooks, notes, calculators'),
('Electronics',    'Laptops, monitors, accessories'),
('Dorm',           'Furniture, lamps, storage'),
('Vehicle',        'Cycles, helmets, accessories'),
('Skill Services', 'Tutoring, design, repairs');

-- ------------------------------------------------------------
-- 3. Listings (WHAT item) : 12 ads
-- Format: (seller_id, category_id, title, description, price, type, condition, status)
-- seller 1=Asha, 2=Ravi, 3=Prof.Rao, 4=Priya
-- ------------------------------------------------------------
INSERT INTO Listings (seller_id, category_id, title, description, price, type, `condition`, status) VALUES
(1, 2, 'Used Laptop Dell i5', 'Dell Latitude, 8GB RAM, 256GB SSD, battery ok', 25000, 'sale', 'used', 'active'),
(1, 1, 'DBMS Textbook Navathe', 'Elmasri Navathe 7th edition, no markings', 500, 'sale', 'like-new', 'active'),
(2, 3, 'Hostel Table Lamp', 'LED study lamp, 3 brightness levels', 400, 'sale', 'used', 'active'),
(2, 4, 'Hero Cycle + Lock', 'Single speed cycle, new brake pads, with lock', 4500, 'sale', 'used', 'active'),
(4, 2, 'Casio Calculator fx-991ES', 'Engineering calculator, allowed in exams', 800, 'sale', 'like-new', 'active'),
(4, 1, 'Engineering Physics Notes', 'Handwritten notes, all units, neat diagrams', 150, 'sale', 'used', 'active'),
(1, 2, 'Monitor 24 inch for Rent', 'Dell 24 inch monitor, HDMI cable included', 2500, 'rent', 'used', 'active'),
(2, 3, 'Plastic Storage Boxes x3', 'Stackable boxes for hostel room', 600, 'sale', 'used', 'active'),
(4, 5, 'Python Tutoring - 1 hour', 'CSE student, teach Python + DBMS lab', 300, 'service', 'new', 'active'),
(3, 1, 'Lab Coat + Record', 'Mech lab coat size M + observation book', 350, 'sale', 'like-new', 'active'),
(1, 2, 'Sold: Old Keyboard', 'This one is already sold, for testing status', 300, 'sale', 'used', 'sold'),
(4, 5, 'Poster Design Service', 'Canva + Photoshop posters for fests', 500, 'service', 'new', 'active');

-- ------------------------------------------------------------
-- 4. Listing_Images (PHOTOS) : at least 1 photo per first 6 items
-- ------------------------------------------------------------
INSERT INTO Listing_Images (listing_id, image_url, sort_order) VALUES
(1, '/images/laptop1.jpg', 0),
(1, '/images/laptop2.jpg', 1),
(2, '/images/dbms_book.jpg', 0),
(3, '/images/lamp.jpg', 0),
(4, '/images/cycle.jpg', 0),
(5, '/images/calculator.jpg', 0),
(7, '/images/monitor.jpg', 0);

-- ------------------------------------------------------------
-- 5. Rentals (RENT terms) : only for listing 7 (monitor on rent)
-- listing_id 7 = Monitor 24 inch for Rent
-- ------------------------------------------------------------
INSERT INTO Rentals (listing_id, price_per_day, deposit, max_duration_days) VALUES
(7, 50, 1000, 60);

-- ------------------------------------------------------------
-- 6. Conversations (WHO talks about WHAT)
-- Ravi (2) asks Asha (1) about laptop (1). Priya (4) asks Ravi (2) about cycle (4).
-- ------------------------------------------------------------
INSERT INTO Conversations (listing_id, buyer_id, seller_id) VALUES
(1, 2, 1),
(4, 4, 2),
(2, 4, 1),
(9, 2, 4);

-- ------------------------------------------------------------
-- 7. Messages (WHAT they say)
-- conversation 1 = laptop chat, conversation 2 = cycle chat
-- ------------------------------------------------------------
INSERT INTO Messages (conversation_id, sender_id, body) VALUES
(1, 2, 'Hi Asha, is the Dell laptop still available?'),
(1, 1, 'Yes Ravi, available. You can check it in library block.'),
(1, 2, 'Can you give for 22000? I can pick up tomorrow.'),
(2, 4, 'Hi, is the cycle single speed? Final price?'),
(2, 2, 'Yes single speed, 4200 fixed with lock.'),
(3, 4, 'Is the DBMS book the 7th edition?'),
(3, 1, 'Yes, 7th edition, no markings inside.'),
(4, 2, 'Hi Priya, I need Python help for DBMS lab. Are slots open?'),
(4, 4, 'Yes, evening 5-6pm at CSE lab. Bring your laptop.'),
(1, 1, 'Ok 23000 last, with charger and bag.');
