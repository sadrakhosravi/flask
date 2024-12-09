import json
from flask import jsonify, Flask, request

app = Flask(__name__)

@app.route('/health')
def health_check():
    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "healthy"
        }),
    }

# In-memory simulated cryptocurrency database
cryptos = {
    "BTC": {"name": "Bitcoin", "price": 50000, "market_cap": "1T"},
    "ETH": {"name": "Ethereum", "price": 3500, "market_cap": "500B"},
    "DOGE": {"name": "Dogecoin", "price": 0.25, "market_cap": "30B"}
}

# Define a simple health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"message": "Healthy"})

# Endpoint to get all cryptocurrencies
@app.route('/cryptos', methods=['GET'])
def get_cryptos():
    return jsonify(cryptos)

# GET endpoint: Fetch cryptocurrency details by symbol
@app.route('/crypto/<string:symbol>', methods=['GET'])
def get_crypto(symbol):
    symbol = symbol.upper()
    if symbol in cryptos:
        return jsonify({"symbol": symbol, **cryptos[symbol]})
    else:
        return jsonify({"error": f"Cryptocurrency with symbol '{symbol}' not found."}), 404

# POST endpoint: Add a new cryptocurrency
@app.route('/crypto', methods=['POST'])
def add_crypto():
    data = request.get_json()
    symbol = data.get("symbol", "").upper()
    name = data.get("name")
    price = data.get("price")
    market_cap = data.get("market_cap")

    if not symbol or not name or price is None or not market_cap:
        return jsonify({"error": "Missing 'symbol', 'name', 'price', or 'market_cap' in the request body."}), 400

    if symbol in cryptos:
        return jsonify({"error": f"Cryptocurrency with symbol '{symbol}' already exists."}), 400

    cryptos[symbol] = {"name": name, "price": price, "market_cap": market_cap}
    return jsonify({"message": f"Cryptocurrency '{symbol}' added successfully.", "crypto": cryptos[symbol]}), 201

# PUT endpoint: Update an existing cryptocurrency
@app.route('/crypto/<string:symbol>', methods=['PUT'])
def update_crypto(symbol):
    symbol = symbol.upper()
    if symbol not in cryptos:
        return jsonify({"error": f"Cryptocurrency with symbol '{symbol}' not found."}), 404

    data = request.get_json()
    price = data.get("price")
    market_cap = data.get("market_cap")

    if price is not None:
        cryptos[symbol]["price"] = price
    if market_cap is not None:
        cryptos[symbol]["market_cap"] = market_cap

    return jsonify({"message": f"Cryptocurrency '{symbol}' updated successfully.", "crypto": cryptos[symbol]})


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    with app.test_client() as client:
        # Create a request context with the event data
        method = event['httpMethod']
        path = event['path']
        headers = event.get('headers', {})
        body = event.get('body', None)
        if body:
            body = json.loads(body)

        response = client.open(
            path=path,
            method=method,
            headers=headers,
            json=body
        )

        return {
            "statusCode": response.status_code,
            "body": response.get_data(as_text=True),
            "headers": dict(response.headers)
        }

if __name__ == "__main__":
    app.run(debug=True)
