import { useEffect, useState } from "react";
import { getDetails } from "../models/crew";
import { listMovies } from "../models/movie";
import Gallery from "../components/Gallery";

export default function Movie() {
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
      {data.length ? (
        <>
          <header><h1>{personalDetails?.name}</h1></header>
          <h2>Director of</h2>
          {moviesDirectedbyPerson.length ? (
            <Gallery movies={moviesDirectedbyPerson} />
          ) : null}
          <h2>Starred in</h2>
          {moviesDirectedbyPerson.length ? (
            <Gallery movies={moviesStarringPerson} />
          ) : null}
        </>
      ) : isLoading ? (
        <div>Loading....</div>
      ) : error ? (
        <div>Looks like we ran into an unexpected error</div>
      ) : null}
    </main>
  )
}
