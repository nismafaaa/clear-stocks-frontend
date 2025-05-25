import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';
import {
  XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart
} from 'recharts';

const API_BASE = "http://10.34.100.114:8002";

// List of tickers we want to track
const TICKERS = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'F', 'GOOG', 'PONY', 'QBTS', 'IONQ', 'META'];

const MarketsScreen = () => {
  const navigate = useNavigate();
  const [marketData, setMarketData] = useState({});
  const [marketSummary, setMarketSummary] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTicker, setSelectedTicker] = useState('AAPL');
  const [chartData, setChartData] = useState([]);
  const [marketSentiment, setMarketSentiment] = useState('Neutral');
  const [dataDate, setDataDate] = useState(''); // New state for the data date

  // Fetch data for all tickers
  useEffect(() => {
    const fetchAllStockData = async () => {
      setLoading(true);
      try {
        const promises = TICKERS.map(ticker => 
          fetch(`${API_BASE}/fetch-recent?ticker=${ticker}`)
            .then(res => res.json())
            .catch(err => {
              console.error(`Error fetching data for ${ticker}:`, err);
              return null; // Return null for failed requests
            })
        );
        
        const results = await Promise.all(promises);
        const stocksData = {};
        const summaryData = [];
        let latestDate = ''; // To store the latest date found

        results.forEach((data, index) => {
          const ticker = TICKERS[index];
          
          // Handle different data formats
          if (data && !Array.isArray(data) && data.close) {
            // Single object format
            console.log(`Processing single data object for ${ticker}:`, data);
            
            const price = parseFloat(data.close);
            const prevPrice = parseFloat(data.open);
            const changeValue = price - prevPrice;
            const changePercent = ((changeValue) / prevPrice) * 100;
                        
            // For single data point, generate a more realistic looking chart
            const dataPoints = [];
           
            let currentPrice = prevPrice;
            // Generate data points for each hour of trading
            for (let hour = 9; hour <= 16; hour++) {
              // Calculate price trend with more realistic movement
              const progress = (hour - 9) / 7; // Progress through trading day (0 to 1)
              const volatility = price * 0.005; // 0.5% volatility
              const randomChange = (Math.random() - 0.45) * volatility; // Slight bias in trend direction
              const trendComponent = (price - prevPrice) * progress; // Linear trend component
              
              currentPrice = prevPrice + trendComponent + randomChange;
              
              dataPoints.push({
                hour: hour,
                displayTime: `${hour}:00`, // Exact hour format
                value: currentPrice
              });
            }
            
            stocksData[ticker] = {
              price,
              changeValue,
              changePercent,
              data: dataPoints
            };
            
            summaryData.push({
              ticker,
              price,
              changeValue,
              changePercent
            });

            // Capture the date from the 'timestamp' field of the current data point
            if (data.timestamp) {
                latestDate = new Date(data.timestamp).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
            }

          } 
          // Check if data is an array with elements (for historical data, if your API ever returns it)
          else if (data && Array.isArray(data) && data.length > 0) {
            // Original array format handling
            // Get the most recent data point
            const latestData = data[data.length - 1];
            // Get previous day data for change calculation
            const previousData = data.length > 1 ? data[data.length - 2] : null;
            
            const price = parseFloat(latestData.close);
            const prevPrice = previousData ? parseFloat(previousData.close) : price;
            const changeValue = price - prevPrice;
            const changePercent = ((changeValue) / prevPrice) * 100;
            
            stocksData[ticker] = {
              price,
              changeValue,
              changePercent,
              data: data.map(d => ({
                // Use d.timestamp for date parsing if available, otherwise d.date
                date: new Date(d.timestamp || d.date).toLocaleDateString(), 
                value: parseFloat(d.close)
              }))
            };
            
            summaryData.push({
              ticker,
              price,
              changeValue,
              changePercent
            });

            // Capture the date from the 'timestamp' field of the latest data point in the array
            if (latestData.timestamp) {
                latestDate = new Date(latestData.timestamp).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
            }

          } else {
            console.warn(`No valid data for ${ticker}:`, data);
          }
        });
        
        console.log("Processed market data:", stocksData);
        console.log("Summary data:", summaryData);
        
        // Continue only if we have data
        if (summaryData.length > 0) {
          // Sort by percent change
          summaryData.sort((a, b) => b.changePercent - a.changePercent);
          
          // Determine market sentiment (simple approach)
          const positiveStocks = summaryData.filter(stock => stock.changePercent > 0);
          if (positiveStocks.length > summaryData.length / 2) {
            setMarketSentiment('Bullish');
          } else {
            setMarketSentiment('Bearish');
          }
          
          setMarketData(stocksData);
          setMarketSummary(summaryData);
          setDataDate(latestDate); // Set the retrieved date
          
          // Set chart data for the selected ticker
          if (stocksData[selectedTicker]) {
            setChartData(stocksData[selectedTicker].data);
          }
        } else {
          console.error("No valid market data was processed");
        }
      } catch (error) {
        console.error("Error fetching stock data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllStockData();
    
    // Update data every minute
    const intervalId = setInterval(fetchAllStockData, 60000);
    return () => clearInterval(intervalId);
  }, []);
  
  // Update chart data when selected ticker changes
  useEffect(() => {
    if (marketData[selectedTicker]) {
      setChartData(marketData[selectedTicker].data);
    }
  }, [selectedTicker, marketData]);
  
  const handleTickerClick = (ticker) => {
    setSelectedTicker(ticker);
    // You might want to fetch more detailed data here
  };
  
  const handleStockDetailsClick = (ticker) => {
    navigate(`/chart/${ticker}`);
  };

  // Find best and worst performing stocks
  const bestStock = marketSummary.length > 0 ? marketSummary[0] : null;
  const worstStock = marketSummary.length > 0 ? marketSummary[marketSummary.length - 1] : null;
  
  // Find market leader - for simplicity using the stock with highest price
  const leader = marketSummary.length > 0 ? 
    marketSummary.reduce((prev, current) => (prev.price > current.price) ? prev : current) 
    : null;

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
            <span className="text-text-primary text-lg">Loading market data...</span>
          </div>
        </div>
      )}

      <main className="flex-1 p-6 mt-16 mb-16">
        <div className="max-w-7xl mx-auto px-4">
          {/* Back button to SplashScreen */}
          <button
            type="button"
            className="mb-4 text-sm text-text-secondary hover:text-primary transition-colors"
            onClick={() => navigate('/')}
          >
            ← Back
          </button>
          <h1 className="text-3xl font-bold mb-6 text-text-primary">
            Markets Today {dataDate && <span className="text-text-secondary text-xl">({dataDate})</span>}
          </h1>
          
          {/* Insight Boxes */}
          <div className="mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-12 gap-y-4 w-full">
              {/* Market Sentiment */}
              <div className="bg-dark-card p-4 rounded-md border border-dark-border w-full">
                <div className="text-sm text-text-secondary mb-1">Market</div>
                <div className={`text-xl font-bold ${marketSentiment === 'Bullish' ? 'text-success' : 'text-danger'}`}>
                  {marketSentiment}
                </div>
              </div>
              {/* Market Leader */}
              {leader && (
                <div className="bg-dark-card p-4 rounded-md border border-dark-border w-full">
                  <div className="text-sm text-text-secondary mb-1">Leader</div>
                  <div className="text-xl font-bold text-text-primary">{leader.ticker}</div>
                </div>
              )}
              {/* Best Stock */}
              {bestStock && (
                <div className="bg-dark-card p-4 rounded-md border border-dark-border w-full">
                  <div className="text-sm text-text-secondary mb-1">Top Stock</div>
                  <div className="flex justify-between items-center">
                    <div className="text-xl font-bold text-text-primary">{bestStock.ticker}</div>
                    <div className="text-success">+{bestStock.changePercent.toFixed(2)}%</div>
                  </div>
                </div>
              )}
              {/* Worst Stock */}
              {worstStock && (
                <div className="bg-dark-card p-4 rounded-md border border-dark-border w-full">
                  <div className="text-sm text-text-secondary mb-1">Worst Stock</div>
                  <div className="flex justify-between items-center">
                    <div className="text-xl font-bold text-text-primary">{worstStock.ticker}</div>
                    <div className="text-danger">{worstStock.changePercent.toFixed(2)}%</div>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          <h2 className="text-2xl font-bold mb-4 text-text-primary">Market Summary</h2>
          
          <div className="flex flex-col md:flex-row space-y-6 md:space-y-0 md:space-x-6">
            {/* Stock List */}
            <div className="w-full md:w-1/3 bg-dark-card rounded-xl border border-dark-border p-4">
              <div className="flex justify-between pb-2 border-b border-dark-border mb-2">
                <div className="font-bold text-text-primary">Symbol</div>
                <div className="font-bold text-text-primary">Price</div>
                <div className="font-bold text-text-primary">% Change</div>
              </div>
              
              <div className="space-y-2 max-h-96 overflow-auto custom-scrollbar pr-2">
                {loading ? (
                  <p className="text-text-secondary text-center py-4">Loading market data...</p>
                ) : (
                  marketSummary.map(stock => (
                    <div 
                      key={stock.ticker} 
                      className={`flex justify-between py-2 px-1 cursor-pointer rounded hover:bg-dark-bg ${selectedTicker === stock.ticker ? 'bg-dark-bg' : ''}`}
                      onClick={() => handleTickerClick(stock.ticker)}
                    >
                      <div className="font-medium text-text-primary">{stock.ticker}</div>
                      <div className="text-text-primary">${stock.price.toFixed(2)}</div>
                      <div className={stock.changePercent >= 0 ? 'text-success' : 'text-danger'} style={{ marginRight: 6 }}>
                        {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
            
            {/* Chart for Selected Stock */}
            <div className="w-full md:w-2/3 bg-dark-card rounded-xl border border-dark-border p-4 flex flex-col">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-text-primary">{selectedTicker}</h3>
                <button 
                  onClick={() => handleStockDetailsClick(selectedTicker)}
                  className="text-sm text-text-secondary hover:text-primary transition-colors"
                >
                  View Details →
                </button>
              </div>
              
              <div className="flex-1 min-h-0">
                {chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                      data={chartData}
                      margin={{ top: 20, right: 30, left: 70, bottom: 10 }}
                    >
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
                      
                      <XAxis
                        dataKey="displayTime"
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
                        interval={0}
                        minTickGap={10}
                        height={50}
                        padding={{ left: 20, right: 0 }}
                      />
                      <YAxis
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
                        domain={['dataMin - 5', 'dataMax + 5']}
                        tickFormatter={(value) => `$${value.toFixed(2)}`}
                        width={100}
                      />
                      <Tooltip
                        contentStyle={{ 
                          backgroundColor: '#1A1A1A', 
                          borderColor: '#10B981', 
                          color: '#FFF',
                          borderRadius: '8px',
                          boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)'
                        }}
                        labelStyle={{ color: '#FFF' }}
                        itemStyle={{ color: '#10B981' }}
                      />
                      
                      {/* Area with gradient fill */}
                      <Area
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
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-text-secondary">
                    No chart data available for {selectedTicker}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
      
      <div className="fixed bottom-0 left-0 right-0 z-10">
        <Footer />
      </div>
    </div>
  );
};

export default MarketsScreen;