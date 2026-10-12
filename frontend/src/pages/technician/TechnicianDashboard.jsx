
import {
    AlertCircle,
    ArrowRight,
    CalendarDays,
    CheckCircle2,
    ClipboardList,
    Clock3,
    Loader2,
    MapPin,
    Phone,
    RefreshCw,
    Sparkles,
    UserRound,
    Wrench,
} from "lucide-react";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { getAssignedServiceRequests } from "../../api/technician";
import { useAuth } from "../../context/AuthContext";

function normalizeStatus(status) {
    return String(status || "UNKNOWN")
        .trim()
        .toUpperCase()
        .replace(/\s+/g, "_");
}

function getStatusClasses(status) {
    switch (normalizeStatus(status)) {
        case "PENDING":
            return "border-amber-200 bg-amber-50 text-amber-700";

        case "ASSIGNED":
            return "border-violet-200 bg-violet-50 text-violet-700";

        case "IN_PROGRESS":
            return "border-blue-200 bg-blue-50 text-blue-700";

        case "COMPLETED":
            return "border-emerald-200 bg-emerald-50 text-emerald-700";

        case "OPEN":
            return "border-slate-200 bg-slate-50 text-slate-700";

        case "CANCELLED":
            return "border-red-200 bg-red-50 text-red-700";

        default:
            return "border-slate-200 bg-slate-50 text-slate-600";
    }
}

function getPriorityClasses(priority) {
    switch (String(priority || "").trim().toUpperCase()) {
        case "HIGH":
            return "border-red-200 bg-red-50 text-red-700";

        case "MEDIUM":
            return "border-amber-200 bg-amber-50 text-amber-700";

        case "LOW":
            return "border-emerald-200 bg-emerald-50 text-emerald-700";

        default:
            return "border-slate-200 bg-slate-50 text-slate-600";
    }
}

function formatLabel(value) {
    if (!value) return "Unknown";

    return String(value)
        .replace(/_/g, " ")
        .toLowerCase()
        .replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatDate(dateValue) {
    if (!dateValue) return "—";

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) return "—";

    return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    });
}

function getLocation(customer) {
    if (!customer) return "Location unavailable";

    const parts = [
        customer.area,
        customer.city,
        customer.pincode,
    ].filter(Boolean);

    return parts.length ? parts.join(", ") : "Location unavailable";
}

function StatCard({ title, value, description, icon: Icon, iconStyle }) {
    return (
        <div className="group rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm transition duration-200 hover:-translate-y-1 hover:shadow-md sm:p-6">
            <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                    <p className="text-sm font-medium text-slate-500">
                        {title}
                    </p>

                    <p className="mt-3 text-3xl font-bold tracking-tight text-slate-900">
                        {value}
                    </p>

                    <p className="mt-2 text-xs leading-5 text-slate-500">
                        {description}
                    </p>
                </div>

                <div
                    className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${iconStyle}`}
                >
                    <Icon size={21} strokeWidth={1.9} />
                </div>
            </div>
        </div>
    );
}

export default function TechnicianDashboard() {
    const { user } = useAuth();

    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const technicianName =
        user?.name || user?.technician_name || "Technician";

    const firstName = technicianName.trim().split(/\s+/)[0];

    const hour = new Date().getHours();

    const greeting =
        hour >= 5 && hour < 12
            ? "Good morning"
            : hour >= 12 && hour < 17
              ? "Good afternoon"
              : hour >= 17 && hour < 21
                ? "Good evening"
                : "Good night";

    const welcomeMessage = user?.first_login
        ? "We're glad to have you on the team. Let's make every service visit count."
        : "Welcome back! Here's an overview of your assigned work.";

    const loadAssignedRequests = useCallback(async () => {
        try {
            setLoading(true);
            setError("");

            const response = await getAssignedServiceRequests();

            setRequests(
                Array.isArray(response?.service_requests)
                    ? response.service_requests
                    : []
            );
        } catch (requestError) {
            const detail = requestError?.response?.data?.detail;

            setError(
                typeof detail === "string"
                    ? detail
                    : "We couldn't retrieve your assigned requests. Please try again."
            );
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadAssignedRequests();
    }, [loadAssignedRequests]);

    const statistics = useMemo(() => {
        const statuses = requests.map((request) =>
            normalizeStatus(request.status)
        );

        return {
            total: requests.length,

            pending: statuses.filter((status) =>
                ["OPEN", "PENDING", "ASSIGNED"].includes(status)
            ).length,

            inProgress: statuses.filter(
                (status) => status === "IN_PROGRESS"
            ).length,

            completed: statuses.filter(
                (status) => status === "COMPLETED"
            ).length,
        };
    }, [requests]);

    const activeRequests = useMemo(
        () =>
            requests.filter((request) =>
                ["OPEN", "PENDING", "ASSIGNED"].includes(
                    normalizeStatus(request.status)
                )
            ),
        [requests]
    );

    const sortedRequests = useMemo(() => {
        const priorityOrder = {
            HIGH: 0,
            MEDIUM: 1,
            LOW: 2,
        };

        return [...requests].sort((a, b) => {
            const statusA = normalizeStatus(a.status);
            const statusB = normalizeStatus(b.status);

            // Put unfinished work before completed requests.
            const completedA = statusA === "COMPLETED" ? 1 : 0;
            const completedB = statusB === "COMPLETED" ? 1 : 0;

            if (completedA !== completedB) {
                return completedA - completedB;
            }

            // Within unfinished work, show higher priorities first.
            const priorityA =
                priorityOrder[String(a.priority || "").toUpperCase()] ?? 3;
            const priorityB =
                priorityOrder[String(b.priority || "").toUpperCase()] ?? 3;

            if (priorityA !== priorityB) {
                return priorityA - priorityB;
            }

            // Within the same priority, show the newest request first.
            const dateA = new Date(
                a.request_date || a.created_at || 0
            ).getTime();

            const dateB = new Date(
                b.request_date || b.created_at || 0
            ).getTime();

            return dateB - dateA;
        });
    }, [requests]);

    return (
        <div className="min-h-full bg-slate-50/70">
            <main className="mx-auto w-full max-w-[1600px] space-y-8 px-4 py-6 sm:px-6 sm:py-8 lg:px-8">

                {/* Welcome section */}
                <section className="relative overflow-hidden rounded-2xl border border-blue-100 bg-linear-to-br from-white via-white to-blue-50/80 p-6 shadow-sm sm:p-8">
                    <div className="pointer-events-none absolute -right-12 -top-16 h-48 w-48 rounded-full bg-blue-100/50 blur-3xl" />

                    <div className="relative flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
                        <div className="max-w-2xl">
                            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700">
                                <Sparkles size={14} />
                                Technician Work Center
                            </div>

                            <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                                {greeting}, {firstName}!
                            </h1>

                            <p className="mt-3 text-sm leading-6 text-slate-600 sm:text-base">
                                {welcomeMessage}
                            </p>

                            <p className="mt-1 text-sm leading-6 text-slate-500">
                                Review assignments, prioritize your jobs, and
                                keep every service request moving forward.
                            </p>
                        </div>

                        <div className="flex shrink-0 items-center justify-center sm:pr-4">
                            <div className="flex h-20 w-20 items-center justify-center rounded-2xl border border-blue-100 bg-white text-blue-600 shadow-sm sm:h-24 sm:w-24">
                                <Wrench
                                    size={40}
                                    strokeWidth={1.5}
                                    className="-rotate-12"
                                />
                            </div>
                        </div>
                    </div>
                </section>

                {/* Statistics */}
                <section aria-label="Technician work statistics">
                    <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
                        <div>
                            <h2 className="text-lg font-bold text-slate-900">
                                Work Overview
                            </h2>

                            <p className="mt-1 text-sm text-slate-500">
                                A quick look at your assigned workload.
                            </p>
                        </div>

                        <span className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-500">
                            {loading
                                ? "Updating..."
                                : `${statistics.total} ${
                                      statistics.total === 1
                                          ? "request"
                                          : "requests"
                                  }`}
                        </span>
                    </div>

                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
                        <StatCard
                            title="Total Assigned"
                            value={loading ? "—" : statistics.total}
                            description="All requests assigned to you"
                            icon={ClipboardList}
                            iconStyle="bg-blue-50 text-blue-600"
                        />

                        <StatCard
                            title="Pending"
                            value={loading ? "—" : statistics.pending}
                            description="Open, pending or assigned jobs"
                            icon={Clock3}
                            iconStyle="bg-amber-50 text-amber-600"
                        />

                        <StatCard
                            title="In Progress"
                            value={loading ? "—" : statistics.inProgress}
                            description="Jobs currently being handled"
                            icon={Wrench}
                            iconStyle="bg-indigo-50 text-indigo-600"
                        />

                        <StatCard
                            title="Completed"
                            value={loading ? "—" : statistics.completed}
                            description="Successfully completed jobs"
                            icon={CheckCircle2}
                            iconStyle="bg-emerald-50 text-emerald-600"
                        />
                    </div>
                </section>

                {/* Priority summary */}
                {!loading && !error && (
                    <section className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:p-6">
                        <div className="flex items-start gap-3">
                            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
                                <Clock3 size={20} />
                            </div>

                            <div>
                                <h2 className="font-semibold text-slate-900">
                                    Your workload
                                </h2>

                                <p className="mt-1 text-sm leading-5 text-slate-500">
                                    {activeRequests.length > 0
                                        ? `You have ${activeRequests.length} unfinished ${
                                              activeRequests.length === 1
                                                  ? "request"
                                                  : "requests"
                                          } to work on.`
                                        : "You have no unfinished assigned requests. Great work!"}
                                </p>
                            </div>
                        </div>

                        <a
                            href="#assigned-requests"
                            className="inline-flex min-h-10 shrink-0 items-center justify-center gap-2 self-start rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 sm:self-center"
                        >
                            View assignments
                            <ArrowRight size={16} />
                        </a>
                    </section>
                )}

                {/* Assigned requests */}
                <section
                    id="assigned-requests"
                    className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
                >
                    <div className="flex flex-col gap-3 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:justify-between sm:p-6">
                        <div>
                            <h2 className="text-lg font-bold text-slate-900">
                                Assigned Service Requests
                            </h2>

                            <p className="mt-1 text-sm text-slate-500">
                                Prioritized assignments and customer details.
                            </p>
                        </div>

                        <div className="flex flex-wrap items-center gap-2">
                            {!loading && !error && (
                                <span className="rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-600">
                                    {statistics.total}{" "}
                                    {statistics.total === 1
                                        ? "request"
                                        : "requests"}
                                </span>
                            )}

                            <button
                                type="button"
                                onClick={loadAssignedRequests}
                                disabled={loading}
                                className="inline-flex min-h-9 items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                                <RefreshCw
                                    size={15}
                                    className={
                                        loading ? "animate-spin" : ""
                                    }
                                />
                                Refresh
                            </button>
                        </div>
                    </div>

                    {/* Loading */}
                    {loading && (
                        <div
                            className="flex min-h-64 flex-col items-center justify-center px-6 text-center"
                            role="status"
                        >
                            <Loader2
                                size={28}
                                className="animate-spin text-blue-600"
                            />

                            <p className="mt-4 font-semibold text-slate-900">
                                Loading your assignments
                            </p>

                            <p className="mt-1 text-sm text-slate-500">
                                Retrieving your latest service requests...
                            </p>
                        </div>
                    )}

                    {/* Error */}
                    {!loading && error && (
                        <div className="px-6 py-12 text-center">
                            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-red-50 text-red-600">
                                <AlertCircle size={24} />
                            </div>

                            <h3 className="mt-4 font-semibold text-slate-900">
                                Unable to load assignments
                            </h3>

                            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
                                {error}
                            </p>

                            <button
                                type="button"
                                onClick={loadAssignedRequests}
                                className="mt-5 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-100"
                            >
                                <RefreshCw size={16} />
                                Try again
                            </button>
                        </div>
                    )}

                    {/* Empty */}
                    {!loading && !error && requests.length === 0 && (
                        <div className="px-6 py-14 text-center">
                            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-500">
                                <ClipboardList size={26} />
                            </div>

                            <h3 className="mt-4 font-semibold text-slate-900">
                                No assigned requests yet
                            </h3>

                            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
                                New service requests assigned to you will
                                appear here. Check back when your workload
                                changes.
                            </p>
                        </div>
                    )}

                    {/* Request cards */}
                    {!loading && !error && sortedRequests.length > 0 && (
                        <div className="divide-y divide-slate-100">
                            {sortedRequests.map((request) => {
                                const status = normalizeStatus(request.status);

                                const customer = request.customer;

                                const serviceName =
                                    request.service ||
                                    request.skill_name ||
                                    "Service Request";

                                return (
                                    <article
                                        key={
                                            request.request_uuid ||
                                            request.request_id
                                        }
                                        className="p-5 transition hover:bg-slate-50/70 sm:p-6"
                                    >
                                        <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
                                            <div className="min-w-0 flex-1">
                                                <div className="flex flex-wrap items-center gap-2">
                                                    <h3 className="text-base font-semibold text-slate-900">
                                                        {serviceName}
                                                    </h3>

                                                    <span
                                                        className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${getPriorityClasses(
                                                            request.priority
                                                        )}`}
                                                    >
                                                        {formatLabel(
                                                            request.priority ||
                                                                "Normal"
                                                        )}
                                                    </span>

                                                    <span
                                                        className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${getStatusClasses(
                                                            status
                                                        )}`}
                                                    >
                                                        {formatLabel(status)}
                                                    </span>
                                                </div>

                                                <p className="mt-2 line-clamp-2 text-sm leading-6 text-slate-600">
                                                    {request.problem_description ||
                                                        "No problem description provided."}
                                                </p>

                                                <div className="mt-4 grid grid-cols-1 gap-3 text-sm text-slate-500 sm:grid-cols-2">
                                                    <div className="flex min-w-0 items-center gap-2">
                                                        <UserRound
                                                            size={16}
                                                            className="shrink-0 text-slate-400"
                                                        />

                                                        <span className="truncate">
                                                            {customer?.customer_name ||
                                                                "Customer unavailable"}
                                                        </span>
                                                    </div>

                                                    <div className="flex min-w-0 items-center gap-2">
                                                        <MapPin
                                                            size={16}
                                                            className="shrink-0 text-slate-400"
                                                        />

                                                        <span className="wrap-break-word">
                                                            {getLocation(
                                                                customer
                                                            )}
                                                        </span>
                                                    </div>

                                                    <div className="flex min-w-0 items-center gap-2">
                                                        <Phone
                                                            size={16}
                                                            className="shrink-0 text-slate-400"
                                                        />

                                                        <span className="break-all">
                                                            {customer?.phone ||
                                                                "Phone unavailable"}
                                                        </span>
                                                    </div>

                                                    <div className="flex items-center gap-2">
                                                        <CalendarDays
                                                            size={16}
                                                            className="shrink-0 text-slate-400"
                                                        />

                                                        <span>
                                                            {formatDate(
                                                                request.request_date
                                                            )}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="flex shrink-0 xl:pl-4">
                                                <Link
                                                    to={`/technician/requests/${request.request_uuid}`}
                                                    className="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-100 sm:w-auto"
                                                >
                                                    View Details
                                                    <ArrowRight size={16} />
                                                </Link>
                                            </div>
                                        </div>
                                    </article>
                                );
                            })}
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
}
