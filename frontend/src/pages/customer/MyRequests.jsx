import {
    AlertCircle,
    ArrowRight,
    CalendarDays,
    ClipboardList,
    Loader2,
    Plus,
    UserRound,
} from "lucide-react";

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getMyServiceRequests } from "../../api/serviceRequests";


function formatDate(dateValue) {
    if (!dateValue) {
        return "Date unavailable";
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
        return "Date unavailable";
    }

    return date.toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}


function getStatusStyles(status) {
    switch (status) {
        case "OPEN":
            return "bg-blue-50 text-blue-700 border-blue-200";

        case "PENDING":
            return "bg-amber-50 text-amber-700 border-amber-200";

        case "IN_PROGRESS":
            return "bg-indigo-50 text-indigo-700 border-indigo-200";

        case "COMPLETED":
            return "bg-emerald-50 text-emerald-700 border-emerald-200";

        default:
            return "bg-slate-50 text-slate-700 border-slate-200";
    }
}


function formatStatus(status) {
    if (!status) {
        return "Unknown";
    }

    return status
        .toLowerCase()
        .split("_")
        .map(
            (word) =>
                word.charAt(0).toUpperCase() + word.slice(1)
        )
        .join(" ");
}


function getPriorityStyles(priority) {
    switch (priority) {
        case "High":
            return "bg-red-50 text-red-700 border-red-200";

        case "Medium":
            return "bg-amber-50 text-amber-700 border-amber-200";

        case "Low":
            return "bg-slate-50 text-slate-600 border-slate-200";

        default:
            return "bg-slate-50 text-slate-600 border-slate-200";
    }
}


function MyRequests() {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");


    useEffect(() => {
        let isMounted = true;

        async function loadRequests() {
            try {
                setLoading(true);
                setError("");

                const response = await getMyServiceRequests();

                if (!isMounted) {
                    return;
                }

                setRequests(
                    Array.isArray(response?.service_requests)
                        ? response.service_requests
                        : []
                );
            } catch (error) {
                if (!isMounted) {
                    return;
                }

                const message =
                    error?.response?.data?.detail ||
                    "Unable to load your service requests.";

                setError(message);
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


    if (loading) {
        return (
            <div className="rounded-2xl border border-slate-200 bg-white p-10 shadow-sm">

                <div className="flex min-h-70 flex-col items-center justify-center text-center">

                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 text-blue-600">
                        <Loader2
                            size={24}
                            className="animate-spin"
                        />
                    </div>

                    <h2 className="mt-4 text-lg font-bold text-slate-900">
                        Loading your requests
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                        Please wait while we retrieve your service requests.
                    </p>

                </div>

            </div>
        );
    }


    if (error) {
        return (
            <div className="rounded-2xl border border-red-200 bg-white p-8 shadow-sm">

                <div className="flex min-h-70 flex-col items-center justify-center text-center">

                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-50 text-red-600">
                        <AlertCircle size={25} />
                    </div>

                    <h2 className="mt-4 text-lg font-bold text-slate-900">
                        Unable to load requests
                    </h2>

                    <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                        {error}
                    </p>

                </div>

            </div>
        );
    }


    return (
        <div className="space-y-6">

            {/* Page Header */}
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

                <div>
                    <p className="text-sm font-medium text-blue-600">
                        Customer Portal
                    </p>

                    <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
                        My Requests
                    </h1>

                    <p className="mt-1 text-sm text-slate-500">
                        View and track all your service requests.
                    </p>
                </div>

                <Link
                    to="/customer/request"
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
                >
                    <Plus size={18} />
                    New Service Request
                </Link>

            </div>


            {/* Request Count */}
            <div className="rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm">

                <div className="flex items-center gap-3">

                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                        <ClipboardList size={20} />
                    </div>

                    <div>
                        <p className="text-sm font-medium text-slate-500">
                            Total Requests
                        </p>

                        <p className="text-xl font-bold text-slate-900">
                            {requests.length}
                        </p>
                    </div>

                </div>

            </div>


            {/* Empty State */}
            {requests.length === 0 ? (
                <div className="rounded-2xl border border-slate-200 bg-white p-10 shadow-sm">

                    <div className="flex min-h-75 flex-col items-center justify-center text-center">

                        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                            <ClipboardList size={30} />
                        </div>

                        <h2 className="mt-5 text-xl font-bold text-slate-900">
                            No service requests yet
                        </h2>

                        <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                            You haven't created any service requests yet.
                            Describe your problem and let our intelligent
                            matching system find the right service and
                            technician for you.
                        </p>

                        <Link
                            to="/customer/request"
                            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700"
                        >
                            <Plus size={18} />
                            Create Service Request
                        </Link>

                    </div>

                </div>
            ) : (

                /* Request List */
                <div className="space-y-4">

                    {requests.map((request) => (

                        <div
                            key={request.request_uuid}
                            className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md"
                        >

                            {/* Request Header */}
                            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

                                <div className="flex gap-4">

                                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                                        <ClipboardList size={21} />
                                    </div>

                                    <div>

                                        <h2 className="text-lg font-bold text-slate-900">
                                            {request.service}
                                        </h2>

                                        <p className="mt-1 text-xs text-slate-400">
                                            Request ID:{" "}
                                            {request.request_uuid}
                                        </p>

                                    </div>

                                </div>


                                <div className="flex flex-wrap gap-2">

                                    <span
                                        className={`rounded-full border px-3 py-1 text-xs font-semibold ${getStatusStyles(
                                            request.status
                                        )}`}
                                    >
                                        {formatStatus(request.status)}
                                    </span>

                                    {request.priority && (
                                        <span
                                            className={`rounded-full border px-3 py-1 text-xs font-semibold ${getPriorityStyles(
                                                request.priority
                                            )}`}
                                        >
                                            {request.priority} Priority
                                        </span>
                                    )}

                                </div>

                            </div>


                            {/* Problem */}
                            <div className="mt-5 rounded-xl bg-slate-50 p-4">

                                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                                    Problem Description
                                </p>

                                <p className="mt-2 text-sm leading-6 text-slate-700">
                                    {request.problem_description}
                                </p>

                            </div>


                            {/* Request Information */}
                            <div className="mt-5 grid gap-4 border-t border-slate-100 pt-5 sm:grid-cols-2">

                                <div className="flex items-center gap-3">

                                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
                                        <CalendarDays size={17} />
                                    </div>

                                    <div>
                                        <p className="text-xs text-slate-400">
                                            Requested On
                                        </p>

                                        <p className="mt-0.5 text-sm font-medium text-slate-700">
                                            {formatDate(
                                                request.request_date
                                            )}
                                        </p>
                                    </div>

                                </div>


                                <div className="flex items-center gap-3">

                                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
                                        <UserRound size={17} />
                                    </div>

                                    <div>
                                        <p className="text-xs text-slate-400">
                                            Assigned Technician
                                        </p>

                                        <p className="mt-0.5 text-sm font-medium text-slate-700">
                                            {request.technician?.technician_name ||
                                                "Not assigned yet"}
                                        </p>
                                    </div>

                                </div>

                            </div>


                            {/* Details Action */}
                            <div className="mt-5 flex justify-end border-t border-slate-100 pt-5">

                                <Link
                                    to={`/customer/requests/${request.request_uuid}`}
                                    className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
                                >
                                    View Details
                                    <ArrowRight size={17} />
                                </Link>

                            </div>

                        </div>

                    ))}

                </div>

            )}

        </div>
    );
}

export default MyRequests;