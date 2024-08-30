from flask import Flask, jsonify
from flask_cors import CORS  
import yfinance as yf
import os
from datetime import datetime
import pytz

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

        # Hämta kursdata med minutintervall för att få den senaste uppdateringen
        hist = stock.history(period="1d", interval="1m")
        if not hist.empty:
            open_price = hist['Open'][0]  # Detta är öppningspriset från börsdagen
            percent_change = ((current_price - open_price) / open_price) * 100
            percent_change = round(percent_change, 2)  # Begränsar till 2 decimaler

            # Hämta den senaste uppdateringstiden och konvertera till lokal tid
            last_timestamp_utc = hist.index[-1]  # Senaste datapunktens tid i UTC
            local_timezone = pytz.timezone("Europe/Stockholm")
            last_timestamp_local = last_timestamp_utc.tz_convert(local_timezone)  # Konvertera till lokal svensk tid
            last_timestamp = last_timestamp_local.strftime('%Y-%m-%d %H:%M:%S')
        else:
            open_price = "N/A"
            percent_change = "N/A"
            last_timestamp = "N/A"

        # Lägg till aktuell tidpunkt för när anropet gjordes (i svensk tid)
        current_time_local = datetime.now(pytz.timezone("Europe/Stockholm")).strftime('%Y-%m-%d %H:%M:%S')

        return jsonify({
            "companyName": company_name,
            "currentPrice": current_price,
            "percentChange": percent_change,
            "lastUpdated": last_timestamp,  # Tidpunkten för senaste datapunkt från yfinance
            "fetchTime": current_time_local  # Tidpunkten då detta anrop gjordes
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stock/<ticker>/metrics', methods=['GET'])
def get_stock_metrics(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Nyckeltal
        pe_ratio = info.get("trailingPE", "N/A")  # P/E-tal (Price/Earnings ratio)
        ps_ratio = info.get("priceToSalesTrailing12Months", "N/A")  # P/S-tal (Price/Sales ratio)
        peg_ratio = info.get("pegRatio", "N/A")  # PEG-tal (Price/Earnings to Growth ratio)
        pb_ratio = info.get("priceToBook", "N/A")  # P/B-tal (Price/Book ratio)
        dividend_yield = info.get("dividendYield", "N/A")  # Direktavkastning
        market_cap = info.get("marketCap", "N/A")  # Börsvärde

        return jsonify({
            "peRatio": pe_ratio,
            "psRatio": ps_ratio,
            "pegRatio": peg_ratio,
            "pbRatio": pb_ratio,
            "dividendYield": dividend_yield,
            "marketCap": market_cap
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
