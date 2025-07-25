import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import Home from "./pages/Home";
import Movies from "./pages/Movies";
import Movie from "./pages/Movie";
import Crew from "./pages/Crew";
import Page404 from "./pages/Page404";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/home">Home</Link>
      </nav>
      <Routes>
        <Route path="/home" element={<Home />} />
        <Route path="/movies" element={<Movies />} />
        <Route path="/movies/*" element={<Movie />} />
        <Route path="/crew/*" element={<Crew />} />
        <Route path="/*" element={<Page404 />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
