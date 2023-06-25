CREATE TABLE `posts_streaming` (
  `id` BIGINT(19) UNSIGNED NOT NULL AUTO_INCREMENT,
  `mastodon_id` VARCHAR(50) NOT NULL,
  `text` NVARCHAR(2000),
  `created_at` DATETIME,
  `favourites_count` INT,
  `language` VARCHAR(10),
  `uri` VARCHAR(255),
  `tags` NVARCHAR(255),
  PRIMARY KEY (`id`),
  KEY (`mastodon_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `posts_batch` (
  `id` BIGINT(19) UNSIGNED NOT NULL AUTO_INCREMENT,
  `mastodon_id` VARCHAR(50) NOT NULL,
  `text` NVARCHAR(2000),
  `created_at` DATETIME,
  `favourites_count` INT,
  `language` VARCHAR(10),
  `uri` VARCHAR(255),
  `tags` NVARCHAR(255),
  PRIMARY KEY (`id`),
  KEY (`mastodon_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
