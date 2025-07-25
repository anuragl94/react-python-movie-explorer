import { useEffect, useState } from "react";
import { listMovies } from "../models/movie";
import MovieFilters from "../components/MovieFilters";
import Gallery from "../components/Gallery";

export default function Movies() {
  const [movies, setMovies] = useState([]);
  const [filters, setFilters] = useState({
    title: "",
    director: "",
    cast: "",
    genre: "",
    year: ""
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState();
  useEffect(() => {
    setIsLoading(true);
    listMovies(filters)
      .then(setMovies)
      .catch(error => setError(error?.message))
      .finally(() => setIsLoading(false));
  }, [filters]);
  return (
    <main>
      <header><h1>Explore Movies</h1></header>
      <MovieFilters values={filters} onChange={setFilters} />
      {movies?.length ? (
        <Gallery movies={movies} />
      ) : isLoading ? (
        <div>Loading....</div>
      ) : error ? (
        <div>Looks like we ran into an unexpected error</div>
      ) : (
        <div>There are no movies to show. Try resetting filters.</div>
      )}
    </main>
  )
}
