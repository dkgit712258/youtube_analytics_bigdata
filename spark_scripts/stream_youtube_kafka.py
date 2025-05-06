# from pyspark.sql import SparkSession
# from pyspark.sql.functions import col

# # Initialize Spark session
# from pyspark.sql import SparkSession

# spark = SparkSession.builder \
#     .appName("YouTubeTrendingConsumer") \
#     .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1") \
#     .getOrCreate()


# # Define Kafka source
# kafka_df = spark.readStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", "kafka:9092") \
#     .option("subscribe", "youtube_trending") \
#     .load()

# # Extract the message value from Kafka
# message_df = kafka_df.selectExpr("CAST(value AS STRING)")

# # Write the data to console (or any other sink)
# query = message_df.writeStream \
#     .outputMode("append") \
#     .format("console") \
#     .start()

# query.awaitTermination()

# from pyspark.sql import SparkSession
# from pyspark.sql.functions import from_json, col
# from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

# spark = SparkSession.builder \
#     .appName("YouTubeTrendingConsumer") \
#     .config("spark.jars.packages", ",".join([
#         "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1",
#         "com.datastax.spark:spark-cassandra-connector_2.12:3.5.0"
#     ])) \
#     .config("spark.sql.catalog.cass", "com.datastax.spark.connector.datasource.CassandraCatalog") \
#     .config("spark.cassandra.connection.host", "cassandra") \
#     .getOrCreate()

# kafka_df = spark.readStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", "kafka:9092") \
#     .option("subscribe", "youtube_trending") \
#     .load()

# message_df = kafka_df.selectExpr("CAST(value AS STRING)")

# schema = StructType([
#     StructField("video_id", StringType(), True),
#     StructField("title", StringType(), True),
#     StructField("channel_title", StringType(), True),
#     StructField("category_id", IntegerType(), True),
#     StructField("publish_time", TimestampType(), True),
#     StructField("views", IntegerType(), True),
#     StructField("likes", IntegerType(), True),
#     StructField("dislikes", IntegerType(), True),
#     StructField("comment_count", IntegerType(), True),
#     StructField("trending_date", StringType(), True)
# ])

# message_parsed_df = message_df.select(from_json(col("value"), schema).alias("data")).select("data.*")

# # Writing to Cassandra
# query_cassandra = message_parsed_df.writeStream \
#     .outputMode("append") \
#     .format("org.apache.spark.sql.cassandra") \
#     .option("keyspace", "youtube") \
#     .option("table", "trending_videos") \
#     .start()

# # Also print to console (optional for debugging)
# query_console = message_parsed_df.writeStream \
#     .outputMode("append") \
#     .format("console") \
#     .option("checkpointLocation", "./spark_scripts/") \
#     .start()

# query_console.awaitTermination()
# query_cassandra.awaitTermination()






from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

# 1. Initialize Spark session
spark = SparkSession.builder \
    .appName("YouTubeTrendingConsumer") \
    .config("spark.jars.packages", ",".join([
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1",
        "com.datastax.spark:spark-cassandra-connector_2.12:3.5.0"
    ])) \
    .config("spark.sql.catalog.cass", "com.datastax.spark.connector.datasource.CassandraCatalog") \
    .config("spark.cassandra.connection.host", "cassandra") \
    .getOrCreate()

# 2. Define Kafka source
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "youtube_trending") \
    .load()

# 3. Convert Kafka message value to string
message_df = kafka_df.selectExpr("CAST(value AS STRING)")

# 4. Define the schema
schema = StructType([
    StructField("video_id", StringType(), True),
    StructField("title", StringType(), True),
    StructField("channel_title", StringType(), True),
    StructField("category_id", IntegerType(), True),
    StructField("publish_time", TimestampType(), True),
    StructField("views", IntegerType(), True),
    StructField("likes", IntegerType(), True),
    StructField("dislikes", IntegerType(), True),
    StructField("comment_count", IntegerType(), True),
    StructField("trending_date", StringType(), True)
])

# 5. Parse the JSON messages
message_parsed_df = message_df.select(from_json(col("value"), schema).alias("data")).select("data.*")

# 6. Define foreachBatch function to write to Cassandra and print to console
def write_to_sinks(batch_df, batch_id):
    if not batch_df.isEmpty():
        # Write to Cassandra
        batch_df.write \
            .format("org.apache.spark.sql.cassandra") \
            .option("keyspace", "youtube") \
            .option("table", "trending_videos") \
            .mode("append") \
            .save()

        # Optional: print to console for debugging
        batch_df.show(truncate=False)

# 7. Start the streaming query
query = message_parsed_df.writeStream \
    .foreachBatch(write_to_sinks) \
    .option("checkpointLocation", "./checkpoints/youtube_kafka") \
    .start()

query.awaitTermination()
