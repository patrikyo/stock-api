from flask import Flask, jsonify, request
from flask_cors import CORS  
import yfinance as yf
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Aktivera CORS för flera domäner
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://stock-fe.onrender.com"]}})

# Endpoint för att hämta aktieinformation
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
            percent_change = ((current_price - open_price) / open_price) * 100 if open_price != 0 else 0
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

# Hämta aktiens unika ID för blankningsdata
def get_stock_id(ticker):
    stock_ids = {
        "SBB-B.ST": "549300HX9MRFY47AH564",
        "SBB-D.ST": "549300HX9MRFY47AH564",
        "NIBE-B.ST": "549300ZQH0FIF1P0MX67",
        "NEOBO.ST": "213800QBPS3L89U9TZ44",
        "EVO.ST": "549300SUH6ZR1RF6TA88"
    }
    return stock_ids.get(ticker, "Unknown ID")  # Returnera "Unknown ID" om tickern inte finns i ordboken

# Funktion för att hämta blankningsdata baserat på aktiens unika ID
def fetch_short_selling_data_by_id(ticker):
    stock_id = get_stock_id(ticker)
    if stock_id == "Unknown ID":
        return {"error": "Unknown stock ticker"}
    
    url = f"https://www.fi.se/sv/vara-register/blankningsregistret/emittent/?id={stock_id}"
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Hämta första tabellen
    table = soup.find('table')
    
    if not table:
        return {"error": "Table not found"}

    # Hämta det andra <tr>-elementet i tabellen
    rows = table.find_all('tr')
    
    if len(rows) < 2:
        return {"error": "Not enough rows in the table"}

    # Hämta det andra <tr>-elementet och det andra <td>-elementet i den
    second_row = rows[1]
    second_td = second_row.find_all('td')[1]

    # Returnera värdet
    return {"value": second_td.text.strip()}

# Endpoint för att hämta aktiens nyckeltal och blankningsdata
@app.route('/api/stock/<ticker>/metrics', methods=['GET'])
def get_stock_metrics(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Nyckeltal
        market_cap = info.get("marketCap", "N/A")
        enterprise_value = info.get("enterpriseValue", "N/A")
        trailing_pe = info.get("trailingPE", "N/A")
        forward_pe = info.get("forwardPE", "N/A")
        peg_ratio = info.get("pegRatio", "N/A")
        ps_ratio = info.get("priceToSalesTrailing12Months", "N/A")
        pb_ratio = info.get("priceToBook", "N/A")
        ev_revenue = info.get("enterpriseToRevenue", "N/A")
        ev_ebitda = info.get("enterpriseToEbitda", "N/A")

        # Hämta blankningsdata
        short_selling_data = fetch_short_selling_data_by_id(ticker)
        if "error" in short_selling_data:
            short_selling_value = "N/A"
        else:
            short_selling_value = short_selling_data["value"]

        return jsonify({
            "marketCap": market_cap,
            "enterpriseValue": enterprise_value,
            "trailingPE": trailing_pe,
            "forwardPE": forward_pe,
            "pegRatio": peg_ratio,
            "psRatio": ps_ratio,
            "pbRatio": pb_ratio,
            "enterpriseValueRevenue": ev_revenue,
            "enterpriseValueEbitda": ev_ebitda,
            "shortSelling": short_selling_value  # Lägg till blankningsdata
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)  # Lägg till detta för att köra din Flask-app
