import {
    Bot,
    ChartNoAxesCombined,
    Check,
    ChevronRight,
    ClipboardList,
    Clock3,
    LayoutDashboard,
    LogOut,
    Menu,
    Sparkles,
    UserCheck,
    UserRound,
    Wrench,
    X,
} from "lucide-react";

import { useEffect, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import NotificationBell from "../components/NotificationBell";

const navigationItems = [
    {
        name: "Dashboard",
        path: "/technician",
        icon: LayoutDashboard,
        end: true,
    },
    {
        name: "Assigned Requests",
        path: "/technician/requests",
        icon: ClipboardList,
    },
    {
        name: "Service History",
        path: "/technician/history",
        icon: Clock3,
    },
    {
        name: "Availability",
        path: "/technician/availability",
        icon: UserCheck,
    },
    {
        name: "Reports",
        path: "/technician/reports",
        icon: ChartNoAxesCombined,
    },
    {
        name: "AI Assistant",
        path: "/technician/ai-assistant",
        icon: Bot,
    },
];

function getInitials(name) {
    const parts = String(name || "Technician")
        .trim()
        .split(/\s+/)
        .filter(Boolean);

    if (!parts.length) return "T";

    return parts
        .slice(0, 2)
        .map((part) => part[0].toUpperCase())
        .join("");
}

function TechnicianLayout() {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const navigate = useNavigate();
    const { user, logout } = useAuth();

    const technicianName =
        user?.name || user?.technician_name || "Technician";

    const initials = getInitials(technicianName);

    const handleLogout = () => {
        setSidebarOpen(false);
        logout();
        navigate("/login");
    };

    // Close the mobile drawer with Escape.
    useEffect(() => {
        if (!sidebarOpen) return undefined;

        const handleKeyDown = (event) => {
            if (event.key === "Escape") {
                setSidebarOpen(false);
            }
        };

        window.addEventListener("keydown", handleKeyDown);

        return () => {
            window.removeEventListener("keydown", handleKeyDown);
        };
    }, [sidebarOpen]);

    // Prevent background scrolling while the mobile drawer is open.
    useEffect(() => {
        if (!sidebarOpen) return undefined;

        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";

        return () => {
            document.body.style.overflow = previousOverflow;
        };
    }, [sidebarOpen]);

    return (
        <div className="min-h-screen bg-slate-50">
            {/* Mobile backdrop */}
            {sidebarOpen && (
                <button
                    type="button"
                    aria-label="Close navigation menu"
                    onClick={() => setSidebarOpen(false)}
                    className="fixed inset-0 z-40 cursor-default bg-slate-950/60 backdrop-blur-[2px] lg:hidden"
                />
            )}

            {/* Sidebar */}
            <aside
                id="technician-sidebar"
                aria-label="Technician navigation"
                className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-slate-800/80 bg-slate-950 text-white shadow-2xl shadow-slate-950/10 transition-transform duration-300 ease-out lg:translate-x-0 lg:shadow-none ${
                    sidebarOpen ? "translate-x-0" : "-translate-x-full"
                }`}
            >
                {/* Brand */}
                <div className="flex h-20 shrink-0 items-center justify-between border-b border-white/10 px-5 sm:px-6">
                    <NavLink
                        to="/technician"
                        end
                        onClick={() => setSidebarOpen(false)}
                        className="group flex min-w-0 items-center gap-3"
                        aria-label="Smart Service technician dashboard"
                    >
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-600 shadow-lg shadow-blue-600/20 transition group-hover:bg-blue-500">
                            <Wrench size={21} strokeWidth={2} />
                        </div>

                        <div className="min-w-0">
                            <h1 className="text-base font-bold tracking-tight text-white">
                                Smart Service
                            </h1>

                            <p className="mt-0.5 text-[11px] text-slate-400">
                                Intelligent Service Dispatch
                            </p>
                        </div>
                    </NavLink>

                    <button
                        type="button"
                        onClick={() => setSidebarOpen(false)}
                        className="rounded-lg p-2 text-slate-400 transition hover:bg-white/10 hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-400 lg:hidden"
                        aria-label="Close sidebar"
                    >
                        <X size={19} />
                    </button>
                </div>

                {/* Navigation */}
                <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-6">
                    <div className="mb-4 px-3">
                        <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-slate-500">
                            Technician Workspace
                        </p>
                    </div>

                    {navigationItems.map((item) => {
                        const Icon = item.icon;

                        return (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                end={Boolean(item.end)}
                                onClick={() => setSidebarOpen(false)}
                                className={({ isActive }) =>
                                    `group flex items-center gap-3 rounded-xl px-3 py-3 text-[13px] font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-400 ${
                                        isActive
                                            ? "bg-blue-600 text-white shadow-lg shadow-blue-950/30"
                                            : "text-slate-400 hover:bg-white/6 hover:text-white"
                                    }`
                                }
                            >
                                {({ isActive }) => (
                                    <>
                                        <Icon
                                            size={19}
                                            strokeWidth={isActive ? 2.2 : 1.8}
                                            className="shrink-0"
                                        />

                                        <span className="min-w-0 flex-1">
                                            {item.name}
                                        </span>

                                        {isActive && (
                                            <ChevronRight
                                                size={15}
                                                className="shrink-0 text-blue-100"
                                            />
                                        )}
                                    </>
                                )}
                            </NavLink>
                        );
                    })}

                    <div className="mx-3 my-5 border-t border-white/10" />

                    <div className="rounded-xl border border-blue-400/15 bg-blue-500/[0.07] p-3.5">
                        <div className="flex items-center gap-2 text-blue-300">
                            <Sparkles size={16} />
                            <span className="text-xs font-semibold">
                                Work smarter
                            </span>
                        </div>

                        <p className="mt-2 text-xs leading-5 text-slate-400">
                            Get help with service information and your assigned
                            work through the AI Assistant.
                        </p>

                        <NavLink
                            to="/technician/ai-assistant"
                            onClick={() => setSidebarOpen(false)}
                            className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-blue-300 transition hover:text-white"
                        >
                            Ask a question
                            <ChevronRight size={14} />
                        </NavLink>
                    </div>
                </nav>

                {/* Technician account and logout */}
                <div className="shrink-0 border-t border-white/10 p-3">
                    <div className="mb-2 flex items-center gap-3 rounded-xl border border-white/6 bg-white/4 p-3">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-linear-to-br from-blue-500 to-indigo-600 text-sm font-bold text-white shadow-sm">
                            {initials}
                        </div>

                        <div className="min-w-0 flex-1">
                            <p className="truncate text-sm font-semibold text-white">
                                {technicianName}
                            </p>

                            <p className="mt-0.5 flex items-center gap-1.5 text-xs text-slate-400">
                                <Check
                                    size={12}
                                    className="text-emerald-400"
                                />
                                Technician account
                            </p>
                        </div>
                    </div>

                    <button
                        type="button"
                        onClick={handleLogout}
                        className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-[13px] font-medium text-slate-400 transition hover:bg-red-500/10 hover:text-red-300 focus:outline-none focus:ring-2 focus:ring-red-400"
                    >
                        <LogOut size={18} />
                        <span>Log out</span>
                    </button>
                </div>
            </aside>

            {/* Main area */}
            <div className="min-h-screen lg:pl-72">
                {/* Topbar */}
                <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-slate-200/80 bg-white/95 px-4 backdrop-blur-xl sm:px-6 lg:px-8">
                    <div className="flex min-w-0 items-center gap-3">
                        <button
                            type="button"
                            onClick={() => setSidebarOpen(true)}
                            aria-controls="technician-sidebar"
                            aria-expanded={sidebarOpen}
                            aria-label="Open navigation menu"
                            className="rounded-xl border border-slate-200 p-2 text-slate-600 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 lg:hidden"
                        >
                            <Menu size={20} />
                        </button>

                        <div className="min-w-0">
                            <p className="text-xs font-medium text-slate-500 sm:text-sm">
                                Technician Portal
                            </p>

                            <h2 className="mt-0.5 truncate text-base font-bold tracking-tight text-slate-900 sm:text-lg">
                                Service Management
                            </h2>
                        </div>
                    </div>

                    <div className="flex shrink-0 items-center gap-3 sm:gap-4">
                        <NotificationBell />

                        <div className="hidden h-9 w-px bg-slate-200 sm:block" />

                        <div className="flex items-center gap-2.5 sm:gap-3">
                            <div className="flex h-9 w-9 items-center justify-center rounded-full border border-blue-100 bg-blue-50 text-xs font-bold text-blue-700 sm:h-10 sm:w-10 sm:text-sm">
                                {initials}
                            </div>

                            <div className="hidden min-w-0 sm:block">
                                <p className="max-w-40 truncate text-sm font-semibold text-slate-800">
                                    {technicianName}
                                </p>

                                <p className="mt-0.5 text-xs text-slate-500">
                                    Technician account
                                </p>
                            </div>
                        </div>
                    </div>
                </header>

                {/* Page content */}
                <main className="min-h-[calc(100vh-5rem)] p-4 sm:p-6 lg:p-8">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}

export default TechnicianLayout;
