import { useEffect, useState } from "react";
import { getDetails } from "../models/crew";
import { listMovies } from "../models/movie";

function Movie() {
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState();
  useEffect(() => {
    setIsLoading(true);
    const id = location.href.split("/").at(-1);
    Promise.all([
      getDetails({ id }),
      listMovies({ directorId: id }),
      listMovies({ castId: id })
    ]).then(setData)
      .catch(error => setError(error?.message))
      .finally(() => setIsLoading(false));
  }, []);
  const [personalDetails, moviesDirectedbyPerson, moviesStarringPerson] = data;
  return (
    <main>
      {data ? (
        <>
          <header><h1>{data.name}</h1></header>
          <pre>
            {JSON.stringify(personalDetails, null, 2)}
          </pre>
          <pre>
            {JSON.stringify(moviesDirectedbyPerson, null, 2)}
          </pre>
          <pre>
            {JSON.stringify(moviesStarringPerson, null, 2)}
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