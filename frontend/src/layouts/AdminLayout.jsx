import { useState } from "react";
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
} from "lucide-react";

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

function AdminLayout() {
    const navigate = useNavigate();
    const [sidebarOpen, setSidebarOpen] = useState(false);

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
                    sidebarOpen
                        ? "translate-x-0"
                        : "-translate-x-full"
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
                <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/90 px-4 backdrop-blur sm:px-6 lg:px-8">
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

                    <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2">
                        <span className="h-2 w-2 rounded-full bg-emerald-500" />
                        <span className="text-xs font-medium text-slate-600">
                            Admin portal
                        </span>
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