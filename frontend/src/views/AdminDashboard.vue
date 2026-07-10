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
        <!-- Header -->
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary">
            <div>
                <h1 class="gradient-text fw-bold mb-0">Admin Dashboard</h1>
                <p class="text-muted mb-0" v-if="stats">{{ stats.message || 'Campus Placement Administration' }}</p>
            </div>
            <div class="mt-3 mt-md-0 d-flex gap-2">
                <button class="btn btn-danger" @click="logout">Logout</button>
            </div>
        </div>

        <!-- Alert messages -->
        <div v-if="error" class="alert alert-danger d-flex justify-content-between align-items-center mb-4">
            <span>{{ error }}</span>
            <button class="btn btn-danger btn-sm" @click="logout">Try login again</button>
        </div>

        <div v-if="successMsg" class="alert alert-success mb-4">
            {{ successMsg }}
        </div>

        <!-- Trigger buttons -->
        <div class="glass-card mb-4">
            <h3 class="border-bottom border-secondary pb-2 mb-3">System Controls</h3>
            <div class="d-flex flex-wrap gap-2">
                <button @click="sendInterviewReminderManually" :disabled="sendingReminder" class="btn btn-primary">
                    <span v-if="sendingReminder">Sending reminders...</span>
                    <span v-else>Trigger Interview Reminders</span>
                </button>
                <button @click="triggerMonthlyReport" :disabled="generatingReport" class="btn btn-secondary">
                    <span v-if="generatingReport">Generating report...</span>
                    <span v-else>Trigger Monthly Report</span>
                </button>
            </div>
        </div>

        <!-- Stats Section -->
        <div v-if="stats" class="glass-card mb-4">
            <h3 class="border-bottom border-secondary pb-2 mb-3">Overview Statistics</h3>
            <div class="row g-3 text-center">
                <!-- Students Stats -->
                <div class="col-md-4">
                    <div class="glass-panel h-100 p-3">
                        <h5 class="text-white mb-2">Students</h5>
                        <h2 class="text-primary fw-bold mb-1">{{ stats.studentData.total }}</h2>
                        <span class="text-muted small">Active: {{ stats.studentData.active }} | Black: {{ stats.studentData.blacklisted }}</span>
                    </div>
                </div>
                <!-- Companies Stats -->
                <div class="col-md-4">
                    <div class="glass-panel h-100 p-3">
                        <h5 class="text-white mb-2">Companies</h5>
                        <h2 class="text-info fw-bold mb-1">{{ stats.companyData.total }}</h2>
                        <span class="text-muted small">Active: {{ stats.companyData.active }} | Black: {{ stats.companyData.blacklisted }}</span>
                    </div>
                </div>
                <!-- Jobs Stats -->
                <div class="col-md-4">
                    <div class="glass-panel h-100 p-3">
                        <h5 class="text-white mb-2">Job Openings</h5>
                        <h2 class="text-warning fw-bold mb-1">{{ stats.jobData.total }}</h2>
                        <span class="text-muted small">Open: {{ stats.jobData.open }} | Rejected: {{ stats.jobData.rejected }}</span>
                    </div>
                </div>
                <!-- Applications Stats -->
                <div class="col-md-6">
                    <div class="glass-panel p-3">
                        <h5 class="text-white mb-2">Total Applications</h5>
                        <h2 class="text-purple fw-bold mb-1" style="color: #c084fc;">{{ stats.applicationData.total }}</h2>
                        <span class="text-muted small">Applied: {{ stats.applicationData.applied }} | In-Process: {{ stats.applicationData.in_process }}</span>
                    </div>
                </div>
                <!-- Placements Stats -->
                <div class="col-md-6">
                    <div class="glass-panel p-3">
                        <h5 class="text-white mb-2">Secured Placements</h5>
                        <h2 class="text-success fw-bold mb-1">{{ stats.placementData.total }}</h2>
                        <span class="text-muted small">Highest: ₹{{ stats.placementData.highest_salary }} | Avg: ₹{{ stats.placementData.avg_salary }}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Companies Management -->
        <div v-if="companies" class="glass-card mb-4">
            <h3 class="border-bottom border-secondary pb-2 mb-3">Companies Management</h3>
            
            <!-- Pending -->
            <div class="mb-4" v-if="pendingCompanies.length > 0">
                <h5 class="text-warning mb-3">Pending Approvals ({{ pendingCompanies.length }})</h5>
                <div class="custom-table-container">
                    <table class="table text-center table-hover">
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
                            <tr v-for="company in pendingCompanies" :key="company.id">
                                <td>{{ company.id }}</td>
                                <td class="fw-bold text-white">{{ company.name }}</td>
                                <td>{{ company.industry }}</td>
                                <td>
                                    <button @click="router.push({name: 'company-details', params: { id: company.id }})" class="btn btn-primary btn-sm">View</button>
                                </td>
                                <td>
                                    <div class="d-flex justify-content-center gap-2">
                                        <button @click="companyApproval(company.id, APPROVAL_STATUS.APPROVED)" class="btn btn-success btn-sm">Approve</button>
                                        <button @click="companyApproval(company.id, APPROVAL_STATUS.REJECTED)" class="btn btn-danger btn-sm">Reject</button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Rejected -->
            <div class="mb-4" v-if="rejectedCompanies.length > 0">
                <h5 class="text-danger mb-3">Rejected Registrations ({{ rejectedCompanies.length }})</h5>
                <div class="custom-table-container">
                    <table class="table text-center table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Industry</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="company in rejectedCompanies" :key="company.id">
                                <td>{{ company.id }}</td>
                                <td class="fw-bold text-white">{{ company.name }}</td>
                                <td>{{ company.industry }}</td>
                                <td>
                                    <button @click="router.push({name: 'company-details', params: { id: company.id }})" class="btn btn-primary btn-sm">View</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Filter approved & blacklisted -->
            <div class="mb-3">
                <label class="form-label">Search Companies</label>
                <input type="text" v-model="companySearch" class="form-control" placeholder="Search by name or industry...">
            </div>

            <!-- Approved -->
            <div class="mb-4">
                <h5 class="text-success mb-3">Approved Active Companies ({{ filteredApprovedCompanies.length }})</h5>
                <div v-if="filteredApprovedCompanies.length > 0" class="custom-table-container">
                    <table class="table text-center table-hover">
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
                            <tr v-for="company in filteredApprovedCompanies" :key="company.id">
                                <td>{{ company.id }}</td>
                                <td class="fw-bold text-white">{{ company.name }}</td>
                                <td>{{ company.industry }}</td>
                                <td>
                                    <button @click="router.push({name: 'company-details', params: { id: company.id }})" class="btn btn-primary btn-sm">View</button>
                                </td>
                                <td>
                                    <button @click="companyBlacklist(company.id, TOGGLE.TRUE)" class="btn btn-danger btn-sm">Blacklist</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <p v-else class="text-muted small ps-2">No active approved companies found.</p>
            </div>

            <!-- Blacklisted -->
            <div class="mb-4" v-if="filteredBlacklistedCompanies.length > 0">
                <h5 class="text-danger mb-3">Blacklisted Companies ({{ filteredBlacklistedCompanies.length }})</h5>
                <div class="custom-table-container">
                    <table class="table text-center table-hover">
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
                            <tr v-for="company in filteredBlacklistedCompanies" :key="company.id">
                                <td>{{ company.id }}</td>
                                <td class="fw-bold text-white">{{ company.name }}</td>
                                <td>{{ company.industry }}</td>
                                <td>
                                    <button @click="router.push({name: 'company-details', params: { id: company.id }})" class="btn btn-primary btn-sm">View</button>
                                </td>
                                <td>
                                    <button @click="companyBlacklist(company.id, TOGGLE.FALSE)" class="btn btn-success btn-sm">Whitelist</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Students Management -->
        <div v-if="students" class="glass-card mb-4">
            <h3 class="border-bottom border-secondary pb-2 mb-3">Students Management</h3>

            <div class="mb-3">
                <label class="form-label">Search Students</label>
                <input type="text" v-model="studentSearch" class="form-control" placeholder="Search by name or branch...">
            </div>

            <!-- Active Students -->
            <div class="mb-4">
                <h5 class="text-success mb-3">Active Students ({{ filteredStudents.length }})</h5>
                <div v-if="filteredStudents.length > 0" class="custom-table-container">
                    <table class="table text-center table-hover">
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
                            <tr v-for="student in filteredStudents" :key="student.id">
                                <td>{{ student.id }}</td>
                                <td class="fw-bold text-white">{{ student.name }}</td>
                                <td>{{ student.cgpa }}</td>
                                <td>{{ student.branch }}</td>
                                <td>
                                    <button @click="router.push({name: 'student-details', params: { id: student.id }})" class="btn btn-primary btn-sm">View</button>
                                </td>
                                <td>
                                    <button @click="studentBlacklist(student.id, TOGGLE.TRUE)" class="btn btn-danger btn-sm">Blacklist</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <p v-else class="text-muted small ps-2">No active students found.</p>
            </div>

            <!-- Blacklisted Students -->
            <div class="mb-4" v-if="filteredBlacklistedStudents.length > 0">
                <h5 class="text-danger mb-3">Blacklisted Students ({{ filteredBlacklistedStudents.length }})</h5>
                <div class="custom-table-container">
                    <table class="table text-center table-hover">
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
                            <tr v-for="student in filteredBlacklistedStudents" :key="student.id">
                                <td>{{ student.id }}</td>
                                <td class="fw-bold text-white">{{ student.name }}</td>
                                <td>{{ student.cgpa }}</td>
                                <td>{{ student.branch }}</td>
                                <td>
                                    <button @click="router.push({name: 'student-details', params: { id: student.id }})" class="btn btn-primary btn-sm">View</button>
                                </td>
                                <td>
                                    <button @click="studentBlacklist(student.id, TOGGLE.FALSE)" class="btn btn-success btn-sm">Whitelist</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Job Drives Management -->
        <div v-if="jobDrives" class="glass-card mb-4">
            <h3 class="border-bottom border-secondary pb-2 mb-3">Job Drives Management</h3>

            <!-- Pending approvals -->
            <div class="mb-4" v-if="pendingJobDrives.length > 0">
                <h5 class="text-warning mb-3">Pending Job Approvals ({{ pendingJobDrives.length }})</h5>
                <div class="custom-table-container">
                    <table class="table text-center table-hover">
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
                            <tr v-for="job in pendingJobDrives" :key="job.id">
                                <td>{{ job.id }}</td>
                                <td class="fw-bold text-white">{{ job.title }}</td>
                                <td>{{ job.company }}</td>
                                <td>{{ job.vacancies }}</td>
                                <td class="text-warning">{{ formatDate(job.deadline) }}</td>
                                <td>
                                    <button @click="router.push({name: 'job-details', params: { id: job.id }})" class="btn btn-primary btn-sm">View</button>
                                </td>
                                <td>
                                    <div class="d-flex justify-content-center gap-2">
                                        <button @click="jobApproval(job.id, JOB_STATUS.OPEN)" class="btn btn-success btn-sm">Approve</button>
                                        <button @click="jobApproval(job.id, JOB_STATUS.REJECTED)" class="btn btn-danger btn-sm">Reject</button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Rejected jobs -->
            <div class="mb-4" v-if="rejectedJobDrives.length > 0">
                <h5 class="text-danger mb-3">Rejected Job Openings ({{ rejectedJobDrives.length }})</h5>
                <div class="custom-table-container">
                    <table class="table text-center table-hover">
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
                            <tr v-for="job in rejectedJobDrives" :key="job.id">
                                <td>{{ job.id }}</td>
                                <td class="fw-bold text-white">{{ job.title }}</td>
                                <td>{{ job.company }}</td>
                                <td>{{ job.vacancies }}</td>
                                <td>{{ formatDate(job.deadline) }}</td>
                                <td>
                                    <button @click="router.push({name: 'job-details', params: { id: job.id }})" class="btn btn-primary btn-sm">View</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Search -->
            <div class="mb-3">
                <label class="form-label">Search Job Drives</label>
                <input type="text" v-model="jobSearch" class="form-control mb-3" placeholder="Search by title or company...">
            </div>

            <!-- Open Job Drives -->
            <div class="mb-4">
                <h5 class="text-success mb-3">Active Open Drives ({{ filteredJobDrives.length }})</h5>
                <div v-if="filteredJobDrives.length > 0" class="custom-table-container">
                    <table class="table text-center table-hover">
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
                            <tr v-for="job in filteredJobDrives" :key="job.id">
                                <td>{{ job.id }}</td>
                                <td class="fw-bold text-white">{{ job.title }}</td>
                                <td>{{ job.company }}</td>
                                <td>{{ job.vacancies }}</td>
                                <td class="text-warning">{{ formatDate(job.deadline) }}</td>
                                <td>
                                    <button @click="router.push({name: 'job-details', params: { id: job.id }})" class="btn btn-primary btn-sm">View</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <p v-else class="text-muted small ps-2">No active open job drives found.</p>
            </div>

            <!-- Closed Job Drives -->
            <div class="mb-4" v-if="closedJobDrives.length > 0">
                <h5 class="text-muted mb-3">Closed Job Drives ({{ closedJobDrives.length }})</h5>
                <div class="custom-table-container">
                    <table class="table text-center table-hover">
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
                            <tr v-for="job in closedJobDrives" :key="job.id">
                                <td>{{ job.id }}</td>
                                <td class="fw-bold text-white">{{ job.title }}</td>
                                <td>{{ job.company }}</td>
                                <td>{{ job.vacancies }}</td>
                                <td>{{ formatDate(job.deadline) }}</td>
                                <td>
                                    <button @click="router.push({name: 'job-details', params: { id: job.id }})" class="btn btn-primary btn-sm">View</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Applications Management -->
        <div v-if="applications" class="glass-card mb-4">
            <h3 class="border-bottom border-secondary pb-2 mb-3">Applications Management</h3>

            <div class="mb-3">
                <label class="form-label">Filter by Application Status</label>
                <select v-model="applicationState" class="form-select">
                    <option value="">All Application Statuses</option>
                    <option v-for="(value, key) in APPLICATION_STATUS" :key="key" :value="value">
                        {{ key }}
                    </option>
                </select>
            </div>

            <h4 class="mb-3">Applications Found ({{ filteredApplications.length }})</h4>
            <div v-if="filteredApplications.length > 0" class="custom-table-container">
                <table class="table text-center table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Student Name</th>
                            <th>Job Profile @ Company</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="app in filteredApplications" :key="app.id">
                            <td>{{ app.id }}</td>
                            <td class="text-light fw-bold">{{ app.student_name }}</td>
                            <td class="text-white">{{ app.job_title }} @ {{ app.company_name }}</td>
                            <td>
                                <span :class="{
                                    'badge-custom badge-applied': app.status === 'applied',
                                    'badge-custom badge-shortlisted': app.status === 'shortlisted',
                                    'badge-custom badge-interview': app.status === 'interview_scheduled',
                                    'badge-custom badge-success': app.status === 'offer_released' || app.status === 'offer_accepted',
                                    'badge-custom badge-danger': app.status === 'rejected' || app.status === 'offer_rejected'
                                }">
                                    {{ app.status }}
                                </span>
                            </td>
                            <td>
                                <button @click="router.push({name: 'application-details', params: { id: app.id }})" class="btn btn-primary btn-sm">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <p v-else class="text-muted text-center py-4">No applications match the active filter status.</p>
        </div>

        <!-- Placements Management -->
        <div v-if="placements" class="glass-card mb-4">
            <h3 class="border-bottom border-secondary pb-2 mb-3">Placements Management</h3>

            <div class="mb-3">
                <label class="form-label">Search Placement Records</label>
                <input type="text" v-model="placementSearch" class="form-control" placeholder="Search by student name, job title or company...">
            </div>

            <h4 class="mb-3">Placement Records ({{ filteredPlacements.length }})</h4>
            <div v-if="filteredPlacements.length > 0" class="custom-table-container">
                <table class="table text-center table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Student</th>
                            <th>Job Title</th>
                            <th>Company</th>
                            <th>Salary Package</th>
                            <th>Placed On</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="p in filteredPlacements" :key="p.id">
                            <td>{{ p.id }}</td>
                            <td>
                                <button @click="router.push({name: 'student-details', params: { id: p.student_id }})" class="btn btn-link text-info fw-bold p-0 border-0" style="text-decoration:none;">{{ p.student_name }}</button>
                            </td>
                            <td class="text-white">{{ p.job_title }}</td>
                            <td>{{ p.company_name }}</td>
                            <td class="text-success fw-bold">Rs. {{ p.salary?.toLocaleString() }}</td>
                            <td>{{ formatDate(p.placed_at) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <p v-else class="text-muted text-center py-4">No placement records found.</p>
        </div>

    </div>
</template>