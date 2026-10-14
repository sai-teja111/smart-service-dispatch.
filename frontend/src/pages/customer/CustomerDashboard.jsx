
import {
    AlertCircle,
    ArrowRight,
    CalendarDays,
    CheckCircle2,
    ClipboardList,
    Clock3,
    Download,
    FileText,
    Loader2,
    Plus,
    RefreshCw,
    Sparkles,
    Wrench,
} from "lucide-react";

import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getMyServiceRequests } from "../../api/serviceRequests";
import {
    getCustomerReports,
    downloadCustomerReportsPdf,
} from "../../api/reports";
import { useAuth } from "../../context/AuthContext";

const STATUS_STYLES = {
    OPEN: "border-blue-200 bg-blue-50 text-blue-700",
    PENDING: "border-amber-200 bg-amber-50 text-amber-700",
    ASSIGNED: "border-violet-200 bg-violet-50 text-violet-700",
    IN_PROGRESS: "border-indigo-200 bg-indigo-50 text-indigo-700",
    COMPLETED: "border-emerald-200 bg-emerald-50 text-emerald-700",
    CANCELLED: "border-red-200 bg-red-50 text-red-700",
};

function getGreeting() {
    const hour = new Date().getHours();

    if (hour >= 5 && hour < 12) return "Good morning";
    if (hour >= 12 && hour < 17) return "Good afternoon";
    if (hour >= 17 && hour < 21) return "Good evening";

    return "Good night";
}

function getStatusLabel(status) {
    return String(status || "UNKNOWN")
        .replaceAll("_", " ")
        .toLowerCase()
        .replace(/\b\w/g, (character) => character.toUpperCase());
}

function getStatusStyle(status) {
    return (
        STATUS_STYLES[String(status || "").toUpperCase()] ||
        "border-slate-200 bg-slate-50 text-slate-600"
    );
}

function StatCard({
    title,
    value,
    description,
    icon: Icon,
    iconStyle,
}) {
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

function CustomerDashboard() {
    const { user } = useAuth();

    const [requests, setRequests] = useState([]);
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [reportsError, setReportsError] = useState("");
    const [downloadingPdf, setDownloadingPdf] = useState(false);

    const customerName =
        user?.name || user?.customer_name || "Customer";

    const firstName = customerName.trim().split(/\s+/)[0];

    const welcomeMessage = user?.first_login
        ? "We're glad you're here. Let's get the service you need."
        : "Welcome back! Here's what's happening with your services.";

    const loadRequests = useCallback(async () => {
        try {
            setLoading(true);
            setError("");

            const response = await getMyServiceRequests();

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
                    : "We couldn't retrieve your service requests. Please try again."
            );
        } finally {
            setLoading(false);
        }
    }, []);

    const loadCustomerReports = useCallback(async () => {
        try {
            setReportsError("");

            const response = await getCustomerReports();

            setReports(
                Array.isArray(response?.reports)
                    ? response.reports
                    : []
            );
        } catch (reportError) {
            const detail = reportError?.response?.data?.detail;

            setReportsError(
                typeof detail === "string"
                    ? detail
                    : "Unable to load your service reports."
            );
        }
    }, []);

    const handleDownloadPdf = async () => {
        try {
            setDownloadingPdf(true);
            setReportsError("");

            const pdfBlob = await downloadCustomerReportsPdf();

            const downloadUrl = window.URL.createObjectURL(
                new Blob([pdfBlob], {
                    type: "application/pdf",
                })
            );

            const link = document.createElement("a");
            link.href = downloadUrl;
            link.download = "customer_service_reports.pdf";

            document.body.appendChild(link);
            link.click();
            link.remove();

            window.setTimeout(() => {
                window.URL.revokeObjectURL(downloadUrl);
            }, 1000);
        } catch (downloadError) {
            const detail = downloadError?.response?.data?.detail;

            setReportsError(
                typeof detail === "string"
                    ? detail
                    : "Unable to download your PDF. Please try again."
            );
        } finally {
            setDownloadingPdf(false);
        }
    };

    useEffect(() => {
        loadRequests();
        loadCustomerReports();
    }, [loadRequests, loadCustomerReports]);

    const activeRequests = requests.filter((request) =>
        ["OPEN", "PENDING", "ASSIGNED"].includes(
            String(request.status || "").toUpperCase()
        )
    ).length;

    const inProgressRequests = requests.filter(
        (request) =>
            String(request.status || "").toUpperCase() === "IN_PROGRESS"
    ).length;

    const completedRequests = requests.filter(
        (request) =>
            String(request.status || "").toUpperCase() === "COMPLETED"
    ).length;

    const recentRequests = [...requests]
        .sort((a, b) => {
            const dateA = new Date(
                a.request_date || a.created_at || 0
            ).getTime();

            const dateB = new Date(
                b.request_date || b.created_at || 0
            ).getTime();

            return dateB - dateA;
        })
        .slice(0, 3);

    const recentReports = [...reports]
        .sort((a, b) => {
            const dateA = new Date(a.request_date || 0).getTime();
            const dateB = new Date(b.request_date || 0).getTime();

            return dateB - dateA;
        })
        .slice(0, 5);

    return (
        <div className="min-h-full bg-slate-50/70">
            <main className="mx-auto w-full max-w-[1600px] px-4 py-6 sm:px-6 sm:py-8 lg:px-8">

                {/* Welcome section */}
                <section className="relative mb-8 overflow-hidden rounded-2xl border border-blue-100 bg-linear-to-br from-white via-white to-blue-50/80 p-6 shadow-sm sm:p-8">
                    <div className="pointer-events-none absolute -right-12 -top-16 h-48 w-48 rounded-full bg-blue-100/50 blur-3xl" />

                    <div className="relative flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
                        <div className="max-w-2xl">
                            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700">
                                <Sparkles size={14} />
                                Customer Portal
                            </div>

                            <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                                {getGreeting()}, {firstName}!
                            </h1>

                            <p className="mt-3 text-sm leading-6 text-slate-600 sm:text-base">
                                {welcomeMessage}
                            </p>

                            <p className="mt-1 text-sm leading-6 text-slate-500">
                                Manage your service requests and track your
                                technician assignments, all in one place.
                            </p>
                        </div>

                        <div className="flex shrink-0 items-center justify-center sm:pr-4">
                            <div className="flex h-20 w-20 items-center justify-center rounded-2xl border border-blue-100 bg-white text-blue-600 shadow-sm sm:h-24 sm:w-24">
                                <Wrench
                                    size={39}
                                    strokeWidth={1.5}
                                    className="-rotate-12"
                                />
                            </div>
                        </div>
                    </div>
                </section>

                {/* Dashboard content */}
                {loading ? (
                    <section
                        className="rounded-2xl border border-slate-200 bg-white p-12 text-center shadow-sm"
                        role="status"
                    >
                        <Loader2
                            size={30}
                            className="mx-auto animate-spin text-blue-600"
                        />

                        <h2 className="mt-4 font-semibold text-slate-900">
                            Loading your dashboard
                        </h2>

                        <p className="mt-1 text-sm text-slate-500">
                            Fetching your latest service requests...
                        </p>
                    </section>
                ) : error ? (
                    <section className="rounded-2xl border border-red-200 bg-white p-8 text-center shadow-sm">
                        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-red-50 text-red-600">
                            <AlertCircle size={24} />
                        </div>

                        <h2 className="mt-4 font-semibold text-slate-900">
                            Unable to load your dashboard
                        </h2>

                        <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-slate-500">
                            {error}
                        </p>

                        <button
                            type="button"
                            onClick={loadRequests}
                            className="mt-5 inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-100"
                        >
                            <RefreshCw size={16} />
                            Try again
                        </button>
                    </section>
                ) : (
                    <>
                        {/* Statistics */}
                        <section aria-label="Service request statistics">
                            <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
                                <div>
                                    <h2 className="text-lg font-bold text-slate-900">
                                        Your Overview
                                    </h2>

                                    <p className="mt-1 text-sm text-slate-500">
                                        A quick look at your service activity.
                                    </p>
                                </div>

                                <span className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-500">
                                    {requests.length} total{" "}
                                    {requests.length === 1
                                        ? "request"
                                        : "requests"}
                                </span>
                            </div>

                            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
                                <StatCard
                                    title="Total Requests"
                                    value={requests.length}
                                    description="All your service requests"
                                    icon={ClipboardList}
                                    iconStyle="bg-blue-50 text-blue-600"
                                />

                                <StatCard
                                    title="Active Requests"
                                    value={activeRequests}
                                    description="Open, pending or assigned"
                                    icon={Clock3}
                                    iconStyle="bg-amber-50 text-amber-600"
                                />

                                <StatCard
                                    title="In Progress"
                                    value={inProgressRequests}
                                    description="Services being handled"
                                    icon={Wrench}
                                    iconStyle="bg-indigo-50 text-indigo-600"
                                />

                                <StatCard
                                    title="Completed"
                                    value={completedRequests}
                                    description="Successfully completed"
                                    icon={CheckCircle2}
                                    iconStyle="bg-emerald-50 text-emerald-600"
                                />
                            </div>
                        </section>

                        {/* Create service request */}
                        <section className="mt-8 overflow-hidden rounded-2xl border border-blue-100 bg-white shadow-sm">
                            <div className="flex flex-col gap-5 p-6 sm:flex-row sm:items-center sm:justify-between sm:p-7">
                                <div className="flex items-start gap-4">
                                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                                        <Plus size={24} />
                                    </div>

                                    <div>
                                        <h2 className="text-lg font-bold text-slate-900 sm:text-xl">
                                            Need a service?
                                        </h2>

                                        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                                            Tell us what needs fixing. Our
                                            intelligent matching system helps
                                            identify a suitable service and
                                            technician.
                                        </p>
                                    </div>
                                </div>

                                <Link
                                    to="/customer/request"
                                    className="inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-100"
                                >
                                    <Plus size={18} />
                                    Book a Service
                                    <ArrowRight size={16} />
                                </Link>
                            </div>

                            <div className="flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-slate-100 bg-slate-50/70 px-6 py-3.5 text-xs text-slate-500 sm:px-7">
                                <span className="inline-flex items-center gap-2">
                                    <CheckCircle2
                                        size={15}
                                        className="text-emerald-600"
                                    />
                                    Easy request creation
                                </span>

                                <span className="inline-flex items-center gap-2">
                                    <ClipboardList
                                        size={15}
                                        className="text-blue-600"
                                    />
                                    Track service progress
                                </span>
                            </div>
                        </section>

                        {/* My Reports */}
                        <section className="mt-8 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                            <div className="flex flex-col gap-4 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:justify-between sm:p-6">
                                <div className="flex items-start gap-3">
                                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                                        <FileText size={22} />
                                    </div>

                                    <div>
                                        <h2 className="text-lg font-bold text-slate-900">
                                            My Reports
                                        </h2>

                                        <p className="mt-1 text-sm text-slate-500">
                                            Review your service history and
                                            download your personal report.
                                        </p>

                                        <p className="mt-2 text-xs font-medium text-slate-500">
                                            {reports.length} service{" "}
                                            {reports.length === 1
                                                ? "report"
                                                : "reports"}
                                        </p>
                                    </div>
                                </div>

                                <button
                                    type="button"
                                    onClick={handleDownloadPdf}
                                    disabled={downloadingPdf}
                                    className="inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-100 disabled:cursor-not-allowed disabled:opacity-60"
                                >
                                    {downloadingPdf ? (
                                        <Loader2
                                            size={17}
                                            className="animate-spin"
                                        />
                                    ) : (
                                        <Download size={17} />
                                    )}

                                    {downloadingPdf
                                        ? "Downloading..."
                                        : "Download PDF"}
                                </button>
                            </div>

                            {reportsError && (
                                <div
                                    className="m-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 sm:m-6"
                                    role="alert"
                                >
                                    <div className="flex items-start gap-2">
                                        <AlertCircle
                                            size={18}
                                            className="mt-0.5 shrink-0"
                                        />
                                        <span>{reportsError}</span>
                                    </div>

                                    <button
                                        type="button"
                                        onClick={loadCustomerReports}
                                        className="mt-2 font-semibold underline underline-offset-2"
                                    >
                                        Retry loading reports
                                    </button>
                                </div>
                            )}

                            {!reportsError && recentReports.length === 0 ? (
                                <div className="px-6 py-10 text-center">
                                    <ClipboardList
                                        size={28}
                                        className="mx-auto text-slate-400"
                                    />

                                    <h3 className="mt-3 font-semibold text-slate-900">
                                        No reports available yet
                                    </h3>

                                    <p className="mt-1 text-sm text-slate-500">
                                        Your service reports will appear here
                                        when you create service requests.
                                    </p>
                                </div>
                            ) : (
                                recentReports.length > 0 && (
                                    <div className="divide-y divide-slate-100">
                                        {recentReports.map((report) => (
                                            <div
                                                key={report.request_uuid}
                                                className="flex flex-col gap-3 p-5 sm:flex-row sm:items-start sm:justify-between sm:p-6"
                                            >
                                                <div className="min-w-0">
                                                    <div className="flex flex-wrap items-center gap-2">
                                                        <h3 className="font-semibold text-slate-900">
                                                            {report.service ||
                                                                "Service Request"}
                                                        </h3>

                                                        <span
                                                            className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${getStatusStyle(report.status)}`}
                                                        >
                                                            {getStatusLabel(
                                                                report.status
                                                            )}
                                                        </span>
                                                    </div>

                                                    <p className="mt-1.5 text-sm leading-6 text-slate-500">
                                                        {report.problem_description ||
                                                            "No description provided."}
                                                    </p>

                                                    <div className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-xs text-slate-500">
                                                        <span className="inline-flex items-center gap-1.5">
                                                            <CalendarDays
                                                                size={14}
                                                            />
                                                            {report.request_date
                                                                ? new Date(
                                                                      report.request_date
                                                                  ).toLocaleDateString()
                                                                : "Date unavailable"}
                                                        </span>

                                                        <span>
                                                            Priority:{" "}
                                                            <span className="font-medium text-slate-700">
                                                                {getStatusLabel(
                                                                    report.priority ||
                                                                        "Not specified"
                                                                )}
                                                            </span>
                                                        </span>
                                                    </div>

                                                    <p className="mt-2 text-xs text-slate-500">
                                                        Technician:{" "}
                                                        <span className="font-medium text-slate-700">
                                                            {report.technician
                                                                ?.technician_name ||
                                                                "Not assigned"}
                                                        </span>
                                                    </p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )
                            )}

                            {reports.length > 5 && (
                                <div className="border-t border-slate-100 bg-slate-50/60 px-5 py-3 text-center sm:px-6">
                                    <p className="text-xs text-slate-500">
                                        Showing the 5 most recent reports.
                                        Download the PDF for your complete
                                        service history.
                                    </p>
                                </div>
                            )}
                        </section>

                        {/* Recent requests */}
                        <section className="mt-8 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                            <div className="flex flex-col gap-3 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:justify-between sm:p-6">
                                <div>
                                    <h2 className="text-lg font-bold text-slate-900">
                                        Recent Requests
                                    </h2>

                                    <p className="mt-1 text-sm text-slate-500">
                                        Stay up to date with your latest services.
                                    </p>
                                </div>

                                <Link
                                    to="/customer/requests"
                                    className="inline-flex items-center gap-1 self-start text-sm font-semibold text-blue-600 transition hover:text-blue-800 sm:self-center"
                                >
                                    View all requests
                                    <ArrowRight size={16} />
                                </Link>
                            </div>

                            {recentRequests.length === 0 ? (
                                <div className="px-6 py-12 text-center">
                                    <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-500">
                                        <ClipboardList size={25} />
                                    </div>

                                    <h3 className="mt-4 font-semibold text-slate-900">
                                        No service requests yet
                                    </h3>

                                    <p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-slate-500">
                                        Once you create a request, you can track
                                        its status and technician assignment here.
                                    </p>

                                    <Link
                                        to="/customer/request"
                                        className="mt-5 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700"
                                    >
                                        <Plus size={17} />
                                        Create your first request
                                    </Link>
                                </div>
                            ) : (
                                <div className="divide-y divide-slate-100">
                                    {recentRequests.map((request) => {
                                        const status = String(
                                            request.status || "UNKNOWN"
                                        ).toUpperCase();

                                        return (
                                            <Link
                                                key={request.request_uuid}
                                                to={`/customer/requests/${request.request_uuid}`}
                                                className="group block p-5 transition hover:bg-slate-50/80 focus:outline-none focus:bg-blue-50/50 sm:p-6"
                                            >
                                                <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                                                    <div className="flex min-w-0 items-start gap-4">
                                                        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-blue-100 bg-blue-50 text-blue-600">
                                                            <ClipboardList
                                                                size={20}
                                                            />
                                                        </div>

                                                        <div className="min-w-0 flex-1">
                                                            <div className="flex flex-wrap items-center gap-2">
                                                                <h3 className="font-semibold text-slate-900 transition group-hover:text-blue-700">
                                                                    {request.service ||
                                                                        request.skill_name ||
                                                                        "Service Request"}
                                                                </h3>

                                                                <span
                                                                    className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${getStatusStyle(status)}`}
                                                                >
                                                                    {getStatusLabel(
                                                                        status
                                                                    )}
                                                                </span>
                                                            </div>

                                                            <p className="mt-1.5 line-clamp-2 text-sm leading-5 text-slate-500">
                                                                {request.problem_description ||
                                                                    "No additional description provided."}
                                                            </p>

                                                            <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-500">
                                                                {request.request_date && (
                                                                    <span className="inline-flex items-center gap-1.5">
                                                                        <CalendarDays
                                                                            size={14}
                                                                        />
                                                                        {new Date(
                                                                            request.request_date
                                                                        ).toLocaleDateString(
                                                                            undefined,
                                                                            {
                                                                                day: "numeric",
                                                                                month: "short",
                                                                                year: "numeric",
                                                                            }
                                                                        )}
                                                                    </span>
                                                                )}

                                                                {request.priority && (
                                                                    <span>
                                                                        Priority:{" "}
                                                                        <span className="font-medium text-slate-700">
                                                                            {getStatusLabel(
                                                                                request.priority
                                                                            )}
                                                                        </span>
                                                                    </span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <span className="inline-flex shrink-0 items-center gap-1.5 self-start text-sm font-semibold text-blue-600 transition group-hover:translate-x-0.5 lg:self-center">
                                                        View details
                                                        <ArrowRight size={16} />
                                                    </span>
                                                </div>
                                            </Link>
                                        );
                                    })}
                                </div>
                            )}

                            {requests.length > 3 && (
                                <div className="border-t border-slate-100 bg-slate-50/60 px-5 py-3 text-center sm:px-6">
                                    <Link
                                        to="/customer/requests"
                                        className="text-sm font-medium text-slate-600 transition hover:text-blue-600"
                                    >
                                        View {requests.length - 3} more{" "}
                                        {requests.length - 3 === 1
                                            ? "request"
                                            : "requests"}
                                    </Link>
                                </div>
                            )}
                        </section>
                    </>
                )}
            </main>
        </div>
    );
}

export default CustomerDashboard;
