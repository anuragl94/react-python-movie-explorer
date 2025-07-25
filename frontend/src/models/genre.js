import { get, post } from "../lib/api";

export async function listGenres({ name }) {
  return get(`/api/genre?name=${name}`);
}

export async function createGenre({ name }) {
  return post(`/api/genre`, { name });
}