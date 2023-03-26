from flask import Flask, request, abort, make_response
from app.service.item import *

app = Flask(__name__)

@app.route('/')
def items():
    # items = get_items()
    return "Hello World"


@app.route('/insert', methods=['POST'])
def insert_items():
    '''
    Create a function to insert new item. If re-insert an item with the same name, the record should be updated with the new price. The record should have a “las
    t_updated_dt” field to indicate the date of insert/update. Return server assigned ID for the newly created item
    '''
    try:
        request_data = request.get_json()
        return update_item(request_data)
    except Exception as e:
        abort(400, description="insert item error")


@app.route('/get-items-by-dates',  methods=['GET'])
def get_items_by_dates():
    '''
    By passing in a date range as a filter, query all the items that have the “last_updated_dt” within the date range. The response should have an additional field
    to indicate the total price of all the items.
    '''
    try:
        args = request.args
        return list_items_by_start_end(args)
    except:
        abort(400, description="get item by dates error")


@app.route('/get-items-by-category', methods=['GET'])
def get_items_by_category():
    '''
    return items by category and the total price 
    If category: “all” is passed, it should return all category, else it should return items belongs to that category
    '''
    try:
        args = request.args
        return list_items_by_category(args)
    except:
        abort(400, description="get items by category error")


if __name__ == '__main__':
    app.run()
