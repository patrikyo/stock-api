from flask import Flask, jsonify
from flask_cors import CORS  # Importera flask-cors
import yfinance as yf

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
    app.run(debug=True)
