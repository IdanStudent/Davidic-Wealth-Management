import axios from "axios";

// point this to your backend service
const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "https://davidic-wealth-management-2.onrender.com"
});

export default API;
