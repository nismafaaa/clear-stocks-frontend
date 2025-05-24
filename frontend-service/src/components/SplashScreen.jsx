import React from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../assets/logo.png'; // or logo.svg

const SplashScreen = () => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    navigate('/markets');
  };

  return (
    <div className="flex flex-col min-h-screen bg-dark-bg relative overflow-hidden">
      <div 
        className="flex-1 flex flex-col justify-center items-center cursor-pointer relative z-10"
        onClick={handleClick}
      >
        <div className="text-center p-8 mb-8 relative">
          {/* Blue gradient shadow directly behind logo, name, and secondary text */}
          <div
            className="pointer-events-none absolute left-1/2 -translate-x-1/2 top-1/2 -translate-y-1/2 w-[420px] h-60"
            style={{
              background: 'radial-gradient(ellipse at center, rgba(37,99,235,0.35) 0%, rgba(37,99,235,0.10) 60%, transparent 100%)',
              filter: 'blur(32px)',
              zIndex: 0,
            }}
          />
          <div className="relative z-10">
            <div className="mb-6">
              <img src={logo} alt="Clear Stocks Logo" className="w-16 h-16 mx-auto" />
              <h1 className="text-5xl font-bold text-text-primary mt-4">Clear Stocks</h1>
            </div>
            <p className="text-xl text-text-secondary mb-10 max-w-2xl mx-auto">
              Whether you’re a curious newbie or a lowkey market nerd,<br />
              we’ve got the tools to help you invest like you mean it.
            </p>
          </div>
          <div className="mt-16 animate-pulse relative z-10">
            <p className="text-text-secondary italic">Click anywhere to continue</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SplashScreen;
