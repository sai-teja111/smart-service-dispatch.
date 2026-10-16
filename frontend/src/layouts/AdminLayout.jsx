
import { useCallback, useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
    LayoutDashboard,
    Users,
    Wrench,
    ChartNoAxesCombined,
    ShieldCheck,
    Menu,
    X,
    LogOut,
    ChevronRight,
    Bell,
    Check,
    RefreshCw,
    LoaderCircle,
} from "lucide-react";

import {
    getAdminNotifications,
    markAdminNotificationAsRead,
} from "../api/admin";

const navigationItems = [
    {
        label: "Dashboard",
        path: "/admin",
        icon: LayoutDashboard,
        end: true,
    },
    {
        label: "Customers",
        path: "/admin/customers",
        icon: Users,
    },
    {
        label: "Technicians",
        path: "/admin/technicians",
        icon: Wrench,
    },
    {
        label: "Reports",
        path: "/admin/reports",
        icon: ChartNoAxesCombined,
    },
];

function formatNotificationDate(value) {
    if (!value) return "";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) return "";

    return new Intl.DateTimeFormat("en-IN", {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(date);
}

function AdminLayout() {
    const navigate = useNavigate();

    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [notificationOpen, setNotificationOpen] = useState(false);
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [notificationsLoading, setNotificationsLoading] = useState(false);
    const [notificationsError, setNotificationsError] = useState("");
    const [actionNotificationId, setActionNotificationId] = useState(null);

    const notificationRef = useRef(null);

    const loadNotifications = useCallback(async () => {
        setNotificationsLoading(true);
        setNotificationsError("");

        try {
            const data = await getAdminNotifications();

            setNotifications(data.notifications ?? []);
            setUnreadCount(data.unread_count ?? 0);
        } catch (error) {
            setNotificationsError(
                error.response?.data?.detail ||
                    "Unable to load notifications. Please try again."
            );
        } finally {
            setNotificationsLoading(false);
        }
    }, []);

    useEffect(() => {
        loadNotifications();
    }, [loadNotifications]);

    useEffect(() => {
        if (!notificationOpen) return undefined;

        function handleOutsideClick(event) {
            if (
                notificationRef.current &&
                !notificationRef.current.contains(event.target)
            ) {
                setNotificationOpen(false);
            }
        }

        function handleEscape(event) {
            if (event.key === "Escape") {
                setNotificationOpen(false);
            }
        }

        document.addEventListener("mousedown", handleOutsideClick);
        document.addEventListener("keydown", handleEscape);

        return () => {
            document.removeEventListener("mousedown", handleOutsideClick);
            document.removeEventListener("keydown", handleEscape);
        };
    }, [notificationOpen]);

    const handleMarkAsRead = async (notification) => {
        if (notification.is_read || actionNotificationId) return;

        setActionNotificationId(notification.notification_uuid);
        setNotificationsError("");

        try {
            const result = await markAdminNotificationAsRead(
                notification.notification_uuid
            );

            const updatedNotification = result.notification ?? {
                ...notification,
                is_read: true,
                read_at: new Date().toISOString(),
            };

            setNotifications((current) =>
                current.map((item) =>
                    item.notification_uuid === notification.notification_uuid
                        ? { ...item, ...updatedNotification }
                        : item
                )
            );

            setUnreadCount((current) => Math.max(0, current - 1));
        } catch (error) {
            setNotificationsError(
                error.response?.data?.detail ||
                    "Unable to mark this notification as read."
            );
        } finally {
            setActionNotificationId(null);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("admin_access_token");
        navigate("/admin/login", { replace: true });
    };

    return (
        <div className="min-h-screen bg-slate-100 text-slate-900">
            {sidebarOpen && (
                <button
                    type="button"
                    aria-label="Close navigation menu"
                    onClick={() => setSidebarOpen(false)}
                    className="fixed inset-0 z-40 bg-slate-950/50 lg:hidden"
                />
            )}

            <aside
                className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-slate-800 bg-slate-950 text-white transition-transform duration-300 lg:translate-x-0 ${
                    sidebarOpen ? "translate-x-0" : "-translate-x-full"
                }`}
            >
                <div className="flex h-20 items-center gap-3 border-b border-slate-800 px-6">
                    <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-500/15 text-indigo-400">
                        <ShieldCheck size={26} />
                    </div>

                    <div>
                        <h1 className="font-bold tracking-wide">
                            Smart Dispatch
                        </h1>
                        <p className="mt-1 text-xs text-slate-400">
                            Administration
                        </p>
                    </div>

                    <button
                        type="button"
                        aria-label="Close sidebar"
                        onClick={() => setSidebarOpen(false)}
                        className="ml-auto rounded-lg p-2 text-slate-400 hover:bg-slate-800 lg:hidden"
                    >
                        <X size={20} />
                    </button>
                </div>

                <div className="px-4 py-6">
                    <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-widest text-slate-500">
                        Workspace
                    </p>

                    <nav className="space-y-1">
                        {navigationItems.map((item) => {
                            const Icon = item.icon;

                            return (
                                <NavLink
                                    key={item.path}
                                    to={item.path}
                                    end={item.end}
                                    onClick={() => setSidebarOpen(false)}
                                    className={({ isActive }) =>
                                        `flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${
                                            isActive
                                                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-950/30"
                                                : "text-slate-400 hover:bg-slate-800 hover:text-white"
                                        }`
                                    }
                                >
                                    <Icon size={19} />
                                    <span>{item.label}</span>
                                    <ChevronRight
                                        size={16}
                                        className="ml-auto opacity-60"
                                    />
                                </NavLink>
                            );
                        })}
                    </nav>
                </div>

                <div className="mt-auto border-t border-slate-800 p-4">
                    <div className="mb-4 flex items-center gap-3 rounded-xl bg-slate-900 p-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-500/15 text-indigo-400">
                            <ShieldCheck size={21} />
                        </div>

                        <div className="min-w-0">
                            <p className="text-sm font-semibold">
                                Administrator
                            </p>
                            <p className="text-xs text-slate-400">
                                Admin account
                            </p>
                        </div>
                    </div>

                    <button
                        type="button"
                        onClick={handleLogout}
                        className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium text-slate-400 transition hover:bg-red-500/10 hover:text-red-400"
                    >
                        <LogOut size={19} />
                        Sign out
                    </button>
                </div>
            </aside>

            <div className="min-h-screen lg:pl-72">
                <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur sm:px-6 lg:px-8">
                    <div className="flex items-center gap-3">
                        <button
                            type="button"
                            aria-label="Open navigation menu"
                            onClick={() => setSidebarOpen(true)}
                            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden"
                        >
                            <Menu size={22} />
                        </button>

                        <div>
                            <p className="text-sm font-semibold text-slate-900">
                                Admin Workspace
                            </p>
                            <p className="hidden text-xs text-slate-500 sm:block">
                                Manage your service operations
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        {/* Notification bell and popup */}
                        <div className="relative" ref={notificationRef}>
                            <button
                                type="button"
                                onClick={() => {
                                    const willOpen = !notificationOpen;
                                    setNotificationOpen(willOpen);

                                    if (willOpen) {
                                        loadNotifications();
                                    }
                                }}
                                aria-label={`Notifications, ${unreadCount} unread`}
                                aria-expanded={notificationOpen}
                                aria-haspopup="dialog"
                                className="relative flex h-11 w-11 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-700 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            >
                                <Bell size={21} />

                                {unreadCount > 0 && (
                                    <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1 text-[10px] font-bold text-white ring-2 ring-white">
                                        {unreadCount > 99 ? "99+" : unreadCount}
                                    </span>
                                )}
                            </button>

                            {notificationOpen && (
                                <div
                                    role="dialog"
                                    aria-label="Admin notifications"
                                    className="absolute right-0 z-50 mt-3 flex max-h-[min(75vh,34rem)] w-[min(22rem,calc(100vw-2rem))] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl sm:w-96"
                                >
                                    <div className="flex items-center justify-between border-b border-slate-100 px-4 py-4">
                                        <div>
                                            <h2 className="font-semibold text-slate-900">
                                                Notifications
                                            </h2>
                                            <p className="mt-1 text-xs text-slate-500">
                                                {unreadCount} unread
                                            </p>
                                        </div>

                                        <button
                                            type="button"
                                            onClick={loadNotifications}
                                            disabled={notificationsLoading}
                                            aria-label="Refresh notifications"
                                            className="rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 disabled:opacity-50"
                                        >
                                            <RefreshCw
                                                size={16}
                                                className={
                                                    notificationsLoading
                                                        ? "animate-spin"
                                                        : ""
                                                }
                                            />
                                        </button>
                                    </div>

                                    {notificationsError && (
                                        <div
                                            role="alert"
                                            className="mx-3 mt-3 rounded-lg border border-red-200 bg-red-50 p-3 text-xs text-red-700"
                                        >
                                            {notificationsError}
                                            <button
                                                type="button"
                                                onClick={loadNotifications}
                                                className="ml-2 font-semibold underline"
                                            >
                                                Retry
                                            </button>
                                        </div>
                                    )}

                                    <div className="overflow-y-auto">
                                        {notificationsLoading &&
                                        notifications.length === 0 ? (
                                            <div className="flex items-center justify-center gap-2 px-4 py-10 text-sm text-slate-500">
                                                <LoaderCircle
                                                    size={18}
                                                    className="animate-spin"
                                                />
                                                Loading notifications...
                                            </div>
                                        ) : notifications.length === 0 ? (
                                            <div className="px-5 py-10 text-center">
                                                <Bell
                                                    size={25}
                                                    className="mx-auto text-slate-300"
                                                />
                                                <p className="mt-3 font-medium text-slate-800">
                                                    You're all caught up
                                                </p>
                                                <p className="mt-1 text-sm text-slate-500">
                                                    New admin notifications will appear here.
                                                </p>
                                            </div>
                                        ) : (
                                            <ul className="divide-y divide-slate-100">
                                                {notifications.map(
                                                    (notification) => (
                                                        <li
                                                            key={notification.notification_uuid}
                                                            className={`px-4 py-4 ${
                                                                notification.is_read
                                                                    ? "bg-white"
                                                                    : "bg-indigo-50/60"
                                                            }`}
                                                        >
                                                            <div className="flex items-start gap-3">
                                                                <div
                                                                    className={`mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${
                                                                        notification.is_read
                                                                            ? "bg-slate-100 text-slate-500"
                                                                            : "bg-indigo-100 text-indigo-600"
                                                                    }`}
                                                                >
                                                                    <Bell size={17} />
                                                                </div>

                                                                <div className="min-w-0 flex-1">
                                                                    <div className="flex items-start justify-between gap-2">
                                                                        <p className="text-sm font-semibold text-slate-900">
                                                                            {notification.title}
                                                                        </p>

                                                                        {!notification.is_read && (
                                                                            <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-indigo-600" />
                                                                        )}
                                                                    </div>

                                                                    <p className="mt-1 wrap-break-word text-sm leading-5 text-slate-600">
                                                                        {notification.message}
                                                                    </p>

                                                                    <div className="mt-3 flex items-center justify-between gap-2">
                                                                        <span className="text-xs text-slate-400">
                                                                            {formatNotificationDate(
                                                                                notification.created_at
                                                                            )}
                                                                        </span>

                                                                        {!notification.is_read && (
                                                                            <button
                                                                                type="button"
                                                                                disabled={
                                                                                    actionNotificationId ===
                                                                                    notification.notification_uuid
                                                                                }
                                                                                onClick={() =>
                                                                                    handleMarkAsRead(
                                                                                        notification
                                                                                    )
                                                                                }
                                                                                className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-semibold text-indigo-600 hover:bg-indigo-100 disabled:opacity-50"
                                                                            >
                                                                                {actionNotificationId ===
                                                                                notification.notification_uuid ? (
                                                                                    <LoaderCircle
                                                                                        size={13}
                                                                                        className="animate-spin"
                                                                                    />
                                                                                ) : (
                                                                                    <Check size={13} />
                                                                                )}
                                                                                Mark read
                                                                            </button>
                                                                        )}
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </li>
                                                    )
                                                )}
                                            </ul>
                                        )}
                                    </div>

                                    {notifications.length > 0 && (
                                        <div className="border-t border-slate-100 bg-slate-50 px-4 py-3">
                                            <p className="text-center text-xs text-slate-500">
                                                Showing {notifications.length} notification
                                                {notifications.length === 1 ? "" : "s"}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2">
                            <span className="h-2 w-2 rounded-full bg-emerald-500" />
                            <span className="text-xs font-medium text-slate-600">
                                Admin portal
                            </span>
                        </div>
                    </div>
                </header>

                <main className="p-4 sm:p-6 lg:p-8">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}

export default AdminLayout;
