# MILESTONE PROGRESS

### 7th Jan 26: Milestone 0: GitHub Repository Setup (Mandatory)

## Core Requirements (8 Milestones)
### 8th Jan 26: Milestone: Database Models and Schema Setup (Flask)

Created models for:
- User
- Company
- Student
- Job Position
- Application
- Placement

Relationships between tables:
- User-Student: 1-1
- User-Company: 1-1
- Company-JobPosition: 1-N
- JobPosition-Application: 1-N
- Student-Application: 1-N (but with constraint, a stident can have single application for a job)
- Student-Placement: 1-1
- Company-Placement: 1-N
- Logical: JobPosition-Placement: 1-N / 1-1 though it depends on vacancies, default 1 vancancy(not defined as constraint in db)

---

### 10th Jan 26: Milestone: Authentication and Role-Based Access (Admin/Company/ Student) (Flask+Vue) Completed

- Implemented authentication using JWT-based tokens.
- Students can self-register + login.
- Companies can register + login only (after being approved by Admin).
- Admin: predefined login only (no registration).
- Redirect users to role-specific dashboards after login (Admin, Company, Student) and added frontend role based redirection if mismatched then redirected to login page.

---

### 25th Jan 26: Milestone: Admin Dashboard and Management (Flask+Vue) Completed

- Implemented dashboard showing total students, companies, job postings, and applications.
- Admin would be able to approve and remove company profiles.
- Admin would be able to approve and remove job posting created by Companies.
- Search companies (by name / industry) & search students (by name / ID / contact) functionalities.
- View and manage all job postings
- View applications.
- Blacklist/Deactivate companies and students from the system.

---

### 6th Feb 26: Milestone: Company Dashboard and Job/Application Management (Flask+Vue) Completed

- Companies will register their profile.
- Companies can only access the dashboard when approved by admin.
- Dashboard showing job postings, received applications, and shortlisted candidates.
- Post new job positions with required skills, experience, etc.
- View list of applicants for each job.
- Shortlist or reject applicants with feedback.
- Manage job posting status (Active / Closed).
- Schedule interviews with shortlisted candidates.
- Share acceptance or rejection status(Shortlisted / Selected / Rejected) to applicants.

---

### 18th Feb 26: Milestone: Student Dashboard and Job Application System (Flask+Vue) Completed

- Register, log in, and update profile (education, skills, resume, experience).
- View and search job postings by company, position, or required skills.
- Apply for jobs and track application status.
- View applied jobs with detailed application status.
- View interview schedules and feedback from companies.
- Download offer letters or placement confirmations.

---

### 24th Feb 26: Milestone: Job Application History and Status Tracking (Flask+Vue) Completed

- Store and display complete application and placement history.
- Prevent duplicate applications for the same job posting.
- Ensure only approved companies can create placement drives.
- Ensure students can view and apply only to approved placement drives.
- Maintain status updates (Applied / Shortlisted / Interview / Offer / Rejected / Placed).
- Admin and Company can view student profiles and applications; Students can view their own records.

---

### 6th March 26: Milestone: Backend Jobs – Interview Reminders, Placement Reports, and Triggered Jobs (CSV Export using Celery + Redis) (Flask) Completed

- Setup Celery workers, Celery Beat, and Redis server.
- Interview Reminder Job: send reminders (Email) to students with scheduled interviews.
- Placement Report Job: generate monthly reports for companies (PDF) with application statistics, placements, and analytics.
- User-triggered CSV Export: students and companies can export application and placement history asynchronously; alert sent once the batch job is complete.

---

### 8th March 26: Milestone: API Performance Optimization and Caching Using Redis (Flask)

- Use Redis caching for API optimization.
- Cache frequently used endpoints (job listings, company search, student search).
- Implemented proper cache expiry and refresh policies.