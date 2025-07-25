import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import NavBar from "./components/NavBar";

import Home from "./pages/Home";
import Movies from "./pages/Movies";
import Movie from "./pages/Movie";
import Crew from "./pages/Crew";
import Debug from "./pages/Debug";
import Page404 from "./pages/Page404";

import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/movies" element={<Movies />} />
        <Route path="/movies/*" element={<Movie />} />
        <Route path="/crew/*" element={<Crew />} />
        <Route path="/debug" element={<Debug />} />
        <Route path="/*" element={<Page404 />} />
      </Routes>
      <NavBar />
    </BrowserRouter>
  )
}
