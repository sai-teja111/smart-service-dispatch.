import { useCallback, useEffect, useState } from "react";
import {
    Bell,
    CheckCheck,
    LoaderCircle,
    ExternalLink,
} from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";

import {
    getNotifications,
    markNotificationAsRead,
} from "../api/notifications";

export default function NotificationBell() {
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [isOpen, setIsOpen] = useState(false);
    const [loadingIds, setLoadingIds] = useState([]);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [error, setError] = useState("");

    const navigate = useNavigate();
    const location = useLocation();

    // Fetch the latest notifications from the backend.
    const fetchNotifications = useCallback(async () => {
        setIsRefreshing(true);

        try {
            const data = await getNotifications();
            const latestNotifications = data.notifications ?? [];

            setNotifications(latestNotifications);

            setUnreadCount(
                data.unread_count ??
                    latestNotifications.filter(
                        (notification) => !notification.is_read
                    ).length
            );

            setError("");

            return latestNotifications;
        } catch (err) {
            console.error("Failed to fetch notifications:", err);
            setError("Unable to load notifications.");
            return null;
        } finally {
            setIsRefreshing(false);
        }
    }, []);

    // Initial fetch and periodic refresh.
    useEffect(() => {
        fetchNotifications();

        const intervalId = setInterval(() => {
            fetchNotifications();
        }, 30000);

        return () => clearInterval(intervalId);
    }, [fetchNotifications]);

    // Mark a notification as read.
    const handleMarkAsRead = async (notificationUuid) => {
        if (loadingIds.includes(notificationUuid)) {
            return false;
        }

        const notification = notifications.find(
            (item) => item.notification_uuid === notificationUuid
        );

        if (!notification) {
            await fetchNotifications();
            return false;
        }

        if (notification.is_read) {
            return true;
        }

        setLoadingIds((previous) => [
            ...previous,
            notificationUuid,
        ]);

        setError("");

        try {
            await markNotificationAsRead(notificationUuid);

            // Update the notification locally after backend confirmation.
            setNotifications((previous) =>
                previous.map((item) =>
                    item.notification_uuid === notificationUuid
                        ? {
                              ...item,
                              is_read: true,
                          }
                        : item
                )
            );

            setUnreadCount((previous) => Math.max(0, previous - 1));

            // Confirm the latest unread count from the backend.
            await fetchNotifications();

            return true;
        } catch (err) {
            console.error(
                "Failed to mark notification as read:",
                err
            );

            setError("Unable to mark notification as read.");

            await fetchNotifications();

            return false;
        } finally {
            setLoadingIds((previous) =>
                previous.filter((id) => id !== notificationUuid)
            );
        }
    };

    // Navigate immediately; mark the notification as read independently.
    const handleViewNotification = (notification) => {
        // Close the dropdown immediately.
        setIsOpen(false);

        // Navigate to the correct portal's request details page.
        if (notification.request_uuid) {
            const isTechnician =
                location.pathname.startsWith("/technician");

            const requestPath = isTechnician
                ? `/technician/requests/${notification.request_uuid}`
                : `/customer/requests/${notification.request_uuid}`;

            navigate(requestPath);
        }

        // Mark as read without blocking navigation.
        if (!notification.is_read) {
            handleMarkAsRead(notification.notification_uuid);
        }
    };

    // Refresh the notification list when opening the dropdown.
    const handleToggleDropdown = () => {
        const nextOpen = !isOpen;

        setIsOpen(nextOpen);

        if (nextOpen) {
            fetchNotifications();
        }
    };

    return (
        <div className="relative">
            {/* Notification Bell */}
            <button
                type="button"
                onClick={handleToggleDropdown}
                className="relative rounded-xl p-2.5 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
                aria-label={`Notifications, ${unreadCount} unread`}
                aria-expanded={isOpen}
            >
                <Bell size={22} />

                {unreadCount > 0 && (
                    <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-500 px-1 text-xs font-semibold text-white">
                        {unreadCount > 99 ? "99+" : unreadCount}
                    </span>
                )}
            </button>

            {/* Notification Dropdown */}
            {isOpen && (
                <div className="absolute right-0 z-50 mt-3 w-80 max-w-[90vw] overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl sm:w-96">
                    {/* Header */}
                    <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
                        <div>
                            <h3 className="font-semibold text-slate-900">
                                Notifications
                            </h3>

                            <p className="text-xs text-slate-500">
                                {unreadCount} unread
                            </p>
                        </div>

                        <button
                            type="button"
                            onClick={fetchNotifications}
                            disabled={isRefreshing}
                            className="inline-flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-800 disabled:opacity-50"
                        >
                            {isRefreshing && (
                                <LoaderCircle
                                    size={13}
                                    className="animate-spin"
                                />
                            )}

                            Refresh
                        </button>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <p
                            role="alert"
                            className="px-4 py-3 text-sm text-red-600"
                        >
                            {error}
                        </p>
                    )}

                    {/* Notification List */}
                    <div className="max-h-96 overflow-y-auto">
                        {notifications.length === 0 && !error ? (
                            <p className="px-4 py-8 text-center text-sm text-slate-500">
                                No notifications yet.
                            </p>
                        ) : (
                            notifications.map((notification) => {
                                const isMarking = loadingIds.includes(
                                    notification.notification_uuid
                                );

                                return (
                                    <div
                                        key={notification.notification_uuid}
                                        className={`border-b border-slate-100 px-4 py-3 ${
                                            notification.is_read
                                                ? "bg-white"
                                                : "bg-blue-50"
                                        }`}
                                    >
                                        <div className="flex items-start gap-3">
                                            {/* Notification Content */}
                                            <div className="min-w-0 flex-1">
                                                <p className="text-sm font-semibold text-slate-900">
                                                    {notification.title}
                                                </p>

                                                <p className="mt-1 text-sm text-slate-600">
                                                    {notification.message}
                                                </p>

                                                <p className="mt-2 text-xs text-slate-400">
                                                    {new Date(
                                                        notification.created_at
                                                    ).toLocaleString()}
                                                </p>

                                                {notification.request_uuid && (
                                                    <button
                                                        type="button"
                                                        onClick={() =>
                                                            handleViewNotification(
                                                                notification
                                                            )
                                                        }
                                                        className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-800"
                                                    >
                                                        View Notification
                                                        <ExternalLink size={12} />
                                                    </button>
                                                )}
                                            </div>

                                            {/* Mark as Read */}
                                            {!notification.is_read && (
                                                <button
                                                    type="button"
                                                    title="Mark as read"
                                                    aria-label="Mark notification as read"
                                                    disabled={isMarking}
                                                    onClick={() =>
                                                        handleMarkAsRead(
                                                            notification.notification_uuid
                                                        )
                                                    }
                                                    className="rounded-md p-1 text-blue-600 transition hover:bg-blue-100 disabled:opacity-50"
                                                >
                                                    {isMarking ? (
                                                        <LoaderCircle
                                                            size={17}
                                                            className="animate-spin"
                                                        />
                                                    ) : (
                                                        <CheckCheck size={17} />
                                                    )}
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}