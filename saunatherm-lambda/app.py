from decimal import Decimal

import boto3
import chalice

app = chalice.Chalice(app_name="SaunaThermometer")

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
table = dynamodb.Table('temperatures')


@app.route("/", methods=["POST"])
def post_temperature():
    data = app.current_request.json_body
    data['temperature'] = Decimal(data['temperature'])
    table.put_item(Item=data)
    return chalice.Response(body='', status_code=204)
