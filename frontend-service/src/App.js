import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SplashScreen from './components/SplashScreen';
import MarketsScreen from './components/MarketsScreen';
import MainPanel from './components/MainPanel';
import './index.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SplashScreen />} />
        <Route path="/markets" element={<MarketsScreen />} />
        <Route path="/chart/:ticker" element={<MainPanel />} />
      </Routes>
    </Router>
  );
}

export default App;
