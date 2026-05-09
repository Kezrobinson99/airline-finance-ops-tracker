# Airline Finance & Operations Tracker V4 - Live Fuel Pricing

This is the updated build with live-style fuel/oil price tracking.

## What V4 Adds

- Fuel Market page
- Manual fuel/oil price updates
- Mock live market update button for testing
- Oil/jet fuel price conversion into GBP per kg
- New flights automatically use the latest fuel price
- Old flight logs keep the price used at the time
- Random delays and delay costs remain active
- Flight map, flight board, buying page and financial year P&L remain included

## Start Backend on Windows

```bat
cd airline-finance-ops-tracker-v4-live-fuel\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend docs:

```txt
http://127.0.0.1:8000/docs
```

## Start Frontend on Windows

Open another Command Prompt:

```bat
cd airline-finance-ops-tracker-v4-live-fuel\frontend
npm install
npm run dev
```

Open:

```txt
http://localhost:5173
```

## Important Upgrade Note

If you used an older version, delete the old SQLite database before running this one:

```txt
backend\airline_tracker.db
```

## Real API Later

The app currently has a mock live market update button, because real oil/fuel APIs need an API key. The backend is ready for replacing the mock function with OilPriceAPI, EIA, Alpha Vantage, or another fuel/oil data provider.

## Fuel Formula Used

```txt
jet fuel USD/barrel ÷ 42 gallons ÷ 3.04 kg per gallon × USD to GBP × airline margin = GBP/kg
```

Example:

```txt
$181.22/bbl ÷ 42 ÷ 3.04 × 0.79 × 1.08 = about £1.12/kg
```


## V5 Additions

- Hub market filters by selected airline.
- Regal only sees hubs it does not already own. If Regal owns TPA/LAS, they are not offered.
- Custom route pricing: type routes like `MAN - JFK`, price them, then buy them.
- Bought routes appear on the Routes page.
- Routes page now lets you assign/change the route aircraft type, for example changing MAN-JFK to A350-1000.
- Delete `backend\airline_tracker.db` before running V5 if you are upgrading from an older build.
"# airline-finance-ops-tracker" 
