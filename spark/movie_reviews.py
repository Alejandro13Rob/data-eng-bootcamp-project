import argparse
import sys

from pyspark.ml.feature import Tokenizer, StopWordsRemover
from pyspark.sql import SparkSession
import pyspark.sql.functions import array_contains, col, lit, when


def transform_review_into_words(df):
    # get a list of words used by users
    tokenizer = Tokenizer(outputCol="review_words")
    tokenizer.setInputCol("review_str")
    return tokenizer.transform(df)


def remove_stop_words(df):
    # find stop words on english language and filters out stop words
    # from input
    stop_words = StopWordsRemover.loadDefaultStopWords("english")
    remover = StopWordsRemover(stopWords=stop_words)
    remover.setInputCol("review_words")
    remover.setOutputCol("words_clean")

    return remover.transform(df)


def review_sentiment(df):
    # look for data that contain the word “good”, consider the 
    # review as positive
    return df.withColumn("positive_review", 
            array_contains(col("words_clean"), "good"))


def convert_sentiment_to_int(df):
    # from boolean to integer
    # Lit() is required while we are creating columns with exact values.
    return df.withColumn("positive_review", 
            when(col("positive_review") == lit(True), 1).otherwise(0))


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", required=True)
    parser.add_argument("--output_path", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    flags = parse_args(sys.argv[1:])

    # We will save data in .avro as its data definition is in JSON 
    # making it easy to read
    spark = SparkSession.builder.appName("Movie Reviews") \
        .config("spark.jars.packages", "org.apache.spark:spark-avro_2.12:3.1.1") \
        .getOrCreate()
    
    # E
    df = spark.read.option("header", True).csv(flags.input_file)
    # T
    df = transform_review_into_words(df)
    df = remove_stop_words(df)
    df = review_sentiment(df)
    df = convert_sentiment_to_int(df)
    df = df.select("cid", "id_review", "positive_review")
    # L
    df.write.format("avro").save(flags.output_path)
