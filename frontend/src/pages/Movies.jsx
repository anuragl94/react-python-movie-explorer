import { useEffect, useState } from "react";
import { listMovies } from "../models/movie";

function Movies() {
  const [movies, setMovies] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState();
  useEffect(() => {
    setIsLoading(true);
    listMovies()
      .then(setMovies)
      .catch(error => setError(error?.message))
      .finally(() => setIsLoading(false));
  }, []);
  return (
    <main>
      <header><h1>Movies</h1></header>
      {movies?.length ? (
        <div className="card gallery">
          {movies.map(movie => (
            <a key={movie.id} href={`/movies/${movie.id}`}>
              <div className="card image-thumb">
              </div>
              <span>{movie.title}</span>
            </a>
          ))}
        </div>
      ) : isLoading ? (
        <div>Loading....</div>
      ) : error ? (
        <div>Looks like we ran into an unexpected error</div>
      ) : null}
    </main>
  )
}

export default Movies;