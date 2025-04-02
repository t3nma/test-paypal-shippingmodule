from flask import Flask, request, jsonify, render_template, Response
import braintree
import logging
import time
import os
import random

app = Flask(__name__)

# Setup logging test
logging.basicConfig(level=logging.INFO)

@app.route('/')
def hello_world():
    return 'Hello, World from my callback script!'

@app.route('/return')
def success():
    return 'Return URL called!'

@app.route('/cancel')
def cancel():
    return 'Cancel URL called!'

def create_option(id, is_selected):
    return {
        "id": str(id),
        "amount": {
            "currency_code": "USD",
            "value": "{:.2f}".format(random.randrange(10,1000)/100)
        },
        "type": "SHIPPING",
        "label": "Free Shipping" if id == 0 else "Shipping option " + str(id),
        "selected": is_selected
    }

def get_success_response(request):
    number_options = random.randint(1,3)
    selected_option = random.randint(0,number_options)
    selected_amount = None

    options = []
    for i in range(number_options):
        option = create_option(i, i == selected_option)
        if option["selected"] == True:
            selected_amount = float(option["amount"]["value"])
        options.append(option)

    return {
        "id": request['id'],
        "purchase_units": [
            {
                "reference_id": request['purchase_units'][0]['reference_id'],
                "amount": {
                    "currency_code": "USD",
                    "value": "{:.2f}".format(105.0 + selected_amount),
                    "breakdown": {
                        "item_total": {"currency_code": "USD", "value": "100.00"},
                        "tax_total": {"currency_code": "USD", "value": "5.00"},
                        "shipping": {"currency_code": "USD", "value": "{:.2f}".format(selected_amount)}
                    }
                },
                "shipping_options": options
            }
        ]
    }

@app.route('/callback/paypal', methods=['POST'])
def paypal_callback():
    logging.info('PayPal Callback Received:')
    logging.info('Headers: %s', request.headers)
    logging.info('Payload: %s', request.json)

    mode = os.environ.get("MODE")
    response = None

    if mode == 'SUCCESS':
        response = get_success_response(request.json)
    else:
        logging.info('Unknown mode!')
        return 'bad request!', 400

    logging.info('Response: %s', response)
    return jsonify(response), 200