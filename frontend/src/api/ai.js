import api from "./axios";

/**
 * Send a natural-language question to the AI Assistant.
 *
 * Endpoint: POST /ai/ask
 * Authentication: Uses the existing Axios configuration.
 */
export async function askAI(question) {
    const response = await api.post("/ai/ask", {
        question: question.trim(),
    });

    return response.data;
}