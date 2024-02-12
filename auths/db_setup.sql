-- prepares a MySQL server for the project

CREATE DATABASE IF NOT EXISTS `portfolio`;
CREATE USER IF NOT EXISTS 'portfolio'@'localhost' IDENTIFIED WITH mysql_native_password BY '';
GRANT ALL PRIVILEGES ON `portfolio`.* TO 'portfolio'@'localhost';
GRANT SELECT ON `performance_schema`.* TO 'portfolio'@'localhost';
FLUSH PRIVILEGES;

-- creates table for storing accounts
USE portfolio;

CREATE TABLE accounts (
  id INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

--INSERT INTO `accounts` (`username`, `password`, `email`) VALUES ('test', '0ef15de6149819f2d10fc25b8c994b574245f193', 'test@test.com');
-- stores users history
CREATE TABLE IF NOT EXISTS user_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    song_id VARCHAR(50),
    song_name VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES accounts(id),
    INDEX fk_user_history_user_id (user_id),
    INDEX fk_user_history_song_id (song_id)
);
--creates table artists
CREATE TABLE IF NOT EXISTS my_artists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    artist_name VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES accounts(id),
    INDEX fk_my_artists_user_id (user_id)
);
