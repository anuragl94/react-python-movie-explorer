import { get, post } from "../lib/api";
import { listCrew } from "./crew";
import { listGenres } from "./genre";

export async function listMovies({
  title,
  directorId, // or
  director,
  genreId, // or
  genre,
  castId, // or
  cast,
} = {}) {
  if (director) {
    directorId = (await listCrew({ name: director })).map(({ id }) => id).join(",");
  }
  if (cast) {
    castId = (await listCrew({ name: cast })).map(({ id }) => id).join(",");
  }
  if (genre) {
    genreId = (await listGenres({ genre })).map(({ id }) => id).join(",");
  }
  return get("/api/movies", {
    title,
    directed_by_ids: directorId,
    genre_ids: genreId,
    cast_ids: castId
  });
}

// TODO: Map API response to consumable objects in code (casing and format)
export async function getMovie({ id }) {
  return get(`/api/movies/${id}`);
}

export async function createMovie({
  title,
  description,
  directorId,
  castIds,
  genreIds
}) {
  return post(`/api/movies`, {
    title,
    description,
    directed_by: directorId,
    cast: castIds,
    genre: genreIds
  });
}