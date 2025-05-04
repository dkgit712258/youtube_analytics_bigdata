CREATE KEYSPACE IF NOT EXISTS youtube WITH REPLICATION = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

USE youtube;

CREATE TABLE IF NOT EXISTS trending_videos (
  video_id text PRIMARY KEY,
  title text,
  channel_title text,
  category_id int,
  publish_time timestamp,
  views int,
  likes int,
  dislikes int,
  comment_count int,
  trending_date text
);
