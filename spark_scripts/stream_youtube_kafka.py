from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark session
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("YouTubeTrendingConsumer") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1") \
    .getOrCreate()


# Define Kafka source
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "youtube_trending") \
    .load()

# Extract the message value from Kafka
message_df = kafka_df.selectExpr("CAST(value AS STRING)")

# Write the data to console (or any other sink)
query = message_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()
