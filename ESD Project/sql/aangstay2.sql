-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jan 14, 2019 at 06:42 AM
-- Server version: 5.7.19
-- PHP Version: 7.1.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE DATABASE IF NOT EXISTS `g1t3-aangstay` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `g1t3-aangstay`;

CREATE TABLE IF NOT EXISTS`house` (
  `houseId` int NOT NULL AUTO_INCREMENT,
  `houseName` varchar(100) NOT NULL,
  `address` varchar(255) NOT NULL,
  `region` varchar(50) NOT NULL,
  `latitude` decimal(11,8) NOT NULL,
  `longitude` decimal(12,8) NOT NULL,
  `price` decimal(10,0) NOT NULL,
  PRIMARY KEY (`houseId`),
  UNIQUE KEY `houseId_UNIQUE` (`houseId`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;

-- Dumping data for table `house` 

INSERT INTO `g1t3-aangstay`.`house` (`houseId`,`houseName`,`address`,`region`,`latitude`,`longitude`,`price`) VALUES
(1,'Green Vill','254 Onan Rd, Singapore 424643','Singapore',1.3105012607915825, 103.90056226530486,100),
(2, 'Grey Vill','40A Joo Chiat Terrace, Singapore 427202', 'Singapore', 1.3142898987117617, 103.90051734333403,100),
(3, 'Blue Vill', '26 Lor 104 Changi, Singapore 426570', 'Singapore', 1.3158263101456358, 103.90203985871804,150),
(4, 'Red Vill', '10 Sommerville Walk, Singapore 358180', 'Singapore', 1.3446317315238077, 103.87018711335882,120),
(5, 'Blue View', '20 Namly Dr, Singapore 267434', 'Singapore',1.3242667897798606, 103.79729559848167,200),
(6, 'Blue Hill', '10 Namly Garden, Singapore 267339', 'Singapore', 1.3248606850108324, 103.7971154521439,150),
(7, 'Crimson Viel', '11 Robin Ln, Singapore 258241', 'Singapore', 1.3190349100413394, 103.82706295043877,100),
(8, 'Red Hill', '24 Lasia Ave, Singapore 277850', 'Singapore', 1.3293392815629168, 103.7936329699553,300),
(9, 'Brown Hill', '61 Jln Puteh Jerneh, Singapore 278077', 'Singapore', 1.309886407489322, 103.79753976428658,250),
(10, 'Sea View', '74 Jln Kelabu Asap, Singapore 278267', 'Singapore',1.310774945183235, 103.79684233542625,250),
(11, 'River Vale', '43 Jln Chengkek, Singapore 369266', 'Singapore', 1.3306012861113672, 103.88469366829857,200),
(12, 'Hill Vale', '35 Jln Tupai, Singapore 249162', 'Singapore', 1.301830541540901, 103.82685763633978,150);

CREATE TABLE IF NOT EXISTS `transaction` (
  `transactionId` int NOT NULL AUTO_INCREMENT,
  `startDate` date NOT NULL,
  `endDate` date NOT NULL,
  `status` varchar(20) NOT NULL,
  `houseId` int NOT NULL,
  `bookingNum` varchar(6) DEFAULT NULL,
  PRIMARY KEY (`transactionId`),
  UNIQUE KEY `transactionId_UNIQUE` (`transactionId`),
  UNIQUE KEY `bookingNum_UNIQUE` (`bookingNum`),
  KEY `houseId_idx` (`houseId`),
  CONSTRAINT `houseId` FOREIGN KEY (`houseId`) REFERENCES `house` (`houseId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `g1t3-aangstay`.`transaction` (`transactionId`,`startDate`, `endDate`,`status`,`houseId`,`bookingNum`) VALUES
('10000001','2023-04-05', '2023-04-09','confirmed',5,'3FB3B3'); 

INSERT INTO `g1t3-aangstay`.`transaction` (`startDate`, `endDate`,`status`,`houseId`,`bookingNum`) VALUES
('2023-04-05', '2023-04-09','confirmed',6, '347F50'),
('2023-04-05', '2023-04-09','confirmed','5', '1CB14F'),
('2023-04-05', '2023-04-09','confirmed','10', 'FE031C'),
('2023-04-11', '2023-04-15','confirmed','2', '6A1E0F'),
('2023-04-10', '2023-04-12','confirmed','6', '7F86A4'),
('2023-04-18', '2023-04-20','confirmed',7, 'E85981');

CREATE TABLE IF NOT EXISTS `payment` (
  `paymentId` int NOT NULL,
  `tDate` date NOT NULL,
  `paidAmount` decimal(10,0) NOT NULL,
  `status` varchar(25) NOT NULL,
  `invoiceId` varchar(100),
  `houseId` int NOT NULL,
  PRIMARY KEY (`paymentId`),
  KEY `houseId_idx` (`houseId`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

INSERT INTO `g1t3-aangstay`.`payment` (`paymentId`, `tDate`, `paidAmount`, `status`, `houseId`) VALUES 

-- status: COMPLETED/DECLINED/REFUNDED/FAILED
('1', '2023-03-21', '100', 'completed', '1'),
('2', '2023-03-21', '150', 'refunded', '3');