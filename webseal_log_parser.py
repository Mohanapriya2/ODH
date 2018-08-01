import sys
import logging
import shlex
import json
import hashlib
import datetime
import re

from collections import defaultdict
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from kafka import KafkaProducer
#import pyspark_cassandra.streaming

from utils import Utils

def get_channel_and_country_from_url(country_str):
    country = ''
    channel = ''
    country_key='cty'
    channel_key='chl'
    table_dict = defaultdict()
    url_string = country_str.split('?')
    if len(url_string) == 2:
        query_params = url_string[1].split('&')
        for query_param in query_params:
            key_value = query_param.split('=')
            if len(key_value) == 2:
                table_dict[key_value[0]] = key_value[1]
    print("table_dict",table_dict)
    if country_key in table_dict:
        country = table_dict[country_key][0:2]

    if channel_key in table_dict:
        channel = table_dict[channel_key]
    return country, channel


def get_scope_and_grant_from_url(request_url):
    scope = ''
    grant_type = ''
    url_string = request_url.split('?')
    if len(url_string) == 2:
        query_params = url_string[1].split('&')
        for query_param in query_params:
            if 'scope' in query_param:
                if '=' in query_param:
                    scope = query_param[query_param.index('=') + 1:]
                else:
                    scope = query_param
            elif 'grant_type' in query_param:
                if '=' in query_param:
                    grant_type = query_param[query_param.index('=') + 1:]
                else:
                    grant_type = query_param

    return scope, grant_type


def get_country_from_log_name(log_name, message):
    country_string = ""
    if '.' in log_name:
        country_string = log_name.split(".")[1][0:2]
    return country_string


def split_data_m(message):
    try:
        return shlex.split(message.encode('utf-8'))

    except ValueError:
        logging.exception("ValueError when pushing the data push_to_cassandra_kafka()", message)


def hash_id_with_sha256(id_value):
    hash_id = hashlib.sha256(id_value)
    return hash_id.hexdigest()


def create_final_string(message):
    split_data = split_data_m(message)
    print("split_data",split_data)
    country_name = ""
    channel_name = ""
    redirect_url = ""#output
    agent_name = ""
    user_name = ""
    bearer = ""
    final_json_map = None
    insert_time = ""

    try:
        if (len(split_data) == 15) or (len(split_data) == 14):
            if len(split_data) == 15:
                country_name, channel_name = get_channel_and_country_from_url(split_data[9])
                agent_name = split_data[14]
                user_name = hash_id_with_sha256(split_data[13])
                bearer = hash_id_with_sha256(split_data[12])

            elif len(split_data) == 14:
                country_name = get_country_from_log_name(split_data[0], message)
                redirect_url = split_data[12].split("?")[0]
                agent_name = split_data[13]

            scope, grant_type = get_scope_and_grant_from_url(split_data[9])
            log_name = split_data[0]
            ip_address = split_data[4]
            hash_ip = hashlib.sha1(ip_address)
            method = split_data[9].split(" ")[0]
            request_url_data = split_data[9].split(" ")[1]
            request_url = request_url_data.split("?")[0]
            response_code = split_data[10]
            insert_time = str(datetime.datetime.now())
            time_spent = split_data[11]
            reg_number = re.compile(r'\d+')
            if reg_number.match(time_spent):
                time_spent = time_spent
            else:
                time_spent = 0
            log_created_date = str(datetime.datetime.strptime(split_data[7], '%d/%b/%Y:%H:%M:%S')
                                   .strftime('%Y-%m-%d'))
            date_and_time = str(datetime.datetime.strptime(split_data[7], '%d/%b/%Y:%H:%M:%S')
                                .strftime('%Y-%m-%dT%H:%M:%S.%f')) + str(split_data[8])
            final_json_map = dict(
                {"log_name": log_name, "method": method, "country_name": country_name.upper(),
                 "channel_name": channel_name, "scope": scope, "grant_type": grant_type,
                 "response_code": response_code, "time_spent": int(time_spent),
                 "redirect_url": redirect_url, "date_and_time": date_and_time, "agent_name": agent_name,
                 "request_url": request_url, "ip_address": hash_ip.hexdigest(), "user_name": user_name ,
                 "bearer": bearer, "day": log_created_date, "insert_time": insert_time})

            return final_json_map
    except Exception as e:
        logging.exception('Error with the message format inside create_final_string()')
        print(e)


def push_json_to_kafka(message):
        try:
            if None not in message.take(1):
                records = message.collect()
                for record in records:
                    producer.send(configuration.property("kafka")["topic.output"], bytes(json.dumps(record)))
        except Exception as e:
            logging.exception('Error with the message format push_json_to_kafka()')
            print(e)


def push_json_to_cassandra(message):
    try:
        if None not in message.take(1):
            message.saveToCassandra(configuration.property("cassandra.keyspace"),
                                    configuration.property("cassandra.table_name"))
    except TypeError as s:
        logging.exception('Error with the message format TypeError inside push_json_to_cassandra()')
    except Exception as e:
        logging.exception('Error with the message format inside push_json_to_cassandra()')
        print(e)


if __name__ == "__main__":
    configuration = Utils.load_config(sys.argv[:])
    producer = KafkaProducer(bootstrap_servers=configuration.property("kafka")["bootstrap.servers"])
    sc = SparkContext(appName=configuration.property("spark.appName"))
    channel_key = configuration.property("appconfig.channel")
    country_key = configuration.property("appconfig.country")
    ssc = StreamingContext(sc, 5)
    kafka_params = {"bootstrap.servers": configuration.property("kafka")["bootstrap.servers"],
                    "startingOffsets": configuration.property("kafka")["startingOffsets"]}
    messages = KafkaUtils.createDirectStream(ssc, [configuration.property("kafka")["topic.input"]], kafka_params)

    try:
        output = messages.map(lambda message: create_final_string(message[1]))
        output.foreachRDD(push_json_to_kafka)
        output.foreachRDD(push_json_to_cassandra)
    except ValueError:
        logging.exception('Error raised with the JSON format exception inside ouput.foreachRDD()')

    ssc.start()
    ssc.awaitTermination()

