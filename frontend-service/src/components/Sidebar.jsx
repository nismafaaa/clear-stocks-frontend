import React, { useState, useEffect } from 'react';

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
        const res = await fetch(`http://10.34.100.114:8002/fetch-dates?ticker=${selectedStock}`);
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
    <aside className="w-[250px] bg-dark-bg p-4 text-text-primary space-y-4 border-r border-dark-border">
      <h2 className="text-lg font-semi-bold text-text-primary">Settings</h2>

      <div>
        <label className="text-sm block mb-1 text-text-secondary">Select Stock</label>
        <select
          value={selectedStock || ""}
          onChange={(e) => setSelectedStock(e.target.value)}
          className="w-full p-2 rounded bg-dark-card text-text-primary border border-dark-border focus:border-primary focus:outline-none"
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
              className="w-full p-2 rounded bg-dark-card text-text-primary border border-dark-border focus:border-primary focus:outline-none calendar-white"
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
              className="w-full p-2 rounded bg-dark-card text-text-primary border border-dark-border focus:border-primary focus:outline-none calendar-white"
            />
          </div>
        </>
      )}

      <div>
        <label className="text-sm block mb-1 text-text-secondary">Forecast</label>
        <select
          value={forecastDays === 5 || forecastDays === 21 ? forecastDays : ""}
          onChange={e => setForecastDays(Number(e.target.value) || 0)}
          className="w-full p-2 rounded bg-dark-card text-text-primary border border-dark-border focus:border-primary focus:outline-none"
        >
          <option value="">Select prediction</option>
          <option value={5}>Predict 5 days ahead</option>
          <option value={21}>Predict 21 days ahead</option>
        </select>
      </div>
    </aside>
  );
}
