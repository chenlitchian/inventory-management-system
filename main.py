from flask import Flask, jsonify
from app.service.database import * 

app = Flask(__name__)

@app.route('/')
def items():
    items = get_items()
    return items

@app.route('/insert')
def insert_items():
    return 'TODO: Implement Functionality 1'


@app.route('/get-items-by-dates')
def get_items_by_dates():
    return 'TODO: Implement Functionality 2'


@app.route('/get-items-by-category')
def get_items_by_category():
    return 'TODO: Implement Functionality 3'


if __name__ == '__main__':
   app.run()
