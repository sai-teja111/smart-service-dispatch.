
import { Navigate, Route, Routes } from "react-router-dom";

import Home from "../pages/Home";
import Login from "../pages/auth/Login";
import Register from "../pages/auth/Register";

// CUSTOMER
import CustomerLayout from "../layouts/CustomerLayout";
import CustomerDashboard from "../pages/customer/CustomerDashboard";
import CreateServiceRequest from "../pages/customer/CreateServiceRequest";
import MyRequests from "../pages/customer/MyRequests";
import ServiceRequestDetails from "../pages/customer/ServiceRequestDetails";
import CustomerServiceHistory from "../pages/customer/ServiceHistory";
import Feedback from "../pages/customer/Feedback";
import CustomerAIAssistant from "../pages/customer/AIAssistant";

// TECHNICIAN
import TechnicianLayout from "../layouts/TechnicianLayout";
import TechnicianDashboard from "../pages/technician/TechnicianDashboard";
import AssignedRequests from "../pages/technician/AssignedRequests";
import TechnicianRequestDetails from "../pages/technician/TechnicianRequestDetails";
import TechnicianServiceHistory from "../pages/technician/ServiceHistory";
import Availability from "../pages/technician/Availability";
import Reports from "../pages/technician/Reports";
import AIAssistant from "../pages/technician/AIAssistant";

function AppRoutes() {
    return (
        <Routes>
            {/* PUBLIC PAGES */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* CUSTOMER */}
            <Route path="/customer" element={<CustomerLayout />}>
                <Route index element={<CustomerDashboard />} />

                <Route
                    path="request"
                    element={<CreateServiceRequest />}
                />

                <Route
                    path="requests"
                    element={<MyRequests />}
                />

                <Route
                    path="requests/:requestUuid"
                    element={<ServiceRequestDetails />}
                />

                <Route
                    path="history"
                    element={<CustomerServiceHistory />}
                />

                <Route
                    path="feedback"
                    element={<Feedback />}
                />

                {/* CUSTOMER AI ASSISTANT */}
                <Route
                    path="ai-assistant"
                    element={<CustomerAIAssistant />}
                />
            </Route>

            {/* TECHNICIAN */}
            <Route path="/technician" element={<TechnicianLayout />}>
                <Route index element={<TechnicianDashboard />} />

                <Route
                    path="requests"
                    element={<AssignedRequests />}
                />

                <Route
                    path="requests/:requestUuid"
                    element={<TechnicianRequestDetails />}
                />

                <Route
                    path="history"
                    element={<TechnicianServiceHistory />}
                />

                <Route
                    path="availability"
                    element={<Availability />}
                />

                <Route
                    path="reports"
                    element={<Reports />}
                />

                <Route
                    path="ai-assistant"
                    element={<AIAssistant />}
                />
            </Route>

            {/* INVALID ROUTES */}
            <Route
                path="*"
                element={<Navigate to="/" replace />}
            />
        </Routes>
    );
}

export default AppRoutes;
