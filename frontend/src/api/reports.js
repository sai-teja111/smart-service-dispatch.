
import api from "./axios";

/**
 * Fetch technician analytics.
 *
 * Endpoint: GET /reports
 * Access: Authenticated technicians only
 */
export async function getReports() {
    const response = await api.get("/reports");

    return response.data;
}

/**
 * Fetch reports belonging to the logged-in customer.
 *
 * Endpoint: GET /reports/customer
 * Access: Authenticated customers only
 */
export async function getCustomerReports() {
    const response = await api.get("/reports/customer");

    return response.data;
}

/**
 * Download the technician analytics PDF.
 *
 * Endpoint: GET /reports/pdf
 * Access: Authenticated technicians only
 */
export async function downloadTechnicianReportsPdf() {
    const response = await api.get("/reports/pdf", {
        responseType: "blob",
    });

    return response.data;
}

/**
 * Download the logged-in customer's service reports PDF.
 *
 * Endpoint: GET /reports/customer/pdf
 * Access: Authenticated customers only
 */
export async function downloadCustomerReportsPdf() {
    const response = await api.get("/reports/customer/pdf", {
        responseType: "blob",
    });

    return response.data;
}
