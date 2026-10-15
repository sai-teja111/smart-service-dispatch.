import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
    ShieldCheck,
    Eye,
    EyeOff,
    LoaderCircle,
    ArrowLeft,
} from "lucide-react";

import { loginAdmin } from "../../api/admin";

function AdminLogin() {
    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (event) => {
        event.preventDefault();
        setError("");

        const normalizedEmail = email.trim().toLowerCase();

        if (!normalizedEmail || !password) {
            setError("Please enter your email and password.");
            return;
        }

        try {
            setLoading(true);

            const result = await loginAdmin(
                normalizedEmail,
                password
            );

            if (!result?.access_token) {
                throw new Error(
                    "The server did not return an access token."
                );
            }

            localStorage.setItem(
                "admin_access_token",
                result.access_token
            );

            navigate("/admin", { replace: true });
        } catch (requestError) {
            const statusCode = requestError.response?.status;

            if (statusCode === 401) {
                setError("Invalid Admin email or password.");
            } else if (statusCode === 403) {
                setError("Your Admin account is inactive.");
            } else if (requestError.response) {
                setError(
                    requestError.response.data?.detail ||
                    "Admin login failed. Please try again."
                );
            } else {
                setError(
                    "Unable to connect to the server. Check your connection and try again."
                );
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="relative flex min-h-screen items-center justify-center bg-slate-950 px-4 py-10">
            {/* BACK TO HOME */}
            <Link
                to="/"
                onClick={() => {
                    // Explicitly navigate to the public Home route.
                    navigate("/");
                }}
                className="absolute left-4 top-5 inline-flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition hover:border-indigo-500 hover:bg-slate-900 hover:text-white sm:left-8 sm:top-8"
            >
                <ArrowLeft size={17} />
                Back to Home
            </Link>

            <div className="w-full max-w-md">
                <div className="mb-8 text-center">
                    <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-500/15 text-indigo-400">
                        <ShieldCheck size={34} />
                    </div>

                    <p className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-400">
                        Smart Service Dispatch
                    </p>

                    <h1 className="mt-3 text-3xl font-bold text-white">
                        Admin Portal
                    </h1>

                    <p className="mt-2 text-sm text-slate-400">
                        Sign in to manage customers, technicians, and reports.
                    </p>
                </div>

                <div className="rounded-2xl border border-slate-800 bg-slate-900 p-7 shadow-2xl sm:p-8">
                    <h2 className="text-xl font-semibold text-white">
                        Administrator sign in
                    </h2>

                    <p className="mt-1 text-sm text-slate-400">
                        Use your provisioned Admin credentials.
                    </p>

                    <form
                        onSubmit={handleSubmit}
                        className="mt-7 space-y-5"
                    >
                        <div>
                            <label
                                htmlFor="admin-email"
                                className="mb-2 block text-sm font-medium text-slate-200"
                            >
                                Email address
                            </label>

                            <input
                                id="admin-email"
                                type="email"
                                autoComplete="username"
                                value={email}
                                onChange={(event) =>
                                    setEmail(event.target.value)
                                }
                                placeholder="admin@example.com"
                                required
                                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
                            />
                        </div>

                        <div>
                            <label
                                htmlFor="admin-password"
                                className="mb-2 block text-sm font-medium text-slate-200"
                            >
                                Password
                            </label>

                            <div className="relative">
                                <input
                                    id="admin-password"
                                    type={showPassword ? "text" : "password"}
                                    autoComplete="current-password"
                                    value={password}
                                    onChange={(event) =>
                                        setPassword(event.target.value)
                                    }
                                    placeholder="Enter your password"
                                    required
                                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 pr-12 text-white outline-none transition placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
                                />

                                <button
                                    type="button"
                                    onClick={() =>
                                        setShowPassword((current) => !current)
                                    }
                                    aria-label={
                                        showPassword
                                            ? "Hide password"
                                            : "Show password"
                                    }
                                    className="absolute inset-y-0 right-0 flex items-center px-4 text-slate-400 transition hover:text-white"
                                >
                                    {showPassword ? (
                                        <EyeOff size={19} />
                                    ) : (
                                        <Eye size={19} />
                                    )}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <div
                                role="alert"
                                className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300"
                            >
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3 font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                            {loading ? (
                                <>
                                    <LoaderCircle
                                        size={19}
                                        className="animate-spin"
                                    />
                                    Signing in...
                                </>
                            ) : (
                                "Sign in to Admin Portal"
                            )}
                        </button>
                    </form>
                </div>

                <p className="mt-6 text-center text-sm text-slate-400">
                    Return to{" "}
                    <Link
                        to="/"
                        className="font-medium text-indigo-400 transition hover:text-indigo-300"
                    >
                        Home
                    </Link>
                </p>
            </div>
        </main>
    );
}

export default AdminLogin;