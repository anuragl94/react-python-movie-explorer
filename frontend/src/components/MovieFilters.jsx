import { useState } from "react";

// This component behaves like an uncontrolled component
export default function MovieFilters({ onChange }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [filters, setFilters] = useState({
    title: "",
    director: "",
    cast: "",
    genre: "",
    year: "",
  });
  return (
    <>
      <button className="filter-handle" onClick={() => setIsMenuOpen(true)}>
        <svg fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 971.986 971.986">
          <path d="M370.216,459.3c10.2,11.1,15.8,25.6,15.8,40.6v442c0,26.601,32.1,40.101,51.1,21.4l123.3-141.3 c16.5-19.8,25.6-29.601,25.6-49.2V500c0-15,5.7-29.5,15.8-40.601L955.615,75.5c26.5-28.8,6.101-75.5-33.1-75.5h-873 c-39.2,0-59.7,46.6-33.1,75.5L370.216,459.3z"></path>
        </svg>
      </button>
      <div className={`filter-panel w-80 ${isMenuOpen ? "" : "collapsed"}`}>
        <h4>Filters</h4>
        <button className="close-button" onClick={() => setIsMenuOpen(false)}>✕</button>
        <label>
          <div>Title</div>
          <input type="text" onChange={e => setFilters(f => ({ ...f, title: e.target.value }))}></input>
        </label>
        <label>
          <div>Director</div>
          <input type="text" onChange={e => setFilters(f => ({ ...f, director: e.target.value }))}></input>
        </label>
        <label>
          <div>Cast</div>
          <input type="text" onChange={e => setFilters(f => ({ ...f, cast: e.target.value }))}></input>
        </label>
        <label>
          <div>Genre</div>
          <input type="text" onChange={e => setFilters(f => ({ ...f, genre: e.target.value }))}></input>
        </label>
        <label>
          <div>Release year</div>
          <input type="number" onChange={e => setFilters(f => ({ ...f, year: e.target.value }))}></input>
        </label>
        <button onClick={() => onChange(filters)}>Apply</button>
      </div>
    </>
  );
}