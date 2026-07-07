# Hey there, this is my MAD2 Project repo for Jan 26 term.

## Project Title: `Placement Portal Application - V2`

### Project Statement :
`Institutes require efficient systems to manage campus recruitment activities involving companies and students. Currently, many institutes rely on spreadsheets, emails, or manual coordination, which makes it difficult to manage company approvals, placement drives, student registrations, and application tracking.
`

`You are required to build a Placement Portal Application (PPA) web application that allows Admin (Institute), Companies, and Students to interact with the system based on their roles.`

## 8th Jan 26: Milestone: Database Models and Schema Setup (Flask) Completed
- Defined relationships.
- Ensured that Admin user is pre-created programmatically through


## 10th Jan 26: Milestone: Authentication and Role-Based Access (Admin/Company/ Student) (Flask+Vue) Completed
- Implemented authentication using JWT
- Redirect to role specific dashboards

## 25th Jan 26 :Milestone: Admin Dashboard and Management (Flask+Vue)
- Created admin dashboard with the ability to manage companies, students and applications.
- Search functionalities for companies and students, filter functionality for application status.

## 6th Feb: Milestone: Company Dashboard and Job/Application Management (Flask+Vue)
- Created company dashboard with the ability to manage jobs, applications and release placement offers.
- Manage different stages of applications.

## 18th Feb: Milestone: Student Dashboard and Job Application System (Flask+Vue)
- Created student dashboard where she/he can apply for jobs, accept reject placement offers.
- Ability to download offer letters and placement confirmation letter.

## 24th Feb: Milestone: Job Application History and Status Tracking (Flask+Vue)
- Added resume upload functionality and few minor changes.
- Most of the requirements were already completed in previous milestones.

## 6th March: Milestone: Backend Jobs – Interview Reminders, Placement Reports, and Triggered Jobs (CSV Export using Celery + Redis) (Flask)
- Setup and tested celery workers, beat and redis server.
- Manually trigger interview reminder by admin, auto schedule reminder twice a day.
- Monthly placement report auto generated aswell as companies can download previous month's report + csv of appicatants data manually triggered.

## 8th March: Milestone: API Performance Optimization and Caching Using Redis (Flask)
- Used Redis caching for endpoints
- Implement proper cache expiry(faster expiry for say job listing, slower for placement and so on) and refresh policies whenever relevant db change/write occurs.

## 9th March: Milestone: Final Project Submission
- Made few final changes regarding few errors.

## 10th March: Milestone: Final Project Submission
- Partial gatekeeping was pending regarding blacklist errors(if already logged in(jwt), then students/companies could apply) which shall not happen.