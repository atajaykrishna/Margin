import MetaTrader5 as mt5
from flask import Flask, jsonify, render_template_string
import logging

app = Flask(__name__)

# Suppress Flask log messages
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

SYMBOL = 'XAUUSD.r'  # Use the correct symbol with suffix

# Function to fetch live price data
def fetch_live_prices(symbol):
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return {'error': 'No data'}
    return {
        'time': tick.time,
        'bid': tick.bid,
        'ask': tick.ask,
        'last': tick.last
    }

# Route to serve live price data
@app.route('/prices')
def prices():
    data = fetch_live_prices(SYMBOL)
    if 'error' in data:
        return jsonify({'error': 'Failed to fetch data'})
    return jsonify(data)

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Price Data</title>
    <script>
        function fetchPrices() {
            fetch('/prices')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('time').textContent = data.error;
                        document.getElementById('bid').textContent = '';
                        document.getElementById('ask').textContent = '';
                        document.getElementById('last').textContent = '';
                        return;
                    }
                    document.getElementById('time').textContent = new Date(data.time * 1000).toLocaleTimeString();
                    document.getElementById('bid').textContent = data.bid;
                    document.getElementById('ask').textContent = data.ask;
                    document.getElementById('last').textContent = data.last;
                })
                .catch(error => {
                    document.getElementById('time').textContent = 'Error fetching data';
                    console.error('Error fetching data:', error);
                });
        }

        setInterval(fetchPrices, 1000);  // Update every second
        window.onload = fetchPrices;  // Fetch initial data
    </script>
</head>
<body>
    <h1>Live Price Data for {{ symbol }}</h1>
    <p><strong>Time:</strong> <span id="time"></span></p>
    <p><strong>Bid:</strong> <span id="bid"></span></p>
    <p><strong>Ask:</strong> <span id="ask"></span></p>
    <p><strong>Last:</strong> <span id="last"></span></p>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, symbol=SYMBOL)

def run_server():
    # Start MetaTrader 5
    if not mt5.initialize():
        print("MetaTrader 5 initialization failed")
        mt5.shutdown()
        exit()
    
    # Run Flask server
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting...")
    finally:
        mt5.shutdown()
