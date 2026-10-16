
import {
    ArrowLeft,
    CalendarDays,
    CheckCircle2,
    ClipboardList,
    Clock3,
    Loader2,
    UserRound,
} from "lucide-react";

import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getServiceRequest } from "../../api/serviceRequests";


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
    switch (status?.toUpperCase()) {
        case "OPEN":
            return "bg-blue-50 text-blue-700 border-blue-200";

        case "PENDING":
            return "bg-amber-50 text-amber-700 border-amber-200";

        case "IN_PROGRESS":
        case "IN PROGRESS":
            return "bg-indigo-50 text-indigo-700 border-indigo-200";

        case "COMPLETED":
            return "bg-emerald-50 text-emerald-700 border-emerald-200";

        case "CANCELLED":
            return "bg-red-50 text-red-700 border-red-200";

        default:
            return "bg-slate-50 text-slate-700 border-slate-200";
    }
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


function getProgressSteps(status, technician) {
    const normalizedStatus = status?.toUpperCase();

    const hasTechnician = Boolean(technician);

    const completed = normalizedStatus === "COMPLETED";

    const inProgress =
        normalizedStatus === "IN_PROGRESS" ||
        normalizedStatus === "IN PROGRESS";

    const cancelled = normalizedStatus === "CANCELLED";

    // A technician is assigned when technician details are
    // present in the API response. In-progress and completed
    // requests also imply that assignment has already occurred.
    const technicianAssigned =
        hasTechnician ||
        inProgress ||
        completed;

    const steps = [
        {
            title: "Request Created",
            description: "Your service request has been created.",
            completed: true,
        },
        {
            title: "Technician Assigned",
            description: technicianAssigned
                ? technician?.technician_name
                    ? `Technician ${technician.technician_name} has been assigned.`
                    : "A suitable technician has been assigned."
                : "Waiting for technician assignment.",
            completed: technicianAssigned,
        },
        {
            title: "Service In Progress",
            description: completed
                ? "The technician completed the service."
                : "The technician will work on your service request.",
            completed: inProgress || completed,
        },
        {
            title: "Service Completed",
            description: "Your service request has been completed.",
            completed,
        },
    ];

    // A cancelled request should not display later stages as
    // completed simply because its previous status was advanced.
    if (cancelled) {
        return steps.map((step, index) => ({
            ...step,
            completed: index === 0,
        }));
    }

    return steps;
}


function ServiceRequestDetails() {
    const { requestUuid } = useParams();
    const navigate = useNavigate();

    const [request, setRequest] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");


    useEffect(() => {
        let isMounted = true;

        async function loadRequest() {
            try {
                setLoading(true);
                setError("");

                const response =
                    await getServiceRequest(requestUuid);

                if (!isMounted) {
                    return;
                }

                setRequest(response);
            } catch (error) {
                if (!isMounted) {
                    return;
                }

                const message =
                    error?.response?.data?.detail ||
                    "Unable to load this service request.";

                setError(message);
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        }

        if (requestUuid) {
            loadRequest();
        } else {
            setError("Service request ID is missing.");
            setLoading(false);
        }

        return () => {
            isMounted = false;
        };
    }, [requestUuid]);


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
                        Loading request details
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                        Please wait while we retrieve the service request.
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
                        <ClipboardList size={24} />
                    </div>

                    <h2 className="mt-4 text-lg font-bold text-slate-900">
                        Unable to load request
                    </h2>

                    <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                        {error}
                    </p>

                    <button
                        type="button"
                        onClick={() => navigate("/customer/requests")}
                        className="mt-6 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700"
                    >
                        <ArrowLeft size={18} />
                        Back to My Requests
                    </button>
                </div>
            </div>
        );
    }


    if (!request) {
        return null;
    }


    const progressSteps = getProgressSteps(
        request.status,
        request.technician
    );


    return (
        <div className="space-y-6">

            {/* Header */}
            <div>
                <Link
                    to="/customer/requests"
                    className="inline-flex items-center gap-2 text-sm font-medium text-slate-500 transition hover:text-blue-600"
                >
                    <ArrowLeft size={17} />
                    Back to My Requests
                </Link>

                <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                        <p className="text-sm font-medium text-blue-600">
                            Customer Portal
                        </p>

                        <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
                            Service Request Details
                        </h1>

                        <p className="mt-1 text-sm text-slate-500">
                            View the current status and details of your request.
                        </p>
                    </div>

                    <div className="flex flex-wrap gap-2">
                        <span
                            className={`rounded-full border px-3 py-1.5 text-xs font-semibold ${getStatusStyles(
                                request.status
                            )}`}
                        >
                            {formatStatus(request.status)}
                        </span>

                        {request.priority && (
                            <span
                                className={`rounded-full border px-3 py-1.5 text-xs font-semibold ${getPriorityStyles(
                                    request.priority
                                )}`}
                            >
                                {request.priority} Priority
                            </span>
                        )}
                    </div>
                </div>
            </div>


            {/* Main Details */}
            <div className="grid gap-6 lg:grid-cols-3">

                {/* Request Information */}
                <div className="space-y-6 lg:col-span-2">

                    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
                        <div className="border-b border-slate-100 p-6">
                            <div className="flex items-start gap-4">
                                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                                    <ClipboardList size={23} />
                                </div>

                                <div className="min-w-0">
                                    <h2 className="text-xl font-bold text-slate-900">
                                        {request.service}
                                    </h2>

                                    <p className="mt-1 break-all text-xs text-slate-400">
                                        Request ID: {request.request_uuid}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-6 p-6">
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                                    Problem Description
                                </p>

                                <div className="mt-3 rounded-xl bg-slate-50 p-4">
                                    <p className="text-sm leading-6 text-slate-700">
                                        {request.problem_description}
                                    </p>
                                </div>
                            </div>

                            <div className="grid gap-5 sm:grid-cols-2">
                                <div className="flex items-center gap-3">
                                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
                                        <CalendarDays size={18} />
                                    </div>

                                    <div>
                                        <p className="text-xs text-slate-400">
                                            Requested On
                                        </p>

                                        <p className="mt-1 text-sm font-medium text-slate-700">
                                            {formatDate(request.request_date)}
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3">
                                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
                                        <Clock3 size={18} />
                                    </div>

                                    <div>
                                        <p className="text-xs text-slate-400">
                                            Current Status
                                        </p>

                                        <p className="mt-1 text-sm font-medium text-slate-700">
                                            {formatStatus(request.status)}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>


                    {/* Technician */}
                    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                        <div className="flex items-center gap-3">
                            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                                <UserRound size={21} />
                            </div>

                            <div>
                                <h2 className="text-lg font-bold text-slate-900">
                                    Assigned Technician
                                </h2>

                                <p className="text-sm text-slate-500">
                                    Technician assigned to this request.
                                </p>
                            </div>
                        </div>

                        {request.technician ? (
                            <div className="mt-5 rounded-xl border border-slate-100 bg-slate-50 p-4">
                                <div className="flex items-center gap-4">
                                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-blue-600 text-lg font-bold text-white">
                                        {request.technician.technician_name
                                            ?.charAt(0)
                                            ?.toUpperCase() || "T"}
                                    </div>

                                    <div>
                                        <p className="font-semibold text-slate-900">
                                            {request.technician.technician_name}
                                        </p>

                                        <p className="mt-1 text-xs text-slate-400">
                                            Technician assigned to your service request
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="mt-5 rounded-xl border border-amber-100 bg-amber-50 p-4">
                                <p className="text-sm font-semibold text-amber-800">
                                    Technician not assigned yet
                                </p>

                                <p className="mt-1 text-sm leading-6 text-amber-700">
                                    We are still looking for a suitable technician for your request.
                                </p>
                            </div>
                        )}
                    </div>

                </div>


                {/* Progress */}
                <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                    <div>
                        <h2 className="text-lg font-bold text-slate-900">
                            Service Progress
                        </h2>

                        <p className="mt-1 text-sm text-slate-500">
                            Track the progress of your request.
                        </p>
                    </div>

                    <div className="mt-7">
                        {progressSteps.map((step, index) => (
                            <div
                                key={step.title}
                                className="relative flex gap-4"
                            >
                                {index < progressSteps.length - 1 && (
                                    <div
                                        className={`absolute left-4 top-8 h-full w-px ${
                                            step.completed &&
                                            progressSteps[index + 1].completed
                                                ? "bg-blue-500"
                                                : "bg-slate-200"
                                        }`}
                                    />
                                )}

                                <div
                                    className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border ${
                                        step.completed
                                            ? "border-blue-600 bg-blue-600 text-white"
                                            : "border-slate-200 bg-white text-slate-400"
                                    }`}
                                >
                                    {step.completed ? (
                                        <CheckCircle2 size={17} />
                                    ) : (
                                        <span className="text-xs font-semibold">
                                            {index + 1}
                                        </span>
                                    )}
                                </div>

                                <div className="pb-8">
                                    <p
                                        className={`text-sm font-semibold ${
                                            step.completed
                                                ? "text-slate-900"
                                                : "text-slate-400"
                                        }`}
                                    >
                                        {step.title}
                                    </p>

                                    <p className="mt-1 text-xs leading-5 text-slate-500">
                                        {step.description}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

            </div>

        </div>
    );
}

export default ServiceRequestDetails;
