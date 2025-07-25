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
  year
} = {}) {
  if (director) {
    directorId = (await listCrew({ name: director })).map(({ id }) => id).join(",");
    // When no such director exists, no movie would also exist
    if (!directorId) {
      return [];
    }
  }
  if (cast) {
    castId = (await listCrew({ name: cast })).map(({ id }) => id).join(",");
    // When no such cast members exist, no movie would also exist
    if (!castId) {
      return [];
    }
  }
  if (genre) {
    genreId = (await listGenres({ genre })).map(({ id }) => id).join(",");
    // When no such genres exist, no movie would also exist
    if (!genreId) {
      return [];
    }
  }
  return get("/api/movies", {
    title,
    directed_by_ids: directorId,
    genre_ids: genreId,
    cast_ids: castId,
    release_year: year
  });
}

// TODO: Map API response to consumable objects in code (casing and format)
export async function getMovie({ id }) {
  return get(`/api/movies/${id}`);
}

export async function createMovie({
  title,
  posterUrl,
  releaseYear,
  audienceRating,
  description,
  directorId,
  castIds,
  genreIds
}) {
  return post(`/api/movies`, {
    title,
    image_url: posterUrl,
    release_year: releaseYear,
    user_rating: audienceRating,
    description,
    directed_by: directorId,
    cast: castIds,
    genre: genreIds
  });
}