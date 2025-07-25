import { get } from "../lib/api";

export async function getDetails({ id }) {
  return get(`/api/crew/${id}`);
}
