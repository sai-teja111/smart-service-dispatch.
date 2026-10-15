
from decimal import Decimal

from sqlmodel import select

from Orm.database import get_session_context

from Orm.customer import Customer
from Orm.technician import Technician
from Orm.skills import Skill
from Orm.technician_skill import TechnicianSkill
from Orm.service_request import ServiceRequest
from Orm.assignment import Assignment


MAX_WORKLOAD = 5


NEARBY_AREAS = {

    "manikonda": [
        "gachibowli",
        "narsingi",
        "khajaguda"
    ],

    "gachibowli": [
        "manikonda",
        "kondapur",
        "madhapur",
        "narsingi"
    ],

    "madhapur": [
        "gachibowli",
        "kondapur",
        "hitech city",
        "jubilee hills"
    ],

    "kondapur": [
        "gachibowli",
        "madhapur",
        "hitech city"
    ],

    "hitech city": [
        "madhapur",
        "kondapur",
        "gachibowli"
    ],

    "narsingi": [
        "manikonda",
        "gachibowli"
    ],

    "lb nagar": [
        "dilsukhnagar",
        "kothapet",
        "uppal"
    ],

    "dilsukhnagar": [
        "lb nagar",
        "kothapet"
    ],

    "kothapet": [
        "lb nagar",
        "dilsukhnagar",
        "uppal"
    ],

    "uppal": [
        "kothapet",
        "dilsukhnagar"
    ]
}


def generate_matching_explanation(
    customer_area,
    customer_pincode,
    technician_area,
    technician_pincode,
    location_type,
    experience,
    expertise,
    rating,
    workload,
    skill_score,
    verified_score,
    area_score,
    pincode_score,
    experience_score,
    expertise_score,
    rating_score,
    workload_score
):

    reasons = []

    if skill_score == 20:
        reasons.append(
            "Required service skill matches exactly"
        )

    if verified_score == 15:
        reasons.append(
            "Required skill is verified"
        )

    reasons.append(
        "Technician is currently available"
    )

    if location_type == "Same Area":
        reasons.append(
            "Technician is from the same area"
        )

    elif location_type == "Nearby Area":
        reasons.append(
            "Technician is from a nearby area"
        )

    else:
        reasons.append(
            "Technician is from another area"
        )

    if pincode_score > 0:
        reasons.append(
            "Technician pincode matches customer pincode"
        )

    else:
        reasons.append(
            "Technician pincode does not match"
        )

    if experience >= 5:
        reasons.append(
            f"{experience} years of relevant experience"
        )

    elif experience >= 3:
        reasons.append(
            f"{experience} years of relevant experience"
        )

    elif experience >= 1:
        reasons.append(
            f"{experience} year(s) of relevant experience"
        )

    if expertise:
        reasons.append(
            f"{expertise.title()} expertise level"
        )

    if rating >= 4.5:
        reasons.append(
            "Excellent customer rating"
        )

    elif rating >= 4:
        reasons.append(
            "Good customer rating"
        )

    elif rating > 0:
        reasons.append(
            "Existing customer rating available"
        )

    if workload == 0:
        reasons.append(
            "No active workload"
        )

    elif workload <= 2:
        reasons.append(
            "Low current workload"
        )

    elif workload <= 4:
        reasons.append(
            "Moderate current workload"
        )

    return reasons


def find_best_technician(request_id):

    try:

        with get_session_context() as session:

            service_request = session.get(
                ServiceRequest,
                request_id
            )

            if not service_request:

                print(
                    "\nService Request Not Found."
                )

                return None

            # Prevent duplicate assignments for the same request.
            existing_assignment_statement = (
                select(Assignment)
                .where(
                    Assignment.request_id == request_id
                )
            )

            existing_assignment = session.exec(
                existing_assignment_statement
            ).first()

            if existing_assignment:

                print(
                    "\nThis service request already has "
                    "an assignment."
                )

                print(
                    f"Request ID    : {request_id}"
                )

                print(
                    f"Technician ID : "
                    f"{existing_assignment.technician_id}"
                )

                return existing_assignment.technician_id

            skill_id = service_request.skill_id
            priority = service_request.priority

            customer = session.get(
                Customer,
                service_request.customer_id
            )

            if not customer:

                print(
                    "\nCustomer Not Found."
                )

                return None

            customer_area = str(
                customer.area
            ).strip().lower()

            customer_pincode = str(
                customer.pincode
            ).strip()

            skill = session.get(
                Skill,
                skill_id
            )

            if skill:
                skill_name = skill.skill_name
            else:
                skill_name = "Unknown Service"

            # Only verified technician-skill associations
            # for the requested skill are eligible.
            technician_skill_statement = (
                select(TechnicianSkill)
                .where(
                    TechnicianSkill.skill_id == skill_id,
                    TechnicianSkill.is_verified == True
                )
            )

            technician_skills = (
                session.exec(
                    technician_skill_statement
                ).all()
            )

            if not technician_skills:

                print(
                    "\nNo available verified technician found"
                )

                print(
                    "for the requested service."
                )

                return None

            technician_ids = [
                ts.technician_id
                for ts in technician_skills
            ]

            # Only approved, available technicians with
            # a verified matching skill are considered.
            technician_statement = (
                select(Technician)
                .where(
                    Technician.technician_id.in_(
                        technician_ids
                    ),
                    Technician.approval_status == "Approved",
                    Technician.availability == "Available"
                )
            )

            technicians = (
                session.exec(
                    technician_statement
                ).all()
            )

            technicians = [
                technician
                for technician in technicians
                if (technician.workload or 0)
                < MAX_WORKLOAD
            ]

            if not technicians:

                print(
                    "\nNo available approved technician "
                    "with the required verified skill "
                    "was found."
                )

                return None

            nearby_areas = NEARBY_AREAS.get(
                customer_area,
                []
            )

            best_technician = None
            best_score = -1
            best_details = None
            best_technician_skill = None

            for technician in technicians:

                technician_id = (
                    technician.technician_id
                )

                technician_name = (
                    technician.technician_name
                )

                technician_area = str(
                    technician.area
                ).strip().lower()

                technician_pincode = str(
                    technician.pincode
                ).strip()

                workload = (
                    technician.workload or 0
                )

                rating = float(
                    technician.rating or 0
                )

                technician_skill = next(
                    (
                        ts
                        for ts in technician_skills
                        if ts.technician_id == technician_id
                    ),
                    None
                )

                if not technician_skill:
                    continue

                # Defensive verification before scoring.
                if not technician_skill.is_verified:
                    continue

                if technician_skill.skill_id != skill_id:
                    continue

                experience = (
                    technician_skill.experience_years
                    or 0
                )

                expertise = str(
                    technician_skill.expertise_level
                    or ""
                ).strip().lower()

                score = 0

                if technician_area == customer_area:

                    area_score = 20
                    location_type = "Same Area"

                elif technician_area in nearby_areas:

                    area_score = 10
                    location_type = "Nearby Area"

                else:

                    area_score = 0
                    location_type = "Other Area"

                score += area_score

                if technician_pincode == customer_pincode:
                    pincode_score = 10
                else:
                    pincode_score = 0

                score += pincode_score

                if experience >= 5:
                    experience_score = 15
                elif experience >= 3:
                    experience_score = 12
                elif experience >= 1:
                    experience_score = 8
                else:
                    experience_score = 0

                score += experience_score

                if expertise == "expert":
                    expertise_score = 10
                elif expertise == "advanced":
                    expertise_score = 8
                elif expertise == "intermediate":
                    expertise_score = 6
                elif expertise == "beginner":
                    expertise_score = 4
                else:
                    expertise_score = 0

                score += expertise_score

                if rating >= 4.5:
                    rating_score = 5
                elif rating >= 4.0:
                    rating_score = 4
                elif rating >= 3.5:
                    rating_score = 3
                elif rating > 0:
                    rating_score = 2
                else:
                    rating_score = 0

                score += rating_score

                if workload == 0:
                    workload_score = 5
                elif workload == 1:
                    workload_score = 4
                elif workload == 2:
                    workload_score = 3
                elif workload == 3:
                    workload_score = 2
                elif workload == 4:
                    workload_score = 1
                else:
                    workload_score = 0

                score += workload_score

                if technician_skill.is_verified:
                    verified_score = 15
                else:
                    verified_score = 0

                score += verified_score

                skill_score = 20

                score += skill_score

                print(
                    "\n------------------------------------------"
                )

                print(
                    f"Technician      : "
                    f"{technician_name}"
                )

                print(
                    f"Area            : "
                    f"{technician_area}"
                )

                print(
                    f"Location Match  : "
                    f"{location_type}"
                )

                print(
                    f"Skill Match     : "
                    f"{skill_score}/20"
                )

                print(
                    f"Verified Skill  : "
                    f"{verified_score}/15"
                )

                print(
                    f"Area Score      : "
                    f"{area_score}/20"
                )

                print(
                    f"Pincode Score   : "
                    f"{pincode_score}/10"
                )

                print(
                    f"Experience      : "
                    f"{experience_score}/15"
                )

                print(
                    f"Expertise       : "
                    f"{expertise_score}/10"
                )

                print(
                    f"Rating          : "
                    f"{rating_score}/5"
                )

                print(
                    f"Workload        : "
                    f"{workload_score}/5"
                )

                print(
                    f"Total Score     : "
                    f"{score}/100"
                )

                print(
                    "------------------------------------------"
                )

                if score > best_score:

                    best_score = score

                    best_technician = technician

                    best_technician_skill = (
                        technician_skill
                    )

                    best_details = {
                        "location_type": location_type,
                        "skill_score": skill_score,
                        "verified_score": verified_score,
                        "area_score": area_score,
                        "pincode_score": pincode_score,
                        "experience_score": experience_score,
                        "expertise_score": expertise_score,
                        "rating_score": rating_score,
                        "workload_score": workload_score
                    }

            if best_technician is None:

                print(
                    "\nNo suitable technician available."
                )

                return None

            technician_id = (
                best_technician.technician_id
            )

            technician = session.get(
                Technician,
                technician_id
            )

            if not technician:

                print(
                    "\nSelected technician no longer exists."
                )

                return None

            # Recheck eligibility immediately before assignment.
            if technician.approval_status != "Approved":

                print(
                    "\nSelected technician is not approved."
                )

                return None

            if technician.availability != "Available":

                print(
                    "\nSelected technician is "
                    "no longer available."
                )

                print(
                    f"Current Status : "
                    f"{technician.availability}"
                )

                return None

            current_workload = (
                technician.workload or 0
            )

            if current_workload >= MAX_WORKLOAD:

                print(
                    "\nSelected technician has reached "
                    "maximum workload."
                )

                return None

            # Recheck the verified skill association.
            verified_skill_statement = (
                select(TechnicianSkill)
                .where(
                    TechnicianSkill.technician_id
                    == technician_id,
                    TechnicianSkill.skill_id == skill_id,
                    TechnicianSkill.is_verified == True
                )
            )

            current_verified_skill = session.exec(
                verified_skill_statement
            ).first()

            if not current_verified_skill:

                print(
                    "\nSelected technician no longer has "
                    "the required verified skill."
                )

                return None

            # Check once more before creating the assignment.
            existing_assignment = session.exec(
                select(Assignment).where(
                    Assignment.request_id == request_id
                )
            ).first()

            if existing_assignment:

                print(
                    "\nThis service request was already "
                    "assigned."
                )

                return existing_assignment.technician_id

            new_workload = (
                current_workload + 1
            )

            service_request.assigned_technician_id = (
                technician_id
            )

            service_request.status = "PENDING"

            assignment = Assignment(
                request_id=request_id,
                technician_id=technician_id,
                assignment_score=Decimal(
                    str(best_score)
                )
            )

            session.add(
                assignment
            )

            technician.workload = (
                new_workload
            )

            if new_workload >= MAX_WORKLOAD:

                technician.availability = "Busy"

            session.commit()

            technician_name = (
                technician.technician_name
            )

            technician_area = str(
                technician.area
            ).strip().lower()

            technician_pincode = str(
                technician.pincode
            ).strip()

            experience = (
                best_technician_skill.experience_years
                or 0
            )

            expertise = str(
                best_technician_skill.expertise_level
                or ""
            )

            rating = float(
                technician.rating or 0
            )

            reasons = generate_matching_explanation(
                customer_area,
                customer_pincode,
                technician_area,
                technician_pincode,
                best_details["location_type"],
                experience,
                expertise,
                rating,
                current_workload,
                best_details["skill_score"],
                best_details["verified_score"],
                best_details["area_score"],
                best_details["pincode_score"],
                best_details["experience_score"],
                best_details["expertise_score"],
                best_details["rating_score"],
                best_details["workload_score"]
            )

            print("\n")

            print("=" * 60)

            print(
                "                 MATCHING ANALYSIS"
            )

            print("=" * 60)

            print(
                f"\nCustomer Area       : "
                f"{customer_area.title()}"
            )

            print(
                f"Customer Pincode    : "
                f"{customer_pincode}"
            )

            print(
                f"Requested Service   : "
                f"{skill_name}"
            )

            print(
                f"Priority            : "
                f"{priority}"
            )

            print(
                f"\nSelected Technician : "
                f"{technician_name}"
            )

            print(
                f"Technician Area     : "
                f"{technician_area}"
            )

            print(
                f"Technician Pincode  : "
                f"{technician_pincode}"
            )

            print(
                "\nWhy this technician was selected:"
            )

            for reason in reasons:

                print(
                    f"✓ {reason}"
                )

            print(
                "\nScore Breakdown"
            )

            print(
                "-" * 60
            )

            print(
                f"Skill Match         : "
                f"{best_details['skill_score']}/20"
            )

            print(
                f"Verified Skill      : "
                f"{best_details['verified_score']}/15"
            )

            print(
                f"Area Match          : "
                f"{best_details['area_score']}/20"
            )

            print(
                f"Pincode Match       : "
                f"{best_details['pincode_score']}/10"
            )

            print(
                f"Experience          : "
                f"{best_details['experience_score']}/15"
            )

            print(
                f"Expertise           : "
                f"{best_details['expertise_score']}/10"
            )

            print(
                f"Rating              : "
                f"{best_details['rating_score']}/5"
            )

            print(
                f"Workload            : "
                f"{best_details['workload_score']}/5"
            )

            print(
                "-" * 60
            )

            print(
                f"FINAL SCORE         : "
                f"{best_score}/100"
            )

            print(
                "\nDecision:"
            )

            if best_details["location_type"] == "Same Area":

                print(
                    f"{technician_name} was selected because "
                    "the technician is in the same area and "
                    "has the required verified skill."
                )

            elif best_details["location_type"] == "Nearby Area":

                print(
                    f"{technician_name} was selected because "
                    "the technician is available in a nearby "
                    "area with the required verified skill."
                )

            else:

                print(
                    f"{technician_name} was selected as the "
                    "highest-scoring available technician "
                    "for this service request."
                )

            print(
                "\nAssignment Summary:"
            )

            print(
                f"Request ID       : "
                f"{request_id}"
            )

            print(
                f"Request UUID     : "
                f"{service_request.request_uuid}"
            )

            print(
                f"Technician ID    : "
                f"{technician_id}"
            )

            print(
                f"Technician UUID  : "
                f"{technician.technician_uuid}"
            )

            print(
                f"Previous Workload: "
                f"{current_workload}"
            )

            print(
                f"New Workload     : "
                f"{new_workload}"
            )

            if new_workload >= MAX_WORKLOAD:

                print(
                    "Availability     : Busy"
                )

            else:

                print(
                    "Availability     : Available"
                )

            print(
                "=" * 60
            )

            return technician_id

    except Exception as err:

        print(
            "\nMatching Error :",
            err
        )

        return None
