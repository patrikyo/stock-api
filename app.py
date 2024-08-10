from flask import Flask, jsonify
from flask_cors import CORS  
import yfinance as yf
import os  # Importera os för att läsa miljövariabler

app = Flask(__name__)

# Aktivera CORS för en specifik domän
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

@app.route('/api/stock/<ticker>', methods=['GET'])
def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        company_name = info.get("longName", "N/A")
        current_price = info.get("currentPrice", "N/A")
        return jsonify({
            "companyName": company_name,
            "currentPrice": current_price
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Läsa in port från miljövariabeln PORT, annars använd 5000 som standard
    port = int(os.environ.get("PORT", 5000))
    # Kör applikationen på alla nätverksgränssnitt, inte bara localhost
    app.run(host='0.0.0.0', port=port)
