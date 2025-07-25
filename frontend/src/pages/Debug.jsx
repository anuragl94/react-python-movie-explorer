import { createRef, useState } from "react"
import { clearDatabase } from "../models/debug";
import { createCrewMember, listCrew } from "../models/crew";
import { createGenre, listGenres } from "../models/genre";
import { createMovie } from "../models/movie";

import { TEST_PRESET } from "../data/moviePresetData";

// This function will make sure duplicate entries are not created for director/cast/genre
async function createMovieSmartly(data, logger) {
  const {
    title,
    overview,
    director,
    cast,
    genres
  } = data;

  const genreIds = [];
  const castIds = [];
  let directorId = "";

  for await (const genreName of genres) {
    const existingData = await listGenres({ name: genreName });
    if (!existingData.length) {
      logger("Creating genre data");
      const newData = await createGenre({ name: genreName });
      genreIds.push(newData.id);
    } else {
      genreIds.push(existingData[0].id);
    }
  }

  for await (const castMemberName of cast) {
    const existingData = await listCrew({ name: castMemberName });
    if (!existingData.length) {
      logger("Creating crew data");
      const newData = await createCrewMember({ name: castMemberName });
      castIds.push(newData.id);
    } else {
      castIds.push(existingData[0].id);
    }
  }

  const existingData = await listCrew({ name: director });
  if (!existingData.length) {
      logger("Creating crew data");
    const newData = await createCrewMember({ name: director });
    directorId = newData.id;
  } else {
    directorId = existingData[0].id;
  }

  logger("Creating moview data");
  await createMovie({
    title,
    description: overview,
    directorId: directorId,
    castIds: castIds,
    genreIds: genreIds
  });
  logger("Inserted movie data");
}

async function loadPreset(preset, outputEl) {
  console.log(preset, outputEl);
  const logger = (text) => outputEl.innerHTML += `${text}<br>`;

  await clearDB(outputEl);

  const total = preset.length;
  let index = 1;
  for (const movie of preset) {
    await createMovieSmartly(movie, logger);
    logger(`Progress: ${index}/${total}`);
    logger("");
    index += 1;
  }
}

async function clearDB(outputEl) {
  const logger = (text) => outputEl.innerHTML += `${text}<br>`;

  await clearDatabase();
  logger("Cleared all data in DB");
}

export default function Debug() {
  const outputLogRef = createRef();

  return (
    <main>
      <p>
        To make it easier to populate the content, I have created a few presets to populate the DB with.
      </p>
      <p>
        All data has been scraped from TMDB.
      </p>
      <p>
        Please note that loading a preset will clear existing data first.
      </p>
      <div className="button-group">
        <button onClick={() => loadPreset(TEST_PRESET, outputLogRef?.current)}>Load Test Preset</button>
        <button>Load Preset 1</button>
        <button onClick={() => clearDB(outputLogRef?.current)}>Clear DB</button>
      </div>
      <div className="output" ref={outputLogRef}></div>
    </main>
  )
}
