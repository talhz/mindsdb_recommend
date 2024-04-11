# DynamoDB Handler

This is the implementation of the DynamoDB handler for MindsDB.

## DynamoDB
Amazon DynamoDB is a fully managed, serverless, key-value NoSQL database designed to run high-performance applications at any scale. DynamoDB offers built-in security, continuous backups, automated multi-Region replication, in-memory caching, and data export tools.
<br>
https://aws.amazon.com/dynamodb/

## Implementation
This handler was implemented using the `boto3`, the AWS SDK for Python.

The required arguments to establish a connection are,
* `aws_access_key_id`: the AWS access key
* `aws_secret_access_key`: the AWS secret access key
* `region_name`: the AWS region

## Usage
In order to make use of this handler and connect to DynamoDB in MindsDB, the following syntax can be used,
~~~~sql
CREATE DATABASE dynamodb_datasource
WITH
engine='dynamodb',
parameters={
    "aws_access_key_id": "PCAQ2LJDOSWLNSQKOCPW",
    "aws_secret_access_key": "U/VjewPlNopsDmmwItl34r2neyC6WhZpUiip57i",
    "region_name": "us-east-1"
};
~~~~

Now, you can use this established connection to query DynamoDB as follows,
~~~~sql
SELECT * FROM dynamodb_datasource.example_tbl
~~~~
Queries to DynamoDB can be issued in PartiQL using this handler,
https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ql-reference.html