export default function Gallery({ movies }) {
  return (
    <div className="card gallery">
      {movies.map(movie => (
        <a key={movie.id} href={`/movies/${movie.id}`}>
          <div className="card image-thumb">
          </div>
          <span>{movie.title}</span>
        </a>
      ))}
    </div>
  );
}
