import os
from datetime import datetime, timezone
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError

# Setup AWS DynamoDB client
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def ensure_table_exists(table_name: str, sort_key_name: str = 'timestamp'):
    try:
        table = dynamodb.Table(table_name)
        table.load()  # This will raise exception if table doesn't exist
        return table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"[INFO] Table '{table_name}' not found. Creating new one...")
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'symbol', 'KeyType': 'HASH'},
                    {'AttributeName': sort_key_name, 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'symbol', 'AttributeType': 'S'},
                    {'AttributeName': sort_key_name, 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            table.wait_until_exists()
            print(f"[INFO] Table '{table_name}' created.")
            return table
        else:
            raise e

def write_historical_stock_data(ticker: str, stock_data: list[dict]):
    table_name = f"{ticker.lower()}_stockprice"
    table = ensure_table_exists(table_name)

    for record in stock_data:
        table.put_item(
            Item={
                'symbol': ticker,
                'timestamp': record['Date'],
                'open': Decimal(str(record['Open'])),
                'high': Decimal(str(record['High'])),
                'low': Decimal(str(record['Low'])),
                'close': Decimal(str(record['Close'])),
                'volume': Decimal(str(record['Volume']))
            },
            ConditionExpression="attribute_not_exists(#ts)",
            ExpressionAttributeNames={
                "#ts": "timestamp"
            }
        )

def write_recent_stock_data(ticker: str, record: dict):
    write_historical_stock_data(ticker, [record])

def write_predicted_data(ticker: str, forecast: dict):
    """
    forecast = {"date": [...], "values": [...]}
    """
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    table_name = f"{ticker.lower()}_predict_{today}"
    table = ensure_table_exists(table_name)

    for date_str, value in zip(forecast["date"], forecast["values"]):
        try:
            table.put_item(Item={
                'symbol': ticker,
                'timestamp': str(date_str),
                'predicted_close': Decimal(str(value))
            })
        except Exception as e:
            print(f"Error writing to {table_name}: {e}")
