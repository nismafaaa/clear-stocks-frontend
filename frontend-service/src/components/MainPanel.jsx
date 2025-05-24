import React, { useEffect, useState, useMemo } from "react";
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from "./Sidebar";
import Header from "./Header";
import Footer from "./Footer";
import {
  ChartCanvas,
  Chart,
  CandlestickSeries,
  XAxis,
  YAxis,
  CrossHairCursor,
  MouseCoordinateX,
  MouseCoordinateY,
  BarSeries,
} from "react-financial-charts";
import {
  LineChart as SimpleLineChart,
  Line as SimpleLine,
  XAxis as SimpleXAxis,
  YAxis as SimpleYAxis,
  Tooltip as SimpleTooltip,
  ResponsiveContainer as SimpleResponsiveContainer,
  AreaChart as SimpleAreaChart,
  Area as SimpleArea,
} from "recharts";
import { format } from "d3-format";
import { timeFormat } from "d3-time-format";
import { scaleTime } from "d3-scale";

const API_BASE = "http://10.34.100.114:8002";

export default function MainPanel() {
  const { ticker } = useParams(); // Get ticker from URL params
  const navigate = useNavigate();
  const [selectedStock, setSelectedStock] = useState(ticker || "AAPL");
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [forecastDays, setForecastDays] = useState(0); // Set initial value to 0 (neither selected)
  const [historicalData, setHistoricalData] = useState([]);
  const [forecastData, setForecastData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistorical = async () => {
      if (!selectedStock || !startDate || !endDate) return;

      setLoading(true);
      try {
        const res = await fetch(
          `${API_BASE}/fetch-historical?ticker=${selectedStock}&start_date=${startDate}&end_date=${endDate}`
        );
        const data = await res.json();
        setHistoricalData(data);
      } catch (err) {
        console.error("Error fetching historical data:", err);
        setHistoricalData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchHistorical();
  }, [selectedStock, startDate, endDate]);

  // Fetch forecast data for AAPL when 5 days is selected
  useEffect(() => {
    if (selectedStock === "AAPL" && forecastDays === 5) {
      console.log("Fetching forecast data for AAPL");
      fetch(`${API_BASE}/fetch-recent-weekly-predict?ticker=test2`)
        .then(res => res.json())
        .then(data => {
          console.log("Raw forecast data:", data);
          
          // Process the forecast data structure properly
          const processedData = Array.isArray(data)
            ? data.map(d => ({
                date: d.timestamp || "",
                // Use close_predict instead of value or close
                value: parseFloat(d.close_predict) || 0 
              }))
            : [];
          
          console.log("Processed forecast data:", processedData);
          setForecastData(processedData);
        })
        .catch(err => {
          console.error("Error fetching forecast data:", err);
          setForecastData([]);
        });
    } else {
      setForecastData([]);
    }
  }, [selectedStock, forecastDays]);

  // Extract insights from historical data
  const insights = useMemo(() => {
    if (!historicalData || historicalData.length === 0) return null;

    const closes = historicalData.map((d) => d.close);
    const volumes = historicalData.map((d) => d.volume);
    const highs = historicalData.map((d) => d.high);
    const lows = historicalData.map((d) => d.low);
    const opens = historicalData.map((d) => d.open);

    const average = (arr) =>
      arr.reduce((sum, val) => sum + val, 0) / arr.length;

    // Calculate percentage change from first open to last close
    const firstOpen = opens[0];
    const lastClose = closes[closes.length - 1];
    const percentChange = ((lastClose - firstOpen) / firstOpen) * 100;

    return {
      highestClose: Math.max(...closes),
      lowestClose: Math.min(...closes),
      avgClose: average(closes).toFixed(2),
      totalVolume: volumes.reduce((a, b) => a + b, 0).toLocaleString(),
      highestPrice: Math.max(...highs),
      lowestPrice: Math.min(...lows),
      percentChange: percentChange.toFixed(2),
    };
  }, [historicalData]);

  // Format data for candlestick chart - improved with better logging
  const formattedData = useMemo(() => {
    if (!historicalData || historicalData.length === 0) {
      console.log("No historical data available");
      return [];
    }

    console.log("Processing historical data:", historicalData.slice(0, 2));

    const processed = historicalData
      .filter((d) => {
        // Check for either date or timestamp field and not null
        if (!d || (!d.date && !d.timestamp)) {
          console.log("Filtered out entry with no date or timestamp:", d);
          return false;
        }
        return true;
      })
      .map((d) => {
        // Use timestamp field if date is not available
        const dateString = d.date || d.timestamp;
        const dateObj = new Date(dateString);

        const item = {
          date: dateObj,
          open: +d.open,
          high: +d.high,
          low: +d.low,
          close: +d.close,
          volume: +d.volume,
        };

        if (isNaN(dateObj.getTime())) {
          console.log("Invalid date:", dateString, d);
          return null;
        }

        return item;
      })
      .filter((d) => {
        if (!d || !(d.date instanceof Date) || isNaN(d.date.getTime())) {
          console.log("Filtered out entry with invalid date:", d);
          return false;
        }
        return true;
      })
      .sort((a, b) => a.date - b.date);

    console.log("Processed data length:", processed.length);
    if (processed.length > 0) {
      console.log("First processed item:", processed[0]);
      console.log("Last processed item:", processed[processed.length - 1]);
    }

    return processed;
  }, [historicalData]);

  // Add debugging for data flow - moved after formattedData is defined
  useEffect(() => {
    console.log("Historical data:", historicalData);
    console.log("Formatted data:", formattedData);
  }, [historicalData, formattedData]);

  // Update selected stock when URL param changes
  useEffect(() => {
    if (ticker) {
      setSelectedStock(ticker);
    }
  }, [ticker]);

  return (
    <div className="flex flex-col min-h-screen bg-dark-bg">
      <div className="fixed top-0 left-0 right-0 z-10">
        <Header />
      </div>

      {/* Loading overlay */}
      {loading && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60">
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
            <span className="text-text-primary text-lg">Loading data...</span>
          </div>
        </div>
      )}

      <div className="flex flex-1 mt-16 mb-16">
        <Sidebar
          selectedStock={selectedStock}
          setSelectedStock={(newStock) => {
            setSelectedStock(newStock);
            navigate(`/chart/${newStock}`);
          }}
          startDate={startDate}
          setStartDate={setStartDate}
          endDate={endDate}
          setEndDate={setEndDate}
          forecastDays={forecastDays}
          setForecastDays={setForecastDays}
        />

        <div className="flex-1 p-6 space-y-6 bg-dark-bg">
          {/* Back button */}
          <button 
            onClick={() => navigate('/markets')}
            className="mb-4 flex items-center text-text-secondary hover:text-primary"
          >
            <span className="mr-1">←</span> Back to Markets
          </button>

          <h1 className="text-3xl font-bold text-center text-text-primary">
            What's Up with {selectedStock}? 📈
          </h1>

          {loading ? (
            <p className="text-center text-text-primary">Loading data...</p>
          ) : (
            <>
              {/* ⚡️Market Insights Cards */}
              {insights && (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-7 gap-7">
                  <div className="bg-dark-card p-2 rounded-md border border-dark-border shadow-blue-glow min-w-[120px]">
                    <div className="text-xs text-text-secondary">Highest Close</div>
                    <div className="text-text-primary font-bold">${insights.highestClose}</div>
                  </div>
                  <div className="bg-dark-card p-2 rounded-md border border-dark-border shadow-blue-glow min-w-[120px]">
                    <div className="text-xs text-text-secondary">Lowest Close</div>
                    <div className="text-text-primary font-bold">${insights.lowestClose}</div>
                  </div>
                  <div className="bg-dark-card p-2 rounded-md border border-dark-border shadow-blue-glow min-w-[120px]">
                    <div className="text-xs text-text-secondary">Average Close</div>
                    <div className="text-text-primary font-bold">${insights.avgClose}</div>
                  </div>
                  <div className="bg-dark-card p-2 rounded-md border border-dark-border shadow-blue-glow min-w-[120px]">
                    <div className="text-xs text-text-secondary">Highest Price</div>
                    <div className="text-text-primary font-bold">${insights.highestPrice}</div>
                  </div>
                  <div className="bg-dark-card p-2 rounded-md border border-dark-border shadow-blue-glow min-w-[120px]">
                    <div className="text-xs text-text-secondary">Lowest Price</div>
                    <div className="text-text-primary font-bold">${insights.lowestPrice}</div>
                  </div>
                  <div className="bg-dark-card p-2 rounded-md border border-dark-border shadow-blue-glow min-w-[120px]">
                    <div className="text-xs text-text-secondary">% Change</div>
                    <div className={insights.percentChange >= 0 ? "text-success font-bold" : "text-danger font-bold"}>
                      {insights.percentChange >= 0 ? "+" : ""}{insights.percentChange}%
                    </div>
                  </div>
                  <div className="bg-dark-card p-2 rounded-md border border-dark-border shadow-blue-glow min-w-[120px]">
                    <div className="text-xs text-text-secondary">Total Volume</div>
                    <div className="text-text-primary font-bold">{insights.totalVolume}</div>
                  </div>
                </div>
              )}

              {/* Candlestick Chart */}
              <div className="bg-dark-card p-4 pb-8 pt-8 rounded-xl border border-dark-border shadow-blue-glow mb-16">
                <h2 className="text-lg font-semibold mb-6 text-text-primary">
                  {selectedStock} Historical Prices ({startDate} to {endDate})
                </h2>
                {formattedData.length > 0 ? (
                  <div className="flex justify-center items-center" style={{ height: 500 }}>
                    <ChartCanvas
                      height={460}
                      width={window.innerWidth - 330}
                      ratio={1}
                      margin={{ left: 50, right: 50, top: 30, bottom: 30 }}
                      data={formattedData}
                      seriesName={selectedStock}
                      xAccessor={(d) => d?.date ?? null}
                      xScale={scaleTime()}
                      xExtents={
                        formattedData.length > 0
                          ? [
                              formattedData[0].date,
                              formattedData[formattedData.length - 1].date,
                            ]
                          : []
                      }
                      clamp={false}
                      pointsPerPxThreshold={1}
                      minPointsPerPxThreshold={0.001}
                    >
                      {/* Main price chart */}
                      <Chart 
                        id={1} 
                        yExtents={(d) => [d.high * 1.05, d.low * 0.95]}
                        height={320} 
                        padding={{ top: 10, bottom: 20 }}
                      >
                        <XAxis
                          axisAt="bottom"
                          orient="bottom"
                          ticks={6}
                          stroke="#FFFFFF"
                          tickStroke="#FFFFFF"
                          tickLabelFill="#FFFFFF"
                          fontFamily="Poppins, sans-serif"
                          fontSize={12}
                          fontWeight="normal"
                        />
                        
                        <YAxis
                          axisAt="right"
                          orient="right"
                          ticks={5}
                          stroke="#FFFFFF"
                          tickStroke="#FFFFFF"
                          tickLabelFill="#FFFFFF"
                          fontFamily="Poppins, sans-serif"
                          fontSize={12}
                          fontWeight="normal"
                        />

                        <MouseCoordinateX
                          at="bottom"
                          orient="bottom"
                          displayFormat={timeFormat("%Y-%m-%d")}
                          fill="#1A1A1A"
                          textFill="white"
                        />
                        <MouseCoordinateY
                          at="right"
                          orient="right"
                          displayFormat={format(".2f")}
                          fill="#1A1A1A"
                          textFill="white"
                        />

                        <CandlestickSeries
                          wickStroke={(d) =>
                            d.close > d.open ? "#10B981" : "#EF4444"
                          }
                          fill={(d) => (d.close > d.open ? "#10B981" : "#EF4444")}
                          stroke={(d) =>
                            d.close > d.open ? "#10B981" : "#EF4444"
                          }
                          opacity={1}
                        />
                      </Chart>
                      
                      {/* Volume chart */}
                      <Chart 
                        id={2}
                        yExtents={(d) => d.volume}
                        height={100}
                        origin={(w, h) => [0, 330]} /* Fixed position below price chart */
                        padding={{ top: 15, bottom: 10 }}
                      >
                        <YAxis
                          axisAt="right"
                          orient="right"
                          ticks={4}
                          stroke="#FFFFFF"
                          tickStroke="#FFFFFF"
                          tickLabelFill="#FFFFFF"
                          tickFormat={format(".2s")}
                          fontFamily="Poppins, sans-serif"
                          fontSize={10}
                          fontWeight="normal"
                        />
                        
                        <MouseCoordinateY
                          at="right"
                          orient="right"
                          displayFormat={format(".4s")}
                          fill="#1A1A1A"
                          textFill="white"
                        />
                        
                        <BarSeries
                          yAccessor={(d) => d.volume}
                          fill={(d) => d.close > d.open ? "rgba(16, 185, 129, 0.5)" : "rgba(239, 68, 68, 0.5)"}
                          opacity={0.5}
                        />
                      </Chart>
                      
                      <CrossHairCursor stroke="#FFFFFF" />
                    </ChartCanvas>
                  </div>
                ) : (
                  <div>
                    <p className="text-text-secondary">No chart data available.</p>
                    <pre className="text-xs text-text-secondary mt-2">
                      Debug: Has data:{" "}
                      {historicalData.length > 0 ? "Yes" : "No"}, Formatted data:{" "}
                      {formattedData.length}
                    </pre>
                  </div>
                )}
              </div>
              {/* Forecast Line Chart for AAPL 5 days */}
              {selectedStock === "AAPL" && forecastDays === 5 && forecastData.length > 0 && (
                <div className="bg-dark-card p-4 rounded-xl border border-dark-border shadow-blue-glow mb-16">
                  <h2 className="text-lg font-semibold mb-6 text-text-primary">
                    {selectedStock} 5-Day Forecast
                  </h2>
                  <div className="w-full h-80">
                    <SimpleResponsiveContainer width="100%" height="100%">
                      <SimpleAreaChart data={forecastData} margin={{ top: 20, right: 30, left: 70, bottom: 10 }}>
                        <defs>
                          {/* Main area gradient with electric blue (#2563EB) and more subtle stops */}
                          <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#2563EB" stopOpacity={0.25}/>
                            <stop offset="50%" stopColor="#2563EB" stopOpacity={0.10}/>
                            <stop offset="100%" stopColor="#2563EB" stopOpacity={0}/>
                          </linearGradient>
                          
                          {/* Glow effect filter */}
                          <filter id="glow">
                            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                            <feMerge> 
                              <feMergeNode in="coloredBlur"/>
                              <feMergeNode in="SourceGraphic"/>
                            </feMerge>
                          </filter>
                          
                          {/* Shadow filter */}
                          <filter id="dropshadow" x="-20%" y="-20%" width="140%" height="140%">
                            <feDropShadow dx="0" dy="4" stdDeviation="8" floodColor="#2563EB" floodOpacity="0.15"/>
                          </filter>
                        </defs>
                        
                        <SimpleXAxis
                          dataKey="date"
                          stroke="#B0B0B0"
                          tick={{
                            fill: '#B0B0B0',
                            fontSize: 12,
                            fontWeight: 100, 
                            fontFamily: 'Poppins, sans-serif',
                            dy: 10
                          }}
                          tickLine={false}
                          axisLine={false}
                        />
                        <SimpleYAxis
                          stroke="#B0B0B0"
                          tick={{
                            fill: '#B0B0B0',
                            fontSize: 12,
                            fontWeight: 100, 
                            fontFamily: 'Poppins, sans-serif',
                            dx: -10
                          }}
                          tickLine={false}
                          axisLine={false}
                          domain={['dataMin - 1', 'dataMax + 1']}
                          tickFormatter={(value) => `$${value.toFixed(2)}`}
                          width={70}
                        />
                        <SimpleTooltip
                          contentStyle={{ 
                            backgroundColor: '#1A1A1A', 
                            borderColor: '#10B981', 
                            color: '#FFF',
                            borderRadius: '8px',
                            boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)'
                          }}
                          labelStyle={{ color: '#FFF' }}
                          itemStyle={{ color: '#10B981' }}
                          formatter={(value) => [`$${value.toFixed(2)}`, "Price"]}
                          labelFormatter={(date) => `Forecast: ${date}`}
                        />
                        
                        {/* Area with gradient fill */}
                        <SimpleArea
                          type="monotone"
                          dataKey="value"
                          stroke="#2563EB"
                          strokeWidth={3}
                          fill="url(#areaGradient)"
                          fillOpacity={1}
                          dot={false}
                          activeDot={{ 
                            r: 6, 
                            fill: '#2563EB', 
                            stroke: '#fff', 
                            strokeWidth: 2,
                            filter: "url(#glow)"
                          }}
                          isAnimationActive={true}
                          filter="url(#dropshadow)"
                        />
                      </SimpleAreaChart>
                    </SimpleResponsiveContainer>
                  </div>
                </div>
              )}
              {/* Add extra space below the chart */}
              <div className="h-12" />
            </>
          )}
        </div>
      </div>
      
      <div className="fixed bottom-0 left-0 right-0 z-10">
        <Footer />
      </div>
    </div>
  );
}