import axios from "axios";

const api = axios.create({
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 60000,
  withCredentials: true,
});

export default api;
