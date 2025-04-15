from flask import Flask, request, jsonify, render_template, Response
import braintree
import logging
import time
import os
import random
import time

app = Flask(__name__)

# global variables for error scenario
errors = [
        "ADDRESS_ERROR",
        "COUNTRY_ERROR",
        "STATE_ERROR",
        "ZIP_ERROR",
        "METHOD_UNAVAILABLE",
        "STORE_UNAVAILABLE"
    ]

# global variables for 2-step scenarios
scenario_state = 0

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
        "id": str(id+1),
        "amount": {
            "currency_code": "USD",
            "value": "0.00" if id == 0 else "{:.2f}".format(random.randrange(10,1000)/100)
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
    for i in range(number_options+1):
        option = create_option(i, i == selected_option)
        if option["selected"] == True:
            selected_amount = float(option["amount"]["value"])
        options.append(option)

    result = {
        "id": request['id'],
        "purchase_units": [
            {
                "reference_id": request['purchase_units'][0]['reference_id'],
                "items": [
                    {
                        "name": "T-Shirt",
                        "unit_amount":
                        {
                            "currency_code": "USD",
                            "value": "50.00"
                        },
                        "quantity": "1"
                    },
                    {
                        "name": "Shoes",
                        "unit_amount":
                            {
                                "currency_code": "USD",
                                "value": "25.00"
                            },
                        "quantity": "2"
                    }
                ],
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

    logging.info('Response: %s', result)
    return jsonify(result), 200

def get_success_items_response(request):
    number_options = random.randint(1,3)
    selected_option = random.randint(0,number_options)
    selected_amount = None

    options = []
    for i in range(number_options+1):
        option = create_option(i, i == selected_option)
        if option["selected"] == True:
            selected_amount = float(option["amount"]["value"])
        options.append(option)

    result = {
        "id": request['id'],
        "purchase_units": [
            {
                "reference_id": request['purchase_units'][0]['reference_id'],
                "items": [
                    {
                        "name": "T-Shirt",
                        "unit_amount":
                        {
                            "currency_code": "USD",
                            "value": "50.00"
                        },
                        "quantity": "1"
                    }
                ],
                "amount": {
                    "currency_code": "USD",
                    "value": "{:.2f}".format(55.0 + selected_amount),
                    "breakdown": {
                        "item_total": {"currency_code": "USD", "value": "50.00"},
                        "tax_total": {"currency_code": "USD", "value": "5.00"},
                        "shipping": {"currency_code": "USD", "value": "{:.2f}".format(selected_amount)}
                    }
                },
                "shipping_options": options
            }
        ]
    }

    logging.info('Response: %s', result)
    return jsonify(result), 200

def get_error_response():
    result = {
        "name": "UNPROCESSABLE_ENTITY",
        "details": [{
            "issue": errors[random.randint(0, len(errors)-1)]
        }]
    }

    logging.info('Response: %s', result)
    return jsonify(result), 422

def get_fatal_response():
    return 'internal server error!', 500

def get_timeout_response(request):
    timeout_seconds = int(os.environ.get("TIMEOUT"))
    logging.info("Sleeping for {:d} seconds...".format(timeout_seconds))
    time.sleep(timeout_seconds)
    logging.info('AWAKE!')
    return get_success_response(request)

@app.route('/callback/paypal', methods=['POST'])
def paypal_callback():
    global scenario_state

    logging.info('PayPal Callback Received:')
    logging.info('Headers: %s', request.headers)
    logging.info('Payload: %s', request.json)

    # mode = os.environ.get("MODE")
    mode = request.json['purchase_units'][0]['reference_id']

    if mode == 'FAILFAST':
        return get_timeout_response(request.json)

    if mode == 'SUCCESS' or scenario_state == 0:
        scenario_state = 1
        return get_success_response(request.json)

    if mode == 'ITEMS':
        return get_success_items_response(request.json)
    if mode == 'ERROR':
        return get_error_response()
    elif mode == 'FATAL':
        return get_fatal_response()
    elif mode == 'TIMEOUT':
        return get_timeout_response(request.json)
    else:
        return 'bad request!', 400