import api from "./axios";


export async function detectService(problemDescription) {
    const response = await api.post(
        "/service-requests",
        {
            problem_description: problemDescription
        }
    );

    return response.data;
}


export async function createServiceRequest(
    problemDescription,
    skillId,
    priority
) {
    const response = await api.post(
        "/service-requests",
        {
            problem_description: problemDescription,
            skill_id: skillId,
            priority: priority
        }
    );

    return response.data;
}


export async function getMyServiceRequests() {
    const response = await api.get(
        "/service-requests"
    );

    return response.data;
}


export async function getServiceRequest(requestUuid) {
    const response = await api.get(
        `/service-requests/${requestUuid}`
    );

    return response.data;
}

export async function getServiceHistory(requestUuid) {
    const response = await api.get(
        `/service-history/${requestUuid}`
    );

    return response.data;
}

export async function createFeedback(
    requestUuid,
    rating,
    comments
) {
    const response = await api.post(
        "/feedback",
        {
            request_uuid: requestUuid,
            rating: rating,
            comments: comments || null
        }
    );

    return response.data;
}


export async function getFeedback(requestUuid) {
    const response = await api.get(
        `/feedback/${requestUuid}`
    );

    return response.data;
}