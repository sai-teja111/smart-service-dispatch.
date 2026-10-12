# ============================================================
# DATABASE SCHEMA
# Single source of truth for the AI database assistant
# ============================================================


DATABASE_SCHEMA = """

DATABASE: Smart Service Dispatch System

TABLE: customers

Columns:
customer_id SERIAL PRIMARY KEY
customer_uuid UUID UNIQUE
customer_name VARCHAR(100)
phone VARCHAR(15)
city VARCHAR(50)
area VARCHAR(100)
pincode VARCHAR(10)


TABLE: technicians

Columns:
technician_id SERIAL PRIMARY KEY
technician_uuid UUID UNIQUE
technician_name VARCHAR(100)
phone VARCHAR(15)
city VARCHAR(50)
area VARCHAR(100)
pincode VARCHAR(10)
availability VARCHAR(20)
workload INTEGER
rating DECIMAL(2,1)


TABLE: skills

Columns:
skill_id SERIAL PRIMARY KEY
skill_uuid UUID UNIQUE
skill_name VARCHAR(100)
category VARCHAR(50)
difficulty_level VARCHAR(20)
estimated_duration INTEGER
description TEXT


TABLE: technician_skills

Columns:
technician_id INTEGER
skill_id INTEGER
experience_years INTEGER
expertise_level VARCHAR(20)
is_verified BOOLEAN

Primary Key:
technician_id, skill_id


TABLE: service_requests

Columns:
request_id SERIAL PRIMARY KEY
request_uuid UUID UNIQUE
customer_id INTEGER
skill_id INTEGER
problem_description TEXT
priority VARCHAR(20)
assigned_technician_id INTEGER
status VARCHAR(30)
request_date TIMESTAMP


TABLE: assignments

Columns:
assignment_id SERIAL PRIMARY KEY
assignment_uuid UUID UNIQUE
request_id INTEGER
technician_id INTEGER
assignment_score DECIMAL(5,2)
assigned_date TIMESTAMP


TABLE: service_history

Columns:
history_id SERIAL PRIMARY KEY
history_uuid UUID UNIQUE
request_id INTEGER
old_status VARCHAR(30)
new_status VARCHAR(30)
updated_time TIMESTAMP
remarks TEXT


TABLE: feedback

Columns:
feedback_id SERIAL PRIMARY KEY
feedback_uuid UUID UNIQUE
request_id INTEGER
customer_id INTEGER
technician_id INTEGER
rating DECIMAL(2,1)
comments TEXT
feedback_date TIMESTAMP


RELATIONSHIPS:

customers.customer_id
=
service_requests.customer_id

skills.skill_id
=
service_requests.skill_id

technicians.technician_id
=
service_requests.assigned_technician_id

technicians.technician_id
=
technician_skills.technician_id

skills.skill_id
=
technician_skills.skill_id

service_requests.request_id
=
assignments.request_id

technicians.technician_id
=
assignments.technician_id

service_requests.request_id
=
service_history.request_id

service_requests.request_id
=
feedback.request_id

customers.customer_id
=
feedback.customer_id

technicians.technician_id
=
feedback.technician_id


# ============================================================
# BUSINESS MEANINGS
# ============================================================

"customer" means a record in customers.
"customers" means records in customers.

"technician" means a record in technicians.
"technicians" means records in technicians.

"service" means a record in skills.
"services" means records in skills.

"service request" means a record in service_requests.
"service requests" means records in service_requests.

"technician skill" means a record in technician_skills.
"technician skills" means records in technician_skills.

"assignment" means a record in assignments.
"assignments" means records in assignments.

"service history" means a record in service_history.

"feedback" means a record in feedback.

"rating" may refer to technicians.rating
or feedback.rating depending on the question.

"available technician" means technicians
where availability indicates availability.

"available technicians" means technicians
where availability = 'Available'.

"verified technicians" means technicians whose
related technician_skills.is_verified = TRUE.

"technician rating" means technicians.rating.

"customer rating" or "feedback rating" means feedback.rating.

"pending requests" means service_requests where
status represents pending.

"completed requests" means service_requests where
status represents completed.

"open requests" means service_requests where
status represents open.

"in-progress requests" means service_requests where
status represents in-progress.

"highest rated technician" means technicians ordered
by rating descending.

"lowest rated technician" means technicians ordered
by rating ascending.

"number of customers" means COUNT(*) from  customers.

"number of technicians" means COUNT(*) from  technicians.

"number of services" means COUNT(*) from  skills.

"number of service requests" means COUNT(*) from  service_requests.
"""