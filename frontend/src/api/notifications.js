import api from "./axios";

// Fetch notifications for the logged-in user
export async function getNotifications() {
    const response = await api.get("/notifications");
    return response.data;
}

// Mark a notification as read
export async function markNotificationAsRead(notificationUuid) {
    const response = await api.patch(
        `/notifications/${notificationUuid}/read`
    );

    return response.data;
}