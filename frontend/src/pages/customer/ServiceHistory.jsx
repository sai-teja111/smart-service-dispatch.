import {
    AlertCircle,
    CalendarDays,
    CheckCircle2,
    ClipboardList,
    Clock3,
    History,
    Loader2,
    UserRound,
} from "lucide-react";

import { useEffect, useState } from "react";

import {
    getMyServiceRequests,
    getServiceHistory,
} from "../../api/serviceRequests";


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


function getHistoryDotStyles(status) {
    switch (status) {
        case "COMPLETED":
            return "bg-emerald-600";

        case "IN_PROGRESS":
            return "bg-indigo-600";

        case "PENDING":
            return "bg-amber-500";

        case "OPEN":
            return "bg-blue-600";

        default:
            return "bg-slate-500";
    }
}


function ServiceHistory() {
    const [requests, setRequests] = useState([]);
    const [histories, setHistories] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");


    useEffect(() => {
        let isMounted = true;

        async function loadHistory() {
            try {
                setLoading(true);
                setError("");

                const response =
                    await getMyServiceRequests();

                const serviceRequests = Array.isArray(
                    response?.service_requests
                )
                    ? response.service_requests
                    : [];

                if (!isMounted) {
                    return;
                }

                setRequests(serviceRequests);

                if (serviceRequests.length === 0) {
                    return;
                }

                const historyResults =
                    await Promise.all(
                        serviceRequests.map(
                            async (request) => {
                                try {
                                    const history =
                                        await getServiceHistory(
                                            request.request_uuid
                                        );

                                    return {
                                        requestUuid:
                                            request.request_uuid,
                                        history,
                                    };
                                } catch {
                                    return {
                                        requestUuid:
                                            request.request_uuid,
                                        history: null,
                                    };
                                }
                            }
                        )
                    );

                if (!isMounted) {
                    return;
                }

                const historyMap = {};

                historyResults.forEach(
                    ({ requestUuid, history }) => {
                        historyMap[requestUuid] =
                            history;
                    }
                );

                setHistories(historyMap);
            } catch (error) {
                if (!isMounted) {
                    return;
                }

                const message =
                    error?.response?.data?.detail ||
                    "Unable to load your service history.";

                setError(message);
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        }

        loadHistory();

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
                        Loading service history
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                        Retrieving your service activity.
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
                        Unable to load service history
                    </h2>

                    <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                        {error}
                    </p>

                </div>

            </div>
        );
    }


    if (requests.length === 0) {
        return (
            <div className="space-y-6">

                <div>
                    <p className="text-sm font-medium text-blue-600">
                        Customer Portal
                    </p>

                    <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
                        Service History
                    </h1>

                    <p className="mt-1 text-sm text-slate-500">
                        View the history of your service requests.
                    </p>
                </div>


                <div className="rounded-2xl border border-slate-200 bg-white p-10 shadow-sm">

                    <div className="flex min-h-70 flex-col items-center justify-center text-center">

                        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                            <History size={30} />
                        </div>

                        <h2 className="mt-5 text-xl font-bold text-slate-900">
                            No service history yet
                        </h2>

                        <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                            Your service activity and status updates
                            will appear here after you create a service
                            request.
                        </p>

                    </div>

                </div>

            </div>
        );
    }


    return (
        <div className="space-y-6">

            {/* Page Header */}
            <div>

                <p className="text-sm font-medium text-blue-600">
                    Customer Portal
                </p>

                <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
                    Service History
                </h1>

                <p className="mt-1 text-sm text-slate-500">
                    View the status changes and activity for your service requests.
                </p>

            </div>


            {/* History Cards */}
            <div className="space-y-6">

                {requests.map((request) => {

                    const historyData =
                        histories[request.request_uuid];

                    const historyRecords =
                        Array.isArray(
                            historyData?.history
                        )
                            ? historyData.history
                            : [];

                    return (
                        <div
                            key={request.request_uuid}
                            className="rounded-2xl border border-slate-200 bg-white shadow-sm"
                        >

                            {/* Request Header */}
                            <div className="border-b border-slate-100 p-6">

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
                                            {formatStatus(
                                                request.status
                                            )}
                                        </span>

                                        {request.priority && (
                                            <span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-600">
                                                {request.priority} Priority
                                            </span>
                                        )}

                                    </div>

                                </div>


                                <div className="mt-5 rounded-xl bg-slate-50 p-4">

                                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                                        Problem Description
                                    </p>

                                    <p className="mt-2 text-sm leading-6 text-slate-700">
                                        {request.problem_description}
                                    </p>

                                </div>

                            </div>


                            {/* Request Information */}
                            <div className="grid gap-4 border-b border-slate-100 p-6 sm:grid-cols-2">

                                <div className="flex items-center gap-3">

                                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
                                        <CalendarDays size={17} />
                                    </div>

                                    <div>

                                        <p className="text-xs text-slate-400">
                                            Requested On
                                        </p>

                                        <p className="mt-1 text-sm font-medium text-slate-700">
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

                                        <p className="mt-1 text-sm font-medium text-slate-700">
                                            {request.technician
                                                ?.technician_name ||
                                                "Not assigned yet"}
                                        </p>

                                    </div>

                                </div>

                            </div>


                            {/* Timeline */}
                            <div className="p-6">

                                <div className="flex items-center gap-3">

                                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                                        <History size={18} />
                                    </div>

                                    <div>

                                        <h3 className="font-semibold text-slate-900">
                                            Status History
                                        </h3>

                                        <p className="text-xs text-slate-500">
                                            {historyData?.history_count ||
                                                0}{" "}
                                            status update
                                            {historyData?.history_count ===
                                            1
                                                ? ""
                                                : "s"}
                                        </p>

                                    </div>

                                </div>


                                {historyRecords.length === 0 ? (

                                    <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-5">

                                        <p className="text-sm font-medium text-slate-700">
                                            No status history found.
                                        </p>

                                        <p className="mt-1 text-sm leading-6 text-slate-500">
                                            There are currently no recorded
                                            status changes for this request.
                                        </p>

                                    </div>

                                ) : (

                                    <div className="mt-6">

                                        {historyRecords.map(
                                            (record, index) => {

                                                const isLast =
                                                    index ===
                                                    historyRecords.length -
                                                        1;

                                                return (
                                                    <div
                                                        key={`${request.request_uuid}-${record.updated_time}-${index}`}
                                                        className="relative flex gap-4"
                                                    >

                                                        {!isLast && (
                                                            <div className="absolute left-4 top-8 h-full w-px bg-slate-200" />
                                                        )}


                                                        <div
                                                            className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-white ${getHistoryDotStyles(
                                                                record.new_status
                                                            )}`}
                                                        >
                                                            <CheckCircle2
                                                                size={16}
                                                            />
                                                        </div>


                                                        <div className="min-w-0 flex-1 pb-7">

                                                            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">

                                                                <p className="text-sm font-semibold text-slate-900">
                                                                    {formatStatus(
                                                                        record.old_status
                                                                    )}{" "}
                                                                    →{" "}
                                                                    {formatStatus(
                                                                        record.new_status
                                                                    )}
                                                                </p>

                                                                <div className="flex items-center gap-1.5 text-xs text-slate-400">

                                                                    <Clock3
                                                                        size={
                                                                            14
                                                                        }
                                                                    />

                                                                    {formatDate(
                                                                        record.updated_time
                                                                    )}

                                                                </div>

                                                            </div>


                                                            {record.remarks && (
                                                                <div className="mt-2 rounded-lg bg-slate-50 px-3 py-2">

                                                                    <p className="text-sm leading-5 text-slate-600">
                                                                        {record.remarks}
                                                                    </p>

                                                                </div>
                                                            )}

                                                        </div>

                                                    </div>
                                                );
                                            }
                                        )}

                                    </div>

                                )}

                            </div>

                        </div>
                    );
                })}

            </div>

        </div>
    );
}

export default ServiceHistory;