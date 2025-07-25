const defaultImageUrl = "https://cdn.pixabay.com/photo/2019/04/24/21/55/cinema-4153289_1280.jpg";

export default function Gallery({ movies }) {
  return (
    <div className="card gallery">
      {movies.map(movie => (
        <a key={movie.id} className="movie-gallery-card" href={`/movies/${movie.id}`}>
          <div className="card image-thumb" style={{
            backgroundImage: `url(${movie.image_url || defaultImageUrl})`
          }}>
            <div className="user-score-badge">{movie.user_rating}<sup>%</sup></div>
            <div className="year-badge">{movie.release_year}</div>
            <div className="genre-badge">{movie.genre.map(({ name }) => name).join(", ")}</div>
          </div>
          <span>{movie.title}</span>
        </a>
      ))}
    </div>
  );
}
