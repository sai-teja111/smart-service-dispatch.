import { useState } from "react";
import {
    ArrowRight,
    CheckCircle2,
    ClipboardCheck,
    Loader2,
    MapPin,
    Sparkles,
    Wrench,
    XCircle,
} from "lucide-react";

import {
    createServiceRequest,
    detectService,
} from "../../api/serviceRequests";

function CreateServiceRequest() {
    const [problemDescription, setProblemDescription] = useState("");
    const [priority, setPriority] = useState("Medium");

    const [detection, setDetection] = useState(null);
    const [availableServices, setAvailableServices] = useState([]);

    const [selectedSkillId, setSelectedSkillId] = useState("");

    const [detecting, setDetecting] = useState(false);
    const [creating, setCreating] = useState(false);

    const [error, setError] = useState("");
    const [success, setSuccess] = useState(null);

    const handleDetectService = async () => {
        if (!problemDescription.trim()) {
            setError("Please describe your service problem first.");
            return;
        }

        setError("");
        setSuccess(null);
        setDetection(null);
        setAvailableServices([]);
        setSelectedSkillId("");
        setDetecting(true);

        try {
            const data = await detectService(
                problemDescription.trim()
            );

            if (data.service_detection) {
                setDetection(data.service_detection);
                setSelectedSkillId(
                    String(data.service_detection.skill_id)
                );
            } else {
                setAvailableServices(
                    data.available_services || []
                );
            }
        } catch (error) {
            const message =
                error.response?.data?.detail ||
                "Unable to detect the service. Please try again.";

            setError(message);
        } finally {
            setDetecting(false);
        }
    };

    const handleCreateRequest = async () => {
        if (!problemDescription.trim()) {
            setError("Please describe your service problem.");
            return;
        }

        if (!selectedSkillId) {
            setError("Please select a service before continuing.");
            return;
        }

        setError("");
        setSuccess(null);
        setCreating(true);

        try {
            const data = await createServiceRequest(
                problemDescription.trim(),
                Number(selectedSkillId),
                priority
            );

            setSuccess(data);

            setProblemDescription("");
            setPriority("Medium");
            setDetection(null);
            setAvailableServices([]);
            setSelectedSkillId("");
        } catch (error) {
            const message =
                error.response?.data?.detail ||
                "Unable to create the service request.";

            setError(message);
        } finally {
            setCreating(false);
        }
    };

    return (
        <div className="mx-auto max-w-6xl">

            {/* Page Header */}
            <div className="mb-8">

                <div className="mb-3 flex items-center gap-2 text-sm font-medium text-blue-600">
                    <Wrench size={18} />
                    Service Request
                </div>

                <h1 className="text-3xl font-bold tracking-tight text-slate-900">
                    Create a Service Request
                </h1>

                <p className="mt-2 max-w-2xl text-slate-500">
                    Tell us what's wrong. Our intelligent service detection
                    system will identify the most suitable service for your
                    problem.
                </p>

            </div>

            {/* Error */}
            {error && (
                <div className="mb-6 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">

                    <XCircle
                        size={20}
                        className="mt-0.5 shrink-0"
                    />

                    <div>
                        <p className="font-semibold">
                            Request could not be completed
                        </p>

                        <p className="mt-1 text-sm">
                            {error}
                        </p>
                    </div>

                </div>
            )}

            {/* Success */}
            {success && (
                <div className="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-6">

                    <div className="flex items-start gap-3">

                        <CheckCircle2
                            size={24}
                            className="mt-0.5 shrink-0 text-emerald-600"
                        />

                        <div>
                            <h2 className="text-lg font-bold text-emerald-900">
                                Service request created successfully
                            </h2>

                            <p className="mt-1 text-sm text-emerald-700">
                                Your request has been submitted and the
                                technician matching process has been completed.
                            </p>
                        </div>

                    </div>

                    <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

                        <div className="rounded-xl bg-white/70 p-4">
                            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                                Service
                            </p>

                            <p className="mt-1 font-semibold text-slate-900">
                                {success.service}
                            </p>
                        </div>

                        <div className="rounded-xl bg-white/70 p-4">
                            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                                Priority
                            </p>

                            <p className="mt-1 font-semibold text-slate-900">
                                {success.priority}
                            </p>
                        </div>

                        <div className="rounded-xl bg-white/70 p-4">
                            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                                Status
                            </p>

                            <p className="mt-1 font-semibold text-slate-900">
                                {success.status}
                            </p>
                        </div>

                        <div className="rounded-xl bg-white/70 p-4">
                            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                                Technician
                            </p>

                            <p className="mt-1 font-semibold text-slate-900">
                                {success.technician?.technician_name ||
                                    "Being assigned"}
                            </p>
                        </div>

                    </div>

                    {success.technician && (
                        <div className="mt-4 flex items-center gap-2 text-sm text-emerald-800">

                            <MapPin size={17} />

                            <span>
                                Technician assigned successfully.
                            </span>

                        </div>
                    )}

                </div>
            )}

            <div className="grid gap-6 lg:grid-cols-3">

                {/* Main Form */}
                <div className="lg:col-span-2">

                    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">

                        {/* Form Header */}
                        <div className="border-b border-slate-200 p-6">

                            <div className="flex items-center gap-3">

                                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-100 text-blue-600">
                                    <ClipboardCheck size={22} />
                                </div>

                                <div>
                                    <h2 className="font-bold text-slate-900">
                                        Service Details
                                    </h2>

                                    <p className="text-sm text-slate-500">
                                        Describe the problem you are experiencing.
                                    </p>
                                </div>

                            </div>

                        </div>

                        <div className="space-y-6 p-6">

                            {/* Problem Description */}
                            <div>

                                <label
                                    htmlFor="problem-description"
                                    className="mb-2 block text-sm font-semibold text-slate-700"
                                >
                                    What problem are you experiencing?
                                </label>

                                <textarea
                                    id="problem-description"
                                    value={problemDescription}
                                    onChange={(event) =>
                                        setProblemDescription(
                                            event.target.value
                                        )
                                    }
                                    placeholder="Example: My AC is running but it is not cooling the room properly."
                                    rows={6}
                                    className="w-full resize-none rounded-xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
                                />

                                <div className="mt-2 flex justify-between text-xs text-slate-400">
                                    <span>
                                        Describe the issue in your own words.
                                    </span>

                                    <span>
                                        {problemDescription.length} characters
                                    </span>
                                </div>

                            </div>

                            {/* Detect Button */}
                            <button
                                type="button"
                                onClick={handleDetectService}
                                disabled={
                                    detecting ||
                                    !problemDescription.trim()
                                }
                                className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3.5 font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                {detecting ? (
                                    <>
                                        <Loader2
                                            size={19}
                                            className="animate-spin"
                                        />

                                        Analyzing your problem...
                                    </>
                                ) : (
                                    <>
                                        <Sparkles size={19} />

                                        Detect Suitable Service
                                        <ArrowRight size={18} />
                                    </>
                                )}
                            </button>

                            {/* Detected Service */}
                            {detection && (
                                <div className="rounded-2xl border border-blue-200 bg-blue-50 p-5">

                                    <div className="flex items-start gap-4">

                                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white">
                                            <Sparkles size={23} />
                                        </div>

                                        <div className="flex-1">

                                            <div className="flex flex-wrap items-center gap-2">

                                                <h3 className="font-bold text-slate-900">
                                                    {detection.skill_name}
                                                </h3>

                                                {detection.match_type && (
                                                    <span className="rounded-full bg-white px-2.5 py-1 text-xs font-medium text-blue-700">
                                                        {detection.match_type}
                                                    </span>
                                                )}

                                            </div>

                                            <p className="mt-1 text-sm text-slate-600">
                                                Our service detection system
                                                identified this as the most
                                                suitable service.
                                            </p>

                                        </div>

                                    </div>

                                    <div className="mt-5">

                                        <label
                                            htmlFor="priority"
                                            className="mb-2 block text-sm font-semibold text-slate-700"
                                        >
                                            Priority
                                        </label>

                                        <select
                                            id="priority"
                                            value={priority}
                                            onChange={(event) =>
                                                setPriority(
                                                    event.target.value
                                                )
                                            }
                                            className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
                                        >
                                            <option value="Low">
                                                Low
                                            </option>

                                            <option value="Medium">
                                                Medium
                                            </option>

                                            <option value="High">
                                                High
                                            </option>
                                        </select>

                                    </div>

                                </div>
                            )}

                            {/* Manual Service Selection */}
                            {availableServices.length > 0 && (
                                <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">

                                    <div className="mb-4">

                                        <h3 className="font-bold text-slate-900">
                                            Select a Service
                                        </h3>

                                        <p className="mt-1 text-sm text-slate-600">
                                            We couldn't confidently identify
                                            the service. Please select the
                                            closest option.
                                        </p>

                                    </div>

                                    <div className="grid gap-3 sm:grid-cols-2">

                                        {availableServices.map(
                                            (service) => (
                                                <button
                                                    key={service.skill_id}
                                                    type="button"
                                                    onClick={() =>
                                                        setSelectedSkillId(
                                                            String(
                                                                service.skill_id
                                                            )
                                                        )
                                                    }
                                                    className={`
                                                        rounded-xl border p-4
                                                        text-left transition
                                                        ${
                                                            selectedSkillId ===
                                                            String(
                                                                service.skill_id
                                                            )
                                                                ? "border-blue-500 bg-blue-50 ring-2 ring-blue-200"
                                                                : "border-slate-200 bg-white hover:border-blue-300 hover:bg-blue-50/50"
                                                        }
                                                    `}
                                                >
                                                    <div className="flex items-center justify-between gap-3">

                                                        <span className="text-sm font-semibold text-slate-800">
                                                            {service.skill_name}
                                                        </span>

                                                        {selectedSkillId ===
                                                            String(
                                                                service.skill_id
                                                            ) && (
                                                            <CheckCircle2
                                                                size={18}
                                                                className="shrink-0 text-blue-600"
                                                            />
                                                        )}

                                                    </div>
                                                </button>
                                            )
                                        )}

                                    </div>

                                    {selectedSkillId && (
                                        <div className="mt-5">

                                            <label
                                                htmlFor="manual-priority"
                                                className="mb-2 block text-sm font-semibold text-slate-700"
                                            >
                                                Priority
                                            </label>

                                            <select
                                                id="manual-priority"
                                                value={priority}
                                                onChange={(event) =>
                                                    setPriority(
                                                        event.target.value
                                                    )
                                                }
                                                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
                                            >
                                                <option value="Low">
                                                    Low
                                                </option>

                                                <option value="Medium">
                                                    Medium
                                                </option>

                                                <option value="High">
                                                    High
                                                </option>
                                            </select>

                                        </div>
                                    )}

                                </div>
                            )}

                            {/* Create Request */}
                            {selectedSkillId && (
                                <button
                                    type="button"
                                    onClick={handleCreateRequest}
                                    disabled={creating}
                                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-slate-950 px-5 py-3.5 font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                                >
                                    {creating ? (
                                        <>
                                            <Loader2
                                                size={19}
                                                className="animate-spin"
                                            />

                                            Creating Service Request...
                                        </>
                                    ) : (
                                        <>
                                            <ClipboardCheck size={19} />

                                            Submit Service Request
                                        </>
                                    )}
                                </button>
                            )}

                        </div>

                    </div>

                </div>

                {/* Information Panel */}
                <div className="space-y-6">

                    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

                        <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-blue-100 text-blue-600">
                            <Sparkles size={21} />
                        </div>

                        <h3 className="font-bold text-slate-900">
                            Intelligent Service Detection
                        </h3>

                        <p className="mt-2 text-sm leading-6 text-slate-500">
                            You don't need to know the exact service name.
                            Simply describe your problem and the system will
                            identify the most suitable service.
                        </p>

                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

                        <h3 className="font-bold text-slate-900">
                            What happens next?
                        </h3>

                        <div className="mt-5 space-y-5">

                            <div className="flex gap-3">

                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700">
                                    1
                                </div>

                                <div>
                                    <p className="text-sm font-semibold text-slate-800">
                                        Describe your problem
                                    </p>

                                    <p className="mt-1 text-xs leading-5 text-slate-500">
                                        Tell us what is wrong in your own words.
                                    </p>
                                </div>

                            </div>

                            <div className="flex gap-3">

                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700">
                                    2
                                </div>

                                <div>
                                    <p className="text-sm font-semibold text-slate-800">
                                        Service is identified
                                    </p>

                                    <p className="mt-1 text-xs leading-5 text-slate-500">
                                        Semantic matching identifies the
                                        appropriate service.
                                    </p>
                                </div>

                            </div>

                            <div className="flex gap-3">

                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700">
                                    3
                                </div>

                                <div>
                                    <p className="text-sm font-semibold text-slate-800">
                                        Technician matching
                                    </p>

                                    <p className="mt-1 text-xs leading-5 text-slate-500">
                                        The system searches for the most
                                        suitable available technician.
                                    </p>
                                </div>

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
}

export default CreateServiceRequest;