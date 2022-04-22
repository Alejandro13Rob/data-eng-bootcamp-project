import argparse
import sys

# API for parsing xml data in the csv file
import xml.etree.ElementTree as ET
# spark imports
from pyspark.sql.session import SparkSession
from pyspark.sql import functions
from pyspark.context import SparkContext
from pyspark.sql.types import StructType, StructField, StringType


logs_dataframe_schema = StructType(
    [
        StructField("log_date", StringType(), True),
        StructField("device", StringType(), True),
        StructField("location", StringType(), True),
        StructField("os", StringType(), True),
        StructField("ip", StringType(), True),
        StructField("phone_number", StringType(), True),
    ]
)


def select_text(root, xpath):
    nodes = [e.text for e in root.findall(xpath) if isinstance(e, ET.Element)]
    return next(iter(nodes), None)


def extract_data_from_xml(xml_text):
    root = ET.fromstring(xml_text)
    return {
        "log_date": _select_text(root, "log/logDate"),
        "device": _select_text(root, "log/device"),
        "location": _select_text(root, "log/location"),
        "os": _select_text(root, "log/os"),
        "ip": _select_text(root, "log/ipAddress"),
        "phone_number": _select_text(root, "log/phoneNumber"),
    }


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", required=True)
    parser.add_argument("--output_path", required=True)
    return parser.parse_args()


extract_columns_from_xml = functions.udf(extract_data_from_xml, logs_dataframe_schema)


if __name__ == "__main__":
    flags = parse_args(sys.argv[1:])

    spark = SparkSession(SparkContext())

    # E
    raw_df = spark.read.option("header", True).csv(flags.input_file)
    # T
    df = raw_df.withColumn(
        "info", extract_columns_from_xml("log")
    ).select(
        "id_review",
        functions.to_date(F.col("info.log_date"), "MM-dd-yyyy").alias("log_date"),
        "info.device",
        "info.location",
        "info.os",
        "info.ip",
        "info.phone_number",
    )
    # L
    df.write.format("avro").save(flags.output_path)
