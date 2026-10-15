import { useCallback, useEffect, useState } from "react";
import {
    Users,
    Wrench,
    Clock3,
    CheckCircle2,
    XCircle,
    ClipboardList,
    RefreshCw,
    AlertCircle,
    ChartNoAxesCombined,
} from "lucide-react";

import { getAdminReportSummary } from "../../api/admin";

const summaryCards = [
    {
        key: "total_customers",
        label: "Total Customers",
        icon: Users,
        color: "blue",
    },
    {
        key: "total_technicians",
        label: "Total Technicians",
        icon: Wrench,
        color: "violet",
    },
    {
        key: "pending_technicians",
        label: "Pending Approvals",
        icon: Clock3,
        color: "amber",
    },
    {
        key: "approved_technicians",
        label: "Approved Technicians",
        icon: CheckCircle2,
        color: "emerald",
    },
    {
        key: "rejected_technicians",
        label: "Rejected Technicians",
        icon: XCircle,
        color: "rose",
    },
    {
        key: "total_service_requests",
        label: "Total Service Requests",
        icon: ClipboardList,
        color: "cyan",
    },
];

const colorStyles = {
    blue: "bg-blue-50 text-blue-600",
    violet: "bg-violet-50 text-violet-600",
    amber: "bg-amber-50 text-amber-600",
    emerald: "bg-emerald-50 text-emerald-600",
    rose: "bg-rose-50 text-rose-600",
    cyan: "bg-cyan-50 text-cyan-600",
};

function formatStatus(status) {
    return String(status)
        .replaceAll("_", " ")
        .toLowerCase()
        .replace(/\b\w/g, (character) => character.toUpperCase());
}

function AdminDashboard() {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadSummary = useCallback(async () => {
        setLoading(true);
        setError("");

        try {
            const data = await getAdminReportSummary();
            setSummary(data);
        } catch (requestError) {
            if (requestError.response?.status === 401) {
                setError(
                    "Your Admin session is invalid or expired. Please sign in again."
                );
            } else if (requestError.response?.status === 403) {
                setError(
                    "You do not have permission to view this dashboard."
                );
            } else {
                setError(
                    requestError.response?.data?.detail ||
                    "Unable to load dashboard statistics. Please try again."
                );
            }
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadSummary();
    }, [loadSummary]);

    const completedRequests = summary?.completed_requests ?? 0;
    const totalRequests = summary?.total_service_requests ?? 0;

    const completionPercentage =
        totalRequests > 0
            ? Math.round((completedRequests / totalRequests) * 100)
            : 0;

    return (
        <div className="mx-auto max-w-7xl space-y-8">
            <section className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                <div>
                    <p className="text-sm font-medium text-indigo-600">
                        Overview
                    </p>

                    <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                        Admin Dashboard
                    </h1>

                    <p className="mt-2 text-sm text-slate-500">
                        Monitor customers, technician approvals, and service operations.
                    </p>
                </div>

                <button
                    type="button"
                    onClick={loadSummary}
                    disabled={loading}
                    className="inline-flex items-center justify-center gap-2 self-start rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60 sm:self-auto"
                >
                    <RefreshCw
                        size={16}
                        className={loading ? "animate-spin" : ""}
                    />
                    Refresh
                </button>
            </section>

            {error && (
                <div
                    role="alert"
                    className="flex flex-col gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 sm:flex-row sm:items-center sm:justify-between"
                >
                    <div className="flex items-start gap-3">
                        <AlertCircle size={20} className="mt-0.5 shrink-0" />
                        <p>{error}</p>
                    </div>

                    <button
                        type="button"
                        onClick={loadSummary}
                        className="self-start font-semibold underline sm:self-auto"
                    >
                        Try again
                    </button>
                </div>
            )}

            {loading && !summary ? (
                <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                    {summaryCards.map((card) => (
                        <div
                            key={card.key}
                            className="animate-pulse rounded-2xl border border-slate-200 bg-white p-6"
                        >
                            <div className="h-10 w-10 rounded-xl bg-slate-200" />
                            <div className="mt-5 h-4 w-32 rounded bg-slate-200" />
                            <div className="mt-3 h-8 w-20 rounded bg-slate-200" />
                        </div>
                    ))}
                </div>
            ) : summary ? (
                <>
                    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                        {summaryCards.map((card) => {
                            const Icon = card.icon;
                            const value = summary[card.key] ?? 0;

                            return (
                                <article
                                    key={card.key}
                                    className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md sm:p-6"
                                >
                                    <div className="flex items-start justify-between gap-4">
                                        <div>
                                            <p className="text-sm font-medium text-slate-500">
                                                {card.label}
                                            </p>

                                            <p className="mt-3 text-3xl font-bold tracking-tight text-slate-900">
                                                {value.toLocaleString()}
                                            </p>
                                        </div>

                                        <div
                                            className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${colorStyles[card.color]}`}
                                        >
                                            <Icon size={22} />
                                        </div>
                                    </div>
                                </article>
                            );
                        })}
                    </section>

                    <section className="grid gap-6 lg:grid-cols-2">
                        <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                            <div className="flex items-center gap-3">
                                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                                    <ChartNoAxesCombined size={21} />
                                </div>

                                <div>
                                    <h2 className="font-semibold text-slate-900">
                                        Service Request Progress
                                    </h2>
                                    <p className="mt-1 text-sm text-slate-500">
                                        Completed versus all requests
                                    </p>
                                </div>
                            </div>

                            <div className="mt-6 flex items-end justify-between gap-4">
                                <div>
                                    <p className="text-3xl font-bold text-slate-900">
                                        {completionPercentage}%
                                    </p>
                                    <p className="mt-1 text-sm text-slate-500">
                                        Completion rate
                                    </p>
                                </div>

                                <p className="text-sm text-slate-500">
                                    {completedRequests} of {totalRequests}
                                </p>
                            </div>

                            <div
                                className="mt-4 h-3 overflow-hidden rounded-full bg-slate-100"
                                role="progressbar"
                                aria-label="Service request completion rate"
                                aria-valuemin={0}
                                aria-valuemax={100}
                                aria-valuenow={completionPercentage}
                            >
                                <div
                                    className="h-full rounded-full bg-indigo-600 transition-all duration-500"
                                    style={{
                                        width: `${completionPercentage}%`,
                                    }}
                                />
                            </div>
                        </article>

                        <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                            <div>
                                <h2 className="font-semibold text-slate-900">
                                    Requests by Status
                                </h2>
                                <p className="mt-1 text-sm text-slate-500">
                                    Current distribution of service requests
                                </p>
                            </div>

                            <div className="mt-5 space-y-4">
                                {Object.entries(
                                    summary.requests_by_status ?? {}
                                ).length === 0 ? (
                                    <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">
                                        No service requests available yet.
                                    </p>
                                ) : (
                                    Object.entries(
                                        summary.requests_by_status ?? {}
                                    ).map(([status, count]) => {
                                        const percentage =
                                            totalRequests > 0
                                                ? Math.round(
                                                    (count / totalRequests) * 100
                                                )
                                                : 0;

                                        return (
                                            <div key={status}>
                                                <div className="mb-2 flex items-center justify-between gap-4 text-sm">
                                                    <span className="font-medium text-slate-700">
                                                        {formatStatus(status)}
                                                    </span>

                                                    <span className="font-semibold text-slate-900">
                                                        {count}
                                                    </span>
                                                </div>

                                                <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                                                    <div
                                                        className="h-full rounded-full bg-indigo-500 transition-all duration-500"
                                                        style={{
                                                            width: `${percentage}%`,
                                                        }}
                                                    />
                                                </div>
                                            </div>
                                        );
                                    })
                                )}
                            </div>
                        </article>
                    </section>
                </>
            ) : (
                !loading && (
                    <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center">
                        <p className="font-medium text-slate-700">
                            Dashboard data is unavailable.
                        </p>
                        <p className="mt-2 text-sm text-slate-500">
                            Use Refresh to try loading the statistics again.
                        </p>
                    </div>
                )
            )}
        </div>
    );
}

export default AdminDashboard;