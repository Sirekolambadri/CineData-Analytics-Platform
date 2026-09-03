-- ==========================================================
-- CineData Analytics Platform: Database Backup
-- Database: movies_bookig_db
-- ==========================================================

CREATE DATABASE IF NOT EXISTS `movies_bookig_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `movies_bookig_db`;

-- ----------------------------------------------------------
-- 1. Table structure for `theatres`
-- ----------------------------------------------------------
DROP TABLE IF EXISTS `bookings`;
DROP TABLE IF EXISTS `screens`;
DROP TABLE IF EXISTS `movies`;
DROP TABLE IF EXISTS `customers`;
DROP TABLE IF EXISTS `theatres`;

CREATE TABLE `theatres` (
    `theatre_id` INT AUTO_INCREMENT PRIMARY KEY,
    `theatre_name` VARCHAR(100) NOT NULL,
    `city` VARCHAR(50) NOT NULL,
    `state` VARCHAR(50) NOT NULL,
    `address` VARCHAR(255) DEFAULT NULL,
    `total_screens` INT NOT NULL DEFAULT 1,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- 2. Table structure for `screens`
-- ----------------------------------------------------------
CREATE TABLE `screens` (
    `screen_id` INT AUTO_INCREMENT PRIMARY KEY,
    `theatre_id` INT NOT NULL,
    `screen_name` VARCHAR(50) NOT NULL,
    `seating_capacity` INT NOT NULL,
    `screen_type` VARCHAR(30) NOT NULL DEFAULT 'Standard',
    CONSTRAINT `fk_screens_theatres` FOREIGN KEY (`theatre_id`) 
        REFERENCES `theatres` (`theatre_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- 3. Table structure for `movies`
-- ----------------------------------------------------------
CREATE TABLE `movies` (
    `movie_id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(150) NOT NULL,
    `genre` VARCHAR(50) NOT NULL,
    `duration_minutes` INT NOT NULL,
    `release_date` DATE NOT NULL,
    `rating` DECIMAL(3,1) NOT NULL DEFAULT 0.0,
    `language` VARCHAR(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- 4. Table structure for `customers`
-- ----------------------------------------------------------
CREATE TABLE `customers` (
    `customer_id` INT AUTO_INCREMENT PRIMARY KEY,
    `full_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `phone` VARCHAR(20) DEFAULT NULL,
    `city` VARCHAR(50) DEFAULT NULL,
    `registration_date` DATE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- 5. Table structure for `bookings`
-- ----------------------------------------------------------
CREATE TABLE `bookings` (
    `booking_id` INT AUTO_INCREMENT PRIMARY KEY,
    `customer_id` INT NOT NULL,
    `movie_id` INT NOT NULL,
    `screen_id` INT NOT NULL,
    `show_time` DATETIME NOT NULL,
    `booking_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `seats_booked` INT NOT NULL,
    `total_amount` DECIMAL(10,2) NOT NULL,
    `payment_status` VARCHAR(20) NOT NULL DEFAULT 'Completed',
    `booking_status` VARCHAR(20) NOT NULL DEFAULT 'Confirmed',
    CONSTRAINT `fk_bookings_customers` FOREIGN KEY (`customer_id`) 
        REFERENCES `customers` (`customer_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_bookings_movies` FOREIGN KEY (`movie_id`) 
        REFERENCES `movies` (`movie_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_bookings_screens` FOREIGN KEY (`screen_id`) 
        REFERENCES `screens` (`screen_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- Sample Data Insertion for Backup/Replication
-- ----------------------------------------------------------

-- Theatres
INSERT INTO `theatres` (`theatre_id`, `theatre_name`, `city`, `state`, `address`, `total_screens`) VALUES
(1, 'PVR Grand Mall', 'Mumbai', 'Maharashtra', 'Phoenix Marketcity, Kurla', 6),
(2, 'INOX Metroplex', 'Delhi', 'Delhi', 'Connaught Place', 4),
(3, 'Cinepolis Forum', 'Bengaluru', 'Karnataka', 'Koramangala 7th Block', 8),
(4, 'PVR Nexus Mall', 'Hyderabad', 'Telangana', 'Kukatpally Housing Board', 5),
(5, 'SPI Cinemas Palazzo', 'Chennai', 'Tamil Nadu', 'Vadapalani', 7);

-- Screens
INSERT INTO `screens` (`screen_id`, `theatre_id`, `screen_name`, `seating_capacity`, `screen_type`) VALUES
(1, 1, 'Audi 1 (IMAX)', 250, 'IMAX 3D'),
(2, 1, 'Audi 2 (Dolby)', 180, 'Dolby Atmos'),
(3, 2, 'Audi 1 (Gold)', 120, 'Gold Class'),
(4, 2, 'Audi 2 (Prime)', 200, 'Standard'),
(5, 3, 'Audi 1 (4DX)', 140, '4DX'),
(6, 3, 'Audi 2 (Macro)', 280, 'Standard'),
(7, 4, 'Screen 1 (IMAX)', 300, 'IMAX 2D'),
(8, 5, 'Palazzo Audi 1', 320, 'Dolby Atmos');

-- Movies
INSERT INTO `movies` (`movie_id`, `title`, `genre`, `duration_minutes`, `release_date`, `rating`, `language`) VALUES
(1, 'Oppenheimer', 'Biography/Drama', 180, '2023-07-21', 8.9, 'English'),
(2, 'Interstellar', 'Sci-Fi/Adventure', 169, '2014-11-07', 8.7, 'English'),
(3, 'Dune: Part Two', 'Sci-Fi/Action', 166, '2024-03-01', 8.6, 'English'),
(4, 'Inception', 'Sci-Fi/Thriller', 148, '2010-07-16', 8.8, 'English'),
(5, 'Kantara', 'Action/Drama', 148, '2022-09-30', 8.3, 'Kannada'),
(6, 'RRR', 'Action/Period', 187, '2022-03-25', 7.8, 'Telugu'),
(7, 'Jawan', 'Action/Thriller', 169, '2023-09-07', 7.0, 'Hindi'),
(8, 'Vikram', 'Action/Crime', 174, '2022-06-03', 8.3, 'Tamil');

-- Customers
INSERT INTO `customers` (`customer_id`, `full_name`, `email`, `phone`, `city`, `registration_date`) VALUES
(1, 'Aarav Sharma', 'aarav.sharma@example.com', '+91-9876543210', 'Mumbai', '2023-01-15'),
(2, 'Diya Patel', 'diya.patel@example.com', '+91-9876543211', 'Delhi', '2023-02-20'),
(3, 'Rohan Verma', 'rohan.verma@example.com', '+91-9876543212', 'Bengaluru', '2023-03-10'),
(4, 'Ananya Rao', 'ananya.rao@example.com', '+91-9876543213', 'Hyderabad', '2023-04-05'),
(5, 'Karthik Iyer', 'karthik.iyer@example.com', '+91-9876543214', 'Chennai', '2023-05-12'),
(6, 'Pooja Nair', 'pooja.nair@example.com', '+91-9876543215', 'Bengaluru', '2023-06-18'),
(7, 'Siddharth Roy', 'siddharth.roy@example.com', '+91-9876543216', 'Mumbai', '2023-07-22');

-- Bookings
INSERT INTO `bookings` (`booking_id`, `customer_id`, `movie_id`, `screen_id`, `show_time`, `booking_date`, `seats_booked`, `total_amount`, `payment_status`, `booking_status`) VALUES
(1, 1, 1, 1, '2024-03-15 18:30:00', '2024-03-14 10:15:00', 2, 900.00, 'Completed', 'Confirmed'),
(2, 2, 3, 3, '2024-03-15 20:00:00', '2024-03-14 12:40:00', 1, 650.00, 'Completed', 'Confirmed'),
(3, 3, 2, 5, '2024-03-16 14:00:00', '2024-03-15 09:10:00', 3, 1350.00, 'Completed', 'Confirmed'),
(4, 4, 6, 7, '2024-03-16 19:15:00', '2024-03-15 16:30:00', 4, 1600.00, 'Completed', 'Confirmed'),
(5, 5, 8, 8, '2024-03-17 18:00:00', '2024-03-16 11:20:00', 2, 800.00, 'Completed', 'Confirmed'),
(6, 6, 3, 5, '2024-03-17 21:30:00', '2024-03-16 14:00:00', 2, 900.00, 'Completed', 'Confirmed'),
(7, 7, 1, 2, '2024-03-18 15:45:00', '2024-03-17 08:50:00', 1, 400.00, 'Completed', 'Confirmed'),
(8, 1, 4, 1, '2024-03-19 18:30:00', '2024-03-18 10:00:00', 2, 900.00, 'Completed', 'Confirmed'),
(9, 2, 7, 4, '2024-03-20 20:00:00', '2024-03-19 15:10:00', 2, 700.00, 'Completed', 'Confirmed'),
(10, 3, 5, 6, '2024-03-21 16:00:00', '2024-03-20 11:30:00', 3, 1050.00, 'Completed', 'Confirmed');

COMMIT;
