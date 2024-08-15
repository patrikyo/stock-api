from flask import Flask, jsonify
from flask_cors import CORS  
import yfinance as yf
import os

app = Flask(__name__)

# Aktivera CORS för flera domäner
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://stock-fe.onrender.com"]}})

@app.route('/api/stock/<ticker>', methods=['GET'])
def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        company_name = info.get("longName", "N/A")
        current_price = info.get("currentPrice", "N/A")

        # Hämta dagens kursdata
        hist = stock.history(period="1d")
        if not hist.empty:
            open_price = hist['Open'][0]
            percent_change = ((current_price - open_price) / open_price) * 100
            percent_change = round(percent_change, 2)  # Begränsar till 3 decimaler

            # Hämta tidsstämpeln för den senaste datapunkten
            last_timestamp = hist.index[-1].strftime('%Y-%m-%d %H:%M:%S')
        else:
            open_price = "N/A"
            percent_change = "N/A"
            last_timestamp = "N/A"

        return jsonify({
            "companyName": company_name,
            "currentPrice": current_price,
            "percentChange": percent_change,
            "lastUpdated": last_timestamp  # Lägg till tidsstämpeln i responsen
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
