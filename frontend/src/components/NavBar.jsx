import { useState } from "react";
import { Link } from "react-router";

export default function NavBar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  return (
    <>
      <button className="nav-handle" onClick={() => setIsMenuOpen(true)}>
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 18L20 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"></path>
          <path d="M4 12L20 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"></path>
          <path d="M4 6L20 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"></path>
        </svg>
      </button>
      <nav className={isMenuOpen ? "" : "collapsed"}>
        <button className="close-button" onClick={() => setIsMenuOpen(false)}>✕</button>
        <Link to="/">Home</Link>
        <Link to="/movies">Movies</Link>
        <Link to="/debug">Debug</Link>
      </nav>
    </>
  );
}
