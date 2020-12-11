"""
Created on 01 Dec 2020

@author: Jade Page (Jade.Page@southcoastscience.com)
"""
import boto3

from scs_core.aws.data.aws_aggregate import AWSAggregator
from scs_core.data.datetime import LocalizedDatetime


def run_aggregate_test():
    aws_access_key = ""
    aws_secret_key = ""

    lambda_client = boto3.client(
        'lambda',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name='us-west-2'
    )

    topic = "south-coast-science-test/aws/loc/1/climate"
    start = "2020-01-11T12:15:36Z"
    start = LocalizedDatetime.construct_from_iso8601(start)
    end = LocalizedDatetime.now()
    checkpoint = "**:/15:00"

    aggy = AWSAggregator(lambda_client, topic, start, end, checkpoint, 150, False)
    aggy.setup()
    res, next_url = aggy.run()
    print(res, next_url)





run_aggregate_test()
