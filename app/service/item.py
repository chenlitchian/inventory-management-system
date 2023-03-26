import time
import datetime
import os
import logging
from boto3 import resource
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import uuid
from decimal import Decimal
import json
from flask import jsonify

from app.model.item import InventoryItem

logger = logging.getLogger(__name__)
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
REGION_NAME = os.environ.get("REGION_NAME")

resource = resource(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION_NAME
)

InventoryTable = resource.Table('Item')


def get_items():
    response = InventoryTable.scan()
    return response['Items']


def update_item(request_data):
    '''
    insert item to inventory 
    '''
    try:
        name = request_data['name']
        category = request_data['category']
        price = request_data['price']

        # check if name and category exist in table
        item = InventoryTable.scan(
            FilterExpression=(
                Key('name').eq(name) & Key('category').eq(category)))

        # yes, update price and timestamp and return item ID
        if len(item['Items']):

            item_ = item['Items'][0]

            InventoryTable.update_item(
                Key={'name': item_['name']},
                UpdateExpression="set category=:c, price=:p, last_updated_dt=:d",
                ExpressionAttributeValues={
                    ':p': Decimal(str(price)), ':c': str(category), ':d': int(time.time())},
                ReturnValues="NONE")

            return {"id": item_['id']}
        else:
            # no, insert Item with new ID
            new_uuid = str(uuid.uuid4())
            InventoryTable.put_item(
                Item={'id': new_uuid, 'name': name,
                      'category': category, 'price': price, 'last_updated_dt': int(time.time())},
                ReturnValues='NONE',
            )
            return {"id": new_uuid}

    except ClientError as err:
        logger.error(
            "Couldn't update item %s in table %s. Here's why: %s: %s",
            name, InventoryTable.name,
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


def list_items_by_start_end(args):
    '''
    return items from start to end last_updated_dt
    '''
    try:
        from_dt = args['dt_from']
        to_dt = args['dt_to']

        # Convert datetime string to datetime object
        from_dt_object = datetime.datetime.strptime(
            from_dt, "%Y-%m-%d %H:%M:%S")
        to_dt_object = datetime.datetime.strptime(to_dt, "%Y-%m-%d %H:%M:%S")

        # convert object to unix timestamp
        from_timestamp = int(time.mktime(from_dt_object.timetuple()))
        to_timestamp = int(time.mktime(to_dt_object.timetuple()))

        attributes = ['id', 'name', 'price', 'category']
        projection_expression = ', '.join(['#' + attr for attr in attributes])
        expression_attribute_names = {
            ('#' + attr): attr for attr in attributes}

        response = InventoryTable.scan(
            FilterExpression=(Key('last_updated_dt').between(
                from_timestamp, to_timestamp)),
            ProjectionExpression=projection_expression,
            ExpressionAttributeNames=expression_attribute_names
        )

        result = {}
        total_price = 0

        items = response['Items']
        inventory_items = []

        for item in items:
            inventory_item = InventoryItem(**item)
            inventory_items.append(inventory_item)

        for item in inventory_items:
            total_price = total_price + Decimal(item.price)

        result['total_price'] = float(total_price)
        result['items'] = [item.__dict__ for item in inventory_items]

        return jsonify(json.loads(json.dumps(result)))

    except ClientError as err:
        logger.error(
            "Couldn't query item in table %s. Here's why: %s: %s",
            InventoryTable.name,
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise


def list_items_by_category(args):
    '''
    list item by category
    '''
    try:
        category = args['category']
        scan_kwargs = {}

        # set category filter if not "all"
        if category != "all":
            scan_kwargs['FilterExpression'] = Key('category').eq(category)

        response = InventoryTable.scan(**scan_kwargs)

        items = response['Items']

        category = {}
        # process each item and compute total price and count for each category
        for item in items:
            c = item['category']
            if c not in category:
                category[c] = {'category': c, 'total_price': float(
                    item['price']), 'count': 1}
            else:
                category[c]['total_price'] += float(item['price'])
                category[c]['count'] += 1

        return {"items": list(category.values())}

    except ClientError as err:
        logger.error(
            "Couldn't query item in table %s. Here's why: %s: %s",
            InventoryTable.name,
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise
