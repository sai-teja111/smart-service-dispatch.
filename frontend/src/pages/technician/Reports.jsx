
import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  Users,
  UserRoundCheck,
  ClipboardList,
  CheckCircle2,
  Clock3,
  Star,
  RefreshCw,
  AlertCircle,
  Wrench,
  TrendingUp,
  Download,
} from "lucide-react";

import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
} from "recharts";

import { getReports } from "../../api/reports";
import api from "../../api/axios";

const STATUS_COLORS = [
  "#64748b",
  "#f59e0b",
  "#3b82f6",
  "#10b981",
];

function SummaryCard({ title, value, icon: Icon, description }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">
            {value ?? 0}
          </p>
          {description && (
            <p className="mt-1 text-xs text-gray-500">{description}</p>
          )}
        </div>

        <div className="rounded-lg bg-blue-50 p-3">
          <Icon size={22} className="text-blue-600" />
        </div>
      </div>
    </div>
  );
}

function ReportCard({ title, children }) {
  return (
    <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="mb-5 text-base font-semibold text-gray-900">
        {title}
      </h2>
      {children}
    </section>
  );
}

function formatRating(value) {
  if (value === null || value === undefined) {
    return "N/A";
  }

  return Number(value).toFixed(1);
}

export default function Reports() {
  const [reports, setReports] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");
  const [downloadError, setDownloadError] = useState("");

  const loadReports = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    setError("");

    try {
      const data = await getReports();
      setReports(data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load reports. Please try again."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  const handleDownloadPdf = async () => {
    setDownloading(true);
    setDownloadError("");

    try {
      const response = await api.get("/reports/pdf", {
        responseType: "blob",
      });

      const blob = new Blob([response.data], {
        type: "application/pdf",
      });

      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = downloadUrl;
      link.download = "technician_analytics_report.pdf";

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      setDownloadError(
        "Unable to download the PDF. Please try again."
      );
    } finally {
      setDownloading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, [loadReports]);

  if (loading) {
    return (
      <div className="flex min-h-64 items-center justify-center">
        <div className="text-center">
          <RefreshCw
            size={30}
            className="mx-auto animate-spin text-blue-600"
          />
          <p className="mt-3 text-sm text-gray-500">
            Loading reports...
          </p>
        </div>
      </div>
    );
  }

  if (error && !reports) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="mt-0.5 text-red-600" size={22} />
          <div className="flex-1">
            <h2 className="font-semibold text-red-800">
              Failed to load reports
            </h2>
            <p className="mt-1 text-sm text-red-700">{error}</p>
            <button
              onClick={() => loadReports()}
              className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!reports) {
    return null;
  }

  const summary = reports.customer_technician_summary;
  const status = reports.service_request_status;
  const servicePerformance = reports.service_performance;
  const technicianPerformance = reports.technician_performance;
  const feedback = reports.feedback_summary;
  const workload = reports.technician_workload ?? [];

  const statusData = [
    { name: "Open", value: Number(status.open_requests) || 0 },
    { name: "Pending", value: Number(status.pending_requests) || 0 },
    {
      name: "In Progress",
      value: Number(status.in_progress_requests) || 0,
    },
    {
      name: "Completed",
      value: Number(status.completed_requests) || 0,
    },
  ];

  const hasStatusData = statusData.some((item) => item.value > 0);

  const workloadData = workload.map((technician) => ({
    name: technician.technician_name,
    workload: Number(technician.workload) || 0,
    rating:
      technician.rating === null || technician.rating === undefined
        ? 0
        : Number(technician.rating),
  }));

  return (
    <div className="space-y-6 pb-8">
      {/* Page heading */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900">
            Reports Dashboard
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Overview of service requests, technicians, and customer feedback.
          </p>
        </div>

        <div className="flex flex-col gap-2 sm:flex-row">
          <button
            onClick={handleDownloadPdf}
            disabled={downloading}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Download size={16} />
            {downloading ? "Downloading..." : "Download PDF"}
          </button>

          <button
            onClick={() => loadReports(true)}
            disabled={refreshing}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <RefreshCw
              size={16}
              className={refreshing ? "animate-spin" : ""}
            />
            {refreshing ? "Refreshing..." : "Refresh Reports"}
          </button>
        </div>
      </div>

      {downloadError && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {downloadError}
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {error} Showing the last successfully loaded reports.
        </div>
      )}

      {/* Summary cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard
          title="Total Customers"
          value={summary.total_customers}
          icon={Users}
          description="Registered customers"
        />
        <SummaryCard
          title="Total Technicians"
          value={summary.total_technicians}
          icon={UserRoundCheck}
          description="Registered technicians"
        />
        <SummaryCard
          title="Total Services"
          value={summary.total_services}
          icon={Wrench}
          description="Available service types"
        />
        <SummaryCard
          title="Service Requests"
          value={summary.total_service_requests}
          icon={ClipboardList}
          description="All recorded requests"
        />
      </div>

      {/* Status chart and status summary */}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <ReportCard title="Service Request Status">
          {hasStatusData ? (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="45%"
                    outerRadius={85}
                    paddingAngle={3}
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {statusData.map((entry, index) => (
                      <Cell
                        key={entry.name}
                        fill={STATUS_COLORS[index]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend verticalAlign="bottom" />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex h-64 items-center justify-center text-sm text-gray-500">
              No service request data available yet.
            </div>
          )}
        </ReportCard>

        <ReportCard title="Request Status Breakdown">
          <div className="space-y-4">
            {[
              {
                label: "Open Requests",
                value: status.open_requests,
                icon: Activity,
                color: "text-slate-600",
                background: "bg-slate-100",
              },
              {
                label: "Pending Requests",
                value: status.pending_requests,
                icon: Clock3,
                color: "text-amber-600",
                background: "bg-amber-50",
              },
              {
                label: "In Progress",
                value: status.in_progress_requests,
                icon: TrendingUp,
                color: "text-blue-600",
                background: "bg-blue-50",
              },
              {
                label: "Completed Requests",
                value: status.completed_requests,
                icon: CheckCircle2,
                color: "text-emerald-600",
                background: "bg-emerald-50",
              },
            ].map((item) => {
              const Icon = item.icon;

              return (
                <div
                  key={item.label}
                  className="flex items-center justify-between rounded-lg border border-gray-100 p-4"
                >
                  <div className="flex items-center gap-3">
                    <div className={`rounded-lg p-2 ${item.background}`}>
                      <Icon size={20} className={item.color} />
                    </div>
                    <span className="text-sm font-medium text-gray-700">
                      {item.label}
                    </span>
                  </div>
                  <span className="text-lg font-bold text-gray-900">
                    {item.value ?? 0}
                  </span>
                </div>
              );
            })}
          </div>
        </ReportCard>
      </div>

      {/* Technician workload */}
      <ReportCard title="Technician Workload">
        {workloadData.length > 0 ? (
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={workloadData}
                margin={{ top: 10, right: 15, left: 0, bottom: 40 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="name"
                  angle={-25}
                  textAnchor="end"
                  interval={0}
                  height={65}
                  tick={{ fontSize: 11 }}
                />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Bar
                  dataKey="workload"
                  name="Assigned Requests"
                  fill="#3b82f6"
                  radius={[5, 5, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p className="py-12 text-center text-sm text-gray-500">
            No technician workload data available yet.
          </p>
        )}
      </ReportCard>

      {/* Performance cards */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <ReportCard title="Most Requested Service">
          <div className="flex items-start gap-3">
            <div className="rounded-lg bg-blue-50 p-3">
              <Wrench className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-lg font-bold text-gray-900">
                {servicePerformance.most_requested_service || "No data"}
              </p>
              <p className="mt-1 text-sm text-gray-500">
                {servicePerformance.total_requests_for_service ?? 0} requests
              </p>
            </div>
          </div>
        </ReportCard>

        <ReportCard title="Technician Performance">
          <div className="flex items-start gap-3">
            <div className="rounded-lg bg-amber-50 p-3">
              <Star className="text-amber-500" size={24} />
            </div>
            <div>
              <p className="font-bold text-gray-900">
                {technicianPerformance.highest_rated_technician || "No data"}
              </p>
              <p className="mt-1 text-sm text-gray-500">
                Highest rating:{" "}
                {formatRating(technicianPerformance.highest_rating)}
              </p>
              <p className="mt-1 text-sm text-gray-500">
                Average technician rating:{" "}
                {formatRating(technicianPerformance.average_technician_rating)}
              </p>
            </div>
          </div>
        </ReportCard>

        <ReportCard title="Customer Feedback">
          <div className="flex items-start gap-3">
            <div className="rounded-lg bg-emerald-50 p-3">
              <Star className="text-emerald-600" size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {formatRating(feedback.average_customer_rating)}
                <span className="ml-1 text-sm font-normal text-gray-500">
                  / 5
                </span>
              </p>
              <p className="mt-1 text-sm text-gray-500">
                Average customer rating
              </p>
              <p className="mt-2 text-sm text-gray-500">
                {feedback.total_feedback ?? 0} feedback submissions
              </p>
            </div>
          </div>
        </ReportCard>
      </div>

      {/* Workload details */}
      <ReportCard title="Technician Performance Details">
        {workload.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr className="text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                  <th className="px-4 py-3">Technician</th>
                  <th className="px-4 py-3">Assigned Requests</th>
                  <th className="px-4 py-3">Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {workload.map((technician) => (
                  <tr
                    key={technician.technician_id}
                    className="hover:bg-gray-50"
                  >
                    <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-900">
                      {technician.technician_name}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {technician.workload ?? 0}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {formatRating(technician.rating)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="py-8 text-center text-sm text-gray-500">
            No technician records available yet.
          </p>
        )}
      </ReportCard>
    </div>
  );
}
