import { useCallback, useEffect, useMemo, useState } from "react";
import {
    Users,
    Search,
    RefreshCw,
    AlertCircle,
    Eye,
    X,
    MapPin,
    Phone,
    ClipboardList,
    UserRound,
    CheckCircle2,
    Clock3,
    LoaderCircle,
} from "lucide-react";

import {
    getAdminCustomers,
    getAdminCustomerDetails,
    getAdminCustomerRequests,
} from "../../api/admin";

function formatDate(value) {
    if (!value) return "—";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) return "—";

    return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    });
}

function formatStatus(status) {
    return String(status || "Unknown")
        .replaceAll("_", " ")
        .toLowerCase()
        .replace(/\b\w/g, (character) => character.toUpperCase());
}

function getStatusStyle(status) {
    const normalized = String(status || "").toUpperCase();

    if (normalized === "COMPLETED") {
        return "bg-emerald-50 text-emerald-700 ring-emerald-600/20";
    }

    if (normalized === "IN PROGRESS") {
        return "bg-blue-50 text-blue-700 ring-blue-600/20";
    }

    if (normalized === "PENDING") {
        return "bg-amber-50 text-amber-700 ring-amber-600/20";
    }

    if (normalized === "CANCELLED") {
        return "bg-rose-50 text-rose-700 ring-rose-600/20";
    }

    return "bg-slate-100 text-slate-700 ring-slate-500/20";
}

function getCustomerName(customer) {
    return customer?.customer_name || "Unnamed customer";
}

function CustomerModal({
    customer,
    requests,
    loadingDetails,
    loadingRequests,
    error,
    onClose,
    onShowRequests,
}) {
    if (!customer) return null;

    return (
        <div
            className="fixed inset-0 z-60 flex items-center justify-center overflow-y-auto bg-slate-950/50 p-4 backdrop-blur-sm"
            onMouseDown={(event) => {
                if (event.target === event.currentTarget) onClose();
            }}
        >
            <section
                role="dialog"
                aria-modal="true"
                aria-labelledby="customer-modal-title"
                className="my-8 w-full max-w-3xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl"
            >
                <div className="flex items-start justify-between gap-4 border-b border-slate-100 p-5 sm:p-6">
                    <div className="flex items-start gap-3">
                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                            <UserRound size={24} />
                        </div>

                        <div>
                            <h2
                                id="customer-modal-title"
                                className="text-lg font-bold text-slate-900 sm:text-xl"
                            >
                                {getCustomerName(customer)}
                            </h2>

                            <p className="mt-1 break-all text-sm text-slate-500">
                                Customer details and service requests
                            </p>
                        </div>
                    </div>

                    <button
                        type="button"
                        aria-label="Close customer details"
                        onClick={onClose}
                        className="rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
                    >
                        <X size={20} />
                    </button>
                </div>

                <div className="space-y-6 p-5 sm:p-6">
                    {loadingDetails ? (
                        <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-5 text-sm text-slate-600">
                            <LoaderCircle size={19} className="animate-spin" />
                            Loading customer details...
                        </div>
                    ) : (
                        <div className="grid gap-4 sm:grid-cols-2">
                            <div className="rounded-xl border border-slate-200 p-4">
                                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                                    <Phone size={15} />
                                    Phone
                                </div>
                                <p className="mt-2 wrap-break-word text-sm font-semibold text-slate-900">
                                    {customer.phone || "Not provided"}
                                </p>
                            </div>

                            <div className="rounded-xl border border-slate-200 p-4">
                                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                                    <MapPin size={15} />
                                    Location
                                </div>
                                <p className="mt-2 text-sm font-semibold text-slate-900">
                                    {[customer.area, customer.city]
                                        .filter(Boolean)
                                        .join(", ") || "Not provided"}
                                </p>
                                {customer.pincode && (
                                    <p className="mt-1 text-xs text-slate-500">
                                        PIN code: {customer.pincode}
                                    </p>
                                )}
                            </div>

                            <div className="rounded-xl border border-slate-200 p-4">
                                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                                    Customer ID
                                </p>
                                <p className="mt-2 break-all text-sm font-semibold text-slate-900">
                                    {customer.customer_id ?? "—"}
                                </p>
                            </div>

                            <div className="rounded-xl border border-slate-200 p-4">
                                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                                    Last login
                                </p>
                                <p className="mt-2 text-sm font-semibold text-slate-900">
                                    {formatDate(customer.last_login_at)}
                                </p>
                            </div>
                        </div>
                    )}

                    {error && (
                        <div
                            role="alert"
                            className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
                        >
                            <AlertCircle size={19} className="mt-0.5 shrink-0" />
                            <p>{error}</p>
                        </div>
                    )}

                    <div>
                        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
                            <div>
                                <h3 className="font-semibold text-slate-900">
                                    Service requests
                                </h3>
                                <p className="mt-1 text-sm text-slate-500">
                                    Requests associated with this customer.
                                </p>
                            </div>

                            <button
                                type="button"
                                onClick={onShowRequests}
                                disabled={loadingRequests}
                                className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
                            >
                                {loadingRequests ? (
                                    <LoaderCircle size={16} className="animate-spin" />
                                ) : (
                                    <ClipboardList size={16} />
                                )}
                                Load requests
                            </button>
                        </div>

                        {requests !== null && (
                            <div className="mt-4 overflow-hidden rounded-xl border border-slate-200">
                                {loadingRequests ? (
                                    <div className="flex items-center justify-center gap-2 p-6 text-sm text-slate-500">
                                        <LoaderCircle size={18} className="animate-spin" />
                                        Loading requests...
                                    </div>
                                ) : requests.length === 0 ? (
                                    <div className="p-6 text-center">
                                        <ClipboardList className="mx-auto text-slate-300" size={28} />
                                        <p className="mt-2 text-sm font-medium text-slate-700">
                                            No service requests found
                                        </p>
                                    </div>
                                ) : (
                                    <div className="max-h-72 overflow-auto">
                                        <table className="min-w-full divide-y divide-slate-200 text-sm">
                                            <thead className="sticky top-0 bg-slate-50">
                                                <tr>
                                                    <th className="px-4 py-3 text-left font-semibold text-slate-600">
                                                        Service
                                                    </th>
                                                    <th className="px-4 py-3 text-left font-semibold text-slate-600">
                                                        Status
                                                    </th>
                                                    <th className="px-4 py-3 text-left font-semibold text-slate-600">
                                                        Date
                                                    </th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-slate-100 bg-white">
                                                {requests.map((request, index) => (
                                                    <tr
                                                        key={request.request_uuid || index}
                                                        className="align-top"
                                                    >
                                                        <td className="max-w-xs px-4 py-3">
                                                            <p className="font-medium text-slate-900">
                                                                {request.service || "Service request"}
                                                            </p>
                                                            <p className="mt-1 line-clamp-2 text-xs text-slate-500">
                                                                {request.problem_description || "No description"}
                                                            </p>
                                                        </td>
                                                        <td className="whitespace-nowrap px-4 py-3">
                                                            <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${getStatusStyle(request.status)}`}>
                                                                {formatStatus(request.status)}
                                                            </span>
                                                        </td>
                                                        <td className="whitespace-nowrap px-4 py-3 text-slate-500">
                                                            {formatDate(request.request_date)}
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex justify-end border-t border-slate-100 bg-slate-50 px-5 py-4 sm:px-6">
                    <button
                        type="button"
                        onClick={onClose}
                        className="rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
                    >
                        Close
                    </button>
                </div>
            </section>
        </div>
    );
}

function AdminCustomers() {
    const [customers, setCustomers] = useState([]);
    const [search, setSearch] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [selectedCustomer, setSelectedCustomer] = useState(null);
    const [loadingDetails, setLoadingDetails] = useState(false);
    const [requests, setRequests] = useState(null);
    const [loadingRequests, setLoadingRequests] = useState(false);
    const [modalError, setModalError] = useState("");

    const loadCustomers = useCallback(async () => {
        setLoading(true);
        setError("");

        try {
            const response = await getAdminCustomers();
            const customerList = Array.isArray(response)
                ? response
                : response?.customers;

            if (!Array.isArray(customerList)) {
                throw new Error("The server returned an unexpected customer response.");
            }

            setCustomers(customerList);
        } catch (requestError) {
            if (requestError.response?.status === 401) {
                setError("Your Admin session is invalid or expired. Please sign in again.");
            } else if (requestError.response?.status === 403) {
                setError("You do not have permission to view customers.");
            } else {
                setError(
                    requestError.response?.data?.detail ||
                    requestError.message ||
                    "Unable to load customers. Please try again."
                );
            }
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadCustomers();
    }, [loadCustomers]);

    const filteredCustomers = useMemo(() => {
        const term = search.trim().toLowerCase();

        if (!term) return customers;

        return customers.filter((customer) => {
            const searchableValues = [
                customer.customer_name,
                customer.phone,
                customer.city,
                customer.area,
                customer.pincode,
            ];

            return searchableValues.some((value) =>
                String(value ?? "").toLowerCase().includes(term)
            );
        });
    }, [customers, search]);

    const openCustomer = async (customer) => {
        setSelectedCustomer(customer);
        setRequests(null);
        setModalError("");
        setLoadingDetails(true);

        try {
            const uuid = customer.customer_uuid;

            if (!uuid) {
                throw new Error("This customer does not have a customer UUID.");
            }

            const details = await getAdminCustomerDetails(uuid);
            setSelectedCustomer((current) =>
                current?.customer_uuid === uuid
                    ? { ...current, ...details }
                    : current
            );
        } catch (requestError) {
            setModalError(
                requestError.response?.data?.detail ||
                requestError.message ||
                "Unable to load customer details."
            );
        } finally {
            setLoadingDetails(false);
        }
    };

    const loadCustomerRequests = async () => {
        if (!selectedCustomer?.customer_uuid) {
            setModalError("A valid customer UUID is required to load requests.");
            return;
        }

        setLoadingRequests(true);
        setModalError("");

        try {
            const response = await getAdminCustomerRequests(
                selectedCustomer.customer_uuid
            );

            const requestList = Array.isArray(response)
                ? response
                : response?.requests;

            if (!Array.isArray(requestList)) {
                throw new Error("The server returned an unexpected service-request response.");
            }

            setRequests(requestList);
        } catch (requestError) {
            setModalError(
                requestError.response?.data?.detail ||
                requestError.message ||
                "Unable to load this customer's service requests."
            );
        } finally {
            setLoadingRequests(false);
        }
    };

    return (
        <div className="mx-auto max-w-7xl space-y-8">
            <section className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                <div>
                    <p className="text-sm font-medium text-indigo-600">
                        Administration
                    </p>
                    <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                        Customer Management
                    </h1>
                    <p className="mt-2 text-sm text-slate-500">
                        Browse registered customers and review their service activity.
                    </p>
                </div>

                <button
                    type="button"
                    onClick={loadCustomers}
                    disabled={loading}
                    className="inline-flex items-center justify-center gap-2 self-start rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60 sm:self-auto"
                >
                    <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
                    Refresh
                </button>
            </section>

            <section className="grid gap-4 sm:grid-cols-2">
                <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                    <div className="flex items-center justify-between gap-4">
                        <div>
                            <p className="text-sm font-medium text-slate-500">
                                Registered Customers
                            </p>
                            <p className="mt-3 text-3xl font-bold text-slate-900">
                                {loading ? "—" : customers.length.toLocaleString()}
                            </p>
                        </div>
                        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                            <Users size={22} />
                        </div>
                    </div>
                </article>

                <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                    <div className="flex items-center justify-between gap-4">
                        <div>
                            <p className="text-sm font-medium text-slate-500">
                                Matching Search Results
                            </p>
                            <p className="mt-3 text-3xl font-bold text-slate-900">
                                {loading ? "—" : filteredCustomers.length.toLocaleString()}
                            </p>
                        </div>
                        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-violet-50 text-violet-600">
                            <Search size={22} />
                        </div>
                    </div>
                </article>
            </section>

            <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="flex flex-col gap-4 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:justify-between sm:p-6">
                    <div>
                        <h2 className="font-semibold text-slate-900">
                            Registered Customers
                        </h2>
                        <p className="mt-1 text-sm text-slate-500">
                            Search by name, phone, city, area, or PIN code.
                        </p>
                    </div>

                    <div className="relative w-full sm:max-w-sm">
                        <Search
                            size={18}
                            className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"
                        />
                        <input
                            type="search"
                            value={search}
                            onChange={(event) => setSearch(event.target.value)}
                            placeholder="Search customers..."
                            aria-label="Search customers"
                            className="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:ring-4 focus:ring-indigo-500/10"
                        />
                    </div>
                </div>

                {error && (
                    <div
                        role="alert"
                        className="m-5 flex flex-col gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 sm:flex-row sm:items-center sm:justify-between"
                    >
                        <div className="flex items-start gap-3">
                            <AlertCircle size={19} className="mt-0.5 shrink-0" />
                            <p>{error}</p>
                        </div>
                        <button
                            type="button"
                            onClick={loadCustomers}
                            className="self-start font-semibold underline sm:self-auto"
                        >
                            Try again
                        </button>
                    </div>
                )}

                {loading && customers.length === 0 ? (
                    <div className="flex items-center justify-center gap-3 p-12 text-sm text-slate-500">
                        <LoaderCircle size={20} className="animate-spin" />
                        Loading customers...
                    </div>
                ) : !error && filteredCustomers.length === 0 ? (
                    <div className="p-12 text-center">
                        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
                            {search ? <Search size={25} /> : <Users size={25} />}
                        </div>
                        <h3 className="mt-4 font-semibold text-slate-900">
                            {search ? "No matching customers" : "No customers registered"}
                        </h3>
                        <p className="mt-2 text-sm text-slate-500">
                            {search
                                ? "Try another name, phone number, or location."
                                : "Customer accounts will appear here after registration."}
                        </p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-slate-200">
                            <thead className="bg-slate-50">
                                <tr>
                                    <th className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                                        Customer
                                    </th>
                                    <th className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                                        Phone
                                    </th>
                                    <th className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                                        Location
                                    </th>
                                    <th className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                                        Last Login
                                    </th>
                                    <th className="px-5 py-4 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                                        Action
                                    </th>
                                </tr>
                            </thead>

                            <tbody className="divide-y divide-slate-100 bg-white">
                                {filteredCustomers.map((customer, index) => (
                                    <tr
                                        key={customer.customer_uuid || customer.customer_id || index}
                                        className="transition hover:bg-slate-50/80"
                                    >
                                        <td className="px-5 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-sm font-bold text-indigo-600">
                                                    {getCustomerName(customer)
                                                        .charAt(0)
                                                        .toUpperCase()}
                                                </div>
                                                <div className="min-w-0">
                                                    <p className="font-semibold text-slate-900">
                                                        {getCustomerName(customer)}
                                                    </p>
                                                    <p className="mt-1 text-xs text-slate-500">
                                                        ID: {customer.customer_id ?? "—"}
                                                    </p>
                                                </div>
                                            </div>
                                        </td>

                                        <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600">
                                            {customer.phone || "—"}
                                        </td>

                                        <td className="px-5 py-4">
                                            <p className="text-sm font-medium text-slate-700">
                                                {[customer.area, customer.city]
                                                    .filter(Boolean)
                                                    .join(", ") || "—"}
                                            </p>
                                            {customer.pincode && (
                                                <p className="mt-1 text-xs text-slate-500">
                                                    PIN: {customer.pincode}
                                                </p>
                                            )}
                                        </td>

                                        <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-500">
                                            {formatDate(customer.last_login_at)}
                                        </td>

                                        <td className="whitespace-nowrap px-5 py-4 text-right">
                                            <button
                                                type="button"
                                                onClick={() => openCustomer(customer)}
                                                className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 transition hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700"
                                            >
                                                <Eye size={15} />
                                                View details
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                <div className="flex flex-col gap-2 border-t border-slate-100 bg-slate-50/70 px-5 py-4 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between">
                    <span>
                        Showing {filteredCustomers.length} of {customers.length} customers
                    </span>
                    <span className="inline-flex items-center gap-1.5">
                        <CheckCircle2 size={14} className="text-emerald-600" />
                        Data from the Admin API
                    </span>
                </div>
            </section>

            {selectedCustomer && (
                <CustomerModal
                    customer={selectedCustomer}
                    requests={requests}
                    loadingDetails={loadingDetails}
                    loadingRequests={loadingRequests}
                    error={modalError}
                    onClose={() => {
                        setSelectedCustomer(null);
                        setRequests(null);
                        setModalError("");
                    }}
                    onShowRequests={loadCustomerRequests}
                />
            )}
        </div>
    );
}

export default AdminCustomers;
