import React from "react";
import Header from "./components/Header";
import Footer from "./components/Footer";
import MainPanel from "./components/MainPanel";

export default function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1">
        <MainPanel />
      </main>
      <Footer />
    </div>
  );
}
