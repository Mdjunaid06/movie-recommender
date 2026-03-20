import axios from "axios";

const API = axios.create({
  baseURL: "https://movie-recommender-li21.onrender.com",
  timeout: 30000,
});

// Search movies by title
export const searchMovies = async (query) => {
  const res = await API.get(`/search?q=${encodeURIComponent(query)}&top_n=8`);
  return res.data;
};

// Get recommendations
export const getRecommendations = async (payload) => {
  const res = await API.post("/recommend", payload);
  return res.data;
};

// Get popular movies
export const getPopularMovies = async (top_n = 20) => {
  const res = await API.get(`/movies/popular?top_n=${top_n}`);
  return res.data;
};

// Get all genres
export const getGenres = async () => {
  const res = await API.get("/genres");
  return res.data;
};

// Get single movie
export const getMovie = async (title) => {
  const res = await API.get(`/movie/${encodeURIComponent(title)}`);
  return res.data;
};

// Suggest actors
export const suggestActors = async (query) => {
  const res = await API.get(`/suggest/actors?q=${encodeURIComponent(query)}`);
  return res.data;
};

// Suggest directors
export const suggestDirectors = async (query) => {
  const res = await API.get(`/suggest/directors?q=${encodeURIComponent(query)}`);
  return res.data;
};