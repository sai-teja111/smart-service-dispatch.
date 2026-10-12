import {
    AlertCircle,
    CheckCircle2,
    Clock,
    LoaderCircle,
    ShieldCheck,
    UserRound,
    Wifi,
} from "lucide-react";

import { useEffect, useState } from "react";

import {
    getTechnicianAvailability,
    updateTechnicianAvailability,
} from "../../api/technician";

const AVAILABILITY_OPTIONS = [
    {
        value: "Available",
        title: "Available",
        description: "You can receive new service assignments.",
        color: "emerald",
    },
    {
        value: "Busy",
        title: "Busy",
        description: "You are occupied with current work.",
        color: "amber",
    },
    {
        value: "Unavailable",
        title: "Unavailable",
        description: "You cannot accept new service assignments.",
        color: "rose",
    },
];

function getStatusStyles(status) {
    switch (status) {
        case "Available":
            return {
                badge: "bg-emerald-50 text-emerald-700 border-emerald-200",
                dot: "bg-emerald-500",
                icon: "text-emerald-600 bg-emerald-50",
            };

        case "Busy":
            return {
                badge: "bg-amber-50 text-amber-700 border-amber-200",
                dot: "bg-amber-500",
                icon: "text-amber-600 bg-amber-50",
            };

        case "Unavailable":
            return {
                badge: "bg-rose-50 text-rose-700 border-rose-200",
                dot: "bg-rose-500",
                icon: "text-rose-600 bg-rose-50",
            };

        default:
            return {
                badge: "bg-slate-100 text-slate-600 border-slate-200",
                dot: "bg-slate-400",
                icon: "text-slate-600 bg-slate-100",
            };
    }
}

export default function Availability() {
    const [availability, setAvailability] = useState("");
    const [selectedAvailability, setSelectedAvailability] = useState("");
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    async function loadAvailability() {
        try {
            setLoading(true);
            setError("");

            const data = await getTechnicianAvailability();

            setAvailability(data.availability);
            setSelectedAvailability(data.availability);
        } catch (err) {
            console.error("Failed to load availability:", err);

            setError(
                err?.response?.data?.detail ||
                    "Unable to load your availability."
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadAvailability();
    }, []);

    async function handleSaveAvailability() {
        if (!selectedAvailability || selectedAvailability === availability) {
            return;
        }

        try {
            setSaving(true);
            setError("");
            setSuccess("");

            const response = await updateTechnicianAvailability(
                selectedAvailability
            );

            const updatedAvailability =
                response.new_availability || selectedAvailability;

            setAvailability(updatedAvailability);
            setSelectedAvailability(updatedAvailability);

            setSuccess(
                response.message ||
                    "Your availability has been updated successfully."
            );
        } catch (err) {
            console.error("Failed to update availability:", err);

            setError(
                err?.response?.data?.detail ||
                    "Unable to update your availability."
            );
        } finally {
            setSaving(false);
        }
    }

    if (loading) {
        return (
            <div className="flex min-h-80 items-center justify-center">
                <div className="flex items-center gap-3 text-slate-500">
                    <LoaderCircle size={22} className="animate-spin" />
                    <span>Loading your availability...</span>
                </div>
            </div>
        );
    }

    const styles = getStatusStyles(availability);

    return (
        <div className="mx-auto max-w-5xl space-y-6">
            {/* Page Header */}
            <div>
                <p className="text-sm font-medium text-blue-600">
                    Technician Portal
                </p>

                <h1 className="mt-1 text-2xl font-bold text-slate-900">
                    Technician Availability
                </h1>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                    Manage your availability so the service dispatch system
                    knows whether you can accept new assignments.
                </p>
            </div>

            {/* Current Availability */}
            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
                <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex items-center gap-4">
                        <div
                            className={`flex h-14 w-14 items-center justify-center rounded-2xl ${styles.icon}`}
                        >
                            <Wifi size={26} />
                        </div>

                        <div>
                            <p className="text-sm text-slate-500">
                                Current availability
                            </p>

                            <div className="mt-1 flex flex-wrap items-center gap-2">
                                <h2 className="text-xl font-bold text-slate-900">
                                    {availability || "Unknown"}
                                </h2>

                                <span
                                    className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold ${styles.badge}`}
                                >
                                    <span
                                        className={`h-2 w-2 rounded-full ${styles.dot}`}
                                    />
                                    {availability || "Unknown"}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-2 text-sm text-slate-500">
                        <ShieldCheck size={18} />
                        <span>Saved to your account</span>
                    </div>
                </div>
            </section>

            {/* Error */}
            {error && (
                <div
                    role="alert"
                    className="flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-rose-700"
                >
                    <AlertCircle size={20} className="mt-0.5 shrink-0" />

                    <p className="text-sm">{error}</p>
                </div>
            )}

            {/* Success */}
            {success && (
                <div
                    role="status"
                    className="flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-emerald-700"
                >
                    <CheckCircle2
                        size={20}
                        className="mt-0.5 shrink-0"
                    />

                    <p className="text-sm">{success}</p>
                </div>
            )}

            {/* Availability Options */}
            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
                <div className="flex items-center gap-3">
                    <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                        <UserRound size={21} />
                    </div>

                    <div>
                        <h2 className="text-lg font-bold text-slate-900">
                            Set Your Availability
                        </h2>

                        <p className="text-sm text-slate-500">
                            Choose the status that best describes your current
                            work situation.
                        </p>
                    </div>
                </div>

                <div className="mt-6 grid gap-4 md:grid-cols-3">
                    {AVAILABILITY_OPTIONS.map((option) => {
                        const isSelected =
                            selectedAvailability === option.value;

                        return (
                            <button
                                key={option.value}
                                type="button"
                                onClick={() => {
                                    setSelectedAvailability(option.value);
                                    setError("");
                                    setSuccess("");
                                }}
                                aria-pressed={isSelected}
                                className={`rounded-xl border p-5 text-left transition ${
                                    isSelected
                                        ? "border-blue-500 bg-blue-50 ring-2 ring-blue-100"
                                        : "border-slate-200 hover:border-slate-300 hover:bg-slate-50"
                                }`}
                            >
                                <div className="flex items-center justify-between gap-2">
                                    <span className="font-semibold text-slate-900">
                                        {option.title}
                                    </span>

                                    <span
                                        className={`h-3 w-3 rounded-full ${getStatusStyles(option.value).dot}`}
                                    />
                                </div>

                                <p className="mt-3 text-sm leading-6 text-slate-500">
                                    {option.description}
                                </p>

                                {isSelected && (
                                    <span className="mt-4 inline-flex items-center gap-1.5 text-xs font-semibold text-blue-700">
                                        <CheckCircle2 size={15} />
                                        Selected
                                    </span>
                                )}
                            </button>
                        );
                    })}
                </div>

                <div className="mt-6 flex flex-col gap-3 border-t border-slate-100 pt-6 sm:flex-row sm:items-center sm:justify-between">
                    <p className="text-sm text-slate-500">
                        <Clock size={16} className="mr-1 inline" />
                        Changes are saved when you click the button.
                    </p>

                    <button
                        type="button"
                        onClick={handleSaveAvailability}
                        disabled={
                            saving ||
                            !selectedAvailability ||
                            selectedAvailability === availability
                        }
                        className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        {saving ? (
                            <LoaderCircle
                                size={18}
                                className="animate-spin"
                            />
                        ) : (
                            <CheckCircle2 size={18} />
                        )}

                        {saving ? "Saving..." : "Save Availability"}
                    </button>
                </div>
            </section>

            {/* Helpful Information */}
            <div className="rounded-xl border border-blue-100 bg-blue-50 p-5">
                <h3 className="font-semibold text-blue-900">
                    How availability works
                </h3>

                <ul className="mt-3 space-y-2 text-sm leading-6 text-blue-800">
                    <li>
                        <strong>Available:</strong> You can be considered for
                        new service assignments.
                    </li>
                    <li>
                        <strong>Busy:</strong> You are occupied with current
                        work.
                    </li>
                    <li>
                        <strong>Unavailable:</strong> You are not available for
                        new assignments.
                    </li>
                </ul>

                <p className="mt-3 text-xs leading-5 text-blue-700">
                    The backend saves your selected status. Whether this status
                    affects technician matching depends on the assignment
                    logic configured in your backend.
                </p>
            </div>
        </div>
    );
}