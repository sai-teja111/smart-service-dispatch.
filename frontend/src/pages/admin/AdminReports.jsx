import { useEffect, useState } from "react";
import {
    FileDown,
    Users,
    UserRoundCog,
    ClipboardList,
    CheckCircle2,
    RefreshCw,
    FileText,
    AlertCircle,
    Eye,
    X,
    Search,
    ArrowLeft,
} from "lucide-react";

import { adminApi } from "../../api/axios";

function StatCard({ title, value, icon: Icon, description }) {
    return (
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-start justify-between gap-4">
                <div>
                    <p className="text-sm font-medium text-slate-500">
                        {title}
                    </p>
                    <h3 className="mt-2 text-3xl font-bold text-slate-900">
                        {value ?? "—"}
                    </h3>
                    <p className="mt-2 text-xs text-slate-500">
                        {description}
                    </p>
                </div>

                <div className="rounded-xl bg-indigo-50 p-3 text-indigo-600">
                    <Icon size={23} />
                </div>
            </div>
        </div>
    );
}

function ReportCard({
    title,
    description,
    filename,
    downloading,
    viewing,
    onDownload,
    onView,
    icon: Icon,
}) {
    return (
        <div className="flex flex-col justify-between gap-5 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div>
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                    <Icon size={25} />
                </div>

                <h3 className="text-lg font-semibold text-slate-900">
                    {title}
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                    {description}
                </p>

                <p className="mt-3 text-xs text-slate-400">
                    PDF file: {filename}
                </p>
            </div>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <button
                    type="button"
                    onClick={onView}
                    disabled={viewing}
                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-indigo-200 bg-white px-4 py-3 text-sm font-semibold text-indigo-700 transition hover:bg-indigo-50 disabled:cursor-not-allowed disabled:opacity-60"
                >
                    {viewing ? (
                        <RefreshCw size={17} className="animate-spin" />
                    ) : (
                        <Eye size={18} />
                    )}
                    {viewing ? "Loading..." : "View Report"}
                </button>

                <button
                    type="button"
                    onClick={onDownload}
                    disabled={downloading}
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                    {downloading ? (
                        <>
                            <RefreshCw size={17} className="animate-spin" />
                            Generating...
                        </>
                    ) : (
                        <>
                            <FileDown size={18} />
                            Download PDF
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}

function getReportColumns(rows) {
    const preferredColumns = [
        "customer_name",
        "technician_name",
        "name",
        "full_name",
        "phone",
        "email",
        "city",
        "area",
        "pincode",
        "approval_status",
        "availability",
        "workload",
        "rating",
        "total_requests",
        "assigned_requests",
        "completed_requests",
        "outstanding_requests",
        "verified_skills_count",
    ];

    const availableColumns = [
        ...new Set(rows.flatMap((row) => Object.keys(row))),
    ];

    return [
        ...preferredColumns.filter((column) =>
            availableColumns.includes(column)
        ),
        ...availableColumns.filter(
            (column) => !preferredColumns.includes(column)
        ),
    ];
}

function formatColumnName(value) {
    return value
        .replace(/_/g, " ")
        .replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatCellValue(value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    if (typeof value === "boolean") {
        return value ? "Yes" : "No";
    }

    if (typeof value === "object") {
        return JSON.stringify(value);
    }

    return String(value);
}

function ReportTable({ report, search, setSearch }) {
    const columns = getReportColumns(report.rows);

    const filteredRows = report.rows.filter((row) =>
        Object.values(row).some((value) =>
            formatCellValue(value)
                .toLowerCase()
                .includes(search.toLowerCase())
        )
    );

    return (
        <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="flex flex-col gap-4 border-b border-slate-200 p-5 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h2 className="text-xl font-bold text-slate-900">
                        {report.title}
                    </h2>
                    <p className="mt-1 text-sm text-slate-500">
                        {filteredRows.length} of {report.rows.length} records
                    </p>
                </div>

                <div className="relative w-full sm:max-w-sm">
                    <Search
                        size={18}
                        className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                    />
                    <input
                        type="search"
                        value={search}
                        onChange={(event) => setSearch(event.target.value)}
                        placeholder="Search report..."
                        className="w-full rounded-xl border border-slate-200 py-2.5 pl-10 pr-4 text-sm outline-none transition focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100"
                    />
                </div>
            </div>

            {report.rows.length === 0 ? (
                <div className="p-10 text-center">
                    <FileText
                        size={35}
                        className="mx-auto text-slate-300"
                    />
                    <p className="mt-3 font-semibold text-slate-700">
                        No records found
                    </p>
                    <p className="mt-1 text-sm text-slate-500">
                        This report currently has no records to display.
                    </p>
                </div>
            ) : columns.length === 0 ? (
                <div className="p-8 text-center text-sm text-slate-500">
                    The API returned records without displayable fields.
                </div>
            ) : filteredRows.length === 0 ? (
                <div className="p-8 text-center text-sm text-slate-500">
                    No records match your search.
                </div>
            ) : (
                <div className="max-h-150 overflow-auto">
                    <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
                        <thead className="sticky top-0 z-10 bg-slate-50">
                            <tr>
                                {columns.map((column) => (
                                    <th
                                        key={column}
                                        className="whitespace-nowrap px-5 py-3 font-semibold text-slate-600"
                                    >
                                        {formatColumnName(column)}
                                    </th>
                                ))}
                            </tr>
                        </thead>

                        <tbody className="divide-y divide-slate-100">
                            {filteredRows.map((row, index) => (
                                <tr
                                    key={
                                        row.customer_uuid ||
                                        row.technician_uuid ||
                                        row.id ||
                                        index
                                    }
                                    className="transition hover:bg-slate-50"
                                >
                                    {columns.map((column) => (
                                        <td
                                            key={column}
                                            className="max-w-xs px-5 py-4 text-slate-700"
                                        >
                                            <span className="wrap-break-word">
                                                {formatCellValue(row[column])}
                                            </span>
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </section>
    );
}

function AdminReports() {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [downloadingReport, setDownloadingReport] = useState("");
    const [viewingReport, setViewingReport] = useState("");
    const [activeReport, setActiveReport] = useState(null);
    const [search, setSearch] = useState("");
    const [error, setError] = useState("");

    const fetchSummary = async () => {
        setLoading(true);
        setError("");

        try {
            const response = await adminApi.get("/admin/reports/summary");
            setSummary(response.data);
        } catch (err) {
            console.error("Failed to load admin report summary:", err);

            setError(
                err.response?.data?.detail ||
                    "Unable to load report statistics. Please try again."
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSummary();
    }, []);

    const viewReport = async (reportType) => {
        const reports = {
            customers: {
                endpoint: "/admin/reports/customers",
                title: "Customer Report",
                collectionKey: "customers",
            },
            technicians: {
                endpoint: "/admin/reports/technicians",
                title: "Technician Report",
                collectionKey: "technicians",
            },
        };

        const report = reports[reportType];

        if (!report) {
            return;
        }

        setViewingReport(reportType);
        setError("");

        try {
            const response = await adminApi.get(report.endpoint);
            const rows = response.data?.[report.collectionKey];

            if (!Array.isArray(rows)) {
                throw new Error(
                    `The server returned an unexpected ${reportType} report format.`
                );
            }

            setActiveReport({
                type: reportType,
                title: report.title,
                rows,
            });
            setSearch("");
        } catch (err) {
            console.error("Failed to load report:", err);

            setError(
                err.response?.data?.detail ||
                    err.message ||
                    "Unable to load the report. Please try again."
            );
        } finally {
            setViewingReport("");
        }
    };

    const downloadPdf = async (reportType) => {
        const reports = {
            customers: {
                endpoint: "/admin/reports/customers/pdf",
                filename: "customer_report.pdf",
            },
            technicians: {
                endpoint: "/admin/reports/technicians/pdf",
                filename: "technician_report.pdf",
            },
        };

        const report = reports[reportType];

        if (!report) {
            return;
        }

        setDownloadingReport(reportType);
        setError("");

        try {
            const response = await adminApi.get(report.endpoint, {
                responseType: "blob",
            });

            const contentType = response.headers["content-type"] || "";

            if (!contentType.includes("application/pdf")) {
                throw new Error(
                    "The server did not return a PDF file. Please check the deployed endpoint."
                );
            }

            const blob = new Blob([response.data], {
                type: "application/pdf",
            });

            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");

            link.href = url;
            link.download = report.filename;

            document.body.appendChild(link);
            link.click();
            link.remove();

            // Delay revocation to allow the browser to begin downloading.
            window.setTimeout(() => {
                window.URL.revokeObjectURL(url);
            }, 1000);
        } catch (err) {
            console.error("PDF download failed:", err);

            let message =
                err.response?.data?.detail ||
                err.message ||
                "Unable to download the report. Please try again.";

            if (err.response?.data instanceof Blob) {
                try {
                    const errorText = await err.response.data.text();
                    const errorData = JSON.parse(errorText);
                    message = errorData.detail || message;
                } catch {
                    // Keep the original error message.
                }
            }

            setError(message);
        } finally {
            setDownloadingReport("");
        }
    };

    const summaryCards = [
        {
            title: "Total Customers",
            value: summary?.total_customers,
            icon: Users,
            description: "Registered customer accounts",
        },
        {
            title: "Total Technicians",
            value: summary?.total_technicians,
            icon: UserRoundCog,
            description: "Registered technician accounts",
        },
        {
            title: "Total Requests",
            value: summary?.total_requests,
            icon: ClipboardList,
            description: "Service requests recorded",
        },
        {
            title: "Completed Requests",
            value: summary?.completed_requests,
            icon: CheckCircle2,
            description: "Successfully completed requests",
        },
    ];

    const requestsByStatus = summary?.requests_by_status || {};
    const statusEntries = Object.entries(requestsByStatus);
    const totalRequests = Number(summary?.total_requests) || 0;

    return (
        <div className="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
            <div className="mx-auto max-w-7xl space-y-8">
                {/* PAGE HEADER */}
                <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                    <div>
                        <div className="flex items-center gap-2 text-sm font-medium text-indigo-600">
                            <FileText size={17} />
                            Admin / Reports
                        </div>

                        <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">
                            Reports & Analytics
                        </h1>

                        <p className="mt-2 text-sm text-slate-500">
                            View report records and download customer and
                            technician reports as PDFs.
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={fetchSummary}
                        disabled={loading}
                        className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-100 disabled:opacity-60"
                    >
                        <RefreshCw
                            size={17}
                            className={loading ? "animate-spin" : ""}
                        />
                        Refresh Statistics
                    </button>
                </div>

                {/* ERROR MESSAGE */}
                {error && (
                    <div
                        role="alert"
                        className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
                    >
                        <AlertCircle
                            size={20}
                            className="mt-0.5 shrink-0"
                        />

                        <div className="flex-1">
                            <p className="font-semibold">
                                Something went wrong
                            </p>
                            <p className="mt-1 wrap-break-word">{error}</p>
                        </div>

                        <button
                            type="button"
                            onClick={() => setError("")}
                            className="font-semibold hover:text-red-900"
                        >
                            Dismiss
                        </button>
                    </div>
                )}

                {/* REPORT TABLE */}
                {activeReport && (
                    <section className="space-y-4">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                            <button
                                type="button"
                                onClick={() => {
                                    setActiveReport(null);
                                    setSearch("");
                                }}
                                className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 transition hover:text-indigo-600"
                            >
                                <ArrowLeft size={17} />
                                Back to Reports
                            </button>

                            <div className="flex flex-wrap gap-2">
                                <button
                                    type="button"
                                    onClick={() =>
                                        downloadPdf(activeReport.type)
                                    }
                                    disabled={
                                        downloadingReport === activeReport.type
                                    }
                                    className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:opacity-60"
                                >
                                    {downloadingReport === activeReport.type ? (
                                        <RefreshCw
                                            size={17}
                                            className="animate-spin"
                                        />
                                    ) : (
                                        <FileDown size={17} />
                                    )}
                                    Download PDF
                                </button>

                                <button
                                    type="button"
                                    onClick={() =>
                                        viewReport(activeReport.type)
                                    }
                                    disabled={
                                        viewingReport === activeReport.type
                                    }
                                    className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
                                >
                                    <RefreshCw
                                        size={16}
                                        className={
                                            viewingReport === activeReport.type
                                                ? "animate-spin"
                                                : ""
                                        }
                                    />
                                    Refresh Report
                                </button>
                            </div>
                        </div>

                        <ReportTable
                            report={activeReport}
                            search={search}
                            setSearch={setSearch}
                        />
                    </section>
                )}

                {/* SUMMARY CARDS */}
                {!activeReport && (
                    <>
                        <section>
                            <div className="mb-4">
                                <h2 className="text-lg font-semibold text-slate-900">
                                    System Overview
                                </h2>
                                <p className="mt-1 text-sm text-slate-500">
                                    Current statistics from your admin dashboard.
                                </p>
                            </div>

                            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
                                {summaryCards.map((card) => (
                                    <StatCard
                                        key={card.title}
                                        {...card}
                                        value={
                                            loading
                                                ? "..."
                                                : card.value ?? 0
                                        }
                                    />
                                ))}
                            </div>
                        </section>

                        {/* REPORT ACTIONS */}
                        <section>
                            <div className="mb-4">
                                <h2 className="text-lg font-semibold text-slate-900">
                                    Customer & Technician Reports
                                </h2>
                                <p className="mt-1 text-sm text-slate-500">
                                    View report records before downloading
                                    the PDF.
                                </p>
                            </div>

                            <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
                                <ReportCard
                                    title="Customer Report"
                                    description="View customer information and service request statistics, or download the report as a PDF."
                                    filename="customer_report.pdf"
                                    icon={Users}
                                    downloading={
                                        downloadingReport === "customers"
                                    }
                                    viewing={viewingReport === "customers"}
                                    onView={() => viewReport("customers")}
                                    onDownload={() => downloadPdf("customers")}
                                />

                                <ReportCard
                                    title="Technician Report"
                                    description="View technician information, approval details, and service performance statistics, or download the report as a PDF."
                                    filename="technician_report.pdf"
                                    icon={UserRoundCog}
                                    downloading={
                                        downloadingReport === "technicians"
                                    }
                                    viewing={viewingReport === "technicians"}
                                    onView={() => viewReport("technicians")}
                                    onDownload={() =>
                                        downloadPdf("technicians")
                                    }
                                />
                            </div>
                        </section>

                        {/* REQUEST STATUS */}
                        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                            <div className="mb-6">
                                <h2 className="text-lg font-semibold text-slate-900">
                                    Service Request Status
                                </h2>
                                <p className="mt-1 text-sm text-slate-500">
                                    Distribution of requests by status.
                                </p>
                            </div>

                            {loading ? (
                                <div className="py-8 text-center text-sm text-slate-500">
                                    Loading request statistics...
                                </div>
                            ) : statusEntries.length > 0 ? (
                                <div className="space-y-5">
                                    {statusEntries.map(
                                        ([statusName, count]) => {
                                            const numericCount =
                                                Number(count) || 0;

                                            const percentage =
                                                totalRequests > 0
                                                    ? Math.min(
                                                          100,
                                                          (numericCount /
                                                              totalRequests) *
                                                              100
                                                      )
                                                    : 0;

                                            return (
                                                <div key={statusName}>
                                                    <div className="mb-2 flex items-center justify-between gap-3">
                                                        <span className="text-sm font-medium capitalize text-slate-700">
                                                            {statusName.replaceAll(
                                                                "_",
                                                                " "
                                                            )}
                                                        </span>

                                                        <span className="text-sm font-semibold text-slate-900">
                                                            {numericCount}
                                                        </span>
                                                    </div>

                                                    <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
                                                        <div
                                                            className="h-full rounded-full bg-indigo-600 transition-all duration-500"
                                                            style={{
                                                                width: `${percentage}%`,
                                                            }}
                                                        />
                                                    </div>
                                                </div>
                                            );
                                        }
                                    )}
                                </div>
                            ) : (
                                <div className="py-8 text-center">
                                    <ClipboardList
                                        size={32}
                                        className="mx-auto text-slate-300"
                                    />

                                    <p className="mt-3 text-sm font-medium text-slate-600">
                                        No request status data available.
                                    </p>
                                </div>
                            )}
                        </section>
                    </>
                )}
            </div>
        </div>
    );
}

export default AdminReports;
