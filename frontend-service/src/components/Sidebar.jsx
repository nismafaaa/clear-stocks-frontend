import React, { useState, useEffect } from 'react';

// Use environment variable with fallback
const API_BASE = process.env.REACT_APP_API_BASE;

const TICKERS = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'F', 'GOOG', 'PONY', 'QBTS', 'IONQ', 'META'];

export default function Sidebar({
  selectedStock,
  setSelectedStock,
  startDate,
  setStartDate,
  endDate,
  setEndDate,
  forecastDays,
  setForecastDays
}) {
  const [availableDates, setAvailableDates] = useState([]);

  // Fetch date range from API based on selectedStock
  useEffect(() => {
    if (!selectedStock) return;

    const fetchDates = async () => {
      try {
        const res = await fetch(`${API_BASE}/fetch-dates?ticker=${selectedStock}`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'true',
            'User-Agent': 'StockApp/1.0', // Add a custom user agent
            'X-Requested-With': 'XMLHttpRequest' // Additional header to bypass some protections
          },
          mode: 'cors', // Explicitly set CORS mode
          cache: 'no-store',
          credentials: 'omit' // Don't send credentials
        });

        if (!res.ok) {
          // Check if it's the ngrok abuse protection page
          const contentType = res.headers.get('content-type');
          if (contentType && contentType.includes('text/html')) {
            const htmlText = await res.text();
            if (htmlText.includes('ngrok') && htmlText.includes('abuse')) {
              console.error('ngrok abuse protection triggered');
              return;
            }
          }
          console.warn(`Bad response: ${res.status}`);
          return;
        }

        const result = await res.json();

        console.log("Raw dates response for", selectedStock, ":", result);

        const dates = result.dates;
        if (!Array.isArray(dates) || dates.length === 0) {
          console.warn("No valid dates in response for", selectedStock);
          return;
        }

        const sorted = [...dates].sort((a, b) => new Date(a) - new Date(b));
        setAvailableDates(sorted);
        setStartDate(sorted[0]);
        setEndDate(sorted.at(-1));
      } catch (err) {
        console.error("Failed to fetch date range:", err);
      }
    };

    fetchDates();
  }, [selectedStock, setStartDate, setEndDate]);

  const isReady = availableDates.length > 0;

  return (
    <aside className="w-[250px] bg-dark-bg p-4 text-text-primary space-y-4 border-r border-dark-border rounded-r-2xl">
      <h2 className="text-lg font-semi-bold text-text-primary">Settings</h2>

      <div>
        <label className="text-sm block mb-1 text-text-secondary">Select Stock</label>
        <select
          value={selectedStock || ""}
          onChange={(e) => setSelectedStock(e.target.value)}
          className="w-full p-2 rounded-xl bg-dark-card text-text-primary border border-dark-border focus:border-primary focus:outline-none"
        >
          <option value="" disabled>Select a stock</option>
          {TICKERS.map((ticker) => (
            <option key={ticker} value={ticker}>
              {ticker}
            </option>
          ))}
        </select>
      </div>

      {isReady && (
        <>
          <div>
            <label className="text-sm block mb-1 text-text-secondary">Start Date</label>
            <input
              type="date"
              value={startDate}
              min={availableDates[0]}
              max={endDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full p-2 rounded-xl bg-dark-card text-text-primary border border-dark-border focus:border-primary focus:outline-none calendar-white"
            />
          </div>

          <div>
            <label className="text-sm block mb-1 text-text-secondary">End Date</label>
            <input
              type="date"
              value={endDate}
              min={startDate}
              max={availableDates.at(-1)}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full p-2 rounded-xl bg-dark-card text-text-primary border border-dark-border focus:border-primary focus:outline-none calendar-white"
            />
          </div>
        </>
      )}

      <div>
        <label className="text-sm block mb-1 text-text-secondary">Forecast</label>
        <select
          value={forecastDays === 5 || forecastDays === 21 ? forecastDays : ""}
          onChange={e => setForecastDays(Number(e.target.value) || 0)}
          className="w-full p-2 rounded-xl bg-dark-card text-text-primary border border-dark-border focus:border-primary focus:outline-none"
        >
          <option value="">Select prediction</option>
          <option value={5}>Predict 5 days ahead</option>
          <option value={21}>Predict 21 days ahead</option>
        </select>
      </div>
    </aside>
  );
}
