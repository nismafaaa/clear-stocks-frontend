export default function Footer() {
  return (
    <footer className="bg-dark-bg text-text-secondary text-center text-sm py-4 mt-auto border-t border-dark-border">
      <div className="max-w-7xl mx-auto">
        © {new Date().getFullYear()} Clear Stocks. Made with 💻 + ☕ + chaos by Kelompok 1.<br />
        This ain’t Wall Street. DYOR. NFA. Good luck out there 🚀
      </div>
    </footer>
  );
}
