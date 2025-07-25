import { get, post } from "../lib/api";

export async function listCrew({ name }) {
  return get(`/api/crew`, { name });
}

export async function getDetails({ id }) {
  return get(`/api/crew/${id}`);
}

export async function createCrewMember({ name }) {
  return post(`/api/crew`, { name });
}