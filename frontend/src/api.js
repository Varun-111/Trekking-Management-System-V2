const BASE = "/api";

async function request(path, options = {}) {
    const res = await fetch(BASE + path, {
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
        throw new Error(data.error || "Request failed");
    }
    return data;
}

export const api = {
    // auth
    register: (payload) => request("/auth/register", { method: "POST", body: JSON.stringify(payload) }),
    login: (payload) => request("/auth/login", { method: "POST", body: JSON.stringify(payload) }),
    logout: () => request("/auth/logout", { method: "POST" }),
    me: () => request("/auth/me"),

    // admin
    adminDashboard: () => request("/admin/dashboard"),
    adminTreks: (params = {}) => request(`/admin/treks?${new URLSearchParams(params)}`),
    adminAddTrek: (payload) => request("/admin/treks", { method: "POST", body: JSON.stringify(payload) }),
    adminEditTrek: (id, payload) => request(`/admin/treks/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
    adminDeleteTrek: (id) => request(`/admin/treks/${id}`, { method: "DELETE" }),

    adminStaffList: (params = {}) => request(`/admin/staff?${new URLSearchParams(params)}`),
    adminAddStaff: (payload) => request("/admin/staff", { method: "POST", body: JSON.stringify(payload) }),
    adminRemoveStaff: (id) => request(`/admin/staff/${id}`, { method: "DELETE" }),

    adminUsers: (params = {}) => request(`/admin/users?${new URLSearchParams(params)}`),
    adminBlock: (id) => request(`/admin/block/${id}`, { method: "POST" }),
    adminUnblock: (id) => request(`/admin/unblock/${id}`, { method: "POST" }),

    adminBookings: (params = {}) => request(`/admin/bookings?${new URLSearchParams(params)}`),

    // staff
    staffDashboard: () => request("/staff/dashboard"),
    staffTrek: (id) => request(`/staff/trek/${id}`),
    staffUpdateTrek: (id, payload) => request(`/staff/trek/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
    staffParticipants: (params = {}) => request(`/staff/participants?${new URLSearchParams(params)}`),
    staffProfile: () => request("/staff/profile"),
    staffUpdateProfile: (payload) => request("/staff/profile", { method: "PUT", body: JSON.stringify(payload) }),

    // trekker
    trekkerDashboard: () => request("/trekker/dashboard"),
    trekkerTreks: (params = {}) => {
        const clean = Object.fromEntries(Object.entries(params).filter(([, v]) => v !== "" && v !== null && v !== undefined));
        return request(`/trekker/treks?${new URLSearchParams(clean)}`);
    },
    trekkerTrekDetail: (id) => request(`/trekker/treks/${id}`),
    trekkerBookTrek: (id) => request(`/trekker/treks/${id}/book`, { method: "POST" }),
    trekkerBookings: () => request("/trekker/bookings"),
    trekkerCancelBooking: (id) => request(`/trekker/bookings/${id}/cancel`, { method: "POST" }),
    trekkerProfile: () => request("/trekker/profile"),
    trekkerUpdateProfile: (payload) => request("/trekker/profile", { method: "PUT", body: JSON.stringify(payload) }),

    // export
    triggerCsvExport: () => request("/export/history/csv", { method: "POST" }),
    csvExportStatus: (taskId) => request(`/export/history/csv/status/${taskId}`),
};
