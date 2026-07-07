<script setup>
    import { ref, onMounted, computed } from 'vue'
    import api from '../services/api'
    import logout from '../services/logout'
    import { useRouter } from 'vue-router'

    const stats = ref(null)
    const error = ref(null)
    const successMsg = ref(null)
    const companies = ref(null)
    const students = ref(null)
    const jobDrives = ref(null)
    const applications = ref(null)
    const placements = ref(null)
    const sendingReminder = ref(false)
    const generatingReport = ref(false)

    const router = useRouter()

    const companySearch = ref('')
    const studentSearch = ref('')
    const jobSearch = ref('')
    const applicationState = ref('')
    const placementSearch = ref('')

    async function loadStats() {
        try {
            stats.value = (await api.get('/admin/stats')).data
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to load stats'
        }
    }

    async function loadCompanies() {
        try {
            companies.value = (await api.get('/admin/companies')).data
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to load companies'
        }
    }

    async function companyApproval(id, status) {
        try {
            successMsg.value = (await api.patch(`/admin/company/${id}`, {approval_status: status})).data.message
            await loadCompanies()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to update company approval status'
        }
    }

    const TOGGLE = {
        TRUE: true,
        FALSE: false
    }

    async function companyBlacklist(id, status) {
        try {
            successMsg.value = (await api.patch(`/admin/company/${id}/blacklist-status`, {is_blacklisted: status})).data.message
            await loadCompanies()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to update company blacklist status'
        }
    }

    async function studentBlacklist(id, status) {
        try {
            successMsg.value = (await api.patch(`/admin/student/${id}`, {is_blacklisted: status})).data.message
            await loadStudents()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to update student blacklist status'
        }
    }

    async function loadStudents() {
        try {
            students.value = (await api.get('/admin/students')).data
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to load students'
        }
    }

    async function loadJobDrives() {
        try {
            jobDrives.value = (await api.get('/admin/jobs')).data
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to load job'
        }
    }

    async function jobApproval(id, status) {
        try {
            successMsg.value = (await api.patch(`/admin/job/${id}`, {status: status})).data.message
            await loadJobDrives()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to update job approval'
        }
    }

    async function loadApplications() {
        try {
            applications.value = (await api.get('/admin/applications')).data
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to load applications'
        }
    }

    async function loadPlacements() {
        try {
            placements.value = (await api.get('/admin/placements')).data
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to load placements'
        }
    }

    async function sendInterviewReminderManually() {
        sendingReminder.value = true
        try {
            successMsg.value = (await api.post('/admin/trigger/interview-reminder')).data.message
            setTimeout(() => {
                successMsg.value = null
                sendingReminder.value = false
            }, 10000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to send interview trigger'
            sendingReminder.value = false
        }
    }

    async function triggerMonthlyReport() {
        generatingReport.value = true
        try {
            successMsg.value = (await api.post('/admin/trigger/monthly-report')).data.message
            setTimeout(() => {
                successMsg.value = null
                generatingReport.value = false
            }, 10000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to trigger monthly report'
            generatingReport.value = false
        }
    }

    const APPROVAL_STATUS = {
        APPROVED: 'approved',
        REJECTED: 'rejected',
        PENDING: 'pending'
    }

    const pendingCompanies = computed(
        () => companies.value?.companyData?.filter(c => c.isApproved === APPROVAL_STATUS.PENDING) || []
    )

    const rejectedCompanies = computed(
        () => companies.value?.companyData?.filter(c => c.isApproved === APPROVAL_STATUS.REJECTED) || []
    )

    const approvedCompanies = computed(
        () => companies.value?.companyData?.filter(c => c.isApproved === APPROVAL_STATUS.APPROVED && !c.isBlacklisted) || []
    )

    const blacklistedCompanies = computed(
        () => companies.value?.companyData?.filter(c => c.isBlacklisted) || []
    )

    const filteredApprovedCompanies = computed(
        () => {
            if (!companySearch.value) return approvedCompanies.value
            return approvedCompanies.value.filter(
                c => c.name.toLowerCase().includes(companySearch.value.toLowerCase()) ||
                c.industry.toLowerCase().includes(companySearch.value.toLowerCase())
            ) || []
        }
    )

    const filteredBlacklistedCompanies = computed(
        () => {
            if (!companySearch.value) return blacklistedCompanies.value
            return blacklistedCompanies.value.filter(
                c => c.name.toLowerCase().includes(companySearch.value.toLowerCase()) ||
                c.industry.toLowerCase().includes(companySearch.value.toLowerCase())
            ) || []
        }
    )

    const activeStudents = computed(
        () => students.value?.studentData?.filter(s => !s.isBlacklisted) || []
    )

    const blacklistedStudents = computed(
        () => students.value?.studentData?.filter(s => s.isBlacklisted) || []
    )

    const filteredStudents = computed(
        () => {
            if (!activeStudents.value) return activeStudents.value
            return activeStudents.value.filter(
                s => s.name.toLowerCase().includes(studentSearch.value.toLowerCase()) ||
                s.branch.toLowerCase().includes(studentSearch.value.toLowerCase())
            ) || []
        }
    )

    const filteredBlacklistedStudents = computed(
        () => {
            if (!blacklistedStudents.value) return blacklistedStudents.value
            return blacklistedStudents.value.filter(
                s => s.name.toLowerCase().includes(studentSearch.value.toLowerCase()) ||
                s.branch.toLowerCase().includes(studentSearch.value.toLowerCase())
            ) || []
        }
    )

    const JOB_STATUS = {
        OPEN: 'open',
        CLOSED: 'closed',
        PENDING: 'pending',
        REJECTED: 'rejected',
    }

    const pendingJobDrives = computed(
        () => jobDrives.value?.jobData?.filter(j => j.status === JOB_STATUS.PENDING) || []
    )

    const openJobDrives = computed(
        () => jobDrives.value?.jobData?.filter(j => j.status === JOB_STATUS.OPEN) || []
    )

    const closedJobDrives = computed(
        () => jobDrives.value?.jobData?.filter(j => j.status === JOB_STATUS.CLOSED) || []
    )

    const rejectedJobDrives = computed(
        () => jobDrives.value?.jobData?.filter(j => j.status === JOB_STATUS.REJECTED) || []
    )

    const filteredJobDrives = computed(
        () => {
            if (!jobSearch.value) return openJobDrives.value
            return openJobDrives.value.filter(
                j => j.title.toLowerCase().includes(jobSearch.value.toLowerCase()) ||
                j.company.toLowerCase().includes(jobSearch.value.toLowerCase())
            ) || []
        }
    )

    const APPLICATION_STATUS = {
        APPLIED: 'applied',
        SHORTLISTED: 'shortlisted',
        INTERVIEW_SCHEDULED: 'interview_scheduled',
        REJECTED: 'rejected',
        OFFER_RELEASED: 'offer_released',
        OFFER_ACCEPTED: 'offer_accepted',
        OFFER_REJECTED: 'offer_rejected'
    }

    const filteredApplications = computed(
        () => {
            if (!applications.value) return []
            if (!applicationState.value) return applications.value.applicationData
            return applications.value.applicationData.filter(
                a => a.status === applicationState.value) || []
        }
    )

    const filteredPlacements = computed(() => {
        if (!placements.value?.placementData) return []
        if (!placementSearch.value) return placements.value.placementData
        const search = placementSearch.value.toLowerCase()
        return placements.value.placementData.filter(p =>
            p.student_name.toLowerCase().includes(search) ||
            p.job_title.toLowerCase().includes(search) ||
            p.company_name.toLowerCase().includes(search)
        )
    })

    function formatDate(dateStr) {
        return new Date(dateStr).toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'})
    }

    onMounted(async () => {
        await loadStats()
        loadCompanies()
        loadJobDrives()
        loadStudents()
        loadApplications()
        loadPlacements()
    })
</script>

<template>
    <div class="container py-4">
        <div class="text-center">
            <h1>Admin Dashboard</h1>
        </div>

        <div v-if="error" class="alert alert-danger">
            {{ error }}
            <button class="btn btn-danger" @click="logout">Try login again</button>
        </div>

        <div v-if="successMsg" class="alert alert-success">
            {{ successMsg }}
        </div>

        <div v-if="stats">
            <p class="text-muted text-center">{{ stats.message }}</p>
             <div class="text-end">
                <button class="btn btn-danger" @click="logout">Logout</button>
            </div>
            <h3>Overview Statistics</h3>
            <div class="row text-center mt-3">
                <div class="col">
                    <h5>Students</h5>
                    <p>{{ stats.studentData.total }}</p>
                    <small>Active: {{ stats.studentData.active }} | Blacklisted: {{ stats.studentData.blacklisted }}</small>
                </div>
                <div class="col">
                    <h5>Companies</h5>
                    <p>{{ stats.companyData.total }}</p>
                    <small>Active: {{ stats.companyData.active }} | Blacklisted: {{ stats.companyData.blacklisted }}</small>
                </div>
                <div class="col">
                    <h5>Jobs</h5>
                    <p>{{ stats.jobData.total }}</p>
                    <small>Open: {{ stats.jobData.open }} | Rejected: {{ stats.jobData.rejected }}</small>
                </div>
            </div>
            <div class="row text-center mt-3">
                <div class="col">
                    <h5>Applications</h5>
                    <p>{{ stats.applicationData.total }}</p>
                    <small>Applied: {{ stats.applicationData.applied }} | In Process: {{ stats.applicationData.in_process }}</small>
                </div>
                <div class="col">
                    <h5>Placements</h5>
                    <p>{{ stats.placementData.total }}</p>
                    <small>Highest Salary: ₹{{ stats.placementData.highest_salary }} | Average: ₹{{ stats.placementData.avg_salary }}</small>
                </div>
            </div>
        </div>

        <div class="mt-3">
            <button @click="sendInterviewReminderManually" :disabled="sendingReminder" class="btn btn-primary">Send interview triggers</button>
            <button @click="triggerMonthlyReport" :disabled="generatingReport" class="btn btn-secondary">Generate Monthly Report</button>
        </div>

<!--Company-->

        <div v-if="companies">
            <h3 class="mt-5">Companies Management</h3>
            
            <h4 class="mt-3">Pending Approvals: {{ pendingCompanies.length }}</h4>
            <div v-if="pendingCompanies.length > 0">    
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Industry</th>
                            <th>Details</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="company in pendingCompanies">
                            <td>{{ company.id }}</td>
                            <td>{{ company.name }}</td>
                            <td>{{ company.industry }}</td>
                            <td>
                                <button @click="router.push({name: 'company-details', params: { id: company.id }})" class="btn btn-primary">View</button>
                            </td>
                            <td>
                                <button @click="companyApproval(company.id, APPROVAL_STATUS.APPROVED)" class="btn btn-success">Approve</button>
                                <button @click="companyApproval(company.id, APPROVAL_STATUS.REJECTED)" class="btn btn-danger">Reject</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <h4 class="mt-3">Rejected Companies: {{ rejectedCompanies.length }}</h4>
            <div v-if="rejectedCompanies.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Industry</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="company in rejectedCompanies">
                            <td>{{ company.id }}</td>
                            <td>{{ company.name }}</td>
                            <td>{{ company.industry }}</td>
                            <td>
                                <button @click="router.push({name: 'company-details', params: { id: company.id }})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div>
                <input type="text" v-model="companySearch" class="form-control" placeholder="Search companies by name or industry..">
            </div>
            
            <h4 class="mt-3">Approved Companies: {{ filteredApprovedCompanies.length }}</h4>
            <div v-if="filteredApprovedCompanies.length > 0">   
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Industry</th>
                            <th>Details</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="company in filteredApprovedCompanies">
                            <td>{{ company.id }}</td>
                            <td>{{ company.name }}</td>
                            <td>{{ company.industry }}</td>
                            <td>
                                <button @click="router.push({name: 'company-details', params: { id: company.id }})" class="btn btn-primary">View</button>
                            </td>
                            <td>
                                <button @click="companyBlacklist(company.id, TOGGLE.TRUE)" class="btn btn-dark">Blacklist</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <h4 class="mt-3">Blacklisted Companies: {{ filteredBlacklistedCompanies.length }}</h4>
            <div v-if="filteredBlacklistedCompanies.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Industry</th>
                            <th>Details</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="company in filteredBlacklistedCompanies">
                            <td>{{ company.id }}</td>
                            <td>{{ company.name }}</td>
                            <td>{{ company.industry }}</td>
                            <td>
                                <button @click="router.push({name: 'company-details', params: { id: company.id }})" class="btn btn-primary">View</button>
                            </td>
                            <td>
                                <button @click="companyBlacklist(company.id, TOGGLE.FALSE)" class="btn btn-light">Whitelist</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

<!--Student-->

        <div v-if="students">
            <h3 class="mt-5">Students Management</h3>

            <div>
                <input type="text" v-model="studentSearch" class="form-control" placeholder="Search students by name or branch..">
            </div>
            
            <h4 class="mt-3">Active Students: {{ filteredStudents.length }}</h4>
            <div v-if="filteredStudents.length > 0">    
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>CGPA</th>
                            <th>Branch</th>
                            <th>Details</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="student in filteredStudents">
                            <td>{{ student.id }}</td>
                            <td>{{ student.name }}</td>
                            <td>{{ student.cgpa }}</td>
                            <td>{{ student.branch }}</td>
                            <td>
                                <button @click="router.push({name: 'student-details', params: { id: student.id }})" class="btn btn-primary">View</button>
                            </td>
                            <td>
                                <button @click="studentBlacklist(student.id, TOGGLE.TRUE)" class="btn btn-dark">Blacklist</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <h4 class="mt-3">Blacklisted Students: {{ filteredBlacklistedStudents.length }}</h4>
            <div v-if="filteredBlacklistedStudents.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>CGPA</th>
                            <th>Branch</th>
                            <th>Details</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="student in filteredBlacklistedStudents">
                            <td>{{ student.id }}</td>
                            <td>{{ student.name }}</td>
                            <td>{{ student.cgpa }}</td>
                            <td>{{ student.branch }}</td>
                            <td>
                                <button @click="router.push({name: 'student-details', params: { id: student.id }})" class="btn btn-primary">View</button>
                            </td>
                            <td>
                                <button @click="studentBlacklist(student.id, TOGGLE.FALSE)" class="btn btn-light">Whitelist</button>
                            </td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>

<!-- Job Drives -->

        <div v-if="jobDrives">
            <h3 class="mt-5">Job Drives Management</h3>

            <h4 class="mt-3">Pending Job Approvals: {{ pendingJobDrives.length }}</h4>
            <div v-if="pendingJobDrives.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Company</th>
                            <th>Vacancies</th>
                            <th>Deadline</th>
                            <th>Details</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="job in pendingJobDrives">
                            <td>{{ job.id }}</td>
                            <td>{{ job.title }}</td>
                            <td>{{ job.company }}</td>
                            <td>{{ job.vacancies }}</td>
                            <td>{{ formatDate(job.deadline) }}</td>
                            <td>
                                <button @click="router.push({name: 'job-details', params: { id: job.id }})" class="btn btn-primary">View</button>
                            </td>
                            <td>
                                <button @click="jobApproval(job.id, JOB_STATUS.OPEN)" class="btn btn-success">Approve</button>
                                <button @click="jobApproval(job.id, JOB_STATUS.REJECTED)" class="btn btn-danger">Reject</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <h4 class="mt-3">Rejected Job Approvals: {{ rejectedJobDrives.length }}</h4>
            <div v-if="rejectedJobDrives.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Company</th>
                            <th>Vacancies</th>
                            <th>Deadline</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="job in rejectedJobDrives">
                            <td>{{ job.id }}</td>
                            <td>{{ job.title }}</td>
                            <td>{{ job.company }}</td>
                            <td>{{ job.vacancies }}</td>
                            <td>{{ formatDate(job.deadline) }}</td>
                            <td>
                                <button @click="router.push({name: 'job-details', params: { id: job.id }})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div>
                <input type="text" v-model="jobSearch" class="form-control mb-3" placeholder="Search jobs by title or company.."/>
            </div>

            <h4 class="mt-3">Open Jobs: {{ filteredJobDrives.length }}</h4>
            <div v-if="filteredJobDrives.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Company</th>
                            <th>Vacancies</th>
                            <th>Deadline</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="job in filteredJobDrives">
                            <td>{{ job.id }}</td>
                            <td>{{ job.title }}</td>
                            <td>{{ job.company }}</td>
                            <td>{{ job.vacancies }}</td>
                            <td>{{ formatDate(job.deadline) }}</td>
                            <td>
                                <button @click="router.push({name: 'job-details', params: { id: job.id }})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <h4 class="mt-3">Closed JobDrives: {{ closedJobDrives.length }}</h4>
            <div v-if="closedJobDrives.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Company</th>
                            <th>Vacancies</th>
                            <th>Deadline</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="job in closedJobDrives">
                            <td>{{ job.id }}</td>
                            <td>{{ job.title }}</td>
                            <td>{{ job.company }}</td>
                            <td>{{ job.vacancies }}</td>
                            <td>{{ formatDate(job.deadline) }}</td>
                            <td>
                                <button @click="router.push({name: 'job-details', params: { id: job.id }})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

<!--Application-->

        <div v-if="applications">
            <h3 class="mt-5">Applications Management</h3>

            <select v-model="applicationState" class="form-select mb-3">
                <option value="">All Applications</option>
                <option v-for="(value, key) in APPLICATION_STATUS" :key="key" :value="value">
                    {{ key }}
                </option>
            </select>

            <h4 class="mt-3">Applications: {{ filteredApplications.length }}</h4>
            <div v-if="filteredApplications.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Student</th>
                            <th>Job @ Company</th>
                            <th>Status</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="app in filteredApplications">
                            <td>{{ app.id }}</td>
                            <td>{{ app.student_name }}</td>
                            <td>{{ app.job_title }} @ {{ app.company_name }}</td>
                            <td>{{ app.status }}</td>
                            <td>
                                <button @click="router.push({name: 'application-details', params: { id: app.id }})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

<!--Placements-->

        <div v-if="placements">
            <h3 class="mt-5">Placements Management</h3>

            <div>
                <input type="text" v-model="placementSearch" class="form-control" placeholder="Search placements by student, job or company..">
            </div>

            <h4 class="mt-3">Placements: {{ filteredPlacements.length }}</h4>
            <div v-if="filteredPlacements.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Student</th>
                            <th>Job Title</th>
                            <th>Company</th>
                            <th>Salary</th>
                            <th>Placed On</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="p in filteredPlacements">
                            <td>{{ p.id }}</td>
                            <td>
                                <button @click="router.push({name: 'student-details', params: { id: p.student_id }})" class="btn btn-link">{{ p.student_name }}</button>
                            </td>
                            <td>{{ p.job_title }}</td>
                            <td>{{ p.company_name }}</td>
                            <td>Rs. {{ p.salary?.toLocaleString() }}</td>
                            <td>{{ formatDate(p.placed_at) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

    </div>
</template>