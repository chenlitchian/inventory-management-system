# inventory-management-system

This repo holds the backend code for the inventory management system.


### Setup
To install the dependencies:
```
# setup and source the virtual env
python3 -m venv venv
. venv/bin/activate
# install using pip
pip install -r requirements.txt
```


create config.py file and copy your aws dynamo db access key
```
AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>
AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>
REGION_NAME=<REGION_NAME>
```


### Run

To run the server:
```
python3 main.py
```


### Deploy

To deploy to AWS lambda:
```
serverless deploy
```