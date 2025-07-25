import { useEffect, useState } from "react";
import { getMovie } from "../models/movie";

function Movie() {
  const [movie, setMovie] = useState();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState();
  useEffect(() => {
    setIsLoading(true);
    getMovie({ id: location.href.split("/").at(-1) })
      .then(setMovie)
      .catch(error => setError(error?.message))
      .finally(() => setIsLoading(false));
  }, []);
  return (
    <main>
      {movie ? (
        <>
          <header><h1>{movie.title}</h1></header>
          <pre>
            {JSON.stringify(movie, null, 2)}
          </pre>
        </>
      ) : isLoading ? (
        <div>Loading....</div>
      ) : error ? (
        <div>Looks like we ran into an unexpected error</div>
      ) : null}
    </main>
  )
}

export default Movie;