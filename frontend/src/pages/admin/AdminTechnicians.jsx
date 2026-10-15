
import { useCallback, useEffect, useMemo, useState } from "react";
import {
    Users,
    Search,
    RefreshCw,
    Wrench,
    Clock3,
    CheckCircle2,
    XCircle,
    MapPin,
    Phone,
    ShieldCheck,
    BadgeCheck,
    AlertCircle,
    LoaderCircle,
    UserRound,
    BriefcaseBusiness,
} from "lucide-react";

import {
    getAdminTechnicians,
    getPendingTechnicians,
    updateTechnicianApproval,
    getAdminTechnicianSkills,
    getPendingTechnicianSkills,
    updateTechnicianSkillVerification,
} from "../../api/admin";

const tabs = [
    { id: "all", label: "All Technicians" },
    { id: "pending", label: "Pending Approval" },
    { id: "skills", label: "Skill Verification" },
];

function formatStatus(value) {
    return String(value ?? "Unknown")
        .replaceAll("_", " ")
        .toLowerCase()
        .replace(/\b\w/g, (character) => character.toUpperCase());
}

function getStatusStyle(status) {
    switch (String(status ?? "").toLowerCase()) {
        case "approved":
        case "available":
            return "border-emerald-200 bg-emerald-50 text-emerald-700";
        case "pending":
            return "border-amber-200 bg-amber-50 text-amber-700";
        case "rejected":
        case "unavailable":
            return "border-red-200 bg-red-50 text-red-700";
        default:
            return "border-slate-200 bg-slate-100 text-slate-600";
    }
}

function StatusBadge({ status }) {
    return (
        <span
            className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${getStatusStyle(status)}`}
        >
            {formatStatus(status)}
        </span>
    );
}

function StatCard({ label, value, icon: Icon, color }) {
    const colors = {
        blue: "bg-blue-50 text-blue-600",
        violet: "bg-violet-50 text-violet-600",
        amber: "bg-amber-50 text-amber-600",
        emerald: "bg-emerald-50 text-emerald-600",
    };

    return (
        <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between gap-4">
                <div>
                    <p className="text-sm font-medium text-slate-500">
                        {label}
                    </p>
                    <p className="mt-3 text-3xl font-bold text-slate-900">
                        {value.toLocaleString()}
                    </p>
                </div>

                <div
                    className={`flex h-12 w-12 items-center justify-center rounded-xl ${colors[color]}`}
                >
                    <Icon size={23} />
                </div>
            </div>
        </article>
    );
}

function getErrorMessage(error, fallback) {
    if (error.response?.status === 401) {
        return "Your Admin session is invalid or expired. Please sign in again.";
    }

    if (error.response?.status === 403) {
        return "You do not have permission to perform this action.";
    }

    return error.response?.data?.detail || fallback;
}

function TechnicianAvatar({ name }) {
    const initial = String(name ?? "T").trim().charAt(0).toUpperCase() || "T";

    return (
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-violet-50 text-sm font-bold text-violet-700">
            {initial}
        </div>
    );
}

function AdminTechnicians() {
    const [activeTab, setActiveTab] = useState("all");
    const [search, setSearch] = useState("");
    const [statusFilter, setStatusFilter] = useState("all");

    const [technicians, setTechnicians] = useState([]);
    const [pendingTechnicians, setPendingTechnicians] = useState([]);
    const [skills, setSkills] = useState([]);
    const [pendingSkills, setPendingSkills] = useState([]);

    const [loading, setLoading] = useState(true);
    const [actionKey, setActionKey] = useState("");
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");

    const loadTechnicians = useCallback(async () => {
        setLoading(true);
        setError("");
        setNotice("");

        try {
            const [
                technicianResponse,
                pendingResponse,
                skillResponse,
                pendingSkillResponse,
            ] = await Promise.all([
                getAdminTechnicians(),
                getPendingTechnicians(),
                getAdminTechnicianSkills(),
                getPendingTechnicianSkills(),
            ]);

            setTechnicians(
                Array.isArray(technicianResponse)
                    ? technicianResponse
                    : technicianResponse.technicians ?? []
            );

            setPendingTechnicians(
                Array.isArray(pendingResponse)
                    ? pendingResponse
                    : pendingResponse.technicians ?? []
            );

            setSkills(
                Array.isArray(skillResponse)
                    ? skillResponse
                    : skillResponse.skills ?? []
            );

            setPendingSkills(
                Array.isArray(pendingSkillResponse)
                    ? pendingSkillResponse
                    : pendingSkillResponse.skills ?? []
            );
        } catch (requestError) {
            setError(
                getErrorMessage(
                    requestError,
                    "Unable to load technician information. Please try again."
                )
            );
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadTechnicians();
    }, [loadTechnicians]);

    const filteredTechnicians = useMemo(() => {
        const query = search.trim().toLowerCase();

        return technicians.filter((technician) => {
            const matchesSearch = [
                technician.technician_name,
                technician.phone,
                technician.city,
                technician.area,
                technician.pincode,
                technician.approval_status,
                technician.availability,
            ].some((value) =>
                String(value ?? "").toLowerCase().includes(query)
            );

            const matchesStatus =
                statusFilter === "all" ||
                String(technician.approval_status ?? "").toLowerCase() ===
                    statusFilter;

            return matchesSearch && matchesStatus;
        });
    }, [technicians, search, statusFilter]);

    const handleApproval = async (technician, approvalStatus) => {
        const technicianUuid = technician.technician_uuid;

        if (!technicianUuid) {
            setError("This technician does not have a valid technician UUID.");
            return;
        }

        const key = `approval-${technicianUuid}`;

        setActionKey(key);
        setError("");
        setNotice("");

        try {
            const result = await updateTechnicianApproval(
                technicianUuid,
                approvalStatus
            );

            setNotice(
                result.message ||
                    `Technician ${approvalStatus.toLowerCase()} successfully.`
            );

            await loadTechnicians();
        } catch (requestError) {
            setError(
                getErrorMessage(
                    requestError,
                    "Unable to update technician approval."
                )
            );
        } finally {
            setActionKey("");
        }
    };

    const handleSkillVerification = async (skill, isVerified) => {
        if (!skill.technician_uuid || skill.skill_id == null) {
            setError("The technician UUID or skill ID is missing.");
            return;
        }

        const key = `skill-${skill.technician_uuid}-${skill.skill_id}`;

        setActionKey(key);
        setError("");
        setNotice("");

        try {
            const result = await updateTechnicianSkillVerification(
                skill.technician_uuid,
                skill.skill_id,
                isVerified
            );

            setNotice(
                result.message ||
                    (isVerified
                        ? "Technician skill verified successfully."
                        : "Technician skill verification removed.")
            );

            await loadTechnicians();
        } catch (requestError) {
            setError(
                getErrorMessage(
                    requestError,
                    "Unable to update skill verification."
                )
            );
        } finally {
            setActionKey("");
        }
    };

    const displayedSkills =
        activeTab === "skills" ? pendingSkills : skills;

    const approvedCount = technicians.filter(
        (technician) => technician.approval_status === "Approved"
    ).length;

    const pendingCount = pendingTechnicians.length;

    return (
        <div className="mx-auto max-w-7xl space-y-7">
            {/* Page heading */}
            <section className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                <div>
                    <p className="text-sm font-semibold text-indigo-600">
                        Administration
                    </p>

                    <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                        Technician Management
                    </h1>

                    <p className="mt-2 text-sm leading-6 text-slate-500">
                        Review technician accounts, manage approvals, and
                        verify submitted skills.
                    </p>
                </div>

                <button
                    type="button"
                    onClick={loadTechnicians}
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

            {/* Notifications */}
            {error && (
                <div
                    role="alert"
                    className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
                >
                    <AlertCircle size={19} className="mt-0.5 shrink-0" />
                    <p>{error}</p>
                </div>
            )}

            {notice && (
                <div
                    role="status"
                    className="flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700"
                >
                    <CheckCircle2
                        size={19}
                        className="mt-0.5 shrink-0"
                    />
                    <p>{notice}</p>
                </div>
            )}

            {/* Statistics */}
            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <StatCard
                    label="Total Technicians"
                    value={technicians.length}
                    icon={Users}
                    color="blue"
                />

                <StatCard
                    label="Pending Approvals"
                    value={pendingCount}
                    icon={Clock3}
                    color="amber"
                />

                <StatCard
                    label="Approved Technicians"
                    value={approvedCount}
                    icon={CheckCircle2}
                    color="emerald"
                />

                <StatCard
                    label="Pending Skill Reviews"
                    value={pendingSkills.length}
                    icon={ShieldCheck}
                    color="violet"
                />
            </section>

            {/* Tabs */}
            <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="flex flex-wrap gap-2 border-b border-slate-200 p-4 sm:px-6">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            type="button"
                            onClick={() => {
                                setActiveTab(tab.id);
                                setSearch("");
                                setStatusFilter("all");
                                setError("");
                                setNotice("");
                            }}
                            className={`rounded-xl px-4 py-2.5 text-sm font-semibold transition ${
                                activeTab === tab.id
                                    ? "bg-indigo-600 text-white shadow-sm"
                                    : "bg-slate-50 text-slate-600 hover:bg-slate-100"
                            }`}
                        >
                            {tab.label}
                            {tab.id === "pending" && pendingCount > 0 && (
                                <span className="ml-2 rounded-full bg-white/20 px-2 py-0.5 text-xs">
                                    {pendingCount}
                                </span>
                            )}
                            {tab.id === "skills" && pendingSkills.length > 0 && (
                                <span className="ml-2 rounded-full bg-white/20 px-2 py-0.5 text-xs">
                                    {pendingSkills.length}
                                </span>
                            )}
                        </button>
                    ))}
                </div>

                {/* Search and filters */}
                <div className="flex flex-col justify-between gap-4 border-b border-slate-100 p-4 sm:flex-row sm:items-center sm:px-6">
                    <div>
                        <h2 className="font-semibold text-slate-900">
                            {activeTab === "skills"
                                ? "Pending Skill Verification"
                                : activeTab === "pending"
                                  ? "Technicians Awaiting Approval"
                                  : "Registered Technicians"}
                        </h2>

                        <p className="mt-1 text-sm text-slate-500">
                            {activeTab === "skills"
                                ? "Review each submitted skill before verifying it."
                                : "Search by name, phone, location, or status."}
                        </p>
                    </div>

                    <div className="flex flex-col gap-3 sm:flex-row">
                        {activeTab !== "skills" && (
                            <select
                                value={statusFilter}
                                onChange={(event) =>
                                    setStatusFilter(event.target.value)
                                }
                                aria-label="Filter by approval status"
                                className="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                            >
                                <option value="all">All statuses</option>
                                <option value="pending">Pending</option>
                                <option value="approved">Approved</option>
                                <option value="rejected">Rejected</option>
                            </select>
                        )}

                        <div className="relative">
                            <Search
                                size={17}
                                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                            />

                            <input
                                type="search"
                                value={search}
                                onChange={(event) =>
                                    setSearch(event.target.value)
                                }
                                placeholder={
                                    activeTab === "skills"
                                        ? "Search skills..."
                                        : "Search technicians..."
                                }
                                className="w-full rounded-xl border border-slate-200 py-2.5 pl-9 pr-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 sm:w-64"
                            />
                        </div>
                    </div>
                </div>

                {/* Loading */}
                {loading ? (
                    <div className="flex min-h-56 flex-col items-center justify-center gap-3 p-8 text-slate-500">
                        <LoaderCircle
                            size={28}
                            className="animate-spin text-indigo-600"
                        />
                        <p className="text-sm">Loading technician data...</p>
                    </div>
                ) : (
                    <>
                        {/* Technician table */}
                        {activeTab !== "skills" && (
                            <div className="overflow-x-auto">
                                <table className="w-full min-w-212.5 text-left">
                                    <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                                        <tr>
                                            <th className="px-6 py-4 font-semibold">
                                                Technician
                                            </th>
                                            <th className="px-6 py-4 font-semibold">
                                                Contact
                                            </th>
                                            <th className="px-6 py-4 font-semibold">
                                                Location
                                            </th>
                                            <th className="px-6 py-4 font-semibold">
                                                Availability
                                            </th>
                                            <th className="px-6 py-4 font-semibold">
                                                Approval
                                            </th>
                                            <th className="px-6 py-4 text-right font-semibold">
                                                Actions
                                            </th>
                                        </tr>
                                    </thead>

                                    <tbody className="divide-y divide-slate-100">
                                        {(activeTab === "pending"
                                            ? pendingTechnicians.filter(
                                                  (technician) => {
                                                      const query =
                                                          search
                                                              .trim()
                                                              .toLowerCase();

                                                      return [
                                                          technician.technician_name,
                                                          technician.phone,
                                                          technician.city,
                                                          technician.area,
                                                          technician.pincode,
                                                      ].some((value) =>
                                                          String(value ?? "")
                                                              .toLowerCase()
                                                              .includes(query)
                                                      );
                                                  }
                                              )
                                            : filteredTechnicians
                                        ).map((technician) => {
                                            const technicianUuid =
                                                technician.technician_uuid;

                                            const busy =
                                                actionKey ===
                                                `approval-${technicianUuid}`;

                                            return (
                                                <tr
                                                    key={
                                                        technicianUuid ||
                                                        technician.technician_id
                                                    }
                                                    className="transition hover:bg-slate-50/80"
                                                >
                                                    <td className="px-6 py-4">
                                                        <div className="flex items-center gap-3">
                                                            <TechnicianAvatar
                                                                name={
                                                                    technician.technician_name
                                                                }
                                                            />
                                                            <div>
                                                                <p className="font-semibold text-slate-900">
                                                                    {technician.technician_name ||
                                                                        "Unnamed technician"}
                                                                </p>
                                                                <p className="mt-1 text-xs text-slate-500">
                                                                    ID:{" "}
                                                                    {technician.technician_id ??
                                                                        "—"}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    </td>

                                                    <td className="px-6 py-4">
                                                        <div className="flex items-center gap-2 text-sm text-slate-600">
                                                            <Phone
                                                                size={15}
                                                                className="shrink-0 text-slate-400"
                                                            />
                                                            {technician.phone ||
                                                                "—"}
                                                        </div>
                                                    </td>

                                                    <td className="px-6 py-4">
                                                        <div className="flex items-start gap-2 text-sm text-slate-700">
                                                            <MapPin
                                                                size={15}
                                                                className="mt-0.5 shrink-0 text-slate-400"
                                                            />
                                                            <div>
                                                                <p>
                                                                    {[
                                                                        technician.area,
                                                                        technician.city,
                                                                    ]
                                                                        .filter(Boolean)
                                                                        .join(", ") ||
                                                                        "Location not provided"}
                                                                </p>
                                                                {technician.pincode && (
                                                                    <p className="mt-1 text-xs text-slate-500">
                                                                        PIN:{" "}
                                                                        {technician.pincode}
                                                                    </p>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </td>

                                                    <td className="px-6 py-4">
                                                        <StatusBadge
                                                            status={
                                                                technician.availability
                                                            }
                                                        />
                                                    </td>

                                                    <td className="px-6 py-4">
                                                        <StatusBadge
                                                            status={
                                                                technician.approval_status
                                                            }
                                                        />
                                                    </td>

                                                    <td className="px-6 py-4">
                                                        <div className="flex justify-end gap-2">
                                                            {technician.approval_status !==
                                                                "Approved" && (
                                                                <button
                                                                    type="button"
                                                                    disabled={
                                                                        Boolean(
                                                                            actionKey
                                                                        )
                                                                    }
                                                                    onClick={() =>
                                                                        handleApproval(
                                                                            technician,
                                                                            "Approved"
                                                                        )
                                                                    }
                                                                    className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-50"
                                                                >
                                                                    {busy ? (
                                                                        <LoaderCircle
                                                                            size={14}
                                                                            className="animate-spin"
                                                                        />
                                                                    ) : (
                                                                        <CheckCircle2
                                                                            size={14}
                                                                        />
                                                                    )}
                                                                    Approve
                                                                </button>
                                                            )}

                                                            {technician.approval_status !==
                                                                "Rejected" && (
                                                                <button
                                                                    type="button"
                                                                    disabled={
                                                                        Boolean(
                                                                            actionKey
                                                                        )
                                                                    }
                                                                    onClick={() =>
                                                                        handleApproval(
                                                                            technician,
                                                                            "Rejected"
                                                                        )
                                                                    }
                                                                    className="inline-flex items-center gap-1.5 rounded-lg border border-red-200 bg-white px-3 py-2 text-xs font-semibold text-red-600 transition hover:bg-red-50 disabled:opacity-50"
                                                                >
                                                                    <XCircle
                                                                        size={14}
                                                                    />
                                                                    Reject
                                                                </button>
                                                            )}
                                                        </div>
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>

                                {(activeTab === "pending"
                                    ? pendingTechnicians.filter((technician) =>
                                          [
                                              technician.technician_name,
                                              technician.phone,
                                              technician.city,
                                              technician.area,
                                              technician.pincode,
                                          ].some((value) =>
                                              String(value ?? "")
                                                  .toLowerCase()
                                                  .includes(
                                                      search.trim().toLowerCase()
                                                  )
                                          )
                                      ).length
                                    : filteredTechnicians.length) === 0 && (
                                    <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
                                        <UserRound
                                            size={35}
                                            className="text-slate-300"
                                        />
                                        <h3 className="mt-4 font-semibold text-slate-800">
                                            No technicians found
                                        </h3>
                                        <p className="mt-1 text-sm text-slate-500">
                                            Try changing your search or filter.
                                        </p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Pending skill verification */}
                        {activeTab === "skills" && (
                            <div className="overflow-x-auto">
                                <table className="w-full min-w-212.5 text-left">
                                    <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                                        <tr>
                                            <th className="px-6 py-4 font-semibold">
                                                Technician
                                            </th>
                                            <th className="px-6 py-4 font-semibold">
                                                Submitted Skill
                                            </th>
                                            <th className="px-6 py-4 font-semibold">
                                                Experience
                                            </th>
                                            <th className="px-6 py-4 font-semibold">
                                                Expertise
                                            </th>
                                            <th className="px-6 py-4 font-semibold">
                                                Technician Status
                                            </th>
                                            <th className="px-6 py-4 text-right font-semibold">
                                                Action
                                            </th>
                                        </tr>
                                    </thead>

                                    <tbody className="divide-y divide-slate-100">
                                        {displayedSkills
                                            .filter((skill) =>
                                                [
                                                    skill.technician_name,
                                                    skill.skill_name,
                                                    skill.category,
                                                    skill.expertise_level,
                                                    skill.technician_approval_status,
                                                ].some((value) =>
                                                    String(value ?? "")
                                                        .toLowerCase()
                                                        .includes(
                                                            search
                                                                .trim()
                                                                .toLowerCase()
                                                        )
                                                )
                                            )
                                            .map((skill) => {
                                                const key = `skill-${skill.technician_uuid}-${skill.skill_id}`;
                                                const busy = actionKey === key;

                                                return (
                                                    <tr
                                                        key={key}
                                                        className="transition hover:bg-slate-50/80"
                                                    >
                                                        <td className="px-6 py-4">
                                                            <div className="flex items-center gap-3">
                                                                <TechnicianAvatar
                                                                    name={
                                                                        skill.technician_name
                                                                    }
                                                                />
                                                                <div>
                                                                    <p className="font-semibold text-slate-900">
                                                                        {skill.technician_name}
                                                                    </p>
                                                                    <p className="mt-1 text-xs text-slate-500">
                                                                        Technician ID:{" "}
                                                                        {skill.technician_id ??
                                                                            "—"}
                                                                    </p>
                                                                </div>
                                                            </div>
                                                        </td>

                                                        <td className="px-6 py-4">
                                                            <p className="font-semibold text-slate-900">
                                                                {skill.skill_name}
                                                            </p>
                                                            <p className="mt-1 text-xs text-slate-500">
                                                                {skill.category ||
                                                                    "General skill"}
                                                            </p>
                                                        </td>

                                                        <td className="px-6 py-4 text-sm text-slate-700">
                                                            {skill.experience_years ??
                                                                0}{" "}
                                                            years
                                                        </td>

                                                        <td className="px-6 py-4 text-sm text-slate-700">
                                                            {formatStatus(
                                                                skill.expertise_level
                                                            )}
                                                        </td>

                                                        <td className="px-6 py-4">
                                                            <StatusBadge
                                                                status={
                                                                    skill.technician_approval_status
                                                                }
                                                            />
                                                        </td>

                                                        <td className="px-6 py-4">
                                                            <div className="flex justify-end">
                                                                <button
                                                                    type="button"
                                                                    disabled={
                                                                        Boolean(
                                                                            actionKey
                                                                        )
                                                                    }
                                                                    onClick={() =>
                                                                        handleSkillVerification(
                                                                            skill,
                                                                            true
                                                                        )
                                                                    }
                                                                    className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-semibold text-white transition hover:bg-indigo-700 disabled:opacity-50"
                                                                >
                                                                    {busy ? (
                                                                        <LoaderCircle
                                                                            size={14}
                                                                            className="animate-spin"
                                                                        />
                                                                    ) : (
                                                                        <BadgeCheck
                                                                            size={14}
                                                                        />
                                                                    )}
                                                                    Verify skill
                                                                </button>
                                                            </div>
                                                        </td>
                                                    </tr>
                                                );
                                            })}
                                    </tbody>
                                </table>

                                {displayedSkills.filter((skill) =>
                                    [
                                        skill.technician_name,
                                        skill.skill_name,
                                        skill.category,
                                        skill.expertise_level,
                                        skill.technician_approval_status,
                                    ].some((value) =>
                                        String(value ?? "")
                                            .toLowerCase()
                                            .includes(
                                                search.trim().toLowerCase()
                                            )
                                    )
                                ).length === 0 && (
                                    <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
                                        <BriefcaseBusiness
                                            size={35}
                                            className="text-slate-300"
                                        />
                                        <h3 className="mt-4 font-semibold text-slate-800">
                                            No pending skills found
                                        </h3>
                                        <p className="mt-1 text-sm text-slate-500">
                                            There are no matching skills waiting for verification.
                                        </p>
                                    </div>
                                )}
                            </div>
                        )}
                    </>
                )}
            </section>

            <p className="text-xs leading-5 text-slate-500">
                Technician approval requires at least one verified skill.
                If the backend rejects an approval, review and verify the
                technician&apos;s submitted skills first.
            </p>
        </div>
    );
}

export default AdminTechnicians;