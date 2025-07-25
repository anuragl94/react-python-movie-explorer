import { useEffect, useState } from "react";
import { getMovie } from "../models/movie";
import { Link } from "react-router";

const defaultImageUrl = "https://cdn.pixabay.com/photo/2019/04/24/21/55/cinema-4153289_1280.jpg";

function CrewLink({ id, name }) {
  return (
    <Link to={`/crew/${id}`}>{name}</Link>
  )
}

export default function Movie() {
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
          <header><h1>{movie.title} ({movie.release_year})</h1></header>
          <div className="card movie-summary">
            <div className="card image-thumb" style={{
              backgroundImage: `url(${movie.image_url || defaultImageUrl})`
            }}></div>
            <div className="summary-group">
              <h4>Average user rating</h4>
              <p>{movie.user_rating} / 100</p>
            </div>
            <div className="summary-group">
              <h4>Genre</h4>
              <div>{movie.genre.map(g => g.name).join(", ")}</div>
            </div>
            <div className="summary-group">
              <h4>Directed by</h4>
              <div><CrewLink id={movie.directed_by.id} name={movie.directed_by.name} /></div>
            </div>
            <div className="summary-group">
              <h4>Cast</h4>
              <div>
                {movie.cast.map(({ id, name }, index) => <span key={id}>
                  {index !== 0 ? ", " : null}
                  <CrewLink id={id} name={name} />
                </span>)}
              </div>
            </div>
            <div className="summary-group long-summary">
              <h4>Overview</h4>
              <p>{movie.description}</p>
            </div>
          </div>
        </>
      ) : isLoading ? (
        <div>Loading....</div>
      ) : error ? (
        <div>Looks like we ran into an unexpected error</div>
      ) : null}
    </main>
  )
}
