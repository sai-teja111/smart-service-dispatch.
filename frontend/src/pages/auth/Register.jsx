
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
    ArrowLeft,
    Eye,
    EyeOff,
    LoaderCircle,
    Plus,
    Trash2,
    UserRound,
    Wrench,
    Zap
} from "lucide-react";

import {
    registerCustomer,
    registerTechnician
} from "../../api/auth";

import { getSkills } from "../../api/skills";


const initialForm = {
    name: "",
    phone: "",
    password: "",
    city: "",
    area: "",
    pincode: ""
};

const initialSkill = {
    skill_id: "",
    experience_years: "",
    expertise_level: "Beginner"
};

function Register() {
    const navigate = useNavigate();

    const [role, setRole] = useState("customer");
    const [form, setForm] = useState(initialForm);
    const [selectedSkills, setSelectedSkills] = useState([
        { ...initialSkill }
    ]);

    const [skills, setSkills] = useState([]);
    const [skillsLoading, setSkillsLoading] = useState(false);
    const [skillsError, setSkillsError] = useState("");

    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    useEffect(() => {
        if (role !== "technician") {
            return;
        }

        let active = true;

        async function loadSkills() {
            setSkillsLoading(true);
            setSkillsError("");

            try {
                const data = await getSkills();

                if (active) {
                    setSkills(data);
                }
            } catch (err) {
                if (active) {
                    setSkillsError(
                        err.response?.data?.detail ||
                        "Unable to load skills. Please try again."
                    );
                }
            } finally {
                if (active) {
                    setSkillsLoading(false);
                }
            }
        }

        loadSkills();

        return () => {
            active = false;
        };
    }, [role]);

    const handleChange = (event) => {
        const { name, value } = event.target;

        setForm((previous) => ({
            ...previous,
            [name]: value
        }));
    };

    const handleSkillChange = (index, field, value) => {
        setSelectedSkills((previous) =>
            previous.map((skill, skillIndex) =>
                skillIndex === index
                    ? { ...skill, [field]: value }
                    : skill
            )
        );
    };

    const addSkill = () => {
        setSelectedSkills((previous) => [
            ...previous,
            { ...initialSkill }
        ]);
    };

    const removeSkill = (index) => {
        setSelectedSkills((previous) =>
            previous.filter((_, skillIndex) => skillIndex !== index)
        );
    };

    const handleRoleChange = (nextRole) => {
        setRole(nextRole);
        setError("");
        setSuccess("");
        setSelectedSkills([{ ...initialSkill }]);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();

        setError("");
        setSuccess("");

        if (!/^\d{10}$/.test(form.phone)) {
            setError("Enter a valid 10-digit phone number.");
            return;
        }

        if (!/^\d{6}$/.test(form.pincode)) {
            setError("Enter a valid 6-digit pincode.");
            return;
        }

        if (role === "technician") {
            if (selectedSkills.length === 0) {
                setError("Select at least one skill.");
                return;
            }

            const hasIncompleteSkill = selectedSkills.some(
                (skill) =>
                    skill.skill_id === "" ||
                    skill.experience_years === "" ||
                    Number(skill.experience_years) < 0 ||
                    !Number.isInteger(Number(skill.experience_years)) ||
                    !skill.expertise_level
            );

            if (hasIncompleteSkill) {
                setError(
                    "Complete the skill, experience and expertise fields."
                );
                return;
            }

            const skillIds = selectedSkills.map(
                (skill) => Number(skill.skill_id)
            );

            if (new Set(skillIds).size !== skillIds.length) {
                setError("Please select each skill only once.");
                return;
            }
        }

        setLoading(true);

        try {
            if (role === "customer") {
                await registerCustomer({
                    customer_name: form.name.trim(),
                    phone: form.phone,
                    password: form.password,
                    city: form.city.trim(),
                    area: form.area.trim(),
                    pincode: form.pincode
                });
            } else {
                await registerTechnician({
                    technician_name: form.name.trim(),
                    phone: form.phone,
                    password: form.password,
                    city: form.city.trim(),
                    area: form.area.trim(),
                    pincode: form.pincode,
                    skills: selectedSkills.map((skill) => ({
                        skill_id: Number(skill.skill_id),
                        experience_years: Number(
                            skill.experience_years
                        ),
                        expertise_level: skill.expertise_level
                    }))
                });
            }

            setSuccess(
                "Registration successful! You can now log in."
            );

            setTimeout(() => {
                navigate("/login");
            }, 1200);
        } catch (err) {
            const detail = err.response?.data?.detail;

            setError(
                typeof detail === "string"
                    ? detail
                    : Array.isArray(detail)
                        ? detail.map((item) => item.msg).join(", ")
                        : "Registration failed. Please check your details and try again."
            );
        } finally {
            setLoading(false);
        }
    };

    const inputClass =
        "w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-100";

    const labelClass =
        "mb-2 block text-sm font-semibold text-slate-700";

    return (
        <div className="min-h-screen bg-slate-50">

            {/* NAVBAR */}
            <header className="border-b border-slate-200 bg-white">
                <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">

                    <Link to="/" className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white">
                            <Zap size={21} />
                        </div>

                        <div>
                            <p className="font-bold text-slate-900">
                                Smart Service
                            </p>
                            <p className="text-xs text-blue-600">
                                Dispatch System
                            </p>
                        </div>
                    </Link>

                    <Link
                        to="/login"
                        className="text-sm font-semibold text-blue-600 hover:text-blue-700"
                    >
                        Already registered? Login
                    </Link>

                </div>
            </header>


            {/* REGISTRATION FORM */}
            <main className="px-4 py-10 sm:px-6">

                <div className="mx-auto max-w-2xl">

                    <Link
                        to="/"
                        className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-blue-600"
                    >
                        <ArrowLeft size={17} />
                        Back to Home
                    </Link>

                    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-9">

                        <div className="mb-7 text-center">

                            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                                {role === "customer" ? (
                                    <UserRound size={28} />
                                ) : (
                                    <Wrench size={28} />
                                )}
                            </div>

                            <h1 className="mt-4 text-2xl font-bold text-slate-900 sm:text-3xl">
                                Create Your Account
                            </h1>

                            <p className="mt-2 text-sm text-slate-500">
                                Join Smart Service Dispatch today.
                            </p>

                        </div>


                        {/* ROLE SELECTION */}
                        <div className="mb-7 grid grid-cols-2 gap-3">

                            <button
                                type="button"
                                onClick={() => handleRoleChange("customer")}
                                className={`flex items-center justify-center gap-2 rounded-xl border px-4 py-3 text-sm font-semibold transition ${
                                    role === "customer"
                                        ? "border-blue-600 bg-blue-50 text-blue-700"
                                        : "border-slate-200 text-slate-600 hover:bg-slate-50"
                                }`}
                            >
                                <UserRound size={18} />
                                Customer
                            </button>

                            <button
                                type="button"
                                onClick={() => handleRoleChange("technician")}
                                className={`flex items-center justify-center gap-2 rounded-xl border px-4 py-3 text-sm font-semibold transition ${
                                    role === "technician"
                                        ? "border-blue-600 bg-blue-50 text-blue-700"
                                        : "border-slate-200 text-slate-600 hover:bg-slate-50"
                                }`}
                            >
                                <Wrench size={18} />
                                Technician
                            </button>

                        </div>


                        {error && (
                            <div
                                role="alert"
                                className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
                            >
                                {error}
                            </div>
                        )}

                        {success && (
                            <div
                                role="status"
                                className="mb-5 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700"
                            >
                                {success}
                            </div>
                        )}


                        <form onSubmit={handleSubmit} className="space-y-5">

                            {/* NAME */}
                            <div>
                                <label className={labelClass} htmlFor="name">
                                    {role === "customer"
                                        ? "Customer Name"
                                        : "Technician Name"}
                                </label>

                                <input
                                    id="name"
                                    name="name"
                                    type="text"
                                    autoComplete="name"
                                    value={form.name}
                                    onChange={handleChange}
                                    placeholder="Enter your full name"
                                    className={inputClass}
                                    required
                                    maxLength={100}
                                />
                            </div>


                            {/* PHONE */}
                            <div>
                                <label className={labelClass} htmlFor="phone">
                                    Phone Number
                                </label>

                                <input
                                    id="phone"
                                    name="phone"
                                    type="tel"
                                    inputMode="numeric"
                                    autoComplete="tel"
                                    value={form.phone}
                                    onChange={handleChange}
                                    placeholder="10-digit phone number"
                                    className={inputClass}
                                    required
                                    maxLength={10}
                                    pattern="[0-9]{10}"
                                />
                            </div>


                            {/* PASSWORD */}
                            <div>
                                <label className={labelClass} htmlFor="password">
                                    Password
                                </label>

                                <div className="relative">

                                    <input
                                        id="password"
                                        name="password"
                                        type={showPassword ? "text" : "password"}
                                        autoComplete="new-password"
                                        value={form.password}
                                        onChange={handleChange}
                                        placeholder="Create a password"
                                        className={`${inputClass} pr-12`}
                                        required
                                        minLength={8}
                                    />

                                    <button
                                        type="button"
                                        onClick={() =>
                                            setShowPassword((value) => !value)
                                        }
                                        aria-label={
                                            showPassword
                                                ? "Hide password"
                                                : "Show password"
                                        }
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-blue-600"
                                    >
                                        {showPassword ? (
                                            <EyeOff size={19} />
                                        ) : (
                                            <Eye size={19} />
                                        )}
                                    </button>

                                </div>

                                <p className="mt-2 text-xs text-slate-500">
                                    Use at least 8 characters.
                                </p>
                            </div>


                            {/* CITY AND AREA */}
                            <div className="grid gap-5 sm:grid-cols-2">

                                <div>
                                    <label className={labelClass} htmlFor="city">
                                        City
                                    </label>

                                    <input
                                        id="city"
                                        name="city"
                                        value={form.city}
                                        onChange={handleChange}
                                        placeholder="e.g. Hyderabad"
                                        className={inputClass}
                                        required
                                        maxLength={100}
                                    />
                                </div>

                                <div>
                                    <label className={labelClass} htmlFor="area">
                                        Area
                                    </label>

                                    <input
                                        id="area"
                                        name="area"
                                        value={form.area}
                                        onChange={handleChange}
                                        placeholder="e.g. Madhapur"
                                        className={inputClass}
                                        required
                                        maxLength={100}
                                    />
                                </div>

                            </div>


                            {/* PINCODE */}
                            <div>
                                <label className={labelClass} htmlFor="pincode">
                                    Pincode
                                </label>

                                <input
                                    id="pincode"
                                    name="pincode"
                                    type="text"
                                    inputMode="numeric"
                                    value={form.pincode}
                                    onChange={handleChange}
                                    placeholder="6-digit pincode"
                                    className={inputClass}
                                    required
                                    maxLength={6}
                                    pattern="[0-9]{6}"
                                />
                            </div>


                            {/* TECHNICIAN SKILLS */}
                            {role === "technician" && (
                                <section className="border-t border-slate-200 pt-6">

                                    <div className="mb-4">
                                        <h2 className="text-lg font-bold text-slate-900">
                                            Your Professional Skills
                                        </h2>

                                        <p className="mt-1 text-sm text-slate-500">
                                            Select your skills and specify your
                                            experience and expertise for each.
                                        </p>
                                    </div>


                                    {skillsLoading && (
                                        <div className="flex items-center gap-2 py-4 text-sm text-slate-500">
                                            <LoaderCircle
                                                size={18}
                                                className="animate-spin"
                                            />
                                            Loading skills from the server...
                                        </div>
                                    )}

                                    {skillsError && (
                                        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                                            <p>{skillsError}</p>

                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setRole("customer");
                                                    setTimeout(
                                                        () => setRole("technician"),
                                                        0
                                                    );
                                                }}
                                                className="mt-2 font-semibold underline"
                                            >
                                                Retry loading skills
                                            </button>
                                        </div>
                                    )}


                                    {!skillsLoading &&
                                        !skillsError &&
                                        skills.length === 0 && (
                                            <p className="rounded-xl bg-amber-50 p-4 text-sm text-amber-800">
                                                No skills are currently available.
                                            </p>
                                        )}


                                    {!skillsLoading &&
                                        skills.length > 0 &&
                                        selectedSkills.map((selected, index) => {

                                            const selectedIds =
                                                selectedSkills
                                                    .filter((_, i) => i !== index)
                                                    .map((skill) =>
                                                        Number(skill.skill_id)
                                                    );

                                            return (
                                                <div
                                                    key={index}
                                                    className="mb-4 rounded-xl border border-slate-200 bg-slate-50 p-4"
                                                >

                                                    <div className="mb-4 flex items-center justify-between">

                                                        <h3 className="text-sm font-bold text-slate-800">
                                                            Skill {index + 1}
                                                        </h3>

                                                        {selectedSkills.length > 1 && (
                                                            <button
                                                                type="button"
                                                                onClick={() =>
                                                                    removeSkill(index)
                                                                }
                                                                aria-label={`Remove skill ${index + 1}`}
                                                                className="rounded-lg p-2 text-red-500 hover:bg-red-50"
                                                            >
                                                                <Trash2 size={17} />
                                                            </button>
                                                        )}

                                                    </div>


                                                    <div className="space-y-4">

                                                        <div>
                                                            <label
                                                                className={labelClass}
                                                                htmlFor={`skill-${index}`}
                                                            >
                                                                Select Skill
                                                            </label>

                                                            <select
                                                                id={`skill-${index}`}
                                                                value={selected.skill_id}
                                                                onChange={(event) =>
                                                                    handleSkillChange(
                                                                        index,
                                                                        "skill_id",
                                                                        event.target.value
                                                                    )
                                                                }
                                                                className={inputClass}
                                                                required
                                                            >
                                                                <option value="">
                                                                    Choose a skill
                                                                </option>

                                                                {skills.map((skill) => (
                                                                    <option
                                                                        key={skill.skill_id}
                                                                        value={skill.skill_id}
                                                                        disabled={selectedIds.includes(
                                                                            skill.skill_id
                                                                        )}
                                                                    >
                                                                        {skill.skill_name}
                                                                        {skill.category
                                                                            ? ` — ${skill.category}`
                                                                            : ""}
                                                                    </option>
                                                                ))}

                                                            </select>
                                                        </div>


                                                        <div className="grid gap-4 sm:grid-cols-2">

                                                            <div>
                                                                <label
                                                                    className={labelClass}
                                                                    htmlFor={`experience-${index}`}
                                                                >
                                                                    Experience (Years)
                                                                </label>

                                                                <input
                                                                    id={`experience-${index}`}
                                                                    type="number"
                                                                    min="0"
                                                                    max="80"
                                                                    step="1"
                                                                    value={selected.experience_years}
                                                                    onChange={(event) =>
                                                                        handleSkillChange(
                                                                            index,
                                                                            "experience_years",
                                                                            event.target.value
                                                                        )
                                                                    }
                                                                    placeholder="e.g. 3"
                                                                    className={inputClass}
                                                                    required
                                                                />
                                                            </div>


                                                            <div>
                                                                <label
                                                                    className={labelClass}
                                                                    htmlFor={`expertise-${index}`}
                                                                >
                                                                    Expertise Level
                                                                </label>

                                                                <select
                                                                    id={`expertise-${index}`}
                                                                    value={selected.expertise_level}
                                                                    onChange={(event) =>
                                                                        handleSkillChange(
                                                                            index,
                                                                            "expertise_level",
                                                                            event.target.value
                                                                        )
                                                                    }
                                                                    className={inputClass}
                                                                    required
                                                                >
                                                                    <option value="Beginner">
                                                                        Beginner
                                                                    </option>

                                                                    <option value="Intermediate">
                                                                        Intermediate
                                                                    </option>

                                                                    <option value="Expert">
                                                                        Expert
                                                                    </option>
                                                                </select>
                                                            </div>

                                                        </div>

                                                    </div>

                                                </div>
                                            );
                                        })}


                                    {!skillsLoading &&
                                        !skillsError &&
                                        skills.length > 0 &&
                                        selectedSkills.length < skills.length && (
                                            <button
                                                type="button"
                                                onClick={addSkill}
                                                className="inline-flex items-center gap-2 rounded-lg border border-blue-200 px-4 py-2.5 text-sm font-semibold text-blue-600 transition hover:bg-blue-50"
                                            >
                                                <Plus size={17} />
                                                Add Another Skill
                                            </button>
                                        )}

                                </section>
                            )}


                            {/* SUBMIT */}
                            <button
                                type="submit"
                                disabled={
                                    loading ||
                                    (role === "technician" &&
                                        (skillsLoading ||
                                            Boolean(skillsError) ||
                                            skills.length === 0))
                                }
                                className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3.5 text-sm font-bold text-white shadow-md transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                {loading && (
                                    <LoaderCircle
                                        size={19}
                                        className="animate-spin"
                                    />
                                )}

                                {loading
                                    ? "Creating Account..."
                                    : `Register as ${role === "customer" ? "Customer" : "Technician"}`}
                            </button>

                        </form>


                        <p className="mt-6 text-center text-sm text-slate-500">
                            Already have an account?{" "}
                            <Link
                                to="/login"
                                className="font-semibold text-blue-600 hover:underline"
                            >
                                Login
                            </Link>
                        </p>

                    </div>

                </div>

            </main>

        </div>
    );
}

export default Register;
