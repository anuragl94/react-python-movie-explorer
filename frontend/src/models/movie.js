import { get } from "../lib/api";

export async function listMovies({ directorId, genreId, castId } = {}) {
  return get("/api/movies", {
    directed_by: directorId,
    genre_id: genreId,
    cast_id: castId
  });
}

export async function getMovie({ id }) {
  return get(`/api/movies/${id}`);
}