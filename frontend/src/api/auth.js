import api from "./axios";


/* ============================================================
   CUSTOMER REGISTRATION
   ============================================================ */

export async function registerCustomer(data) {

    const response = await api.post(
        "/auth/register/customer",
        data
    );

    return response.data;
}


/* ============================================================
   TECHNICIAN REGISTRATION
   ============================================================ */

export async function registerTechnician(data) {

    const response = await api.post(
        "/auth/register/technician",
        data
    );

    return response.data;
}


/* ============================================================
   CUSTOMER LOGIN
   ============================================================ */

export async function loginCustomer(phone, password) {

    const response = await api.post(
        "/auth/login/customer",
        {
            phone,
            password
        }
    );

    return response.data;
}


/* ============================================================
   TECHNICIAN LOGIN
   ============================================================ */

export async function loginTechnician(phone, password) {

    const response = await api.post(
        "/auth/login/technician",
        {
            phone,
            password
        }
    );

    return response.data;
}