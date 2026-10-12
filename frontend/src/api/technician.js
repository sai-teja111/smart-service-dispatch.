import api from "./axios";

// ============================================================
// GET ASSIGNED SERVICE REQUESTS
// ============================================================

export async function getAssignedServiceRequests() {
    const response = await api.get(
        "/technician/service-requests"
    );

    return response.data;
}

// ============================================================
// GET ONE ASSIGNED SERVICE REQUEST
// ============================================================

export async function getAssignedServiceRequest(requestUuid) {
    const response = await api.get(
        `/technician/service-requests/${requestUuid}`
    );

    return response.data;
}

// ============================================================
// UPDATE SERVICE REQUEST STATUS
// ============================================================

export async function updateServiceRequestStatus(
    requestUuid,
    status,
    remarks
) {
    const response = await api.patch(
        `/service-requests/${requestUuid}/status`,
        {
            status,
            remarks,
        }
    );

    return response.data;
}

// ============================================================
// GET TECHNICIAN AVAILABILITY
// ============================================================

export async function getTechnicianAvailability() {
    const response = await api.get(
        "/technician/availability"
    );

    return response.data;
}

// ============================================================
// UPDATE TECHNICIAN AVAILABILITY
// ============================================================

export async function updateTechnicianAvailability(availability) {
    const response = await api.patch(
        "/technician/availability",
        {
            availability,
        }
    );

    return response.data;
}