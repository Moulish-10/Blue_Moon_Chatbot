

CREATE DATABASE IF NOT EXISTS BlueMoon_Cafe;
USE BlueMoon_Cafe;
CREATE TABLE IF NOT EXISTS menu_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    price INT NOT NULL
);
select *from menu_items;
-- Make sure you're using the right database
USE BlueMoon_Cafe;

-- ☕ Coffee Items
INSERT INTO menu_items (category, name, price) VALUES
('Coffee', 'Filter Coffee', 30),
('Coffee', 'Degree Coffee', 40),
('Coffee', 'Sukku Coffee (Dry Ginger)', 35),
('Coffee', 'Karupatti Coffee (Palm Jaggery)', 45),
('Coffee', 'Cold Filter Coffee', 60);

-- 🍵 Tea Items
INSERT INTO menu_items (category, name, price) VALUES
('Tea', 'Regular Tea', 20),
('Tea', 'Masala Tea', 30),
('Tea', 'Ginger Tea (Inji Tea)', 25),
('Tea', 'Karupatti Tea', 30),
('Tea', 'Lemon Tea', 30);

-- 🧃 Juice / Cool Drinks
INSERT INTO menu_items (category, name, price) VALUES
('Juice', 'Nannari Sarbath', 40),
('Juice', 'Lemon Mint Juice', 35),
('Juice', 'Rose Milk', 50),
('Juice', 'Badam Milk', 60),
('Juice', 'Jigarthanda (Madurai special)', 70),
('Juice', 'Tender Coconut Juice', 45);

-- 🍘 Snacks
INSERT INTO menu_items (category, name, price) VALUES
('Snacks', 'Medu Vada', 20),
('Snacks', 'Masala Vada', 20),
('Snacks', 'Mini Idli with Sambar', 40),
('Snacks', 'Veg Paniyaram', 30),
('Snacks', 'Onion Pakoda', 30),
('Snacks', 'Murukku', 15),
('Snacks', 'Samosa (South style)', 20);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    total_price INT NOT NULL,
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
);

-- Use the database
USE BlueMoon_Cafe;



select *from orders;


-- Drop the old table (only if you're okay losing the data)
DROP TABLE IF EXISTS orders;

DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    order_id INT,
    item_id INT,
    quantity INT,
    total_price INT,
    PRIMARY KEY (order_id, item_id),
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
);


INSERT INTO orders (order_id, item_id, quantity, total_price) VALUES
(1, 6, 2, 60),
(1, 13, 1, 50),
(2, 18, 1, 40),
(2, 15, 2, 140);


DROP TABLE IF EXISTS order_tracking;

CREATE TABLE order_tracking (
    order_id INT PRIMARY KEY,
    status VARCHAR(50),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

INSERT INTO order_tracking (order_id, status) VALUES
(1, 'Delivered'),
(2, 'Delivered');




DELIMITER $$

CREATE DEFINER=`root`@`localhost` PROCEDURE `insert_order_item`(
    IN p_item_name VARCHAR(255),
    IN p_quantity INT,
    IN p_order_id INT
)
BEGIN
    DECLARE v_item_id INT;
    DECLARE v_price DECIMAL(10, 2);
    DECLARE v_total_price DECIMAL(10, 2);

    -- Get the item_id and price from menu_items
    SELECT item_id, price INTO v_item_id, v_price
    FROM menu_items
    WHERE name = p_item_name;

    -- Calculate the total price
    SET v_total_price = v_price * p_quantity;

    -- Insert into the orders table
    INSERT INTO orders (order_id, item_id, quantity, total_price)
    VALUES (p_order_id, v_item_id, p_quantity, v_total_price);
END$$

DELIMITER ;


DELIMITER $$

CREATE DEFINER=`root`@`localhost` FUNCTION `get_price_for_item`(p_item_name VARCHAR(255)) 
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE v_price DECIMAL(10, 2);

    -- Check if the item_name exists in the menu_items table
    IF (SELECT COUNT(*) FROM menu_items WHERE name = p_item_name) > 0 THEN
        -- Retrieve the price for the item
        SELECT price INTO v_price
        FROM menu_items
        WHERE name = p_item_name
        LIMIT 1;

        RETURN v_price;
    ELSE
        -- Invalid item_name, return -1
        RETURN -1;
    END IF;
END $$

DELIMITER ;


DELIMITER $$

CREATE DEFINER=`root`@`localhost` FUNCTION `get_total_order_price`(p_order_id INT) 
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE v_total_price DECIMAL(10, 2);

    -- Check if the order_id exists in the orders table
    IF (SELECT COUNT(*) FROM orders WHERE order_id = p_order_id) > 0 THEN
        -- Calculate the total price of all items in the order
        SELECT SUM(total_price) INTO v_total_price
        FROM orders
        WHERE order_id = p_order_id;

        RETURN v_total_price;
    ELSE
        -- If order_id doesn't exist, return -1 as error code
        RETURN -1;
    END IF;
END $$

DELIMITER ;

use bluemoon_cafe;
select *from menu_items;
select *from order_tracking;
select *from orders;




