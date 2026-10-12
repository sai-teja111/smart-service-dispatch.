
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";

import { useAuth } from "../../context/AuthContext";
import {
    loginCustomer,
    loginTechnician
} from "../../api/auth";

function Login() {
    const navigate = useNavigate();
    const { login } = useAuth();

    const [role, setRole] = useState("customer");
    const [phone, setPhone] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (event) => {
        event.preventDefault();

        setError("");
        setLoading(true);

        try {
            let response;

            if (role === "customer") {
                response = await loginCustomer(phone, password);
            } else {
                response = await loginTechnician(phone, password);
            }

            if (
                !response?.access_token ||
                !response?.role ||
                !response?.user_uuid ||
                typeof response?.first_login !== "boolean"
            ) {
                throw new Error(
                    "The server returned an incomplete login response. Please try again."
                );
            }

            login(
                response.access_token,
                {
                    user_uuid: response.user_uuid,
                    name: response.name,
                    role: response.role,
                    first_login: response.first_login
                }
            );

            if (response.role === "customer") {
                navigate("/customer");
            } else if (response.role === "technician") {
                navigate("/technician");
            } else {
                setError("The server returned an unsupported user role.");
            }

        } catch (error) {
            const detail = error.response?.data?.detail;

            let message;

            if (typeof detail === "string") {
                message = detail;
            } else if (Array.isArray(detail)) {
                message = detail
                    .map((item) =>
                        typeof item === "string"
                            ? item
                            : item?.msg || "Invalid input"
                    )
                    .join(". ");
            } else if (error.message) {
                message = error.message;
            } else {
                message =
                    "Login failed. Please check your credentials.";
            }

            setError(message);

        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-950 px-4">
            <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">

                <div className="mb-8 text-center">
                    <h1 className="text-3xl font-bold text-slate-900">
                        Smart Service Dispatch
                    </h1>

                    <p className="mt-2 text-sm text-slate-500">
                        Sign in to continue
                    </p>
                </div>

                {/* Role Selection */}
                <div className="mb-6 grid grid-cols-2 gap-2 rounded-lg bg-slate-100 p-1">
                    <button
                        type="button"
                        onClick={() => {
                            setRole("customer");
                            setError("");
                        }}
                        className={`rounded-md py-2 text-sm font-medium transition ${
                            role === "customer"
                                ? "bg-white text-blue-600 shadow"
                                : "text-slate-500"
                        }`}
                    >
                        Customer
                    </button>

                    <button
                        type="button"
                        onClick={() => {
                            setRole("technician");
                            setError("");
                        }}
                        className={`rounded-md py-2 text-sm font-medium transition ${
                            role === "technician"
                                ? "bg-white text-blue-600 shadow"
                                : "text-slate-500"
                        }`}
                    >
                        Technician
                    </button>
                </div>

                {/* Login Form */}
                <form onSubmit={handleSubmit} className="space-y-5">

                    <div>
                        <label
                            htmlFor="phone"
                            className="mb-2 block text-sm font-medium text-slate-700"
                        >
                            Phone Number
                        </label>

                        <input
                            id="phone"
                            type="tel"
                            value={phone}
                            onChange={(event) =>
                                setPhone(event.target.value)
                            }
                            placeholder="Enter phone number"
                            required
                            className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                        />
                    </div>

                    <div>
                        <label
                            htmlFor="password"
                            className="mb-2 block text-sm font-medium text-slate-700"
                        >
                            Password
                        </label>

                        <div className="relative">
                            <input
                                id="password"
                                type={showPassword ? "text" : "password"}
                                value={password}
                                onChange={(event) =>
                                    setPassword(event.target.value)
                                }
                                placeholder="Enter password"
                                required
                                className="w-full rounded-lg border border-slate-300 px-4 py-3 pr-12 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                            />

                            <button
                                type="button"
                                onClick={() =>
                                    setShowPassword(!showPassword)
                                }
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 transition hover:text-slate-800"
                                aria-label={
                                    showPassword
                                        ? "Hide password"
                                        : "Show password"
                                }
                            >
                                {showPassword ? (
                                    <EyeOff size={20} />
                                ) : (
                                    <Eye size={20} />
                                )}
                            </button>
                        </div>
                    </div>

                    {error && (
                        <div
                            role="alert"
                            className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600"
                        >
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                        {loading
                            ? "Signing in..."
                            : `Sign in as ${role}`}
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-slate-500">
                    Don't have an account?{" "}
                    <Link
                        to="/register"
                        className="font-semibold text-blue-600 hover:underline"
                    >
                        Register
                    </Link>
                </p>
            </div>
        </div>
    );
}

export default Login;
