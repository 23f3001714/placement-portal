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
        <div class="text-center">
            <h1>Company Dashboard</h1>
        </div>

        <div v-if="error" class="alert alert-danger">
            {{ error }}
            <button class="btn btn-danger" @click="logout">Try login again</button>
        </div>

        <div v-if="successMsg" class="alert alert-success">
            {{ successMsg }}
        </div>

        <div v-if="profile">
            <p class="text-muted text-center">Welcome, {{ profile.name }}</p>
            <div class="text-end">
                <button class="btn btn-danger" @click="logout">Logout</button>
            </div>

            <div v-if="stats">
                <h3>Overview Statistics</h3>
                <div class="row text-center mt-3">
                    <div class="col">
                        <h5>Total Jobs</h5>
                        <p>{{ stats.total_jobs }}</p>
                    </div>
                    <div class="col">
                        <h5>Applications</h5>
                        <p>{{ stats.total_applications }}</p>
                    </div>
                    <div class="col">
                        <h5>Shortlisted</h5>
                        <p>{{ stats.shortlisted_count }}</p>
                    </div>
                    <div class="col">
                        <h5>Placements</h5>
                        <p>{{ stats.placements_count }}</p>
                    </div>
                </div>
            </div>

<!-- Profile Section -->
            <h3 class="mt-5">Company Profile</h3>
            <div v-if="!isEditingProfile">
                <div class="row mt-3">
                    <div class="col-6">
                        <p><strong>Name:</strong> {{ profile.name }}</p>
                        <p><strong>HR Email:</strong> {{ profile.hr_email }}</p>
                        <p><strong>Industry:</strong> {{ profile.industry }}</p>
                    </div>
                    <div class="col-6">
                        <p><strong>Location:</strong> {{ profile.location || 'N/A' }}</p>
                        <p><strong>Website:</strong> {{ profile.website_link || 'N/A' }}</p>
                        <p><strong>Status:</strong> {{ profile.is_blacklisted ? 'Blacklisted' : 'Active' }}</p>
                    </div>
                </div>
                <p><strong>Description:</strong> {{ profile.description }}</p>
                <button v-if="!profile.is_blacklisted" @click="startEditProfile" class="btn btn-primary">Edit Profile</button>
            </div>
            <div v-else class="mt-3">
                <div class="row">
                    <div class="col-6 mb-2">
                        <label>HR Email</label>
                        <input v-model="editForm.hr_email" type="email" class="form-control">
                    </div>
                    <div class="col-6 mb-2">
                        <label>Industry</label>
                        <input v-model="editForm.industry" type="text" class="form-control">
                    </div>
                    <div class="col-6 mb-2">
                        <label>Location</label>
                        <input v-model="editForm.location" type="text" class="form-control">
                    </div>
                    <div class="col-6 mb-2">
                        <label>Website</label>
                        <input v-model="editForm.website_link" type="text" class="form-control">
                    </div>
                    <div class="col-12 mb-2">
                        <label>Description</label>
                        <textarea v-model="editForm.description" class="form-control" rows="3"></textarea>
                    </div>
                </div>
                <button @click="saveProfile" class="btn btn-success">Save</button>
                <button @click="cancelEditProfile" class="btn btn-secondary">Cancel</button>
            </div>

            <div class="mt-3">
                <button @click="exportCSV" :disabled="exportingCSV" class="btn btn-primary">Export applicants data</button>
                <button @click="monthlyReport" :disabled="exportingMonthlyReport" class="btn btn-primary mx-3">Generate last month report</button>
            </div>

<!-- Jobs Section -->
            <h3 class="mt-5">Jobs Management</h3>
            <div v-if="profile.is_blacklisted" class="alert alert-danger mb-3">
                Your account is blacklisted. You cant create jobs.
            </div>
            <button v-if="!profile.is_blacklisted" @click="showCreateJob = !showCreateJob" class="btn btn-primary mb-3">
                {{ showCreateJob ? 'Cancel' : ' + Create Job' }}
            </button>

            <div v-if="showCreateJob" class="mb-4">
                <h4>Create New Job</h4>
                <div class="row mb-2">
                    <div class="col-6 mb-2">
                        <label>Title</label>
                        <input v-model="newJob.title" type="text" class="form-control" required>
                    </div>
                    <div class="col-6 mb-2">
                        <label>Deadline</label>
                        <input v-model="newJob.deadline" type="datetime-local" class="form-control" required>
                    </div>
                    <div class="col-4 mb-2">
                        <label>Vacancies</label>
                        <input v-model.number="newJob.vacancies" type="number" min="1" class="form-control" required>
                    </div>
                    <div class="col-4 mb-2">
                        <label>Min CGPA</label>
                        <input v-model.number="newJob.min_cgpa" type="number" step="0.1" min="0" max="10" class="form-control" required>
                    </div>
                    <div class="col-4 mb-2">
                        <label>Eligible Branches</label>
                        <input v-model="newJob.eligible_branches" type="text" class="form-control" placeholder="CSE,IT,AIML" required>
                    </div>
                    <div class="col-6 mb-2">
                        <label>Skills Required</label>
                        <input v-model="newJob.skills_required" type="text" class="form-control" placeholder="Python,JavaScript,SQL" required>
                    </div>
                    <div class="col-6 mb-2">
                        <label>Eligible Graduation Years</label>
                        <input v-model="newJob.eligible_graduation_years" type="text" class="form-control" placeholder="2025,2026" required>
                    </div>
                    <div class="col-12 mb-2">
                        <label>Description</label>
                        <textarea v-model="newJob.description" class="form-control" rows="3" required></textarea>
                    </div>
                </div>
                <button @click="createJob" class="btn btn-success">Submit Job</button>
            </div>

            <h4 class="mt-3">Pending Approval: {{ pendingJobs.length }}</h4>
            <div v-if="pendingJobs.length > 0">
                <table class="table text-center">
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
                        <tr v-for="job in pendingJobs">
                            <td>{{ job.id }}</td>
                            <td>{{ job.title }}</td>
                            <td>{{ job.vacancies }}</td>
                            <td>Pending</td>
                            <td>
                                <button @click="router.push({name: 'company-job-details', params: {id: job.id}})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <h4 class="mt-3">Rejected Jobs: {{ rejectedJobs.length }}</h4>
            <div v-if="rejectedJobs.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>Id</th>
                            <th>Title</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="job in rejectedJobs">
                            <td>{{ job.id }}</td>
                            <td>{{ job.title }}</td>
                            <td>Rejected</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div>
                <input v-model="jobSearch" type="text" class="form-control" placeholder="Search jobs by title..">
            </div>

            <h4 class="mt-3">Open Jobs: {{ filteredOpenJobs.length }}</h4>
            <div v-if="filteredOpenJobs.length > 0">
                <table class="table text-center">
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
                        <tr v-for="job in filteredOpenJobs">
                            <td>{{ job.id }}</td>
                            <td>{{ job.title }}</td>
                            <td>{{ formatDate(job.deadline) }}</td>
                            <td>{{ job.vacancies }}</td>
                            <td>
                                <button @click="router.push({name: 'company-job-details', params: {id: job.id}})" class="btn btn-primary">View</button>
                            </td>
                            <td>
                                <button @click="confirmCloseJob(job)" class="btn btn-danger">Close</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <h4 class="mt-3">Closed Jobs: {{ filteredClosedJobs.length }}</h4>
            <div v-if="filteredClosedJobs.length > 0">
                <table class="table text-center">
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
                        <tr v-for="job in filteredClosedJobs">
                            <td>{{ job.id }}</td>
                            <td>{{ job.title }}</td>
                            <td>{{ formatDate(job.deadline) }}</td>
                            <td>{{ job.vacancies }}</td>
                            <td>
                                <button @click="router.push({name: 'company-job-details', params: {id: job.id}})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

<!-- Applications Section -->
            <h3 class="mt-5">Applications Management</h3>
            <div>
                <input v-model="appSearch" type="text" class="form-control" placeholder="Search by job title..">
            </div>

            <h4 class="mt-3">Applications: {{ filteredApplications.length }}</h4>
            <div v-if="filteredApplications.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>Id</th>
                            <th>Student</th>
                            <th>Job Title</th>
                            <th>Status</th>
                            <th>Applied</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="app in filteredApplications">
                            <td>{{ app.id }}</td>
                            <td>{{ app.student_name }}</td>
                            <td>{{ app.job_title }}</td>
                            <td>{{ app.status }}</td>
                            <td>{{ formatDate(app.applied_at) }}</td>
                            <td>
                                <button @click="router.push({name: 'company-application-details', params: {id: app.id}})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

<!-- Placements Section -->
            <h3 class="mt-5">Placements</h3>
            <h4 class="mt-3">Placements: {{ placements?.length || 0 }}</h4>
            <div v-if="placements?.length > 0">
                <table class="table text-center">
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
                        <tr v-for="placement in placements">
                            <td>{{ placement.id }}</td>
                            <td>{{ placement.student_name }}</td>
                            <td>{{ placement.job_title }}</td>
                            <td>{{ placement.salary?.toLocaleString() || 'N/A' }}</td>
                            <td>{{ formatDate(placement.placed_at) }}</td>
                            <td>
                                <button @click="router.push({name: 'company-placement-details', params: {id: placement.id}})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

<!-- Close Job Confirmation -->
        <div v-if="jobToClose" class="modal d-block">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Confirm Close Job</h5>
                    </div>
                    <div class="modal-body">
                        <p>Warning: Closing this job will automatically reject all pending applications (except those with accepted offers).</p>
                        <p>Are you sure you want to close {{ jobToClose.title }}?</p>
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
