-- prepares a MySQL server for the project

CREATE DATABASE IF NOT EXISTS `portfolio` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER IF NOT EXISTS 'portfolio'@'localhost' IDENTIFIED WITH mysql_native_password BY '';
GRANT ALL PRIVILEGES ON `portfolio`.* TO 'portfolio'@'localhost';
GRANT SELECT ON `performance_schema`.* TO 'portfolio'@'localhost';
FLUSH PRIVILEGES;

-- creates table for storing accounts
USE `portfolio;

CREATE TABLE IF NOT EXISTS `accounts` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
  	`username` varchar(50) NOT NULL,
  	`password` varchar(255) NOT NULL,
  	`email` varchar(100) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

INSERT INTO `accounts` (`id`, `username`, `password`, `email`) VALUES (1, 'test', '0ef15de6149819f2d10fc25b8c994b574245f193', 'test@test.com');
