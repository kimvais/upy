import datetime
from decimal import Decimal

import boto3
import chalice
from boto3.dynamodb.conditions import Key
from chalice import NotFoundError

TABLE_NAME = 'temperatures'

app = chalice.Chalice(app_name="SaunaThermometer")

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
table = dynamodb.Table(TABLE_NAME)


@app.route("/", methods=["POST"])
def post_temperature():
    data = app.current_request.json_body
    data['temperature'] = Decimal(data['temperature'])
    table.put_item(Item=data)
    return chalice.Response(body='', status_code=204)


@app.route("/register/{sensor_id}")
def register(sensor_id):
    ret = dynamodb.meta.client.update_item(
        TableName=TABLE_NAME,
        Key={"sensor_id": "sensors", "timestamp": 0},
        # Key={"sensor_id": {"S": "sensors"}, "timestamp": {"N": 0}},
        UpdateExpression="ADD sensors :sensor_id",
        ExpressionAttributeValues={":sensor_id": {sensor_id}},
        ReturnValues="UPDATED_NEW",
    )
    return list(ret['Attributes']['sensors'])


@app.route("/sensors")
def sensor_list():
    def get_sensor_data(sensors):
        for sensor_id in sensors:
            r = table.get_item(Key=dict(sensor_id=sensor_id, timestamp=0))['Item']
            del r['timestamp']
            yield r
    ret = table.get_item(Key=dict(sensor_id="sensors", timestamp=0))
    print(ret)
    sensors = ret['Item']['sensors']

    return list(get_sensor_data(sensors))


@app.route("/temperature/{sensor_id}")
def get_temperature(sensor_id):
    kce = Key('sensor_id').eq(sensor_id)
    result = table.query(KeyConditionExpression=kce, ScanIndexForward=False, Limit=1)
    try:
        data = result['Items'][0]
    except IndexError:
        raise NotFoundError
    ts = data.pop("timestamp")
    data['timestamp'] = datetime.datetime.utcfromtimestamp(ts).isoformat()
    return data
