<script setup>
    import { ref, onMounted, computed } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
    import api from '../services/api'
    import logout from '../services/logout'

    const router = useRouter()
    const route = useRoute()

    const job = ref(null)
    const stats = ref(null)
    const error = ref(null)
    const applicationState = ref('')

    async function loadJob(id) {
        try {
            job.value = (await api.get(`/admin/job/${id}`)).data
            await loadJobStats(id)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to load job'
        }
    }

    async function loadJobStats(id) {
        try {
            stats.value = (await api.get(`/admin/job/${id}/stats`)).data
        }
        catch (err) {
            console.error('Failed to load job stats:', err)
        }
    }

    async function jobApproval(id, status) {
        try {
            await api.patch(`/admin/job/${id}`, {status: status})
            await loadJob(route.params.id)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to update job status'
        }
    }

    const JOB_STATUS = {
        OPEN: 'open',
        CLOSED: 'closed',
        PENDING: 'pending',
        REJECTED: 'rejected',
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

    function formatDate(dateStr) {
        return new Date(dateStr).toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'})
    }

    const getFilteredApplications = computed(
        () => {
            if (!job.value?.applications) return []
            if (!applicationState.value) return job.value.applications
            return job.value.applications.filter(
                app => app.status === applicationState.value) || []
        }
    )

    onMounted(async() => {
        const id = route.params.id;
        await loadJob(id)
    })
</script>

<template>
    <div class="container py-4">
        <!-- Header -->
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary">
            <div>
                <h1 class="gradient-text fw-bold mb-0">Job Drive Profile</h1>
                <p class="text-muted mb-0" v-if="job">Admin Job Drive Management</p>
            </div>
            <div class="mt-3 mt-md-0 d-flex gap-2">
                <button @click="router.push({ name: 'admin-dashboard' })" class="btn btn-secondary">Back to Dashboard</button>
                <button @click="logout" class="btn btn-danger">Logout</button>
            </div>
        </div>

        <div v-if="error" class="alert alert-danger d-flex justify-content-between align-items-center mb-4">
            <span>{{ error }}</span>
            <button class="btn btn-danger btn-sm" @click="logout">Try login again</button>
        </div>

        <div v-if="job" class="glass-card" style="max-width: 950px; margin: 0 auto;">
            <div class="d-flex justify-content-between align-items-center border-bottom border-secondary pb-2 mb-4">
                <h3 class="mb-0 text-white">{{ job.title }}</h3>
                <span :class="{
                    'badge-custom badge-success': job.status === JOB_STATUS.OPEN,
                    'badge-custom badge-danger': job.status === JOB_STATUS.CLOSED || job.status === JOB_STATUS.REJECTED,
                    'badge-custom badge-interview': job.status === JOB_STATUS.PENDING
                }">{{ job.status }}</span>
            </div>

            <!-- Job Info Grid -->
            <div class="row mb-4">
                <div class="col-md-6 mb-3">
                    <p class="mb-2"><strong>Job ID:</strong> <span class="text-light ms-2">#{{ job.id }}</span></p>
                    <p class="mb-2"><strong>Company:</strong> 
                        <button @click="router.push({ name: 'company-details', params: { id: job.company_id } })" class="btn btn-link text-info fw-bold p-0 border-0" style="text-decoration:none;">
                            {{ job.company_name }}
                        </button>
                    </p>
                    <p class="mb-2"><strong>Application Deadline:</strong> <span class="text-light ms-2 text-warning">{{ formatDate(job.deadline) }}</span></p>
                    <p class="mb-2"><strong>Vacancies:</strong> <span class="text-light ms-2">{{ job.vacancies }}</span></p>
                </div>
                <div class="col-md-6 mb-3">
                    <p class="mb-2"><strong>Minimum CGPA:</strong> <span class="text-light ms-2">{{ job.min_cgpa }}</span></p>
                    <p class="mb-2"><strong>Eligible Branches:</strong> <span class="text-light ms-2">{{ job.eligible_branches }}</span></p>
                    <p class="mb-2"><strong>Eligible Graduation Years:</strong> <span class="text-light ms-2">{{ job.eligible_graduation_years }}</span></p>
                    <p class="mb-2"><strong>Required Skills:</strong> <span class="text-light ms-2">{{ job.skills_required }}</span></p>
                </div>
            </div>

            <div class="glass-panel mb-4">
                <h5 class="text-white mb-2">Detailed Job Description</h5>
                <p class="text-light mb-0">{{ job.description }}</p>
            </div>

            <!-- Pending approvals controls -->
            <div v-if="job.status === JOB_STATUS.PENDING" class="mb-4 pt-3 border-top border-secondary">
                <h5 class="text-white mb-3">Administrative Actions</h5>
                <div class="d-flex gap-2">
                    <button @click="jobApproval(route.params.id, JOB_STATUS.OPEN)" class="btn btn-success">Approve Job Posting</button>
                    <button @click="jobApproval(route.params.id, JOB_STATUS.REJECTED)" class="btn btn-danger">Reject Job Posting</button>
                </div>
            </div>

            <!-- Job Statistics & Candidates section -->
            <div v-if="job.status !== JOB_STATUS.REJECTED && job.status !== JOB_STATUS.PENDING" class="mt-4 pt-3 border-top border-secondary">
                
                <!-- Small Stats Blocks -->
                <div v-if="stats" class="row text-center mb-4 g-3">
                    <div class="col-4">
                        <div class="glass-panel p-2">
                            <span class="text-muted small text-uppercase">Applications</span>
                            <h4 class="mb-0 text-white fw-bold">{{ stats.total_applications }}</h4>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="glass-panel p-2">
                            <span class="text-muted small text-uppercase">Accepted Offers</span>
                            <h4 class="mb-0 text-success fw-bold">{{ stats.accepted_applications }}</h4>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="glass-panel p-2">
                            <span class="text-muted small text-uppercase">Secured Placements</span>
                            <h4 class="mb-0 text-info fw-bold">{{ stats.total_placements }}</h4>
                        </div>
                    </div>
                </div>

                <!-- Candidates Section -->
                <h4 class="text-white mb-3">Applicants List</h4>
                
                <div class="mb-3">
                    <label class="form-label">Filter Applications by Status</label>
                    <select v-model="applicationState" class="form-select">
                        <option value="">All Candidates</option>
                        <option v-for="(value, key) in APPLICATION_STATUS" :key="key" :value="value">
                            {{ key }}
                        </option>
                    </select>
                </div>

                <h5 class="text-white mt-3 mb-2">Candidates Found ({{ getFilteredApplications.length }})</h5>
                <div v-if="getFilteredApplications.length > 0" class="custom-table-container">
                    <table class="table text-center table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Student Name</th>
                                <th>CGPA</th>
                                <th>Applied Date</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="application in getFilteredApplications" :key="application.id">
                                <td>{{ application.id }}</td>
                                <td>
                                    <button @click="router.push({ name: 'student-details', params: { id: application.student_id } })" class="btn btn-link text-info fw-bold p-0 border-0" style="text-decoration:none;">
                                        {{ application.student_name }}
                                    </button>
                                </td>
                                <td>{{ application.cgpa }}</td>
                                <td>{{ formatDate(application.applied_at) }}</td>
                                <td>
                                    <span :class="{
                                        'badge-custom badge-applied': application.status === 'applied',
                                        'badge-custom badge-shortlisted': application.status === 'shortlisted',
                                        'badge-custom badge-interview': application.status === 'interview_scheduled',
                                        'badge-custom badge-success': application.status === 'offer_released' || application.status === 'offer_accepted',
                                        'badge-custom badge-danger': application.status === 'rejected' || application.status === 'offer_rejected'
                                    }">{{ application.status }}</span>
                                </td>
                                <td>
                                    <button @click="router.push({ name: 'application-details', params: { id: application.id } })" class="btn btn-primary btn-sm">View details</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <p v-else class="text-muted py-3 text-center">No applications match this status filter.</p>
            </div>

        </div>
    </div>
</template>