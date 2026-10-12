import {
    AlertCircle,
    ArrowLeft,
    CalendarDays,
    CheckCircle2,
    Clock3,
    Loader2,
    MapPin,
    Phone,
    UserRound,
    Wrench,
} from "lucide-react";

import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
    getAssignedServiceRequest,
    updateServiceRequestStatus,
} from "../../api/technician";


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


function formatDateTime(dateValue) {
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


function getCustomerLocation(customer) {
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


export default function TechnicianRequestDetails() {
    const { requestUuid } = useParams();
    const navigate = useNavigate();

    const [request, setRequest] = useState(null);
    const [loading, setLoading] = useState(true);
    const [updating, setUpdating] = useState(false);

    const [error, setError] = useState("");
    const [updateError, setUpdateError] = useState("");
    const [successMessage, setSuccessMessage] = useState("");

    const [remarks, setRemarks] = useState("");


    useEffect(() => {
        let isMounted = true;

        async function loadRequest() {
            try {
                setLoading(true);
                setError("");

                const response =
                    await getAssignedServiceRequest(
                        requestUuid
                    );

                if (!isMounted) {
                    return;
                }

                setRequest(response);
            } catch (err) {
                if (!isMounted) {
                    return;
                }

                setError(
                    err?.response?.data?.detail ||
                        "Unable to load this service request."
                );
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        }

        loadRequest();

        return () => {
            isMounted = false;
        };
    }, [requestUuid]);


    const handleStatusUpdate = async (newStatus) => {
        if (!request) {
            return;
        }

        try {
            setUpdating(true);
            setUpdateError("");
            setSuccessMessage("");

            const response =
                await updateServiceRequestStatus(
                    request.request_uuid,
                    newStatus,
                    remarks.trim() || null
                );

            setRequest((currentRequest) => ({
                ...currentRequest,
                status: response.new_status,
            }));

            setRemarks("");

            setSuccessMessage(
                response.message ||
                    "Service request status updated successfully."
            );
        } catch (err) {
            setUpdateError(
                err?.response?.data?.detail ||
                    "Unable to update the service request status."
            );
        } finally {
            setUpdating(false);
        }
    };


    if (loading) {
        return (
            <div className="flex min-h-70 items-center justify-center">
                <div className="flex items-center gap-3 text-slate-500">
                    <Loader2
                        size={22}
                        className="animate-spin"
                    />

                    <span className="text-sm">
                        Loading service request...
                    </span>
                </div>
            </div>
        );
    }


    if (error || !request) {
        return (
            <div className="space-y-5">

                <Link
                    to="/technician"
                    className="inline-flex items-center gap-2 text-sm font-semibold text-blue-600 transition hover:text-blue-700"
                >
                    <ArrowLeft size={17} />
                    Back to Dashboard
                </Link>

                <div className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-5 text-red-700">
                    <AlertCircle
                        size={21}
                        className="mt-0.5 shrink-0"
                    />

                    <div>
                        <p className="font-semibold">
                            Unable to load service request
                        </p>

                        <p className="mt-1 text-sm">
                            {error ||
                                "The requested service request could not be found."}
                        </p>
                    </div>
                </div>
            </div>
        );
    }


    const canStart =
        request.status === "PENDING";

    const canComplete =
        request.status === "IN PROGRESS" ||
        request.status === "IN_PROGRESS";


    return (
        <div className="space-y-6">

            {/* =====================================================
                BACK
            ====================================================== */}

            <Link
                to="/technician"
                className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 transition hover:text-blue-600"
            >
                <ArrowLeft size={17} />
                Back to Dashboard
            </Link>


            {/* =====================================================
                PAGE HEADER
            ====================================================== */}

            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">

                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">

                    <div className="flex items-start gap-4">

                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-700">
                            <Wrench size={23} />
                        </div>

                        <div>
                            <div className="flex flex-wrap items-center gap-2">

                                <h1 className="text-2xl font-bold text-slate-900">
                                    {request.service ||
                                        "Service Request"}
                                </h1>

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

                            <p className="mt-2 break-all text-xs text-slate-400">
                                Request ID:{" "}
                                {request.request_uuid}
                            </p>
                        </div>

                    </div>

                    <div className="flex items-center gap-2 text-sm text-slate-500">
                        <CalendarDays size={17} />
                        <span>
                            {formatDate(
                                request.request_date
                            )}
                        </span>
                    </div>

                </div>

            </div>


            {/* =====================================================
                SUCCESS MESSAGE
            ====================================================== */}

            {successMessage && (
                <div className="flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-emerald-700">

                    <CheckCircle2
                        size={20}
                        className="mt-0.5 shrink-0"
                    />

                    <div>
                        <p className="font-semibold">
                            Status updated
                        </p>

                        <p className="mt-1 text-sm">
                            {successMessage}
                        </p>
                    </div>

                </div>
            )}


            {/* =====================================================
                UPDATE ERROR
            ====================================================== */}

            {updateError && (
                <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">

                    <AlertCircle
                        size={20}
                        className="mt-0.5 shrink-0"
                    />

                    <div>
                        <p className="font-semibold">
                            Status update failed
                        </p>

                        <p className="mt-1 text-sm">
                            {updateError}
                        </p>
                    </div>

                </div>
            )}


            <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">

                {/* =================================================
                    REQUEST DETAILS
                ================================================== */}

                <div className="space-y-6 xl:col-span-2">

                    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">

                        <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-700">
                                <ClipboardListIcon />
                            </div>

                            <div>
                                <h2 className="text-lg font-bold text-slate-900">
                                    Service Request
                                </h2>

                                <p className="text-sm text-slate-500">
                                    Details provided by the customer
                                </p>
                            </div>
                        </div>

                        <div className="mt-6">

                            <p className="text-sm font-semibold text-slate-500">
                                Problem Description
                            </p>

                            <div className="mt-2 rounded-xl bg-slate-50 p-4">
                                <p className="text-sm leading-6 text-slate-700">
                                    {request.problem_description ||
                                        "No problem description provided."}
                                </p>
                            </div>

                        </div>

                        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">

                            <div className="rounded-xl border border-slate-200 p-4">
                                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                                    Service
                                </p>

                                <p className="mt-2 font-semibold text-slate-900">
                                    {request.service}
                                </p>
                            </div>

                            <div className="rounded-xl border border-slate-200 p-4">
                                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                                    Priority
                                </p>

                                <span
                                    className={`mt-2 inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${getPriorityClasses(
                                        request.priority
                                    )}`}
                                >
                                    {request.priority ||
                                        "Normal"}
                                </span>
                            </div>

                            <div className="rounded-xl border border-slate-200 p-4">
                                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                                    Current Status
                                </p>

                                <span
                                    className={`mt-2 inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${getStatusClasses(
                                        request.status
                                    )}`}
                                >
                                    {formatStatus(
                                        request.status
                                    )}
                                </span>
                            </div>

                            <div className="rounded-xl border border-slate-200 p-4">
                                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                                    Request Date
                                </p>

                                <p className="mt-2 font-semibold text-slate-900">
                                    {formatDateTime(
                                        request.request_date
                                    )}
                                </p>
                            </div>

                        </div>

                    </div>


                    {/* =================================================
                        CUSTOMER DETAILS
                    ================================================== */}

                    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">

                        <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-700">
                                <UserRound size={20} />
                            </div>

                            <div>
                                <h2 className="text-lg font-bold text-slate-900">
                                    Customer Details
                                </h2>

                                <p className="text-sm text-slate-500">
                                    Customer information for this request
                                </p>
                            </div>
                        </div>

                        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">

                            <div>
                                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                                    Customer Name
                                </p>

                                <p className="mt-1 font-semibold text-slate-900">
                                    {request.customer
                                        ?.customer_name ||
                                        "Unavailable"}
                                </p>
                            </div>

                            <div>
                                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                                    Phone
                                </p>

                                <a
                                    href={
                                        request.customer?.phone
                                            ? `tel:${request.customer.phone}`
                                            : undefined
                                    }
                                    className="mt-1 inline-flex items-center gap-2 font-semibold text-blue-600 hover:text-blue-700"
                                >
                                    <Phone size={15} />
                                    {request.customer
                                        ?.phone ||
                                        "Unavailable"}
                                </a>
                            </div>

                            <div className="sm:col-span-2">
                                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                                    Service Location
                                </p>

                                <div className="mt-1 flex items-start gap-2">
                                    <MapPin
                                        size={17}
                                        className="mt-0.5 shrink-0 text-slate-400"
                                    />

                                    <p className="font-semibold text-slate-900">
                                        {getCustomerLocation(
                                            request.customer
                                        )}
                                    </p>
                                </div>
                            </div>

                        </div>

                    </div>

                </div>


                {/* =================================================
                    STATUS ACTIONS
                ================================================== */}

                <div className="xl:col-span-1">

                    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6 xl:sticky xl:top-24">

                        <div className="flex items-center gap-3">

                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-700">
                                <Clock3 size={20} />
                            </div>

                            <div>
                                <h2 className="text-lg font-bold text-slate-900">
                                    Update Status
                                </h2>

                                <p className="text-sm text-slate-500">
                                    Manage request progress
                                </p>
                            </div>

                        </div>


                        <div className="mt-6">

                            <label
                                htmlFor="remarks"
                                className="text-sm font-semibold text-slate-700"
                            >
                                Remarks
                                <span className="ml-1 font-normal text-slate-400">
                                    (optional)
                                </span>
                            </label>

                            <textarea
                                id="remarks"
                                value={remarks}
                                onChange={(event) =>
                                    setRemarks(
                                        event.target.value
                                    )
                                }
                                rows={4}
                                disabled={
                                    updating ||
                                    request.status ===
                                        "COMPLETED"
                                }
                                placeholder="Add remarks about the service progress..."
                                className="mt-2 w-full resize-none rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-50 disabled:text-slate-400"
                            />

                        </div>


                        <div className="mt-5 space-y-3">

                            {canStart && (
                                <button
                                    type="button"
                                    onClick={() =>
                                        handleStatusUpdate(
                                            "IN PROGRESS"
                                        )
                                    }
                                    disabled={updating}
                                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                                >
                                    {updating ? (
                                        <Loader2
                                            size={18}
                                            className="animate-spin"
                                        />
                                    ) : (
                                        <Wrench size={18} />
                                    )}

                                    {updating
                                        ? "Updating..."
                                        : "Start Service"}
                                </button>
                            )}


                            {canComplete && (
                                <button
                                    type="button"
                                    onClick={() =>
                                        handleStatusUpdate(
                                            "COMPLETED"
                                        )
                                    }
                                    disabled={updating}
                                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
                                >
                                    {updating ? (
                                        <Loader2
                                            size={18}
                                            className="animate-spin"
                                        />
                                    ) : (
                                        <CheckCircle2
                                            size={18}
                                        />
                                    )}

                                    {updating
                                        ? "Updating..."
                                        : "Mark as Completed"}
                                </button>
                            )}


                            {request.status ===
                                "COMPLETED" && (
                                <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-center">

                                    <CheckCircle2
                                        size={22}
                                        className="mx-auto text-emerald-600"
                                    />

                                    <p className="mt-2 text-sm font-semibold text-emerald-800">
                                        Service Completed
                                    </p>

                                    <p className="mt-1 text-xs text-emerald-700">
                                        This request has already
                                        been completed.
                                    </p>

                                </div>
                            )}


                            {request.status !==
                                "PENDING" &&
                                request.status !==
                                    "IN PROGRESS" &&
                                request.status !==
                                    "IN_PROGRESS" &&
                                request.status !==
                                    "COMPLETED" && (
                                    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-center">

                                        <p className="text-sm font-semibold text-slate-700">
                                            No status action available
                                        </p>

                                    </div>
                                )}

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
}


function ClipboardListIcon() {
    return (
        <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="h-5 w-5"
            aria-hidden="true"
        >
            <rect
                width="8"
                height="4"
                x="8"
                y="2"
                rx="1"
            />

            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />

            <path d="M8 12h8" />
            <path d="M8 16h8" />
        </svg>
    );
}