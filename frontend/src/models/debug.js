import { post } from "../lib/api";

export async function clearDatabase() {
  return post(`/api/clear`);
}