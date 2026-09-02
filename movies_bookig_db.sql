-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: movies_bookig_db
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bookings`
--

DROP TABLE IF EXISTS `bookings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookings` (
  `booking_id` int NOT NULL,
  `customer_id` int DEFAULT NULL,
  `movie_id` int DEFAULT NULL,
  `theatre_id` int DEFAULT NULL,
  `booking_date` date DEFAULT NULL,
  `show_time` time DEFAULT NULL,
  `tickets_booked` int DEFAULT NULL,
  `total_amount` decimal(10,2) DEFAULT NULL,
  `payment_method` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`booking_id`),
  KEY `customer_id` (`customer_id`),
  KEY `movie_id` (`movie_id`),
  KEY `theatre_id` (`theatre_id`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`movie_id`) REFERENCES `movies` (`movie_id`),
  CONSTRAINT `bookings_ibfk_3` FOREIGN KEY (`theatre_id`) REFERENCES `theatres` (`theatre_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookings`
--

LOCK TABLES `bookings` WRITE;
/*!40000 ALTER TABLE `bookings` DISABLE KEYS */;
INSERT INTO `bookings` VALUES (1001,1,101,1,'2025-07-01','10:00:00',2,700.00,'UPI'),(1002,2,102,2,'2025-07-01','14:30:00',3,1350.00,'Credit Card'),(1003,3,103,3,'2025-07-02','18:00:00',2,800.00,'Cash'),(1004,4,104,4,'2025-07-02','21:15:00',4,1800.00,'UPI'),(1005,5,105,5,'2025-07-03','11:00:00',1,250.00,'Debit Card'),(1006,6,106,6,'2025-07-03','15:30:00',5,1000.00,'UPI'),(1007,7,107,7,'2025-07-04','19:00:00',2,600.00,'Cash'),(1008,8,108,8,'2025-07-04','13:00:00',3,900.00,'Credit Card'),(1009,9,109,9,'2025-07-05','17:45:00',2,700.00,'UPI'),(1010,10,110,10,'2025-07-05','20:30:00',6,2100.00,'Debit Card'),(1011,11,111,11,'2025-07-06','09:30:00',2,500.00,'Cash'),(1012,12,112,12,'2025-07-06','16:15:00',4,1600.00,'UPI'),(1013,13,113,13,'2025-07-07','18:30:00',3,1050.00,'Credit Card'),(1014,14,114,14,'2025-07-07','12:00:00',2,600.00,'Cash'),(1015,15,115,15,'2025-07-08','15:00:00',5,1250.00,'UPI'),(1016,16,116,16,'2025-07-08','21:00:00',2,700.00,'Debit Card'),(1017,17,117,17,'2025-07-09','11:30:00',3,900.00,'Credit Card'),(1018,18,118,18,'2025-07-09','18:15:00',4,1400.00,'UPI'),(1019,19,119,19,'2025-07-10','20:00:00',1,300.00,'Cash'),(1020,20,120,20,'2025-07-10','14:00:00',2,700.00,'UPI');
/*!40000 ALTER TABLE `bookings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `customer_id` int NOT NULL,
  `customer_name` varchar(100) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`customer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (1,'Sai Kiran','Hyderabad',24,'Male','9876543201'),(2,'Sravani','Hyderabad',22,'Female','9876543202'),(3,'Vamshi','Hyderabad',28,'Male','9876543203'),(4,'Harika','Hyderabad',25,'Female','9876543204'),(5,'Praveen','Hyderabad',30,'Male','9876543205'),(6,'Tejaswini','Hyderabad',27,'Female','9876543206'),(7,'Naveen','Hyderabad',23,'Male','9876543207'),(8,'Keerthi','Hyderabad',26,'Female','9876543208'),(9,'Charan','Hyderabad',29,'Male','9876543209'),(10,'Likitha','Hyderabad',24,'Female','9876543210'),(11,'Rakesh','Hyderabad',31,'Male','9876543211'),(12,'Divya','Hyderabad',21,'Female','9876543212'),(13,'Mahesh','Hyderabad',32,'Male','9876543213'),(14,'Sindhu','Hyderabad',28,'Female','9876543214'),(15,'Karthik','Hyderabad',26,'Male','9876543215'),(16,'Bhavya','Hyderabad',27,'Female','9876543216'),(17,'Sandeep','Hyderabad',29,'Male','9876543217'),(18,'Anusha','Hyderabad',23,'Female','9876543218'),(19,'Ajay','Hyderabad',30,'Male','9876543219'),(20,'Deepika','Hyderabad',25,'Female','9876543220');
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movies`
--

DROP TABLE IF EXISTS `movies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movies` (
  `movie_id` int NOT NULL,
  `movie_name` varchar(100) DEFAULT NULL,
  `genre` varchar(50) DEFAULT NULL,
  `language` varchar(30) DEFAULT NULL,
  `duration` int DEFAULT NULL,
  `release_date` date DEFAULT NULL,
  `rating` decimal(3,1) DEFAULT NULL,
  PRIMARY KEY (`movie_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movies`
--

LOCK TABLES `movies` WRITE;
/*!40000 ALTER TABLE `movies` DISABLE KEYS */;
INSERT INTO `movies` VALUES (101,'Pushpa 2','Action','Telugu',182,'2024-12-05',9.2),(102,'Kalki 2898 AD','Sci-Fi','Telugu',181,'2024-06-27',9.4),(103,'Salaar','Action','Telugu',175,'2023-12-22',8.8),(104,'RRR','Action','Telugu',187,'2022-03-25',9.5),(105,'Hi Nanna','Drama','Telugu',155,'2023-12-07',8.9),(106,'Dasara','Action','Telugu',157,'2023-03-30',8.6),(107,'Lucky Baskhar','Drama','Telugu',148,'2024-10-31',8.8),(108,'HanuMan','Fantasy','Telugu',158,'2024-01-12',9.1),(109,'Saripodhaa Sanivaaram','Action','Telugu',170,'2024-08-29',8.7),(110,'Tillu Square','Comedy','Telugu',145,'2024-03-29',8.5),(111,'MAD','Comedy','Telugu',128,'2023-10-06',8.4),(112,'Virupaksha','Thriller','Telugu',146,'2023-04-21',8.9),(113,'Eagle','Action','Telugu',159,'2024-02-09',8.2),(114,'Bhagavanth Kesari','Action','Telugu',164,'2023-10-19',8.7),(115,'Baby','Romance','Telugu',177,'2023-07-14',8.8),(116,'DJ Tillu','Comedy','Telugu',124,'2022-02-12',8.6),(117,'Ante Sundaraniki','Comedy','Telugu',176,'2022-06-10',8.5),(118,'Sita Ramam','Romance','Telugu',163,'2022-08-05',9.3),(119,'Aadikeshava','Action','Telugu',150,'2023-11-24',7.8),(120,'Gaami','Adventure','Telugu',147,'2024-03-08',8.7);
/*!40000 ALTER TABLE `movies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `screens`
--

DROP TABLE IF EXISTS `screens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `screens` (
  `screen_id` int NOT NULL,
  `theatre_id` int DEFAULT NULL,
  `screen_name` varchar(20) DEFAULT NULL,
  `seating_capacity` int DEFAULT NULL,
  PRIMARY KEY (`screen_id`),
  KEY `theatre_id` (`theatre_id`),
  CONSTRAINT `screens_ibfk_1` FOREIGN KEY (`theatre_id`) REFERENCES `theatres` (`theatre_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `screens`
--

LOCK TABLES `screens` WRITE;
/*!40000 ALTER TABLE `screens` DISABLE KEYS */;
INSERT INTO `screens` VALUES (1,1,'Screen 1',420),(2,1,'Screen 2',250),(3,2,'PCX',630),(4,2,'Screen 2',280),(5,3,'Screen 1',400),(6,3,'Screen 2',180),(7,4,'Audi 1',300),(8,5,'Screen 1',220),(9,6,'Main',900),(10,7,'Main',950),(11,8,'Main',700),(12,9,'Screen 1',260),(13,10,'Screen 3',240),(14,11,'Screen 1',210),(15,12,'Screen 2',290),(16,13,'Main',350),(17,14,'Main',380),(18,15,'Main',300),(19,16,'Screen 1',260),(20,17,'Main',850);
/*!40000 ALTER TABLE `screens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `theatres`
--

DROP TABLE IF EXISTS `theatres`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `theatres` (
  `theatre_id` int NOT NULL,
  `theatre_name` varchar(100) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `total_screens` int DEFAULT NULL,
  PRIMARY KEY (`theatre_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `theatres`
--

LOCK TABLES `theatres` WRITE;
/*!40000 ALTER TABLE `theatres` DISABLE KEYS */;
INSERT INTO `theatres` VALUES (1,'AMB Cinemas','Hyderabad',7),(2,'Prasads Multiplex','Hyderabad',6),(3,'AAA Cinemas','Hyderabad',5),(4,'PVR Nexus Mall','Hyderabad',8),(5,'INOX GSM Mall','Hyderabad',4),(6,'Sandhya 70MM','Hyderabad',1),(7,'Devi 70MM','Hyderabad',1),(8,'Sudarshan 35MM','Hyderabad',1),(9,'Asian CineSquare','Hyderabad',5),(10,'Cinepolis DSL Virtue Mall','Hyderabad',6),(11,'Miraj Cinemas','Hyderabad',4),(12,'PVR Irrum Manzil','Hyderabad',5),(13,'Arjun Theatre','Hyderabad',2),(14,'Mallikarjuna Theatre','Hyderabad',2),(15,'Sri Sai Raja Theatre','Hyderabad',1),(16,'Shanti Theatre','Hyderabad',2),(17,'Sree Ramulu 70MM','Hyderabad',1),(18,'Vimal 70MM','Hyderabad',1),(19,'Sri Mayuri Theatre','Hyderabad',2),(20,'BR Hitech Theatre','Hyderabad',3);
/*!40000 ALTER TABLE `theatres` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-02 21:18:06
