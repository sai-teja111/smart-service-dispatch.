import {
    AlertCircle,
    ArrowRight,
    CalendarDays,
    ClipboardList,
    Loader2,
    MapPin,
    Phone,
    UserRound,
} from "lucide-react";

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getAssignedServiceRequests } from "../../api/technician";


function getStatusClasses(status) {
    switch (status) {
        case "PENDING":
            return "bg-amber-50 text-amber-700 border border-amber-200";

        case "IN PROGRESS":
        case "IN_PROGRESS":
            return "bg-blue-50 text-blue-700 border border-blue-200";

        case "COMPLETED":
            return "bg-emerald-50 text-emerald-700 border border-emerald-200";

        case "OPEN":
            return "bg-slate-100 text-slate-700 border border-slate-200";

        default:
            return "bg-slate-100 text-slate-700 border border-slate-200";
    }
}


function getPriorityClasses(priority) {
    switch (String(priority || "").toUpperCase()) {
        case "HIGH":
            return "bg-red-50 text-red-700 border border-red-200";

        case "MEDIUM":
            return "bg-amber-50 text-amber-700 border border-amber-200";

        case "LOW":
            return "bg-emerald-50 text-emerald-700 border border-emerald-200";

        default:
            return "bg-slate-100 text-slate-700 border border-slate-200";
    }
}


function formatStatus(status) {
    if (!status) {
        return "Unknown";
    }

    return status
        .toLowerCase()
        .split(" ")
        .map(
            (word) =>
                word.charAt(0).toUpperCase() +
                word.slice(1)
        )
        .join(" ");
}


function formatDate(dateValue) {
    if (!dateValue) {
        return "—";
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
        return "—";
    }

    return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    });
}


function getLocation(customer) {
    if (!customer) {
        return "Location unavailable";
    }

    const parts = [
        customer.area,
        customer.city,
        customer.pincode,
    ].filter(Boolean);

    return parts.length > 0
        ? parts.join(", ")
        : "Location unavailable";
}


export default function AssignedRequests() {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");


    useEffect(() => {
        let isMounted = true;

        async function loadRequests() {
            try {
                setLoading(true);
                setError("");

                const response =
                    await getAssignedServiceRequests();

                if (!isMounted) {
                    return;
                }

                setRequests(
                    Array.isArray(response?.service_requests)
                        ? response.service_requests
                        : []
                );
            } catch (err) {
                if (!isMounted) {
                    return;
                }

                setError(
                    err?.response?.data?.detail ||
                        "Unable to load assigned service requests."
                );
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        }

        loadRequests();

        return () => {
            isMounted = false;
        };
    }, []);


    return (
        <div className="space-y-6">

            {/* =====================================================
                PAGE HEADER
            ====================================================== */}

            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

                <div className="flex items-center gap-3">

                    <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-700">
                        <ClipboardList size={22} />
                    </div>

                    <div>
                        <h1 className="text-2xl font-bold text-slate-900">
                            Assigned Requests
                        </h1>

                        <p className="mt-1 text-sm text-slate-500">
                            View and manage service requests assigned to you.
                        </p>
                    </div>

                </div>

                {!loading && !error && (
                    <div className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-600 shadow-sm">
                        {requests.length}{" "}
                        {requests.length === 1
                            ? "request"
                            : "requests"}
                    </div>
                )}

            </div>


            {/* =====================================================
                ERROR
            ====================================================== */}

            {error && (
                <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">

                    <AlertCircle
                        size={20}
                        className="mt-0.5 shrink-0"
                    />

                    <div>
                        <p className="font-semibold">
                            Unable to load requests
                        </p>

                        <p className="mt-1 text-sm">
                            {error}
                        </p>
                    </div>

                </div>
            )}


            {/* =====================================================
                LOADING
            ====================================================== */}

            {loading && (
                <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">

                    <div className="flex min-h-70 items-center justify-center">

                        <div className="flex items-center gap-3 text-slate-500">

                            <Loader2
                                size={22}
                                className="animate-spin"
                            />

                            <span className="text-sm">
                                Loading assigned requests...
                            </span>

                        </div>

                    </div>

                </div>
            )}


            {/* =====================================================
                EMPTY STATE
            ====================================================== */}

            {!loading &&
                !error &&
                requests.length === 0 && (
                    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">

                        <div className="flex min-h-70 flex-col items-center justify-center px-6 text-center">

                            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 text-slate-500">
                                <ClipboardList size={26} />
                            </div>

                            <h2 className="mt-4 text-base font-semibold text-slate-900">
                                No assigned requests
                            </h2>

                            <p className="mt-1 max-w-md text-sm text-slate-500">
                                You currently don't have any service
                                requests assigned to you.
                            </p>

                        </div>

                    </div>
                )}


            {/* =====================================================
                REQUEST LIST
            ====================================================== */}

            {!loading &&
                !error &&
                requests.length > 0 && (
                    <div className="space-y-4">

                        {requests.map((request) => (
                            <div
                                key={request.request_uuid}
                                className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md sm:p-6"
                            >

                                {/* Request Header */}

                                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">

                                    <div className="min-w-0">

                                        <div className="flex flex-wrap items-center gap-2">

                                            <h2 className="text-lg font-bold text-slate-900">
                                                {request.service ||
                                                    "Service Request"}
                                            </h2>

                                            <span
                                                className={`rounded-full px-2.5 py-1 text-xs font-semibold ${getPriorityClasses(
                                                    request.priority
                                                )}`}
                                            >
                                                {request.priority ||
                                                    "Normal"}
                                            </span>

                                            <span
                                                className={`rounded-full px-2.5 py-1 text-xs font-semibold ${getStatusClasses(
                                                    request.status
                                                )}`}
                                            >
                                                {formatStatus(
                                                    request.status
                                                )}
                                            </span>

                                        </div>

                                        <p className="mt-2 wrap-break-word text-sm leading-6 text-slate-600">
                                            {request.problem_description ||
                                                "No problem description provided."}
                                        </p>

                                    </div>

                                    <Link
                                        to={`/technician/requests/${request.request_uuid}`}
                                        className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700"
                                    >
                                        View Details
                                        <ArrowRight size={17} />
                                    </Link>

                                </div>


                                {/* Request Information */}

                                <div className="mt-5 grid grid-cols-1 gap-4 border-t border-slate-100 pt-5 sm:grid-cols-2 lg:grid-cols-4">

                                    <div className="flex items-start gap-3">

                                        <UserRound
                                            size={18}
                                            className="mt-0.5 shrink-0 text-slate-400"
                                        />

                                        <div className="min-w-0">
                                            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                                                Customer
                                            </p>

                                            <p className="mt-1 truncate text-sm font-semibold text-slate-800">
                                                {request.customer
                                                    ?.customer_name ||
                                                    "Unavailable"}
                                            </p>
                                        </div>

                                    </div>


                                    <div className="flex items-start gap-3">

                                        <MapPin
                                            size={18}
                                            className="mt-0.5 shrink-0 text-slate-400"
                                        />

                                        <div className="min-w-0">
                                            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                                                Location
                                            </p>

                                            <p className="mt-1 text-sm font-semibold text-slate-800">
                                                {getLocation(
                                                    request.customer
                                                )}
                                            </p>
                                        </div>

                                    </div>


                                    <div className="flex items-start gap-3">

                                        <Phone
                                            size={18}
                                            className="mt-0.5 shrink-0 text-slate-400"
                                        />

                                        <div className="min-w-0">
                                            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                                                Phone
                                            </p>

                                            <p className="mt-1 text-sm font-semibold text-slate-800">
                                                {request.customer
                                                    ?.phone ||
                                                    "Unavailable"}
                                            </p>
                                        </div>

                                    </div>


                                    <div className="flex items-start gap-3">

                                        <CalendarDays
                                            size={18}
                                            className="mt-0.5 shrink-0 text-slate-400"
                                        />

                                        <div className="min-w-0">
                                            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                                                Requested
                                            </p>

                                            <p className="mt-1 text-sm font-semibold text-slate-800">
                                                {formatDate(
                                                    request.request_date
                                                )}
                                            </p>
                                        </div>

                                    </div>

                                </div>

                            </div>
                        ))}

                    </div>
                )}

        </div>
    );
}