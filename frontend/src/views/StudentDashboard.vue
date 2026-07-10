<script setup>
    import { ref, onMounted, computed } from 'vue'
    import { useRouter } from 'vue-router'
    import api from '../services/api'
    import logout from '../services/logout'

    const router = useRouter()

    const profile = ref(null)
    const jobs = ref(null)
    const applications = ref(null)
    const error = ref(null)
    const successMsg = ref(null)
    const isEditingProfile = ref(false)
    const editForm = ref({})
    const resumeFile = ref(null)
    const jobSearch = ref('')
    const appSearch = ref('')
    const exportingCSV = ref(false)

    async function loadProfile() {
        try {
            profile.value = (await api.get('/student/profile')).data
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to load profile'
        }
    }

    async function loadJobs() {
        try {
            jobs.value = (await api.get('/student/jobs')).data.jobData || []
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to load jobs'
        }
    }

    async function loadApplications() {
        try {
            applications.value = (await api.get('/student/applications')).data.applicationData || []
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to load applications'
        }
    }

    function startEditProfile() {
        editForm.value = {
            skills: profile.value.skills || '',
            cgpa: profile.value.cgpa || ''
        }
        resumeFile.value = null
        isEditingProfile.value = true
    }

    function cancelEditProfile() {
        isEditingProfile.value = false
        editForm.value = {}
        resumeFile.value = null
    }

    function onResumeFileChange(event) {
        resumeFile.value = event.target.files[0] || null
    }

    async function saveProfile() {
        try {
            const formData = new FormData()
            if (editForm.value.skills) formData.append('skills', editForm.value.skills)
            if (editForm.value.cgpa) formData.append('cgpa', editForm.value.cgpa)
            if (resumeFile.value) formData.append('resume', resumeFile.value)
            successMsg.value = (await api.patch('/student/profile', formData)).data.message || 'Updated profile successfully'
            isEditingProfile.value = false
            resumeFile.value = null
            await loadProfile()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to update profile'
        }
    }

    async function downloadResume() {
        try {
            const url = window.URL.createObjectURL(new Blob([(await api.get('/student/resume', { responseType: 'blob' })).data], {type: 'application/pdf'}))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', 'resume.pdf')
            document.body.appendChild(link)
            link.click()
            link.remove()
            window.URL.revokeObjectURL(url)
        }
        catch (err) {
            error.value = 'Failed to load resume'
        }
    }

    async function exportCSV() {
        exportingCSV.value = true
        try {
            successMsg.value = (await api.post('/student/export/csv')).data.message
            setTimeout(() => {
                successMsg.value = false
                exportingCSV.value = false
            }, 10000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'export CSV failed'
            exportingCSV.value = false
        }
    }

    const APPLICATION_STATUS = {
        APPLIED: 'applied',
        SHORTLISTED: 'shortlisted',
        INTERVIEW_SCHEDULED: 'interview_scheduled',
        REJECTED: 'rejected',
        OFFER_RELEASED: 'offer_released',
        OFFER_ACCEPTED: 'offer_accepted',
        OFFER_REJECTED: 'offer_rejected'
    }

    const filteredJobs = computed(() => {
        if (!jobs.value) return []
        if (!jobSearch.value) return jobs.value
        return jobs.value.filter(j =>
            j.title.toLowerCase().includes(jobSearch.value.toLowerCase()) ||
            j.company.toLowerCase().includes(jobSearch.value.toLowerCase()) ||
            j.skills_required.toLowerCase().includes(jobSearch.value.toLowerCase())
        ) || []
    })

    const filteredApplications = computed(() => {
        if (!applications.value) return []
        if (!appSearch.value) return applications.value
        return applications.value.filter(a =>
            a.job_title.toLowerCase().includes(appSearch.value.toLowerCase())
        ) || []
    })

    const appliedApplications = computed(() => {
        return filteredApplications.value?.filter(a => a.status === APPLICATION_STATUS.APPLIED) || []
    })

    const shortlistedApplications = computed(() => {
        return filteredApplications.value?.filter(a => a.status === APPLICATION_STATUS.SHORTLISTED) || []
    })

    const interviewApplications = computed(() => {
        return filteredApplications.value?.filter(a => a.status === APPLICATION_STATUS.INTERVIEW_SCHEDULED) || []
    })

    const rejectedApplications = computed(() => {
        return filteredApplications.value?.filter(a => a.status === APPLICATION_STATUS.REJECTED || a.status === APPLICATION_STATUS.OFFER_REJECTED) || []
    })

    const offerApplications = computed(() => {
        return filteredApplications.value?.filter(a => a.status === APPLICATION_STATUS.OFFER_RELEASED || a.status === APPLICATION_STATUS.OFFER_ACCEPTED) || []
    })

    function formatDate(dateStr) {
        return new Date(dateStr).toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'})
    }

    onMounted(async () => {
        await loadProfile()
        loadJobs()
        loadApplications()
    })
</script>

<template>
    <div class="container py-4">
        <!-- Header -->
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary">
            <div>
                <h1 class="gradient-text fw-bold mb-0">Student Dashboard</h1>
                <p class="text-muted mb-0" v-if="profile">Welcome back, {{ profile.name }}</p>
            </div>
            <div v-if="profile" class="mt-3 mt-md-0 d-flex gap-2">
                <button @click="exportCSV" :disabled="exportingCSV" class="btn btn-primary">
                    <span v-if="exportingCSV">Exporting...</span>
                    <span v-else>Export Application Data</span>
                </button>
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
            <!-- Profile Info Card -->
            <div class="glass-card mb-4">
                <h3 class="border-bottom border-secondary pb-2 mb-3">Student Profile</h3>
                <div class="row">
                    <div class="col-md-6 mb-2">
                        <p class="mb-2"><strong>Name:</strong> <span class="text-light">{{ profile.name }}</span></p>
                        <p class="mb-2"><strong>Email:</strong> <span class="text-light">{{ profile.email }}</span></p>
                        <p class="mb-2"><strong>CGPA:</strong> <span class="text-light">{{ profile.cgpa }}</span></p>
                    </div>
                    <div class="col-md-6 mb-2">
                        <p class="mb-2"><strong>Branch:</strong> <span class="text-light">{{ profile.branch }}</span></p>
                        <p class="mb-2"><strong>Graduation Year:</strong> <span class="text-light">{{ profile.graduation_year }}</span></p>
                        <p class="mb-2">
                            <strong>Status:</strong> 
                            <span :class="profile.placement ? 'badge-custom badge-success ms-2' : 'badge-custom badge-applied ms-2'">
                                {{ profile.placement ? 'Placed' : 'Unplaced' }}
                            </span>
                        </p>
                    </div>
                </div>

                <!-- Sub-profile details (Skills / Resume / Blacklist) -->
                <div class="mt-3 border-top border-secondary pt-3" v-if="!isEditingProfile">
                    <p><strong>Skills:</strong> <span class="text-light">{{ profile.skills || 'N/A' }}</span></p>
                    <p class="d-flex align-items-center flex-wrap gap-2">
                        <strong>Resume:</strong>
                        <button v-if="profile.resume_path" @click="downloadResume" class="btn btn-primary btn-sm py-1 px-2">Download Resume</button>
                        <span v-else class="text-muted">Not uploaded</span>
                    </p>
                    <p v-if="profile.is_blacklisted" class="alert alert-danger py-2 mt-2">
                        Account Status: Blacklisted
                    </p>
                    <button v-if="!profile.is_blacklisted" @click="startEditProfile" class="btn btn-primary mt-2">Edit Profile</button>
                </div>

                <!-- Profile Edit Form -->
                <div class="mt-3 border-top border-secondary pt-3" v-else>
                    <h5 class="mb-3 text-white">Edit Profile</h5>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Skills (comma separated)</label>
                            <input v-model="editForm.skills" type="text" class="form-control" placeholder="Python,JavaScript,SQL">
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label">CGPA</label>
                            <input v-model="editForm.cgpa" type="number" step="0.01" min="0" max="10" class="form-control" placeholder="8.5">
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Resume (PDF File)</label>
                            <input @change="onResumeFileChange" type="file" accept=".pdf" class="form-control">
                        </div>
                    </div>
                    <div class="d-flex gap-2">
                        <button @click="saveProfile" class="btn btn-success">Save changes</button>
                        <button @click="cancelEditProfile" class="btn btn-secondary">Cancel</button>
                    </div>
                </div>
            </div>

            <!-- Placement Details Card -->
            <div v-if="profile.placement" class="glass-card mb-4 border border-success">
                <h3 class="text-success border-bottom border-success pb-2 mb-3">Placement Details 🎉</h3>
                <div class="row">
                    <div class="col-md-6 mb-2">
                        <p class="mb-2"><strong>Company:</strong> <span class="text-light">{{ profile.placement.company_name }}</span></p>
                        <p class="mb-2"><strong>Job Title:</strong> <span class="text-light">{{ profile.placement.job_title }}</span></p>
                    </div>
                    <div class="col-md-6 mb-2">
                        <p class="mb-2"><strong>Salary:</strong> <span class="text-light">Rs. {{ profile.placement.salary?.toLocaleString() }}</span></p>
                        <p class="mb-2"><strong>Joining Date:</strong> <span class="text-light">{{ formatDate(profile.placement.joining_date) }}</span></p>
                    </div>
                </div>
            </div>

            <!-- Available Jobs -->
            <div v-else-if="!profile.is_blacklisted" class="glass-card mb-4">
                <h3 class="border-bottom border-secondary pb-2 mb-3">Available Job Openings</h3>
                <div class="mb-4">
                    <label class="form-label">Search Jobs</label>
                    <input v-model="jobSearch" type="text" class="form-control" placeholder="Search jobs by title, company or skills required...">
                </div>

                <h4 class="mb-3">Open Jobs ({{ filteredJobs.length }})</h4>
                <div v-if="filteredJobs.length > 0" class="custom-table-container">
                    <table class="table text-center table-hover">
                        <thead>
                            <tr>
                                <th>Id</th>
                                <th>Title</th>
                                <th>Company</th>
                                <th>Skills Required</th>
                                <th>Deadline</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="job in filteredJobs" :key="job.id">
                                <td>{{ job.id }}</td>
                                <td class="fw-bold text-white">{{ job.title }}</td>
                                <td>{{ job.company }}</td>
                                <td><span class="text-muted">{{ job.skills_required }}</span></td>
                                <td class="text-warning">{{ formatDate(job.deadline) }}</td>
                                <td>
                                    <button @click="router.push({name: 'student-job-details', params: {id: job.id}})" class="btn btn-primary btn-sm">View Details</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div v-else class="text-center py-4 text-muted">
                    No matching job openings available at the moment.
                </div>
            </div>

            <!-- Blacklist Alert -->
            <div v-else class="alert alert-danger mb-4">
                Your account is blacklisted. You cannot view or apply for job drives.
            </div>

            <!-- Applications Section Card -->
            <div class="glass-card">
                <h3 class="border-bottom border-secondary pb-2 mb-3">My Applications</h3>
                <div class="mb-4">
                    <label class="form-label">Search Applications</label>
                    <input v-model="appSearch" type="text" class="form-control" placeholder="Search by job title...">
                </div>

                <!-- Applied -->
                <div class="mb-4">
                    <h5 class="text-info mb-3">Applied Drives ({{ appliedApplications.length }})</h5>
                    <div v-if="appliedApplications.length > 0" class="custom-table-container">
                        <table class="table text-center table-hover">
                            <thead>
                                <tr>
                                    <th>Id</th>
                                    <th>Job Title</th>
                                    <th>Company</th>
                                    <th>Applied On</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="app in appliedApplications" :key="app.id">
                                    <td>{{ app.id }}</td>
                                    <td class="fw-bold text-white">{{ app.job_title }}</td>
                                    <td>{{ app.company_name }}</td>
                                    <td>{{ formatDate(app.applied_at) }}</td>
                                    <td>
                                        <button @click="router.push({name: 'student-application-details', params: {id: app.id}})" class="btn btn-primary btn-sm">View</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <p v-else class="text-muted small ps-2">No applications in this category.</p>
                </div>

                <!-- Shortlisted -->
                <div class="mb-4">
                    <h5 class="mb-3" style="color: #c084fc;">Shortlisted Drives ({{ shortlistedApplications.length }})</h5>
                    <div v-if="shortlistedApplications.length > 0" class="custom-table-container">
                        <table class="table text-center table-hover">
                            <thead>
                                <tr>
                                    <th>Id</th>
                                    <th>Job Title</th>
                                    <th>Company</th>
                                    <th>Applied On</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="app in shortlistedApplications" :key="app.id">
                                    <td>{{ app.id }}</td>
                                    <td class="fw-bold text-white">{{ app.job_title }}</td>
                                    <td>{{ app.company_name }}</td>
                                    <td>{{ formatDate(app.applied_at) }}</td>
                                    <td>
                                        <button @click="router.push({name: 'student-application-details', params: {id: app.id}})" class="btn btn-primary btn-sm">View</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <p v-else class="text-muted small ps-2">No applications in this category.</p>
                </div>

                <!-- Interview -->
                <div class="mb-4">
                    <h5 class="text-warning mb-3">Interview Scheduled ({{ interviewApplications.length }})</h5>
                    <div v-if="interviewApplications.length > 0" class="custom-table-container">
                        <table class="table text-center table-hover">
                            <thead>
                                <tr>
                                    <th>Id</th>
                                    <th>Job Title</th>
                                    <th>Company</th>
                                    <th>Applied On</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="app in interviewApplications" :key="app.id">
                                    <td>{{ app.id }}</td>
                                    <td class="fw-bold text-white">{{ app.job_title }}</td>
                                    <td>{{ app.company_name }}</td>
                                    <td>{{ formatDate(app.applied_at) }}</td>
                                    <td>
                                        <button @click="router.push({name: 'student-application-details', params: {id: app.id}})" class="btn btn-primary btn-sm">View</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <p v-else class="text-muted small ps-2">No applications in this category.</p>
                </div>

                <!-- Offer Letters -->
                <div class="mb-4">
                    <h5 class="text-success mb-3">Offers Received ({{ offerApplications.length }})</h5>
                    <div v-if="offerApplications.length > 0" class="custom-table-container">
                        <table class="table text-center table-hover">
                            <thead>
                                <tr>
                                    <th>Id</th>
                                    <th>Job Title</th>
                                    <th>Company</th>
                                    <th>Status</th>
                                    <th>Applied On</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="app in offerApplications" :key="app.id">
                                    <td>{{ app.id }}</td>
                                    <td class="fw-bold text-white">{{ app.job_title }}</td>
                                    <td>{{ app.company_name }}</td>
                                    <td>
                                        <span :class="app.status === 'offer_accepted' ? 'badge-custom badge-success' : 'badge-custom badge-interview'">
                                            {{ app.status }}
                                        </span>
                                    </td>
                                    <td>{{ formatDate(app.applied_at) }}</td>
                                    <td>
                                        <button @click="router.push({name: 'student-application-details', params: {id: app.id}})" class="btn btn-primary btn-sm">View</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <p v-else class="text-muted small ps-2">No applications in this category.</p>
                </div>

                <!-- Rejected -->
                <div class="mb-4">
                    <h5 class="text-danger mb-3">Rejected / Closed ({{ rejectedApplications.length }})</h5>
                    <div v-if="rejectedApplications.length > 0" class="custom-table-container">
                        <table class="table text-center table-hover">
                            <thead>
                                <tr>
                                    <th>Id</th>
                                    <th>Job Title</th>
                                    <th>Company</th>
                                    <th>Applied On</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="app in rejectedApplications" :key="app.id">
                                    <td>{{ app.id }}</td>
                                    <td class="fw-bold text-white">{{ app.job_title }}</td>
                                    <td>{{ app.company_name }}</td>
                                    <td>{{ formatDate(app.applied_at) }}</td>
                                    <td>
                                        <button @click="router.push({name: 'student-application-details', params: {id: app.id}})" class="btn btn-primary btn-sm">View</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <p v-else class="text-muted small ps-2">No applications in this category.</p>
                </div>
            </div>
        </div>
    </div>
</template>
