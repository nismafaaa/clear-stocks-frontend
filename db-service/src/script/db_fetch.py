import os
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

# Setup DynamoDB client
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)


def fetch_historical(ticker: str, start_date: str, end_date: str):
    table_name = f"{ticker.lower()}_stockprice"
    table = dynamodb.Table(table_name)

    response = table.scan()
    items = response.get('Items', [])

    # Filter in Python side (karena scan tidak bisa range key jika sort key bukan primary)
    filtered = [
        item for item in items
        if start_date <= item['timestamp'] <= end_date
    ]
    return filtered


def fetch_recent(ticker: str):
    table_name = f"{ticker.lower()}_stockprice"
    table = dynamodb.Table(table_name)

    response = table.scan()
    items = sorted(response.get('Items', []), key=lambda x: x['timestamp'], reverse=True)
    return items[0] if items else {}


def fetch_predict(ticker: str, length: int):
    today = datetime.now().strftime("%Y%m%d")
    table_name = f"{ticker.lower()}_predict_{today}"
    table = dynamodb.Table(table_name)

    response = table.scan()
    items = sorted(response.get('Items', []), key=lambda x: x['timestamp'])[:length]
    return items