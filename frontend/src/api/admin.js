import { adminApi } from "./axios";

/* ============================================================
   ADMIN LOGIN
   ============================================================ */

export async function loginAdmin(email, password) {
    const response = await adminApi.post("/admin/login", {
        email,
        password,
    });

    return response.data;
}

/* ============================================================
   GET CURRENT ADMIN PROFILE
   ============================================================ */

export async function getAdminProfile() {
    const response = await adminApi.get("/admin/me");
    return response.data;
}

/* ============================================================
   ADMIN DASHBOARD SUMMARY
   ============================================================ */

export async function getAdminReportSummary() {
    const response = await adminApi.get("/admin/reports/summary");
    return response.data;
}

/* ============================================================
   CUSTOMER REPORT
   ============================================================ */

export async function getAdminCustomerReport() {
    const response = await adminApi.get("/admin/reports/customers");
    return response.data;
}

/* ============================================================
   TECHNICIAN REPORT
   ============================================================ */

export async function getAdminTechnicianReport() {
    const response = await adminApi.get("/admin/reports/technicians");
    return response.data;
}

/* ============================================================
   CUSTOMER MANAGEMENT
   ============================================================ */

export async function getAdminCustomers() {
    const response = await adminApi.get("/admin/customers");
    return response.data;
}

export async function getAdminCustomerDetails(customerUuid) {
    const response = await adminApi.get(
        `/admin/customers/${customerUuid}`
    );
    return response.data;
}

export async function getAdminCustomerRequests(customerUuid) {
    const response = await adminApi.get(
        `/admin/customers/${customerUuid}/requests`
    );
    return response.data;
}

/* ============================================================
   TECHNICIAN MANAGEMENT
   ============================================================ */

export async function getAdminTechnicians() {
    const response = await adminApi.get("/admin/technicians");
    return response.data;
}

export async function getPendingTechnicians() {
    const response = await adminApi.get("/admin/technicians/pending");
    return response.data;
}

export async function updateTechnicianApproval(
    technicianUuid,
    approvalStatus
) {
    const response = await adminApi.patch(
        `/admin/technicians/${technicianUuid}/approval`,
        {
            approval_status: approvalStatus,
        }
    );
    return response.data;
}

/* ============================================================
   TECHNICIAN SKILL VERIFICATION
   ============================================================ */

export async function getAdminTechnicianSkills() {
    const response = await adminApi.get("/admin/technician-skills");
    return response.data;
}

export async function getPendingTechnicianSkills() {
    const response = await adminApi.get(
        "/admin/technician-skills/pending"
    );
    return response.data;
}

export async function updateTechnicianSkillVerification(
    technicianUuid,
    skillId,
    isVerified
) {
    const response = await adminApi.patch(
        `/admin/technicians/${technicianUuid}/skills/${skillId}/verification`,
        {
            is_verified: isVerified,
        }
    );
    return response.data;
}