# Campus Placement Portal

A decoupled client-server web application designed to connect Students, Companies, and the Placement Cell Admin (PCell) to streamline placement drives, interview scheduling, and report generation.

---

## 🚀 How to Run the Application

Before running the application, ensure **Redis** is running on your system (`redis-cli ping` should return `PONG`). Run the following three commands in **three separate terminals**:

### 1. Backend (Flask API)
```bash
cd backend
source ../venv/bin/activate
python3 app.py
```
*Runs on `http://127.0.0.1:5000`*

### 2. Task Queue (Celery Worker & Scheduler)
```bash
cd backend
source ../venv/bin/activate
celery -A app.celery worker --beat --loglevel=info
```
*Handles scheduled email reminders, PDF report generation, and CSV exports.*

### 3. Frontend (Vue.js 3 SPA)
```bash
cd frontend
npm run dev
```
*Runs on `http://localhost:5173`*

---

## 🔑 Default Administrator Credentials
*   **Email**: `potato05jk@gmail.com`
*   **Password**: `pcell123`

---

## 🛠️ Key Functionalities

### 1. Student Portal
*   **Profile & Resume**: Build a professional profile, input CGPA, branch, graduation year, key skills, and upload a PDF resume.
*   **Job Discovery**: View and apply to active job drives that match eligibility criteria (CGPA, branch, and graduation year checked automatically).
*   **Offer Tracking**: Accept or reject released job offers. Accepting an offer marks the student as placed and automatically generates a placement letter.
*   **Data Export**: Request a complete history of job applications delivered to their registered email as a CSV.

### 2. Company Portal
*   **Profile Management**: Update HR contact email, industry category, website, location, and description.
*   **Job Postings**: Create job drives specifying vacancies, description, CTC/salary, CGPA cutoffs, and eligible branches.
*   **Applicant Funnel**:
    *   **Shortlist** or reject applicants based on resumes.
    *   **Schedule Interviews** by setting date, time, and location/meeting link.
    *   **Release Offer Letters** specifying joining date and salary package.
*   **Applicant Data Export**: Export candidate application files in a rich CSV format containing name, email, CGPA, branch, skills, and current application status.

### 3. Placement Cell (Admin) Portal
*   **Dashboard Statistics**: Real-time counter of total students, registered companies, job postings, applications, and placement statistics.
*   **Company Verification**: Review pending company registrations and approve or reject their access.
*   **Job Verification**: Review company job drives before they go live for students.
*   **Access Control**: Blacklist/whitelist students or companies to restrict or restore system access.
*   **Task Triggers**: Manually trigger daily interview reminders or monthly HTML placement reports.

### 4. Background & Scheduled Tasks (Celery + Redis)
*   **Daily Deadline Reminders**: Sends reminders to eligible students about job drives closing in less than 24 hours. (Includes Google Chat Webhook notifications support).
*   **Daily Interview Reminders**: Automatically reminds candidates about interviews scheduled for the next day.
*   **Monthly Placement Reports**: Devises an HTML activity report sent via email to the Admin on the first day of every month, summarizing drives conducted, applications, selections, and average salary.
