import {
    AlertCircle,
    ArrowLeft,
    CalendarDays,
    CheckCircle2,
    Clock3,
    History,
    Loader2,
    MessageSquare,
    Wrench,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../../api/axios";
import { getAssignedServiceRequests } from "../../api/technician";


function getStatusStyle(status) {
    if (status === "COMPLETED") {
        return "bg-green-50 text-green-700 border-green-200";
    }

    if (status === "IN PROGRESS" || status === "IN_PROGRESS") {
        return "bg-blue-50 text-blue-700 border-blue-200";
    }

    if (status === "PENDING") {
        return "bg-yellow-50 text-yellow-700 border-yellow-200";
    }

    return "bg-slate-50 text-slate-700 border-slate-200";
}


function formatStatus(status) {
    if (status === "IN_PROGRESS") {
        return "In Progress";
    }

    if (status === "IN PROGRESS") {
        return "In Progress";
    }

    if (status === "COMPLETED") {
        return "Completed";
    }

    if (status === "PENDING") {
        return "Pending";
    }

    return status;
}


function formatDate(dateValue) {
    if (!dateValue) {
        return "—";
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
        return "—";
    }

    return date.toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}


function ServiceHistory() {
    const [historyItems, setHistoryItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function loadServiceHistory() {
            try {
                setLoading(true);
                setError("");

                const response = await getAssignedServiceRequests();

                const requests = Array.isArray(
                    response?.service_requests
                )
                    ? response.service_requests
                    : [];

                if (requests.length === 0) {
                    setHistoryItems([]);
                    return;
                }

                const historyResponses = await Promise.all(
                    requests.map(async (request) => {
                        try {
                            const historyResponse = await api.get(
                                `/service-history/${request.request_uuid}`
                            );

                            const history =
                                Array.isArray(
                                    historyResponse.data?.history
                                )
                                    ? historyResponse.data.history
                                    : [];

                            return history.map((record) => ({
                                ...record,
                                request_uuid:
                                    request.request_uuid,
                                service: request.service,
                                problem_description:
                                    request.problem_description,
                                customer:
                                    request.customer,
                            }));
                        } catch {
                            return [];
                        }
                    })
                );

                const combinedHistory =
                    historyResponses.flat();

                combinedHistory.sort(
                    (first, second) =>
                        new Date(second.updated_time) -
                        new Date(first.updated_time)
                );

                setHistoryItems(combinedHistory);
            } catch (requestError) {
                console.error(
                    "Failed to load service history:",
                    requestError
                );

                setError(
                    "Unable to load service history. Please try again."
                );
            } finally {
                setLoading(false);
            }
        }

        loadServiceHistory();
    }, []);


    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-slate-100">
                <div className="flex items-center gap-3 text-slate-600">
                    <Loader2
                        size={24}
                        className="animate-spin text-blue-600"
                    />
                    <span>Loading service history...</span>
                </div>
            </div>
        );
    }


    return (
        <div className="min-h-screen bg-slate-100 px-6 py-8">
            <div className="mx-auto max-w-6xl">

                {/* Header */}
                <div className="mb-8 flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">

                    <div className="flex items-start gap-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50">
                            <History
                                size={25}
                                className="text-blue-600"
                            />
                        </div>

                        <div>
                            <h1 className="text-3xl font-bold text-slate-900">
                                Service History
                            </h1>

                            <p className="mt-1 text-slate-500">
                                View the status history of your assigned service requests.
                            </p>
                        </div>
                    </div>

                    <div className="rounded-xl border border-slate-200 bg-white px-5 py-3 shadow-sm">
                        <p className="text-sm text-slate-500">
                            History Records
                        </p>

                        <p className="text-2xl font-bold text-slate-900">
                            {historyItems.length}
                        </p>
                    </div>
                </div>


                {/* Error */}
                {error && (
                    <div className="mb-6 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
                        <AlertCircle
                            size={22}
                            className="mt-0.5 shrink-0"
                        />

                        <div>
                            <p className="font-semibold">
                                Unable to load history
                            </p>

                            <p className="mt-1 text-sm">
                                {error}
                            </p>
                        </div>
                    </div>
                )}


                {/* Empty State */}
                {!error && historyItems.length === 0 && (
                    <div className="rounded-2xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm">

                        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100">
                            <History
                                size={30}
                                className="text-slate-400"
                            />
                        </div>

                        <h2 className="mt-5 text-xl font-semibold text-slate-900">
                            No service history yet
                        </h2>

                        <p className="mx-auto mt-2 max-w-md text-slate-500">
                            Status changes for your assigned service requests will appear here.
                        </p>

                        <Link
                            to="/technician/requests"
                            className="mt-6 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-700"
                        >
                            <ArrowLeft size={18} />
                            View Assigned Requests
                        </Link>
                    </div>
                )}


                {/* History List */}
                {!error && historyItems.length > 0 && (
                    <div className="space-y-5">

                        {historyItems.map(
                            (item, index) => (
                                <div
                                    key={`${item.request_uuid}-${item.updated_time}-${index}`}
                                    className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
                                >

                                    {/* Top */}
                                    <div className="flex flex-col gap-4 border-b border-slate-100 pb-5 md:flex-row md:items-start md:justify-between">

                                        <div>
                                            <div className="flex flex-wrap items-center gap-3">

                                                <div className="flex items-center gap-2">
                                                    <Wrench
                                                        size={20}
                                                        className="text-blue-600"
                                                    />

                                                    <h2 className="text-lg font-bold text-slate-900">
                                                        {item.service}
                                                    </h2>
                                                </div>

                                                <span
                                                    className={`rounded-full border px-3 py-1 text-xs font-semibold ${getStatusStyle(
                                                        item.new_status
                                                    )}`}
                                                >
                                                    {formatStatus(
                                                        item.new_status
                                                    )}
                                                </span>
                                            </div>

                                            <p className="mt-2 text-sm text-slate-500">
                                                Request ID:{" "}
                                                {item.request_uuid}
                                            </p>
                                        </div>

                                        <div className="flex items-center gap-2 text-sm text-slate-500">
                                            <CalendarDays
                                                size={17}
                                            />

                                            {formatDate(
                                                item.updated_time
                                            )}
                                        </div>
                                    </div>


                                    {/* Status Change */}
                                    <div className="mt-5 grid gap-4 md:grid-cols-2">

                                        <div className="rounded-xl bg-slate-50 p-4">
                                            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                                                Previous Status
                                            </p>

                                            <div className="mt-2">
                                                <span
                                                    className={`inline-flex rounded-full border px-3 py-1 text-sm font-semibold ${getStatusStyle(
                                                        item.old_status
                                                    )}`}
                                                >
                                                    {formatStatus(
                                                        item.old_status
                                                    )}
                                                </span>
                                            </div>
                                        </div>


                                        <div className="rounded-xl bg-slate-50 p-4">
                                            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                                                New Status
                                            </p>

                                            <div className="mt-2">
                                                <span
                                                    className={`inline-flex rounded-full border px-3 py-1 text-sm font-semibold ${getStatusStyle(
                                                        item.new_status
                                                    )}`}
                                                >
                                                    {formatStatus(
                                                        item.new_status
                                                    )}
                                                </span>
                                            </div>
                                        </div>
                                    </div>


                                    {/* Remarks */}
                                    <div className="mt-5 rounded-xl border border-slate-100 bg-white">

                                        <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3">
                                            <MessageSquare
                                                size={17}
                                                className="text-slate-400"
                                            />

                                            <span className="text-sm font-semibold text-slate-700">
                                                Remarks
                                            </span>
                                        </div>

                                        <div className="px-4 py-4">
                                            <p className="text-sm leading-6 text-slate-600">
                                                {item.remarks ||
                                                    "No remarks added for this status update."}
                                            </p>
                                        </div>
                                    </div>


                                    {/* Customer */}
                                    {item.customer && (
                                        <div className="mt-5 flex flex-col gap-3 rounded-xl bg-blue-50 p-4 md:flex-row md:items-center md:justify-between">

                                            <div>
                                                <p className="text-xs font-semibold uppercase tracking-wide text-blue-500">
                                                    Customer
                                                </p>

                                                <p className="mt-1 font-semibold text-slate-900">
                                                    {
                                                        item.customer
                                                            .customer_name
                                                    }
                                                </p>
                                            </div>

                                            <div className="text-sm text-slate-600">
                                                {
                                                    item.customer
                                                        .city
                                                }
                                                ,{" "}
                                                {
                                                    item.customer
                                                        .area
                                                }
                                            </div>
                                        </div>
                                    )}

                                </div>
                            )
                        )}

                    </div>
                )}

            </div>
        </div>
    );
}

export default ServiceHistory;