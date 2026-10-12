
import api from "./axios";

export async function getSkills() {
    const response = await api.get("/skills");
    return response.data;
}
