from flask import Flask, request, jsonify, render_template, Response
import braintree
import logging
import time
import os
app = Flask(__name__)

# Setup logging test
logging.basicConfig(level=logging.INFO)

@app.route('/')
def hello_world():
    return 'Hello, World from my callback script!'

@app.route('/callback/paypal', methods=['POST'])
def paypal_callback():
    logging.info('PayPal Callback Received:')
    logging.info('Headers: %s', request.headers)
    logging.info('Payload: %s', request.json)
    logging.info('ID: %s', request.json['id'])
    logging.info('REF ID: %s', request.json['purchase_units'][0]['reference_id'])

    # JSON response to return
    response_data = {
        "id": request.json['id'],
        "purchase_units": [
            {
                "reference_id": request.json['purchase_units'][0]['reference_id'],
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

    logging.info('Response: %s', response_data)

    return jsonify(response_data), 200