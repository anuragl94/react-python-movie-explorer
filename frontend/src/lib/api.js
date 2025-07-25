export async function get(url, params = {}) {
  try {
    const filteredParams = Object.fromEntries(Object.entries(params).filter(entry => Boolean(entry[1])));
    const queryString = new URLSearchParams(filteredParams).toString();

    const response = await fetch(url + (queryString ? `?${queryString}` : ""));
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const json = await response.json();
    return json;
  } catch (error) {
    console.log(error);
    throw error;
  }
}

export async function post(url, params = {}) {
  try {
    const response = await fetch(url, {
      method: "POST",
      body: JSON.stringify(params)
    });
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const json = await response.json();
    return json;
  } catch (error) {
    console.log(error);
    throw error;
  }
}