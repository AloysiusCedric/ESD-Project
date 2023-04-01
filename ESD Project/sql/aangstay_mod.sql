-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jan 14, 2019 at 06:42 AM
-- Server version: 5.7.19
-- PHP Version: 7.1.9
-- select*from g1t3-aangstay.payment;
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

CREATE TABLE IF NOT EXISTS `g1t3-aangstay`.`house` (
  `houseId` int NOT NULL AUTO_INCREMENT,
  `houseName` varchar(100) NOT NULL,
  `address` varchar(255) NOT NULL,
  `latitude` decimal(11,8) NOT NULL,
  `longitude` decimal(12,8) NOT NULL,
  `price` decimal(10,0) NOT NULL,
  PRIMARY KEY (`houseId`),
  UNIQUE KEY `houseId_UNIQUE` (`houseId`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;


-- Dumping data for table `house` 

INSERT INTO `g1t3-aangstay`.`house` (`houseId`,`houseName`,`address`,`latitude`,`longitude`,`price`) VALUES
(1,'Green Vill','254 Onan Rd, Singapore 424643',1.3105012607915825, 103.90056226530486,100),
(2, 'Grey Vill','40A Joo Chiat Terrace, Singapore 427202', 1.3142898987117617, 103.90051734333403,100),
(3, 'Blue Vill', '26 Lor 104 Changi, Singapore 426570', 1.3158263101456358, 103.90203985871804,150),
(4, 'Red Vill', '10 Sommerville Walk, Singapore 358180', 1.3446317315238077, 103.87018711335882,120),
(5, 'Blue View', '20 Namly Dr, Singapore 267434', 1.3242667897798606, 103.79729559848167,200),
(6, 'Blue Hill', '10 Namly Garden, Singapore 267339',1.3248606850108324, 103.7971154521439,150),
(7, 'Crimson Viel', '11 Robin Ln, Singapore 258241', 1.3190349100413394, 103.82706295043877,100),
(8, 'Red Hill', '24 Lasia Ave, Singapore 277850', 1.3293392815629168, 103.7936329699553,300),
(9, 'Brown Hill', '61 Jln Puteh Jerneh, Singapore 278077', 1.309886407489322, 103.79753976428658,250),
(10, 'Sea View', '74 Jln Kelabu Asap, Singapore 278267', 1.310774945183235, 103.79684233542625,250),
(11, 'River Vale', '43 Jln Chengkek, Singapore 369266', 1.3306012861113672, 103.88469366829857,200),
(12, 'Hill Vale', '35 Jln Tupai, Singapore 249162', 1.301830541540901, 103.82685763633978,150);

-- payment
-- Note: paymentId = transactionId from PayPal
CREATE TABLE IF NOT EXISTS `g1t3-aangstay`.`payment` (
  `paymentId` INT NOT NULL AUTO_INCREMENT,
  `tDate` DATE NOT NULL,
  `paidAmount` DECIMAL(10,0) NOT NULL,
  `status` VARCHAR(25) NOT NULL,
  `housepId` INT NULL,
  PRIMARY KEY (`paymentId`),
  INDEX `housepId_idx` (`housepId` ASC) VISIBLE,
  UNIQUE INDEX `paymentId_UNIQUE` (`paymentId`) VISIBLE,
  CONSTRAINT `housepId`
    FOREIGN KEY (`housepId`)
    REFERENCES `g1t3-aangstay`.`house` (`houseId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

INSERT INTO `g1t3-aangstay`.`payment` (`paymentId`, `tDate`, `paidAmount`, `status`, `housepId`) VALUES 
-- status: COMPLETED/DECLINED/REFUNDED/FAILED
('1000000001', '2023-03-21', '100', 'COMPLETED', 1),
('1000000002', '2023-03-21', '150', 'REFUNDED', 3),
('1000000003', '2023-03-23', '200', 'COMPLETED', 5);
-- ('4AY363202E056942B', '2023-03-23', '200', 'COMPLETED', 5); 
-- FOR PAYPAL CAPTUREID if successful

-- transaction (holds information about the dates and status of booking after payment is completed)
-- status: completed, cancelled

CREATE TABLE IF NOT EXISTS `g1t3-aangstay`.`transaction` (
  `transactionId` INT NOT NULL AUTO_INCREMENT,
  `startDate` DATE NOT NULL,
  `endDate` DATE NOT NULL,
  `status` VARCHAR(20) NOT NULL,
  `houseId` INT NOT NULL,
  `bookingNum` VARCHAR(6) NULL,
  `paymentId` INT NOT NULL,
  PRIMARY KEY (`transactionId`),
  INDEX `houseId_idx` (`houseId` ASC) VISIBLE,
  UNIQUE INDEX `transactionId_UNIQUE` (`transactionId`) VISIBLE,
  CONSTRAINT `houseId`
	  FOREIGN KEY (`houseId`)
	  REFERENCES `g1t3-aangstay`.`house` (`houseId`)
	  ON DELETE NO ACTION
	  ON UPDATE NO ACTION,
  CONSTRAINT `paymentId`
	  FOREIGN KEY (`paymentId`)
	  REFERENCES `g1t3-aangstay`.`payment` (`paymentId`)
	  ON DELETE NO ACTION
	  ON UPDATE NO ACTION
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;