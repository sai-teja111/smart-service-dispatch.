import {
    AlertCircle,
    CalendarDays,
    CheckCircle2,
    ClipboardList,
    Loader2,
    MessageSquare,
    Send,
    Star,
    UserRound,
} from "lucide-react";

import { useEffect, useState } from "react";

import {
    createFeedback,
    getFeedback,
    getMyServiceRequests,
} from "../../api/serviceRequests";


function formatDate(dateValue) {
    if (!dateValue) {
        return "Date unavailable";
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
        return "Date unavailable";
    }

    return date.toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}


function formatStatus(status) {
    if (!status) {
        return "Unknown";
    }

    return status
        .toLowerCase()
        .split("_")
        .map(
            (word) =>
                word.charAt(0).toUpperCase() + word.slice(1)
        )
        .join(" ");
}


function getStatusStyles(status) {
    switch (status) {
        case "OPEN":
            return "bg-blue-50 text-blue-700 border-blue-200";

        case "PENDING":
            return "bg-amber-50 text-amber-700 border-amber-200";

        case "IN_PROGRESS":
            return "bg-indigo-50 text-indigo-700 border-indigo-200";

        case "COMPLETED":
            return "bg-emerald-50 text-emerald-700 border-emerald-200";

        default:
            return "bg-slate-50 text-slate-700 border-slate-200";
    }
}


function RatingStars({
    value,
    onChange,
    disabled = false,
}) {
    return (
        <div className="flex items-center gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
                <button
                    key={star}
                    type="button"
                    disabled={disabled}
                    onClick={() => onChange(star)}
                    className={`rounded-lg p-1 transition ${
                        disabled
                            ? "cursor-default"
                            : "cursor-pointer hover:bg-amber-50"
                    }`}
                    aria-label={`Rate ${star} out of 5`}
                >
                    <Star
                        size={24}
                        className={
                            star <= value
                                ? "fill-amber-400 text-amber-400"
                                : "text-slate-300"
                        }
                    />
                </button>
            ))}
        </div>
    );
}


function FeedbackCard({
    request,
    feedbackData,
    onFeedbackSubmitted,
}) {
    const [rating, setRating] = useState(0);
    const [comments, setComments] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");


    const isCompleted =
        request.status === "COMPLETED";

    const existingFeedback =
        feedbackData?.feedback || null;

    const technicianName =
        feedbackData?.technician?.technician_name ||
        request.technician?.technician_name ||
        "Technician";


    async function handleSubmit(event) {
        event.preventDefault();

        setError("");
        setSuccess("");

        if (rating < 1 || rating > 5) {
            setError("Please select a rating from 1 to 5 stars.");
            return;
        }

        try {
            setSubmitting(true);

            const response = await createFeedback(
                request.request_uuid,
                rating,
                comments.trim()
            );

            setSuccess(
                response?.message ||
                    "Feedback submitted successfully."
            );

            setRating(0);
            setComments("");

            onFeedbackSubmitted(
                request.request_uuid,
                response
            );
        } catch (error) {
            const message =
                error?.response?.data?.detail ||
                "Unable to submit feedback.";

            setError(message);
        } finally {
            setSubmitting(false);
        }
    }


    return (
        <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">

            {/* Request Header */}
            <div className="border-b border-slate-100 p-6">

                <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

                    <div className="flex gap-4">

                        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                            <ClipboardList size={21} />
                        </div>

                        <div>

                            <h2 className="text-lg font-bold text-slate-900">
                                {request.service}
                            </h2>

                            <p className="mt-1 text-xs text-slate-400">
                                Request ID:{" "}
                                {request.request_uuid}
                            </p>

                        </div>

                    </div>


                    <span
                        className={`w-fit rounded-full border px-3 py-1 text-xs font-semibold ${getStatusStyles(
                            request.status
                        )}`}
                    >
                        {formatStatus(request.status)}
                    </span>

                </div>


                <div className="mt-5 rounded-xl bg-slate-50 p-4">

                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                        Problem Description
                    </p>

                    <p className="mt-2 text-sm leading-6 text-slate-700">
                        {request.problem_description}
                    </p>

                </div>


                <div className="mt-5 grid gap-4 sm:grid-cols-2">

                    <div className="flex items-center gap-3">

                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
                            <CalendarDays size={17} />
                        </div>

                        <div>

                            <p className="text-xs text-slate-400">
                                Requested On
                            </p>

                            <p className="mt-1 text-sm font-medium text-slate-700">
                                {formatDate(
                                    request.request_date
                                )}
                            </p>

                        </div>

                    </div>


                    <div className="flex items-center gap-3">

                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
                            <UserRound size={17} />
                        </div>

                        <div>

                            <p className="text-xs text-slate-400">
                                Technician
                            </p>

                            <p className="mt-1 text-sm font-medium text-slate-700">
                                {request.technician
                                    ?.technician_name ||
                                    "Not assigned yet"}
                            </p>

                        </div>

                    </div>

                </div>

            </div>


            {/* Existing Feedback */}
            {existingFeedback ? (

                <div className="p-6">

                    <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">

                        <div className="flex items-start gap-3">

                            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600">
                                <CheckCircle2 size={20} />
                            </div>

                            <div>

                                <h3 className="font-semibold text-emerald-900">
                                    Feedback Submitted
                                </h3>

                                <p className="mt-1 text-sm text-emerald-700">
                                    Thank you for sharing your experience.
                                </p>

                            </div>

                        </div>


                        <div className="mt-5 rounded-xl bg-white p-4">

                            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

                                <div>

                                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                                        Your Rating
                                    </p>

                                    <div className="mt-2 flex items-center gap-1">

                                        {[1, 2, 3, 4, 5].map(
                                            (star) => (
                                                <Star
                                                    key={star}
                                                    size={19}
                                                    className={
                                                        star <=
                                                        Number(
                                                            existingFeedback.rating
                                                        )
                                                            ? "fill-amber-400 text-amber-400"
                                                            : "text-slate-300"
                                                    }
                                                />
                                            )
                                        )}

                                    </div>

                                </div>


                                {existingFeedback.feedback_date && (
                                    <p className="text-xs text-slate-400">
                                        Submitted{" "}
                                        {formatDate(
                                            existingFeedback.feedback_date
                                        )}
                                    </p>
                                )}

                            </div>


                            {existingFeedback.comments && (
                                <div className="mt-4 border-t border-slate-100 pt-4">

                                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                                        Your Comments
                                    </p>

                                    <p className="mt-2 text-sm leading-6 text-slate-700">
                                        {existingFeedback.comments}
                                    </p>

                                </div>
                            )}

                        </div>


                        {feedbackData?.technician && (
                            <div className="mt-4 text-sm text-emerald-800">

                                Technician:{" "}
                                <span className="font-semibold">
                                    {feedbackData.technician.technician_name}
                                </span>

                                {feedbackData.technician.rating !==
                                    null &&
                                    feedbackData.technician.rating !==
                                        undefined && (
                                        <>
                                            {" "}
                                            · Current rating:{" "}
                                            <span className="font-semibold">
                                                {
                                                    feedbackData
                                                        .technician
                                                        .rating
                                                }
                                            </span>
                                        </>
                                    )}

                            </div>
                        )}

                    </div>

                </div>

            ) : !isCompleted ? (

                /* Not Completed */
                <div className="p-6">

                    <div className="rounded-xl border border-amber-200 bg-amber-50 p-5">

                        <div className="flex items-start gap-3">

                            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-amber-100 text-amber-600">
                                <MessageSquare size={20} />
                            </div>

                            <div>

                                <h3 className="font-semibold text-amber-900">
                                    Feedback available after completion
                                </h3>

                                <p className="mt-1 text-sm leading-6 text-amber-700">
                                    Once this service is completed, you will
                                    be able to rate the technician and share
                                    your experience.
                                </p>

                            </div>

                        </div>

                    </div>

                </div>

            ) : (

                /* Feedback Form */
                <form
                    onSubmit={handleSubmit}
                    className="p-6"
                >

                    <div>

                        <div className="flex items-center gap-3">

                            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                                <MessageSquare size={20} />
                            </div>

                            <div>

                                <h3 className="font-semibold text-slate-900">
                                    How was your service?
                                </h3>

                                <p className="text-sm text-slate-500">
                                    Rate your experience with the technician.
                                </p>

                            </div>

                        </div>


                        <div className="mt-6">

                            <label className="text-sm font-semibold text-slate-800">
                                Your Rating
                            </label>

                            <div className="mt-3 flex items-center gap-3">

                                <RatingStars
                                    value={rating}
                                    onChange={setRating}
                                />

                                <span className="text-sm text-slate-500">
                                    {rating === 0
                                        ? "Select a rating"
                                        : `${rating} out of 5`}
                                </span>

                            </div>

                        </div>


                        <div className="mt-6">

                            <label
                                htmlFor={`feedback-${request.request_uuid}`}
                                className="text-sm font-semibold text-slate-800"
                            >
                                Comments
                            </label>

                            <textarea
                                id={`feedback-${request.request_uuid}`}
                                value={comments}
                                onChange={(event) =>
                                    setComments(
                                        event.target.value
                                    )
                                }
                                rows={4}
                                maxLength={1000}
                                placeholder="Tell us about your experience..."
                                className="mt-2 w-full resize-none rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                            />

                            <div className="mt-1 flex justify-end text-xs text-slate-400">
                                {comments.length}/1000
                            </div>

                        </div>


                        {error && (
                            <div className="mt-5 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4">

                                <AlertCircle
                                    size={18}
                                    className="mt-0.5 shrink-0 text-red-600"
                                />

                                <p className="text-sm leading-5 text-red-700">
                                    {error}
                                </p>

                            </div>
                        )}


                        {success && (
                            <div className="mt-5 flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4">

                                <CheckCircle2
                                    size={18}
                                    className="mt-0.5 shrink-0 text-emerald-600"
                                />

                                <p className="text-sm leading-5 text-emerald-700">
                                    {success}
                                </p>

                            </div>
                        )}


                        <div className="mt-6 flex justify-end">

                            <button
                                type="submit"
                                disabled={submitting}
                                className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                            >

                                {submitting ? (
                                    <>
                                        <Loader2
                                            size={18}
                                            className="animate-spin"
                                        />
                                        Submitting...
                                    </>
                                ) : (
                                    <>
                                        <Send size={18} />
                                        Submit Feedback
                                    </>
                                )}

                            </button>

                        </div>

                    </div>

                </form>

            )}

        </div>
    );
}


function Feedback() {
    const [requests, setRequests] = useState([]);
    const [feedbacks, setFeedbacks] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");


    useEffect(() => {
        let isMounted = true;

        async function loadFeedbackData() {
            try {
                setLoading(true);
                setError("");

                const response =
                    await getMyServiceRequests();

                const serviceRequests =
                    Array.isArray(
                        response?.service_requests
                    )
                        ? response.service_requests
                        : [];

                if (!isMounted) {
                    return;
                }

                setRequests(serviceRequests);

                const completedRequests =
                    serviceRequests.filter(
                        (request) =>
                            request.status ===
                            "COMPLETED"
                    );

                if (
                    completedRequests.length ===
                    0
                ) {
                    return;
                }

                const feedbackResults =
                    await Promise.all(
                        completedRequests.map(
                            async (request) => {
                                try {
                                    const feedback =
                                        await getFeedback(
                                            request.request_uuid
                                        );

                                    return {
                                        requestUuid:
                                            request.request_uuid,
                                        feedback,
                                    };
                                } catch {
                                    return {
                                        requestUuid:
                                            request.request_uuid,
                                        feedback: null,
                                    };
                                }
                            }
                        )
                    );

                if (!isMounted) {
                    return;
                }

                const feedbackMap = {};

                feedbackResults.forEach(
                    ({
                        requestUuid,
                        feedback,
                    }) => {
                        feedbackMap[requestUuid] =
                            feedback;
                    }
                );

                setFeedbacks(feedbackMap);
            } catch (error) {
                if (!isMounted) {
                    return;
                }

                const message =
                    error?.response?.data?.detail ||
                    "Unable to load your feedback information.";

                setError(message);
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        }

        loadFeedbackData();

        return () => {
            isMounted = false;
        };
    }, []);


    function handleFeedbackSubmitted(
        requestUuid,
        response
    ) {
        setFeedbacks((current) => ({
            ...current,
            [requestUuid]: {
                request_uuid: requestUuid,
                feedback: {
                    feedback_uuid:
                        response.feedback_uuid,
                    rating: response.rating,
                    comments: response.comments,
                },
                technician:
                    response.technician,
            },
        }));
    }


    if (loading) {
        return (
            <div className="rounded-2xl border border-slate-200 bg-white p-10 shadow-sm">

                <div className="flex min-h-70 flex-col items-center justify-center text-center">

                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 text-blue-600">
                        <Loader2
                            size={24}
                            className="animate-spin"
                        />
                    </div>

                    <h2 className="mt-4 text-lg font-bold text-slate-900">
                        Loading feedback
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                        Checking your completed services.
                    </p>

                </div>

            </div>
        );
    }


    if (error) {
        return (
            <div className="rounded-2xl border border-red-200 bg-white p-8 shadow-sm">

                <div className="flex min-h-70 flex-col items-center justify-center text-center">

                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-50 text-red-600">
                        <AlertCircle size={25} />
                    </div>

                    <h2 className="mt-4 text-lg font-bold text-slate-900">
                        Unable to load feedback
                    </h2>

                    <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                        {error}
                    </p>

                </div>

            </div>
        );
    }


    return (
        <div className="space-y-6">

            {/* Page Header */}
            <div>

                <p className="text-sm font-medium text-blue-600">
                    Customer Portal
                </p>

                <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
                    Feedback
                </h1>

                <p className="mt-1 text-sm text-slate-500">
                    Share your experience after your service is completed.
                </p>

            </div>


            {/* Information Banner */}
            <div className="rounded-2xl border border-blue-100 bg-blue-50 p-5">

                <div className="flex items-start gap-3">

                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-white text-blue-600">
                        <Star size={20} />
                    </div>

                    <div>

                        <h2 className="font-semibold text-blue-900">
                            Your feedback helps improve the service
                        </h2>

                        <p className="mt-1 text-sm leading-6 text-blue-700">
                            You can submit feedback once a service has been
                            completed. Each completed request can receive
                            feedback only once.
                        </p>

                    </div>

                </div>

            </div>


            {/* No Requests */}
            {requests.length === 0 ? (

                <div className="rounded-2xl border border-slate-200 bg-white p-10 shadow-sm">

                    <div className="flex min-h-70 flex-col items-center justify-center text-center">

                        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                            <MessageSquare size={30} />
                        </div>

                        <h2 className="mt-5 text-xl font-bold text-slate-900">
                            No service requests yet
                        </h2>

                        <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                            Feedback will become available after you
                            complete a service.
                        </p>

                    </div>

                </div>

            ) : (

                <div className="space-y-6">

                    {requests.map((request) => (
                        <FeedbackCard
                            key={request.request_uuid}
                            request={request}
                            feedbackData={
                                feedbacks[
                                    request.request_uuid
                                ]
                            }
                            onFeedbackSubmitted={
                                handleFeedbackSubmitted
                            }
                        />
                    ))}

                </div>

            )}

        </div>
    );
}

export default Feedback;