<script setup>
    import { ref, onMounted, computed } from 'vue'
    import { useRouter } from 'vue-router'
    import api from '../services/api'
    import logout from '../services/logout'

    const router = useRouter()

    const profile = ref(null)
    const stats = ref(null)
    const applications = ref(null)
    const placements = ref(null)
    const error = ref(null)
    const successMsg = ref(null)
    const isEditingProfile = ref(false)
    const editForm = ref({})
    const jobSearch = ref('')
    const showCreateJob = ref(false)
    const newJob = ref({title: '', description: '', deadline: '', vacancies: 1, skills_required: '', min_cgpa: 0, eligible_branches: '', eligible_graduation_years: ''})
    const appSearch = ref('')
    const jobToClose = ref(null)
    const exportingCSV = ref(false)
    const exportingMonthlyReport = ref(false)

    async function loadProfile() {
        try {
            profile.value = (await api.get('/company/profile')).data
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to load profile'
        }
    }

    async function loadStats() {
        try {
            stats.value = (await api.get('/company/stats')).data
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to load stats'
        }
    }

    async function loadApplications() {
        try {
            applications.value = (await api.get('/company/applications')).data.applicationData || []
        }
        catch (err) {
            if (err.response?.status !== 204) {
                error.value = err.response?.data?.error || 'Failed to load applications'
            }
        }
    }

    async function loadPlacements() {
        try {
            placements.value = (await api.get('/company/placements')).data.placementData || []
        }
        catch (err) {
            if (err.response?.status !== 204) {
                error.value = err.response?.data?.error || 'Failed to load placements'
            }
        }
    }

    function startEditProfile() {
        editForm.value = {
            hr_email: profile.value.hr_email,
            description: profile.value.description,
            industry: profile.value.industry,
            location: profile.value.location,
            website_link: profile.value.website_link || ''
        }
        isEditingProfile.value = true
    }

    function cancelEditProfile() {
        isEditingProfile.value = false
        editForm.value = {}
    }

    async function saveProfile() {
        try {
            successMsg.value = (await api.patch('/company/profile', editForm.value)).data.message || 'Profile updated successfully'
            isEditingProfile.value = false
            await loadProfile()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to update profile'
        }
    }

    const JOB_STATUS = {
        OPEN: 'open',
        CLOSED: 'closed',
        PENDING: 'pending',
        REJECTED: 'rejected'
    }

    const filteredOpenJobs = computed(() => {
        const jobs = profile.value?.jobs?.filter(j => j.status === JOB_STATUS.OPEN) || []
        if (!jobSearch.value) return jobs
        return jobs.filter(j => j.title.toLowerCase().includes(jobSearch.value.toLowerCase()))
    })

    const filteredClosedJobs = computed(() => {
        const jobs = profile.value?.jobs?.filter(j => j.status === JOB_STATUS.CLOSED) || []
        if (!jobSearch.value) return jobs
        return jobs.filter(j => j.title.toLowerCase().includes(jobSearch.value.toLowerCase()))
    })

    const pendingJobs = computed(() => {
        return profile.value?.jobs?.filter(j => j.status === JOB_STATUS.PENDING) || []
    })

    const rejectedJobs = computed(() => {
        return profile.value?.jobs?.filter(j => j.status === JOB_STATUS.REJECTED) || []
    })

    function confirmCloseJob(job) {
        jobToClose.value = job
    }

    async function closeJob() {
        if (!jobToClose.value) return
        try {
            successMsg.value = (await api.patch(`/company/job/${jobToClose.value.id}`, { approval_status: 'closed' })).data.message
            jobToClose.value = null
            await loadProfile()
            await loadApplications()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to close job'
            jobToClose.value = null
        }
    }

    async function createJob() {
        try {
            successMsg.value = (await api.post('/company/job', newJob.value)).data.message
            showCreateJob.value = false
            newJob.value = {title: '', description: '', deadline: '', vacancies: 1, skills_required: '', min_cgpa: 0, eligible_branches: '', eligible_graduation_years: ''}
            await loadProfile()
            await loadStats()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to create job'
        }
    }

    async function exportCSV() {
        exportingCSV.value = true
        try {
            successMsg.value = (await api.post('/company/export/csv')).data.message
            setTimeout(() => {
                successMsg.value = null
                exportingCSV.value = false
            }, 10000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to export csv'
            exportingCSV.value = false
        }
    }

    async function monthlyReport() {
        exportingMonthlyReport.value = true
        try {
            successMsg.value = (await api.post('/company/report')).data.message
            setTimeout(() => {
                successMsg.value = null
                exportingMonthlyReport.value = false
            }, 10000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to generate/export monthly report'
            exportingMonthlyReport.value = false
        }
    }

    const filteredApplications = computed(() => {
        if (!applications.value) return []
        if (!appSearch.value) return applications.value
        return applications.value.filter(a =>
            a.job_title.toLowerCase().includes(appSearch.value.toLowerCase())
        )
    })

    function formatDate(dateStr) {
        return new Date(dateStr).toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'})
    }

    onMounted(async () => {
        await loadProfile()
        loadStats()
        loadApplications()
        loadPlacements()
    })
</script>

<template>
    <div class="container py-4">
        <!-- Header -->
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary">
            <div>
                <h1 class="gradient-text fw-bold mb-0">Company Dashboard</h1>
                <p class="text-muted mb-0" v-if="profile">Welcome, {{ profile.name }}</p>
            </div>
            <div v-if="profile" class="mt-3 mt-md-0 d-flex gap-2">
                <button class="btn btn-danger" @click="logout">Logout</button>
            </div>
        </div>

        <div v-if="error" class="alert alert-danger d-flex justify-content-between align-items-center mb-4">
            <span>{{ error }}</span>
            <button class="btn btn-danger btn-sm" @click="logout">Try login again</button>
        </div>

        <div v-if="successMsg" class="alert alert-success mb-4">
            {{ successMsg }}
        </div>

        <div v-if="profile">
            <!-- Profile Section -->
            <div class="glass-card mb-4">
                <h3 class="border-bottom border-secondary pb-2 mb-3">Company Profile</h3>
                <div v-if="!isEditingProfile">
                    <div class="row">
                        <div class="col-md-6 mb-2">
                            <p class="mb-2"><strong>Name:</strong> <span class="text-light">{{ profile.name }}</span></p>
                            <p class="mb-2"><strong>HR Email:</strong> <span class="text-light">{{ profile.hr_email }}</span></p>
                            <p class="mb-2"><strong>Industry:</strong> <span class="text-light">{{ profile.industry }}</span></p>
                        </div>
                        <div class="col-md-6 mb-2">
                            <p class="mb-2"><strong>Location:</strong> <span class="text-light">{{ profile.location || 'N/A' }}</span></p>
                            <p class="mb-2"><strong>Website:</strong> <a :href="profile.website_link" target="_blank" class="text-info" v-if="profile.website_link">{{ profile.website_link }}</a><span class="text-light" v-else>N/A</span></p>
                            <p class="mb-2">
                                <strong>Status:</strong> 
                                <span :class="profile.is_blacklisted ? 'badge-custom badge-danger ms-2' : 'badge-custom badge-success ms-2'">
                                    {{ profile.is_blacklisted ? 'Blacklisted' : 'Active' }}
                                </span>
                            </p>
                        </div>
                    </div>
                    <p class="mt-2"><strong>Description:</strong> <span class="text-light">{{ profile.description }}</span></p>
                    
                    <div class="d-flex flex-wrap gap-2 mt-3 pt-3 border-top border-secondary">
                        <button v-if="!profile.is_blacklisted" @click="startEditProfile" class="btn btn-primary">Edit Profile</button>
                        <button @click="exportCSV" :disabled="exportingCSV" class="btn btn-secondary">
                            <span v-if="exportingCSV">Exporting...</span>
                            <span v-else>Export Applicants CSV</span>
                        </button>
                        <button @click="monthlyReport" :disabled="exportingMonthlyReport" class="btn btn-secondary">
                            <span v-if="exportingMonthlyReport">Generating...</span>
                            <span v-else>Last Month Report</span>
                        </button>
                    </div>
                </div>
                <div v-else class="mt-2">
                    <h5 class="mb-3 text-white">Edit Company Details</h5>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">HR Email</label>
                            <input v-model="editForm.hr_email" type="email" class="form-control">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Industry</label>
                            <input v-model="editForm.industry" type="text" class="form-control">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Location</label>
                            <input v-model="editForm.location" type="text" class="form-control">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Website URL</label>
                            <input v-model="editForm.website_link" type="text" class="form-control">
                        </div>
                        <div class="col-12 mb-3">
                            <label class="form-label">Description</label>
                            <textarea v-model="editForm.description" class="form-control" rows="3"></textarea>
                        </div>
                    </div>
                    <div class="d-flex gap-2">
                        <button @click="saveProfile" class="btn btn-success">Save Changes</button>
                        <button @click="cancelEditProfile" class="btn btn-secondary">Cancel</button>
                    </div>
                </div>
            </div>

            <!-- Stats -->
            <div v-if="stats" class="glass-card mb-4">
                <h3 class="border-bottom border-secondary pb-2 mb-3">Overview Statistics</h3>
                <div class="row text-center g-3">
                    <div class="col-6 col-md-3">
                        <div class="glass-panel p-3">
                            <h6 class="text-muted text-uppercase small">Total Jobs</h6>
                            <h2 class="mb-0 text-primary fw-bold">{{ stats.total_jobs }}</h2>
                        </div>
                    </div>
                    <div class="col-6 col-md-3">
                        <div class="glass-panel p-3">
                            <h6 class="text-muted text-uppercase small">Applications</h6>
                            <h2 class="mb-0 text-info fw-bold">{{ stats.total_applications }}</h2>
                        </div>
                    </div>
                    <div class="col-6 col-md-3">
                        <div class="glass-panel p-3">
                            <h6 class="text-muted text-uppercase small">Shortlisted</h6>
                            <h2 class="mb-0 text-warning fw-bold">{{ stats.shortlisted_count }}</h2>
                        </div>
                    </div>
                    <div class="col-6 col-md-3">
                        <div class="glass-panel p-3">
                            <h6 class="text-muted text-uppercase small">Placements</h6>
                            <h2 class="mb-0 text-success fw-bold">{{ stats.placements_count }}</h2>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Jobs Management -->
            <div class="glass-card mb-4">
                <div class="d-flex justify-content-between align-items-center border-bottom border-secondary pb-2 mb-3">
                    <h3 class="mb-0">Jobs Management</h3>
                    <button v-if="!profile.is_blacklisted" @click="showCreateJob = !showCreateJob" class="btn btn-success btn-sm">
                        {{ showCreateJob ? 'Cancel' : ' + Create Job' }}
                    </button>
                </div>

                <div v-if="profile.is_blacklisted" class="alert alert-danger mb-3">
                    Your account is blacklisted. You cannot create jobs.
                </div>

                <!-- Create Job Form -->
                <div v-if="showCreateJob" class="glass-panel mb-4">
                    <h4 class="mb-3 text-white">Create New Job Posting</h4>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Title</label>
                            <input v-model="newJob.title" type="text" class="form-control" placeholder="e.g. Frontend Engineer" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Deadline</label>
                            <input v-model="newJob.deadline" type="datetime-local" class="form-control" required>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Vacancies</label>
                            <input v-model.number="newJob.vacancies" type="number" min="1" class="form-control" required>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Min CGPA</label>
                            <input v-model.number="newJob.min_cgpa" type="number" step="0.1" min="0" max="10" class="form-control" required>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Eligible Branches</label>
                            <input v-model="newJob.eligible_branches" type="text" class="form-control" placeholder="CSE,IT,AIML" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Skills Required</label>
                            <input v-model="newJob.skills_required" type="text" class="form-control" placeholder="Python,JavaScript,SQL" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Eligible Graduation Years</label>
                            <input v-model="newJob.eligible_graduation_years" type="text" class="form-control" placeholder="2025,2026" required>
                        </div>
                        <div class="col-12 mb-3">
                            <label class="form-label">Description</label>
                            <textarea v-model="newJob.description" class="form-control" rows="3" required></textarea>
                        </div>
                    </div>
                    <button @click="createJob" class="btn btn-success">Submit Job</button>
                </div>

                <!-- Pending Jobs -->
                <div class="mb-4" v-if="pendingJobs.length > 0">
                    <h5 class="text-warning mb-3">Pending Approval ({{ pendingJobs.length }})</h5>
                    <div class="custom-table-container">
                        <table class="table text-center table-hover">
                            <thead>
                                <tr>
                                    <th>Id</th>
                                    <th>Title</th>
                                    <th>Vacancies</th>
                                    <th>Status</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="job in pendingJobs" :key="job.id">
                                    <td>{{ job.id }}</td>
                                    <td class="fw-bold text-white">{{ job.title }}</td>
                                    <td>{{ job.vacancies }}</td>
                                    <td><span class="badge-custom badge-interview">Pending</span></td>
                                    <td>
                                        <button @click="router.push({name: 'company-job-details', params: {id: job.id}})" class="btn btn-primary btn-sm">View</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Rejected Jobs -->
                <div class="mb-4" v-if="rejectedJobs.length > 0">
                    <h5 class="text-danger mb-3">Rejected Jobs ({{ rejectedJobs.length }})</h5>
                    <div class="custom-table-container">
                        <table class="table text-center table-hover">
                            <thead>
                                <tr>
                                    <th>Id</th>
                                    <th>Title</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="job in rejectedJobs" :key="job.id">
                                    <td>{{ job.id }}</td>
                                    <td class="fw-bold text-white">{{ job.title }}</td>
                                    <td><span class="badge-custom badge-danger">Rejected</span></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Open Jobs -->
                <div class="mb-4">
                    <div class="mb-3">
                        <label class="form-label">Search Jobs</label>
                        <input v-model="jobSearch" type="text" class="form-control" placeholder="Search jobs by title...">
                    </div>

                    <h5 class="text-success mb-3">Open Jobs ({{ filteredOpenJobs.length }})</h5>
                    <div v-if="filteredOpenJobs.length > 0" class="custom-table-container">
                        <table class="table text-center table-hover">
                            <thead>
                                <tr>
                                    <th>Id</th>
                                    <th>Title</th>
                                    <th>Deadline</th>
                                    <th>Vacancies</th>
                                    <th>Details</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="job in filteredOpenJobs" :key="job.id">
                                    <td>{{ job.id }}</td>
                                    <td class="fw-bold text-white">{{ job.title }}</td>
                                    <td class="text-warning">{{ formatDate(job.deadline) }}</td>
                                    <td>{{ job.vacancies }}</td>
                                    <td>
                                        <button @click="router.push({name: 'company-job-details', params: {id: job.id}})" class="btn btn-primary btn-sm">View</button>
                                    </td>
                                    <td>
                                        <button @click="confirmCloseJob(job)" class="btn btn-danger btn-sm">Close</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <p v-else class="text-muted small ps-2">No active open jobs.</p>
                </div>

                <!-- Closed Jobs -->
                <div class="mb-4">
                    <h5 class="text-muted mb-3">Closed Jobs ({{ filteredClosedJobs.length }})</h5>
                    <div v-if="filteredClosedJobs.length > 0" class="custom-table-container">
                        <table class="table text-center table-hover">
                            <thead>
                                <tr>
                                    <th>Id</th>
                                    <th>Title</th>
                                    <th>Deadline</th>
                                    <th>Vacancies</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="job in filteredClosedJobs" :key="job.id">
                                    <td>{{ job.id }}</td>
                                    <td class="fw-bold text-white">{{ job.title }}</td>
                                    <td>{{ formatDate(job.deadline) }}</td>
                                    <td>{{ job.vacancies }}</td>
                                    <td>
                                        <button @click="router.push({name: 'company-job-details', params: {id: job.id}})" class="btn btn-primary btn-sm">View</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <p v-else class="text-muted small ps-2">No closed jobs.</p>
                </div>
            </div>

            <!-- Applications Management -->
            <div class="glass-card mb-4">
                <h3 class="border-bottom border-secondary pb-2 mb-3">Applications Management</h3>
                <div class="mb-3">
                    <label class="form-label">Search Applications</label>
                    <input v-model="appSearch" type="text" class="form-control" placeholder="Search by job title...">
                </div>

                <h5 class="mb-3">Received Applications ({{ filteredApplications.length }})</h5>
                <div v-if="filteredApplications.length > 0" class="custom-table-container">
                    <table class="table text-center table-hover">
                        <thead>
                            <tr>
                                <th>Id</th>
                                <th>Student</th>
                                <th>Job Title</th>
                                <th>Status</th>
                                <th>Applied On</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="app in filteredApplications" :key="app.id">
                                <td>{{ app.id }}</td>
                                <td class="text-light fw-bold">{{ app.student_name }}</td>
                                <td class="text-white">{{ app.job_title }}</td>
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
                                <td>{{ formatDate(app.applied_at) }}</td>
                                <td>
                                    <button @click="router.push({name: 'company-application-details', params: {id: app.id}})" class="btn btn-primary btn-sm">View</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <p v-else class="text-muted text-center py-4">No applications received yet.</p>
            </div>

            <!-- Placements -->
            <div class="glass-card mb-4">
                <h3 class="border-bottom border-secondary pb-2 mb-3">Placements</h3>
                <h5 class="mb-3">Secured Placements ({{ placements?.length || 0 }})</h5>
                <div v-if="placements?.length > 0" class="custom-table-container">
                    <table class="table text-center table-hover">
                        <thead>
                            <tr>
                                <th>Id</th>
                                <th>Student</th>
                                <th>Job Title</th>
                                <th>Salary</th>
                                <th>Placed On</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="placement in placements" :key="placement.id">
                                <td>{{ placement.id }}</td>
                                <td class="text-light fw-bold">{{ placement.student_name }}</td>
                                <td class="text-white">{{ placement.job_title }}</td>
                                <td class="text-success fw-bold">Rs. {{ placement.salary?.toLocaleString() || 'N/A' }}</td>
                                <td>{{ formatDate(placement.placed_at) }}</td>
                                <td>
                                    <button @click="router.push({name: 'company-placement-details', params: {id: placement.id}})" class="btn btn-primary btn-sm">View</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <p v-else class="text-muted text-center py-4">No placements secured yet.</p>
            </div>
        </div>

        <!-- Close Job Confirmation Modal -->
        <div v-if="jobToClose" class="modal d-block">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Confirm Close Job</h5>
                    </div>
                    <div class="modal-body">
                        <p class="text-light">Warning: Closing this job will automatically reject all pending applications (except those with accepted offers).</p>
                        <p>Are you sure you want to close <strong>{{ jobToClose.title }}</strong>?</p>
                    </div>
                    <div class="modal-footer">
                        <button @click="jobToClose = null" class="btn btn-secondary">Cancel</button>
                        <button @click="closeJob" class="btn btn-danger">Close Job</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
