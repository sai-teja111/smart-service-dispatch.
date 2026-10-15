import axios from "axios";

/* ============================================================
   SHARED API CLIENT
   Used by existing customer and technician features.
   ============================================================ */

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("access_token");

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

/* ============================================================
   ADMIN API CLIENT
   Uses a separate token so Admin login does not overwrite
   the customer or technician access token.
   ============================================================ */

export const adminApi = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

adminApi.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("admin_access_token");

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default api;