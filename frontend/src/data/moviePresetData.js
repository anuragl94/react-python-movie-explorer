/*
  Note for reviewer
  This data is not used in the code at all. If you wish to load this data into the DB,
  please go to /debug page on the web app. The page is designed to load this data into
  the DB systematically.
*/

const PRESET_TEMPLATE = [
  {
    title: "",
    overview: "",
    director: "",
    poster: "",
    rating: 100,
    year: 2000,
    cast: [],
    genres: []
  },
];

export const PRESET1 = [
  {
    title: "Pulp Fiction",
    overview: "A burger-loving hit man, his philosophical partner, a drug-addled gangster's moll and a washed-up boxer converge in this sprawling, comedic crime caper. Their adventures unfurl in three stories that ingeniously trip back and forth in time.",
    director: "Quentin Tarantino",
    poster: "https://www.themoviedb.org/t/p/w600_and_h900_bestv2/vQWk5YBFWF4bZaofAbv0tShwBvQ.jpg",
    rating: 85,
    year: 2000,
    cast: ["Quentin Tarantino", "John Travolta", "Samuel L. Jackson", "Uma Thurman", "Bruce Willis", "Tim Roth"],
    genres: ["Thriller", "Crime", "Comedy"]
  },
  {
    title: "Face/Off",
    overview: "In order to foil a terrorist plot, an FBI agent undergoes facial transplant surgery and assumes the identity of a criminal mastermind. The plan turns sour when the criminal wakes up prematurely and seeks revenge.",
    director: "John Woo",
    poster: "https://www.themoviedb.org/t/p/w600_and_h900_bestv2/69Xzn8UdPbVnmqSChKz2RTpoNfB.jpg",
    rating: 70,
    year: 1997,
    cast: ["John Travolta", "Nicolas Cage"],
    genres: ["Action", "Crime", "Science Fiction"]
  },
  {
    title: "Memento",
    overview: "Leonard Shelby is tracking down the man who raped and murdered his wife. The difficulty of locating his wife's killer, however, is compounded by the fact that he suffers from a rare, untreatable form of short-term memory loss. Although he can recall details of life before his accident, Leonard cannot remember what happened fifteen minutes ago, where he's going, or why.",
    director: "Christopher Nolan",
    poster: "https://www.themoviedb.org/t/p/w600_and_h900_bestv2/fKTPH2WvH8nHTXeBYBVhawtRqtR.jpg",
    rating: 82,
    year: 2000,
    cast: ["Guy Pearce", "Carrie-Anne Moss"],
    genres: ["Mystery", "Thriller"]
  },
  {
    title: "The Matrix",
    overview: "Set in the 22nd century, The Matrix tells the story of a computer hacker who joins a group of underground insurgents fighting the vast and powerful computers who now rule the earth.",
    director: "Lana Wachowski",
    poster: "https://media.themoviedb.org/t/p/w300_and_h450_bestv2/p96dm7sCMn4VYAStA6siNz30G1r.jpg",
    rating: 82,
    year: 1999,
    cast: ["Lana Wachowski", "Lilly Wachowski", "Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss", "Hugo Weaving"],
    genres: ["Action", "Science Fiction"]
  },
  {
    title: "The Matrix Reloaded",
    overview: "The Resistance builds in numbers as humans are freed from the Matrix and brought to the city of Zion. Neo discovers his superpowers, including the ability to see the code inside the Matrix. With machine sentinels digging to Zion in 72 hours, Neo, Morpheus and Trinity must find the Keymaker to ultimately reach the Source.",
    director: "Lana Wachowski",
    poster: "https://media.themoviedb.org/t/p/w300_and_h450_bestv2/9TGHDvWrqKBzwDxDodHYXEmOE6J.jpg",
    rating: 71,
    year: 2003,
    cast: ["Lana Wachowski", "Lilly Wachowski", "Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss", "Hugo Weaving", "Jada Pinkett Smith", "Monica Bellucci", "Harry Lennix"],
    genres: ["Adventure", "Action", "Thriller", "Science Fiction"]
  },
  {
    title: "The Matrix Revolutions",
    overview: "The human city of Zion defends itself against the massive invasion of the machines as Neo fights to end the war at another front while also opposing the rogue Agent Smith.",
    director: "Lana Wachowski",
    poster: "https://media.themoviedb.org/t/p/w300_and_h450_bestv2/t1wm4PgOQ8e4z1C6tk1yDNrps4T.jpg",
    rating: 67,
    year: 2003,
    cast: ["Lana Wachowski","Lilly Wachowski", "Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss", "Hugo Weaving", "Jada Pinkett Smith"],
    genres: ["Adventure", "Action", "Thriller", "Science Fiction"]
  },
  {
    title: "The Matrix Resurrections",
    overview: "Plagued by strange memories, Neo's life takes an unexpected turn when he finds himself back inside the Matrix.",
    director: "Lana Wachowski",
    poster: "https://media.themoviedb.org/t/p/w300_and_h450_bestv2/8c4a8kE7PizaGQQnditMmI1xbRp.jpg",
    rating: 64,
    year: 2021,
    cast: ["Lana Wachowski", "Lilly Wachowski", "David Mitchell", "Aleksandar Hemon", "Keanu Reeves", "Carrie-Anne Moss", "Neil Patrick Harris", "Jada Pinkett Smith", "Priyanka Chopra Jonas"],
    genres: ["Science Fiction", "Action", "Adventure"]
  },

];

export const TEST_PRESET = [
  {
    title: "Horrors of coding",
    overview: "Watch this developer struggle to code in a language he has not touched in 8 years.",
    director: "Anurag",
    poster: "https://cdn.pixabay.com/photo/2024/09/15/09/21/ai-generated-9048651_1280.jpg",
    rating: 88,
    year: 2025,
    cast: ["Anurag", "Anurag's Desktop"],
    genres: ["Drama", "Dystopian", "Suspense", "Thriller"]
  },
  {
    title: "Time to sleep",
    overview: "After finishing this assignment, the protagonist will watch this movie.",
    director: "Anurag",
    poster: null,
    rating: 26,
    year: 2026,
    cast: ["Anurag", "Anurag's Bed"],
    genres: ["Fantasy", "Fiction", "Suspense"]
  }
];