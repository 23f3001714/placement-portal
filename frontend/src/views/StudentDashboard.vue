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
        <div class="text-center">
            <h1>Student Dashboard</h1>
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

            <h3 class="mt-5">Student Profile</h3>
            <div class="row mt-3">
                <div class="col-6">
                    <p><strong>Name:</strong> {{ profile.name }}</p>
                    <p><strong>Email:</strong> {{ profile.email }}</p>
                    <p><strong>CGPA:</strong> {{ profile.cgpa }}</p>
                </div>
                <div class="col-6">
                    <p><strong>Branch:</strong> {{ profile.branch }}</p>
                    <p><strong>Graduation Year:</strong> {{ profile.graduation_year }}</p>
                    <p><strong>Status:</strong> {{ profile.placement ? 'Placed' : 'Unplaced' }}</p>
                </div>
                <div v-if="!isEditingProfile">
                    <p><strong>Skills:</strong> {{ profile.skills || 'N/A' }}</p>
                    <p><strong>Resume:</strong>
                        <button v-if="profile.resume_path" @click="downloadResume" class="btn btn-primary">Download Resume</button>
                        <span v-else class="text-muted">Not uploaded</span>
                    </p>
                    <p v-if="profile.is_blacklisted" class="text-danger">Status: Blacklisted</p>
                    <button v-if="!profile.is_blacklisted" @click="startEditProfile" class="btn btn-primary">Edit Profile</button>
                </div>
                <div v-else>
                    <div class="row mb-3">
                        <div class="col-4">
                            <label>Skills</label>
                            <input v-model="editForm.skills" type="text" class="form-control" placeholder="Python,JavaScript,SQL">
                        </div>
                        <div class="col-4">
                            <label>CGPA</label>
                            <input v-model="editForm.cgpa" type="number" step="0.01" min="0" max="10" class="form-control" placeholder="8.5">
                        </div>
                        <div class="col-4">
                            <label>Resume (PDF)</label>
                            <input @change="onResumeFileChange" type="file" accept=".pdf" class="form-control">
                        </div>
                    </div>
                    <button @click="saveProfile" class="btn btn-success">Save</button>
                    <button @click="cancelEditProfile" class="btn btn-secondary">Cancel</button>
                </div>
            </div>

            <div class="mt-3">
                <button @click="exportCSV" :disabled="exportingCSV" class="btn btn-primary">Export your application data</button>
            </div>

            <div v-if="profile.placement">
                <h3 class="mt-5">Placement Details</h3>
                <div class="row mt-3">
                    <div class="col-6">
                        <p><strong>Company:</strong> {{ profile.placement.company_name }}</p>
                        <p><strong>Job Title:</strong> {{ profile.placement.job_title }}</p>
                    </div>
                    <div class="col-6">
                        <p><strong>Salary:</strong> Rs. {{ profile.placement.salary?.toLocaleString() }}</p>
                        <p><strong>Joining Date:</strong> {{ formatDate(profile.placement.joining_date) }}</p>
                    </div>
                </div>
            </div>
            <div v-else-if="!profile.is_blacklisted">
                <h3 class="mt-5">Available Jobs</h3>
                <div>
                    <input v-model="jobSearch" type="text" class="form-control" placeholder="Search jobs by title, company or skills..">
                </div>

                <h4 class="mt-3">Jobs: {{ filteredJobs.length }}</h4>
                <div v-if="filteredJobs.length > 0">
                    <table class="table text-center">
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
                            <tr v-for="job in filteredJobs">
                                <td>{{ job.id }}</td>
                                <td>{{ job.title }}</td>
                                <td>{{ job.company }}</td>
                                <td>{{ job.skills_required }}</td>
                                <td>{{ formatDate(job.deadline) }}</td>
                                <td>
                                    <button @click="router.push({name: 'student-job-details', params: {id: job.id}})" class="btn btn-primary">View</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div v-else>
                <div class="alert alert-danger mt-5">
                    Your account is blacklisted. You cannot view or apply for job drives.
                </div>
            </div>

            <h3 class="mt-5">My Applications</h3>
            <div>
                <input v-model="appSearch" type="text" class="form-control" placeholder="Search by job title..">
            </div>

            <h4 class="mt-3">Applied: {{ appliedApplications.length }}</h4>
            <div v-if="appliedApplications.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>Id</th>
                            <th>Job Title</th>
                            <th>Company</th>
                            <th>Applied</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="app in appliedApplications">
                            <td>{{ app.id }}</td>
                            <td>{{ app.job_title }}</td>
                            <td>{{ app.company_name }}</td>
                            <td>{{ formatDate(app.applied_at) }}</td>
                            <td>
                                <button @click="router.push({name: 'student-application-details', params: {id: app.id}})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <h4 class="mt-3">Shortlisted: {{ shortlistedApplications.length }}</h4>
            <div v-if="shortlistedApplications.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>Id</th>
                            <th>Job Title</th>
                            <th>Company</th>
                            <th>Applied</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="app in shortlistedApplications">
                            <td>{{ app.id }}</td>
                            <td>{{ app.job_title }}</td>
                            <td>{{ app.company_name }}</td>
                            <td>{{ formatDate(app.applied_at) }}</td>
                            <td>
                                <button @click="router.push({name: 'student-application-details', params: {id: app.id}})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <h4 class="mt-3">Interview: {{ interviewApplications.length }}</h4>
            <div v-if="interviewApplications.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>Id</th>
                            <th>Job Title</th>
                            <th>Company</th>
                            <th>Applied</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="app in interviewApplications">
                            <td>{{ app.id }}</td>
                            <td>{{ app.job_title }}</td>
                            <td>{{ app.company_name }}</td>
                            <td>{{ formatDate(app.applied_at) }}</td>
                            <td>
                                <button @click="router.push({name: 'student-application-details', params: {id: app.id}})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <h4 class="mt-3">Rejected: {{ rejectedApplications.length }}</h4>
            <div v-if="rejectedApplications.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>Id</th>
                            <th>Job Title</th>
                            <th>Company</th>
                            <th>Applied</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="app in rejectedApplications">
                            <td>{{ app.id }}</td>
                            <td>{{ app.job_title }}</td>
                            <td>{{ app.company_name }}</td>
                            <td>{{ formatDate(app.applied_at) }}</td>
                            <td>
                                <button @click="router.push({name: 'student-application-details', params: {id: app.id}})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <h4 class="mt-3">Offer Letter: {{ offerApplications.length }}</h4>
            <div v-if="offerApplications.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>Id</th>
                            <th>Job Title</th>
                            <th>Company</th>
                            <th>Status</th>
                            <th>Applied</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="app in offerApplications">
                            <td>{{ app.id }}</td>
                            <td>{{ app.job_title }}</td>
                            <td>{{ app.company_name }}</td>
                            <td>{{ app.status }}</td>
                            <td>{{ formatDate(app.applied_at) }}</td>
                            <td>
                                <button @click="router.push({name: 'student-application-details', params: {id: app.id}})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
