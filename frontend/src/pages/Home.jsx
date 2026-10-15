import { useState } from "react";
import { Link } from "react-router-dom";
import {
    Activity,
    ArrowDownRight,
    ArrowRight,
    ArrowUpRight,
    Bot,
    Check,
    CheckCircle2,
    ChevronRight,
    Clock3,
    Cpu,
    Database,
    Headphones,
    LayoutDashboard,
    Menu,
    MapPin,
    Search,
    ShieldCheck,
    Sparkles,
    Users,
    Wrench,
    X,
    Zap,
} from "lucide-react";

const features = [
    {
        icon: Sparkles,
        number: "01",
        title: "Smart Service Detection",
        description:
            "Understand customer problems in natural language and identify the relevant service using semantic matching.",
        color: "bg-violet-50 text-violet-600 ring-violet-100",
    },
    {
        icon: Users,
        number: "02",
        title: "Intelligent Technician Matching",
        description:
            "Match service requests with suitable technicians using skills, location, availability, workload, and ratings.",
        color: "bg-blue-50 text-blue-600 ring-blue-100",
    },
    {
        icon: MapPin,
        number: "03",
        title: "Location-Based Matching",
        description:
            "Consider service areas and customer locations to help find an appropriate technician.",
        color: "bg-emerald-50 text-emerald-600 ring-emerald-100",
    },
    {
        icon: Activity,
        number: "04",
        title: "Service Tracking",
        description:
            "Follow service requests through their lifecycle, from creation and assignment to completion.",
        color: "bg-orange-50 text-orange-600 ring-orange-100",
    },
    {
        icon: ShieldCheck,
        number: "05",
        title: "Secure Authentication",
        description:
            "Keep customer and technician access protected with JWT-based authentication and secure password handling.",
        color: "bg-cyan-50 text-cyan-600 ring-cyan-100",
    },
    {
        icon: Bot,
        number: "06",
        title: "Smart Assistance",
        description:
            "Ask questions about supported service data and get answers through the application's assistant.",
        color: "bg-pink-50 text-pink-600 ring-pink-100",
    },
];

const steps = [
    {
        number: "01",
        icon: Search,
        title: "Raise a request",
        description:
            "Describe the problem and provide the details needed for the service.",
    },
    {
        number: "02",
        icon: Sparkles,
        title: "Identify the service",
        description:
            "Use service detection to help identify the appropriate service category.",
    },
    {
        number: "03",
        icon: Users,
        title: "Match a technician",
        description:
            "Evaluate technician suitability using skills and other matching factors.",
    },
    {
        number: "04",
        icon: CheckCircle2,
        title: "Track to completion",
        description:
            "Follow request status and review the service history when finished.",
    },
];

const technologies = [
    "Python",
    "FastAPI",
    "React",
    "PostgreSQL",
    "SQLModel",
    "ChromaDB",
];

function SectionLabel({ children }) {
    return (
        <div className="inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3.5 py-1.5 text-xs font-bold uppercase tracking-[0.16em] text-blue-700">
            <span className="h-1.5 w-1.5 rounded-full bg-blue-600" />
            {children}
        </div>
    );
}

function DashboardPreview() {
    return (
        <div className="relative mx-auto w-full max-w-147.5">
            <div className="absolute -right-10 -top-12 h-48 w-48 rounded-full bg-blue-300/30 blur-3xl" />
            <div className="absolute -bottom-12 -left-12 h-48 w-48 rounded-full bg-violet-300/30 blur-3xl" />

            <div className="absolute -left-4 top-16 hidden h-20 w-20 rounded-2xl border border-white/80 bg-white/70 shadow-lg backdrop-blur-xl sm:block" />

            <div className="relative overflow-hidden rounded-[26px] border border-slate-200/80 bg-white p-3 shadow-2xl shadow-blue-950/10 sm:p-5">
                <div className="flex items-center justify-between border-b border-slate-100 px-2 pb-4">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white">
                            <Zap size={20} />
                        </div>
                        <div>
                            <p className="text-sm font-bold text-slate-900">
                                Dispatch overview
                            </p>
                            <p className="text-xs text-slate-500">
                                Service management
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-1.5 rounded-full border border-emerald-100 bg-emerald-50 px-2.5 py-1.5">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                        <span className="text-[10px] font-semibold text-emerald-700 sm:text-xs">
                            Dashboard preview
                        </span>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-3 py-5 sm:grid-cols-3">
                    <div className="rounded-2xl border border-slate-100 bg-slate-50 p-3 sm:p-4">
                        <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-xl bg-blue-100 text-blue-700">
                            <LayoutDashboard size={18} />
                        </div>
                        <p className="text-[11px] font-medium text-slate-500">
                            Service workflow
                        </p>
                        <p className="mt-1 text-sm font-bold text-slate-900 sm:text-base">
                            End to end
                        </p>
                    </div>

                    <div className="rounded-2xl border border-slate-100 bg-slate-50 p-3 sm:p-4">
                        <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-xl bg-violet-100 text-violet-700">
                            <Users size={18} />
                        </div>
                        <p className="text-[11px] font-medium text-slate-500">
                            Technician selection
                        </p>
                        <p className="mt-1 text-sm font-bold text-slate-900 sm:text-base">
                            Skill-based
                        </p>
                    </div>

                    <div className="col-span-2 rounded-2xl border border-slate-100 bg-slate-50 p-3 sm:col-span-1 sm:p-4">
                        <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
                            <ShieldCheck size={18} />
                        </div>
                        <p className="text-[11px] font-medium text-slate-500">
                            Access
                        </p>
                        <p className="mt-1 text-sm font-bold text-slate-900 sm:text-base">
                            Role-based
                        </p>
                    </div>
                </div>

                <div className="rounded-2xl border border-slate-100 p-4 sm:p-5">
                    <div className="flex items-center justify-between gap-3">
                        <div>
                            <h3 className="text-sm font-bold text-slate-900">
                                Example service workflow
                            </h3>
                            <p className="mt-1 text-xs text-slate-500">
                                A simplified illustration
                            </p>
                        </div>
                        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                            <Activity size={19} />
                        </div>
                    </div>

                    <div className="mt-5 space-y-4">
                        <div className="flex items-start gap-3">
                            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                                <Search size={17} />
                            </div>
                            <div className="min-w-0 flex-1">
                                <div className="flex flex-wrap items-center justify-between gap-2">
                                    <p className="text-sm font-semibold text-slate-800">
                                        Request submitted
                                    </p>
                                    <span className="text-[10px] font-medium text-slate-400">
                                        Step 01
                                    </span>
                                </div>
                                <p className="mt-1 text-xs leading-5 text-slate-500">
                                    Customer describes the service problem.
                                </p>
                            </div>
                            <Check size={16} className="shrink-0 text-emerald-500" />
                        </div>

                        <div className="ml-4 h-4 border-l-2 border-dashed border-slate-200" />

                        <div className="flex items-start gap-3">
                            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-violet-50 text-violet-600">
                                <Sparkles size={17} />
                            </div>
                            <div className="min-w-0 flex-1">
                                <div className="flex flex-wrap items-center justify-between gap-2">
                                    <p className="text-sm font-semibold text-slate-800">
                                        Matching process
                                    </p>
                                    <span className="text-[10px] font-medium text-slate-400">
                                        Step 02
                                    </span>
                                </div>
                                <p className="mt-1 text-xs leading-5 text-slate-500">
                                    The system evaluates service requirements and technician suitability.
                                </p>
                            </div>
                            <Clock3 size={16} className="shrink-0 text-blue-500" />
                        </div>

                        <div className="ml-4 h-4 border-l-2 border-dashed border-slate-200" />

                        <div className="flex items-start gap-3">
                            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
                                <Wrench size={17} />
                            </div>
                            <div className="min-w-0 flex-1">
                                <div className="flex flex-wrap items-center justify-between gap-2">
                                    <p className="text-sm font-semibold text-slate-800">
                                        Service tracking
                                    </p>
                                    <span className="text-[10px] font-medium text-slate-400">
                                        Step 03
                                    </span>
                                </div>
                                <p className="mt-1 text-xs leading-5 text-slate-500">
                                    Follow assignment, progress, and completion.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="mt-3 flex items-center gap-3 rounded-2xl bg-slate-950 p-4 text-white">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/10 text-blue-300">
                        <Bot size={21} />
                    </div>
                    <div className="min-w-0 flex-1">
                        <p className="text-sm font-semibold">
                            Smart Service Dispatch
                        </p>
                        <p className="mt-1 text-xs text-slate-400">
                            One platform for service requests and technicians.
                        </p>
                    </div>
                    <ArrowUpRight size={19} className="shrink-0 text-blue-300" />
                </div>
            </div>

            <div className="absolute -right-3 top-24 hidden items-center gap-3 rounded-2xl border border-white bg-white p-3.5 shadow-xl sm:flex lg:-right-8">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
                    <CheckCircle2 size={22} />
                </div>
                <div>
                    <p className="text-xs font-bold text-slate-900">
                        Structured workflow
                    </p>
                    <p className="mt-1 text-[10px] text-slate-500">
                        From request to resolution
                    </p>
                </div>
            </div>
        </div>
    );
}

function Home() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const navigation = [
        { label: "Home", href: "#home" },
        { label: "About", href: "#about" },
        { label: "Features", href: "#features" },
        { label: "How It Works", href: "#how-it-works" },
        { label: "Technology", href: "#technology" },
    ];

    const closeMenu = () => setMobileMenuOpen(false);

    return (
        <div className="min-h-screen overflow-x-hidden bg-white text-slate-900 selection:bg-blue-100 selection:text-blue-900">
            {/* Navigation */}
            <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl">
                <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-3.5 sm:px-8 lg:px-10">
                    <Link to="/" onClick={closeMenu} className="group flex items-center gap-3">
                        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-600/20 transition duration-300 group-hover:rotate-6 group-hover:scale-105">
                            <Zap size={23} fill="currentColor" />
                        </div>
                        <div>
                            <p className="text-[15px] font-extrabold tracking-tight text-slate-950 sm:text-base">
                                Smart Service
                            </p>
                            <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-blue-600">
                                Dispatch System
                            </p>
                        </div>
                    </Link>

                    <nav className="hidden items-center gap-7 lg:flex">
                        {navigation.map((item) => (
                            <a
                                key={item.href}
                                href={item.href}
                                className="text-[13px] font-semibold text-slate-600 transition-colors hover:text-blue-600"
                            >
                                {item.label}
                            </a>
                        ))}
                    </nav>

                    {/* Desktop actions */}
                    <div className="hidden items-center gap-2 sm:flex">
                        <Link
                            to="/admin/login"
                            className="inline-flex items-center gap-1.5 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-blue-50 hover:text-blue-700"
                        >
                            <ShieldCheck size={16} />
                            Admin
                        </Link>

                        <Link
                            to="/login"
                            className="rounded-xl px-4 py-2.5 text-sm font-bold text-slate-700 transition hover:bg-slate-100 hover:text-blue-700"
                        >
                            Log in
                        </Link>

                        <Link
                            to="/register"
                            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-bold text-white shadow-md shadow-blue-600/20 transition hover:-translate-y-0.5 hover:bg-blue-700 hover:shadow-lg"
                        >
                            Get started <ArrowRight size={16} />
                        </Link>
                    </div>

                    {/* Mobile menu button */}
                    <button
                        type="button"
                        aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
                        aria-expanded={mobileMenuOpen}
                        onClick={() => setMobileMenuOpen((open) => !open)}
                        className="rounded-xl border border-slate-200 p-2.5 text-slate-700 transition hover:bg-slate-50 sm:hidden"
                    >
                        {mobileMenuOpen ? <X size={21} /> : <Menu size={21} />}
                    </button>
                </div>

                {/* Mobile menu */}
                {mobileMenuOpen && (
                    <div className="border-t border-slate-100 bg-white px-5 py-5 shadow-xl sm:hidden">
                        <nav className="flex flex-col gap-1">
                            {navigation.map((item) => (
                                <a
                                    key={item.href}
                                    href={item.href}
                                    onClick={closeMenu}
                                    className="rounded-xl px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-blue-50 hover:text-blue-700"
                                >
                                    {item.label}
                                </a>
                            ))}
                        </nav>

                        <div className="mt-4 grid grid-cols-3 gap-2 border-t border-slate-100 pt-4">
                            <Link
                                to="/admin/login"
                                onClick={closeMenu}
                                className="flex items-center justify-center gap-1 rounded-xl border border-blue-100 px-2 py-3 text-center text-xs font-bold text-blue-700 transition hover:bg-blue-50"
                            >
                                <ShieldCheck size={15} />
                                Admin
                            </Link>

                            <Link
                                to="/login"
                                onClick={closeMenu}
                                className="rounded-xl border border-slate-200 px-2 py-3 text-center text-xs font-bold text-slate-700 transition hover:bg-slate-50"
                            >
                                Log in
                            </Link>

                            <Link
                                to="/register"
                                onClick={closeMenu}
                                className="rounded-xl bg-blue-600 px-2 py-3 text-center text-xs font-bold text-white transition hover:bg-blue-700"
                            >
                                Get started
                            </Link>
                        </div>
                    </div>
                )}
            </header>

            <main>
                {/* Hero */}
                <section id="home" className="relative isolate scroll-mt-24 overflow-hidden bg-[#f8faff]">
                    <div className="pointer-events-none absolute inset-0 -z-10">
                        <div className="absolute -right-32 -top-36 h-120 w-120 rounded-full bg-blue-200/35 blur-3xl" />
                        <div className="absolute -bottom-48 left-[20%] h-105 w-105 rounded-full bg-violet-200/30 blur-3xl" />
                        <div className="absolute inset-0 bg-size-[48px_48px] bg-[linear-gradient(to_right,rgba(148,163,184,0.08)_1px,transparent_1px),linear-gradient(to_bottom,rgba(148,163,184,0.08)_1px,transparent_1px)] mask-[linear-gradient(to_bottom,black,transparent_85%)]" />
                    </div>

                    <div className="mx-auto grid max-w-7xl items-center gap-14 px-5 py-16 sm:px-8 sm:py-20 lg:grid-cols-[0.95fr_1.05fr] lg:gap-12 lg:px-10 lg:py-24">
                        <div className="relative z-10">
                            <div className="inline-flex items-center gap-2 rounded-full border border-blue-200/80 bg-white/80 px-3.5 py-2 text-xs font-bold text-blue-700 shadow-sm backdrop-blur">
                                <Sparkles size={15} />
                                Smarter service management
                                <ChevronRight size={14} />
                            </div>

                            <h1 className="mt-7 max-w-2xl text-4xl font-black leading-[1.12] tracking-[-0.045em] text-slate-950 sm:text-5xl lg:text-[62px]">
                                The right technician.
                                <span className="mt-1 block bg-linear-to-r from-blue-600 via-indigo-600 to-violet-600 bg-clip-text pb-1 text-transparent">
                                    The smarter way.
                                </span>
                            </h1>

                            <p className="mt-6 max-w-xl text-base leading-8 text-slate-600 sm:text-lg">
                                Simplify service requests, connect customers with
                                suitable technicians, and manage the journey from
                                the first request to final resolution.
                            </p>

                            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                                <Link
                                    to="/register"
                                    className="group inline-flex items-center justify-center gap-2.5 rounded-xl bg-blue-600 px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-blue-600/25 transition duration-300 hover:-translate-y-1 hover:bg-blue-700 hover:shadow-xl hover:shadow-blue-600/30"
                                >
                                    Create your account
                                    <ArrowRight size={17} className="transition-transform group-hover:translate-x-1" />
                                </Link>
                                <a
                                    href="#how-it-works"
                                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white/80 px-6 py-3.5 text-sm font-bold text-slate-700 transition hover:border-blue-200 hover:bg-white hover:text-blue-700"
                                >
                                    Explore the workflow
                                    <ArrowDownRight size={17} />
                                </a>
                            </div>

                            <div className="mt-9 flex flex-wrap gap-x-5 gap-y-3 border-t border-slate-200/80 pt-6">
                                {[
                                    "Skill-based matching",
                                    "Service history",
                                    "Role-based access",
                                ].map((item) => (
                                    <div key={item} className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                                        <CheckCircle2 size={15} className="text-emerald-600" />
                                        {item}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="relative px-1 py-2 sm:px-4 lg:px-0">
                            <DashboardPreview />
                        </div>
                    </div>

                    <div className="border-t border-slate-200/70 bg-white/65">
                        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-center gap-x-8 gap-y-3 px-5 py-5 text-xs font-semibold text-slate-500 sm:gap-x-12 sm:px-8 lg:px-10">
                            <span className="uppercase tracking-[0.16em] text-slate-400">
                                Built with
                            </span>
                            {technologies.slice(0, 4).map((technology) => (
                                <span key={technology} className="flex items-center gap-2">
                                    <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                                    {technology}
                                </span>
                            ))}
                        </div>
                    </div>
                </section>

                {/* About */}
                <section id="about" className="scroll-mt-24 bg-white">
                    <div className="mx-auto grid max-w-7xl gap-12 px-5 py-20 sm:px-8 sm:py-24 lg:grid-cols-[0.85fr_1.15fr] lg:items-center lg:gap-20 lg:px-10">
                        <div>
                            <SectionLabel>About the platform</SectionLabel>
                            <h2 className="mt-5 text-3xl font-extrabold leading-tight tracking-tight text-slate-950 sm:text-4xl">
                                Less coordination.
                                <span className="block text-blue-600">
                                    More clarity.
                                </span>
                            </h2>
                            <p className="mt-5 text-base leading-8 text-slate-600">
                                Smart Service Dispatch is a full-stack service
                                management platform that helps organize customer
                                requests and technician workflows in one place.
                                Its matching process considers service requirements
                                and technician suitability to support better
                                assignment decisions.
                            </p>
                            <a
                                href="#features"
                                className="mt-7 inline-flex items-center gap-2 text-sm font-bold text-blue-700 transition hover:gap-3"
                            >
                                Discover the features <ArrowRight size={16} />
                            </a>
                        </div>

                        <div className="grid gap-4 sm:grid-cols-2">
                            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 transition duration-300 hover:-translate-y-1 hover:border-blue-200 hover:bg-blue-50/50">
                                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-700">
                                    <Search size={23} />
                                </div>
                                <h3 className="mt-5 text-lg font-bold text-slate-900">
                                    Understand the request
                                </h3>
                                <p className="mt-2 text-sm leading-7 text-slate-600">
                                    Let customers describe their issue without
                                    needing to know every technical service category.
                                </p>
                            </div>

                            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 transition duration-300 hover:-translate-y-1 hover:border-violet-200 hover:bg-violet-50/50 sm:translate-y-8">
                                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-violet-100 text-violet-700">
                                    <Users size={23} />
                                </div>
                                <h3 className="mt-5 text-lg font-bold text-slate-900">
                                    Coordinate technicians
                                </h3>
                                <p className="mt-2 text-sm leading-7 text-slate-600">
                                    Organize assignments, availability, and
                                    workload in a structured workflow.
                                </p>
                            </div>

                            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 transition duration-300 hover:-translate-y-1 hover:border-emerald-200 hover:bg-emerald-50/50">
                                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-700">
                                    <Activity size={23} />
                                </div>
                                <h3 className="mt-5 text-lg font-bold text-slate-900">
                                    Follow every stage
                                </h3>
                                <p className="mt-2 text-sm leading-7 text-slate-600">
                                    Keep service status, history, and feedback
                                    accessible to the appropriate users.
                                </p>
                            </div>

                            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 transition duration-300 hover:-translate-y-1 hover:border-orange-200 hover:bg-orange-50/50 sm:translate-y-8">
                                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-orange-100 text-orange-700">
                                    <ShieldCheck size={23} />
                                </div>
                                <h3 className="mt-5 text-lg font-bold text-slate-900">
                                    Protect user access
                                </h3>
                                <p className="mt-2 text-sm leading-7 text-slate-600">
                                    Separate customer and technician experiences
                                    with authenticated access.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Features */}
                <section id="features" className="scroll-mt-24 bg-slate-50 py-20 sm:py-24">
                    <div className="mx-auto max-w-7xl px-5 sm:px-8 lg:px-10">
                        <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
                            <div className="max-w-2xl">
                                <SectionLabel>Platform capabilities</SectionLabel>
                                <h2 className="mt-5 text-3xl font-extrabold tracking-tight text-slate-950 sm:text-4xl">
                                    Everything connected.
                                    <span className="block text-blue-600">
                                        One service workflow.
                                    </span>
                                </h2>
                            </div>
                            <p className="max-w-md text-sm leading-7 text-slate-600 sm:text-base">
                                Purpose-built tools help customers and technicians
                                manage the service lifecycle with greater clarity.
                            </p>
                        </div>

                        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                            {features.map((feature) => {
                                const Icon = feature.icon;

                                return (
                                    <article
                                        key={feature.title}
                                        className="group rounded-3xl border border-slate-200/80 bg-white p-6 transition duration-300 hover:-translate-y-1.5 hover:border-blue-200 hover:shadow-xl hover:shadow-slate-900/5 sm:p-7"
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className={`flex h-12 w-12 items-center justify-center rounded-2xl ring-1 ${feature.color}`}>
                                                <Icon size={23} />
                                            </div>
                                            <span className="text-xs font-bold tracking-widest text-slate-300">
                                                {feature.number}
                                            </span>
                                        </div>
                                        <h3 className="mt-6 text-lg font-bold text-slate-900 transition group-hover:text-blue-700">
                                            {feature.title}
                                        </h3>
                                        <p className="mt-3 text-sm leading-7 text-slate-600">
                                            {feature.description}
                                        </p>
                                        <div className="mt-5 flex items-center gap-2 text-xs font-bold text-blue-600 opacity-0 transition duration-300 group-hover:translate-x-1 group-hover:opacity-100">
                                            Built into the workflow <ArrowRight size={14} />
                                        </div>
                                    </article>
                                );
                            })}
                        </div>
                    </div>
                </section>

                {/* How it works */}
                <section id="how-it-works" className="scroll-mt-24 bg-white py-20 sm:py-24">
                    <div className="mx-auto max-w-7xl px-5 sm:px-8 lg:px-10">
                        <div className="mx-auto max-w-2xl text-center">
                            <SectionLabel>How it works</SectionLabel>
                            <h2 className="mt-5 text-3xl font-extrabold tracking-tight text-slate-950 sm:text-4xl">
                                From a service request
                                <span className="block text-blue-600">
                                    to a completed job.
                                </span>
                            </h2>
                            <p className="mt-4 text-sm leading-7 text-slate-600 sm:text-base">
                                A straightforward workflow for customers,
                                technicians, and service coordination.
                            </p>
                        </div>

                        <div className="relative mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
                            <div className="absolute left-[12%] right-[12%] top-9 hidden border-t-2 border-dashed border-blue-100 lg:block" />
                            {steps.map((step) => {
                                const Icon = step.icon;

                                return (
                                    <article
                                        key={step.number}
                                        className="relative rounded-3xl border border-slate-200 bg-white p-6 transition duration-300 hover:-translate-y-1 hover:border-blue-200 hover:shadow-lg hover:shadow-blue-950/5"
                                    >
                                        <div className="relative flex items-center justify-between">
                                            <div className="flex h-17 w-17 items-center justify-center rounded-2xl border border-blue-100 bg-blue-50 text-blue-700 ring-8 ring-white">
                                                <Icon size={27} />
                                            </div>
                                            <span className="text-3xl font-black tracking-tight text-slate-200">
                                                {step.number}
                                            </span>
                                        </div>
                                        <h3 className="mt-6 text-lg font-bold text-slate-900">
                                            {step.title}
                                        </h3>
                                        <p className="mt-3 text-sm leading-7 text-slate-600">
                                            {step.description}
                                        </p>
                                    </article>
                                );
                            })}
                        </div>
                    </div>
                </section>

                {/* Technology */}
                <section id="technology" className="scroll-mt-24 overflow-hidden bg-slate-950 py-20 sm:py-24">
                    <div className="mx-auto grid max-w-7xl gap-12 px-5 sm:px-8 lg:grid-cols-2 lg:items-center lg:px-10">
                        <div>
                            <SectionLabel>Technology stack</SectionLabel>
                            <h2 className="mt-5 text-3xl font-extrabold leading-tight tracking-tight text-white sm:text-4xl">
                                Modern tools.
                                <span className="block text-blue-400">
                                    Practical architecture.
                                </span>
                            </h2>
                            <p className="mt-5 max-w-xl text-sm leading-7 text-slate-400 sm:text-base sm:leading-8">
                                A React frontend, FastAPI backend, SQLModel-based
                                data layer, PostgreSQL database, and semantic
                                matching components form the foundation of the
                                application.
                            </p>

                            <div className="mt-8 flex flex-wrap gap-3">
                                <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3.5 py-2.5 text-xs font-semibold text-slate-300">
                                    <Database size={15} className="text-blue-400" />
                                    Structured data
                                </div>
                                <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3.5 py-2.5 text-xs font-semibold text-slate-300">
                                    <Cpu size={15} className="text-violet-400" />
                                    Semantic matching
                                </div>
                                <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3.5 py-2.5 text-xs font-semibold text-slate-300">
                                    <ShieldCheck size={15} className="text-emerald-400" />
                                    Authenticated access
                                </div>
                            </div>
                        </div>

                        <div className="rounded-3xl border border-white/10 bg-white/4 p-5 sm:p-7">
                            <div className="flex items-center justify-between border-b border-white/10 pb-5">
                                <div>
                                    <p className="text-sm font-bold text-white">
                                        Application stack
                                    </p>
                                    <p className="mt-1 text-xs text-slate-500">
                                        Technologies used in this project
                                    </p>
                                </div>
                                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
                                    <Cpu size={21} />
                                </div>
                            </div>

                            <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3">
                                {technologies.map((technology, index) => (
                                    <div
                                        key={technology}
                                        className="rounded-2xl border border-white/10 bg-white/4 p-4 transition duration-300 hover:border-blue-400/40 hover:bg-blue-500/10"
                                    >
                                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10 text-xs font-extrabold text-blue-300">
                                            {String(index + 1).padStart(2, "0")}
                                        </div>
                                        <p className="mt-4 text-sm font-bold text-slate-200">
                                            {technology}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </section>

                {/* Call to action */}
                <section className="bg-white px-5 py-20 sm:px-8 sm:py-24 lg:px-10">
                    <div className="relative mx-auto max-w-7xl overflow-hidden rounded-4xl bg-linear-to-br from-blue-700 via-blue-600 to-indigo-700 px-6 py-14 shadow-2xl shadow-blue-900/15 sm:px-12 sm:py-16 lg:px-16">
                        <div className="pointer-events-none absolute -right-20 -top-28 h-80 w-80 rounded-full border-45 border-white/5" />
                        <div className="pointer-events-none absolute -bottom-36 right-[25%] h-72 w-72 rounded-full bg-violet-400/20 blur-3xl" />

                        <div className="relative grid gap-9 lg:grid-cols-[1fr_auto] lg:items-center">
                            <div className="max-w-2xl">
                                <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-bold text-blue-50">
                                    <Headphones size={14} />
                                    Your service workflow starts here
                                </div>
                                <h2 className="mt-5 text-3xl font-extrabold leading-tight tracking-tight text-white sm:text-4xl">
                                    Ready to make service management smarter?
                                </h2>
                                <p className="mt-4 max-w-xl text-sm leading-7 text-blue-100 sm:text-base">
                                    Create an account to access the service
                                    management experience and its role-specific
                                    features.
                                </p>
                            </div>

                            <div className="flex flex-col gap-3 sm:flex-row lg:flex-col">
                                <Link
                                    to="/register"
                                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-6 py-3.5 text-sm font-bold text-blue-700 shadow-lg transition hover:-translate-y-0.5 hover:bg-blue-50"
                                >
                                    Create account <ArrowRight size={17} />
                                </Link>
                                <Link
                                    to="/login"
                                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/30 bg-white/10 px-6 py-3.5 text-sm font-bold text-white transition hover:bg-white/15"
                                >
                                    Already registered? Log in
                                </Link>
                            </div>
                        </div>
                    </div>
                </section>
            </main>

            {/* Footer */}
            <footer className="border-t border-slate-800 bg-slate-950">
                <div className="mx-auto flex max-w-7xl flex-col gap-7 px-5 py-8 sm:px-8 md:flex-row md:items-center md:justify-between lg:px-10">
                    <Link to="/" className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white">
                            <Zap size={21} fill="currentColor" />
                        </div>
                        <div>
                            <p className="text-sm font-extrabold text-white">
                                Smart Service Dispatch
                            </p>
                            <p className="mt-1 text-xs text-slate-400">
                                Intelligent service management
                            </p>
                        </div>
                    </Link>

                    <div className="flex flex-wrap gap-x-5 gap-y-3 text-xs font-medium text-slate-400">
                        <a href="#about" className="transition hover:text-white">
                            About
                        </a>
                        <a href="#features" className="transition hover:text-white">
                            Features
                        </a>
                        <a href="#how-it-works" className="transition hover:text-white">
                            How it works
                        </a>
                        <Link to="/login" className="transition hover:text-white">
                            Login
                        </Link>
                        <Link
                            to="/admin/login"
                            className="inline-flex items-center gap-1.5 transition hover:text-blue-400"
                        >
                            <ShieldCheck size={14} />
                            Admin Portal
                        </Link>
                    </div>

                    <p className="text-xs text-slate-500">
                        © {new Date().getFullYear()} Smart Service Dispatch
                    </p>
                </div>
            </footer>
        </div>
    );
}

export default Home;