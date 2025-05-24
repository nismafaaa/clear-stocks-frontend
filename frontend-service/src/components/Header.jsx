import { useNavigate } from 'react-router-dom';
import logo from '../assets/logo.png'; 

export default function Header() {
  const navigate = useNavigate();
  
  return (
    <header className="bg-dark-bg text-text-primary py-4 px-6 shadow border-b border-dark-border">
      <div className="max-w-full w-full mx-auto flex items-center justify-between">
        <h1 
          className="text-2xl font-bold tracking-tight text-text-primary cursor-pointer flex items-center gap-2" 
          onClick={() => navigate('/markets')}
        >
          <img src={logo} alt="Clear Stocks Logo" className="w-8 h-8 inline-block align-middle" />
          Clear Stocks
        </h1>
        <span className="text-sm text-text-primary italic">Stay sharp. Trade smart.</span>
      </div>
    </header>
  );
}
