from flask import Flask, request, jsonify, render_template, Response
import braintree
import logging
import time
import os
import random

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

error_state = 0

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

def get_orcun_response(request):
    return {
        "id": request['id'],
        "purchase_units": [
            {
                "reference_id": request['purchase_units'][0]['reference_id'],
                "amount": {
                    "currency_code": "USD",
                    "value": "105.00",
                    "breakdown": {
                        "item_total": {"currency_code": "USD", "value": "100.00"},
                        "tax_total": {"currency_code": "USD", "value": "5.00"},
                        "shipping": {"currency_code": "USD", "value": "0.00"}
                    }
                },
                "shipping_options": [
                    {
                        "id": "1",
                        "amount": {"currency_code": "USD", "value": "0.00"},
                        "type": "SHIPPING",
                        "label": "Free Shipping",
                        "selected": True
                    },
                    {
                        "id": "2",
                        "amount": {"currency_code": "USD", "value": "10.00"},
                        "type": "SHIPPING",
                        "label": "USPS Priority Shipping",
                        "selected": False
                    },
                    {
                        "id": "3",
                        "amount": {"currency_code": "USD", "value": "10.00"},
                        "type": "SHIPPING",
                        "label": "1-Day Shipping",
                        "selected": False
                    }
                ]
            }
        ]
    }

def get_error_response(request):
    global error_state

    if error_state == 0:
        error_state = 1
        return get_success_response(request)

    error_state = 0

    return {
        "name": "UNPROCESSABLE_ENTITY",
        "details": [{
            "issue": errors[random.randint(0, len(errors)-1)]
        }]
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
    elif mode == 'ERROR':
        response = get_error_response(request.json)
    elif mode == 'ORCUN':
        response = get_orcun_response(request.json)
    else:
        logging.info('Unknown mode!')
        return 'bad request!', 400

    logging.info('Response: %s', response)
    return jsonify(response), 200 if response.get("id") is not None else 422