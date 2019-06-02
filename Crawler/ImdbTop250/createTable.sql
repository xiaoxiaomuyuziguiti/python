CREATE TABLE `t_movie_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_en` varchar(100) NOT NULL,
  `name_zh` varchar(500) DEFAULT NULL,
  `genres` varchar(500) DEFAULT NULL,
  `rating` varchar(45) DEFAULT NULL,
  `allstar` varchar(2000) DEFAULT NULL,
  `rating_people_nums` int(11) DEFAULT NULL,
  `year` varchar(45) DEFAULT NULL,
  `country` varchar(45) DEFAULT NULL,
  `director` varchar(500) DEFAULT NULL,
  `runtime` varchar(45) DEFAULT NULL,
  `first_review` varchar(10000) DEFAULT NULL,
  `ranking` int(11) NOT NULL,
  `description` varchar(5000) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idt_movie_info_UNIQUE` (`id`),
  UNIQUE KEY `rank_UNIQUE` (`ranking`)
) ENGINE=InnoDB AUTO_INCREMENT=810 DEFAULT CHARSET=utf8'