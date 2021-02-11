-- MySQL dump 10.18  Distrib 10.3.27-MariaDB, for debian-linux-gnueabihf (armv8l)
--
-- Host: localhost    Database: borehole
-- ------------------------------------------------------
-- Server version	10.3.27-MariaDB-0+deb10u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `borehole_log`
--

DROP TABLE IF EXISTS `borehole_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `borehole_log` (
  `borehole_log_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `borehole_log_pump_time` int(11) DEFAULT NULL,
  `borehole_log_pump_volume` int(11) DEFAULT NULL,
  `borehole_log_message` varchar(255) DEFAULT NULL,
  `borehole_log_time` bigint(20) NOT NULL DEFAULT unix_timestamp(),
  `borehole_log_code` int(11) NOT NULL,
  `borehole_log_pump` tinyint(4) NOT NULL DEFAULT 0 COMMENT '1=borehole pump, 2=booster pump',
  PRIMARY KEY (`borehole_log_id`),
  KEY `borehole_log_code` (`borehole_log_code`),
  CONSTRAINT `borehole_log_ibfk_1` FOREIGN KEY (`borehole_log_code`) REFERENCES `log_codes` (`log_code_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12075 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `borehole_log`
--

LOCK TABLES `borehole_log` WRITE;
/*!40000 ALTER TABLE `borehole_log` DISABLE KEYS */;

/*!40000 ALTER TABLE `borehole_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log_codes`
--

DROP TABLE IF EXISTS `log_codes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `log_codes` (
  `log_code_id` int(11) NOT NULL,
  `log_code_description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`log_code_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log_codes`
--

LOCK TABLES `log_codes` WRITE;
/*!40000 ALTER TABLE `log_codes` DISABLE KEYS */;

/*!40000 ALTER TABLE `log_codes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warnings`
--

DROP TABLE IF EXISTS `warnings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `warnings` (
  `warning_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `warning_description` text NOT NULL,
  `warning_severity` int(11) NOT NULL,
  PRIMARY KEY (`warning_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warnings`
--

LOCK TABLES `warnings` WRITE;
/*!40000 ALTER TABLE `warnings` DISABLE KEYS */;
/*!40000 ALTER TABLE `warnings` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-02-11 11:00:47
