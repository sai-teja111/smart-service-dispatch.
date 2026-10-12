import api from "./axios";

/**
 * Fetch reports from the backend.
 *
 * Endpoint: GET /reports
 * Access: Authenticated technicians only
 */
export async function getReports() {
    const response = await api.get("/reports");

    return response.data;
}