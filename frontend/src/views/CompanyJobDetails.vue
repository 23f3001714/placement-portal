<script setup>
    import { ref, onMounted, computed } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
    import api from '../services/api'
    import logout from '../services/logout'

    const route = useRoute()
    const router = useRouter()

    const job = ref(null)
    const error = ref(null)
    const successMsg = ref(null)
    const closeConfirm = ref(false)
    const appSearch = ref('')

    async function loadJob() {
        try {
            job.value = (await api.get(`/company/job/${route.params.id}`)).data
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to load job details'
        }
    }

    const JOB_STATUS = {
            OPEN: 'open',
            CLOSED: 'closed',
            PENDING: 'pending',
            REJECTED: 'rejected'
        }

    async function closeJob() {
        try {
            successMsg.value = (await api.patch(`/company/job/${job.value.id}`, { approval_status: JOB_STATUS.CLOSED })).data.message
            closeConfirm.value = false
            await loadJob()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to close job'
            closeConfirm.value = false
        }
    }

    const filteredApplications = computed(() => {
        if (!job.value?.applications) return []
        if (!appSearch.value) return job.value.applications
        return job.value.applications.filter(a =>
            a.student_name.toLowerCase().includes(appSearch.value.toLowerCase())
        )
    })

    function formatDate(dateStr) {
        return new Date(dateStr).toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'})
    }

    function formatDateTime(dateStr) {
        return new Date(dateStr).toLocaleString('en-GB', {day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'})
    }

    onMounted(async () => {
        await loadJob()
    })
</script>

<template>
    <div class="container py-4">
        <!-- Header -->
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary">
            <div>
                <h1 class="gradient-text fw-bold mb-0">Job Posting Details</h1>
                <p class="text-muted mb-0" v-if="job">Drive Details & Candidate Applications</p>
            </div>
            <div class="mt-3 mt-md-0 d-flex gap-2">
                <button @click="router.push({name: 'company-dashboard'})" class="btn btn-secondary">Back to Dashboard</button>
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

        <div v-if="job">
            <!-- Job Info glass-card -->
            <div class="glass-card mb-4">
                <div class="d-flex justify-content-between align-items-center border-bottom border-secondary pb-2 mb-3">
                    <h3 class="mb-0 text-white">{{ job.title }}</h3>
                    <span :class="{
                        'badge-custom badge-success': job.status === JOB_STATUS.OPEN,
                        'badge-custom badge-danger': job.status === JOB_STATUS.CLOSED || job.status === JOB_STATUS.REJECTED,
                        'badge-custom badge-interview': job.status === JOB_STATUS.PENDING
                    }">{{ job.status }}</span>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-2">
                        <p class="mb-2"><strong>Application Deadline:</strong> <span class="text-light text-warning">{{ formatDateTime(job.deadline) }}</span></p>
                        <p class="mb-2"><strong>Vacancies Offered:</strong> <span class="text-light">{{ job.vacancies }}</span></p>
                        <p class="mb-2"><strong>Minimum Required CGPA:</strong> <span class="text-light">{{ job.min_cgpa }}</span></p>
                    </div>
                    <div class="col-md-6 mb-2">
                        <p class="mb-2"><strong>Eligible Branches:</strong> <span class="text-light">{{ job.eligible_branches }}</span></p>
                        <p class="mb-2"><strong>Eligible Grad Years:</strong> <span class="text-light">{{ job.eligible_graduation_years }}</span></p>
                        <p class="mb-2"><strong>Drive Created On:</strong> <span class="text-light">{{ formatDate(job.created_at) }}</span></p>
                    </div>
                </div>

                <p class="mt-2"><strong>Required Skillsets:</strong> <span class="text-light">{{ job.skills_required }}</span></p>
                <div class="glass-panel mt-3">
                    <h6 class="text-white mb-2">Job Description</h6>
                    <p class="text-light mb-0">{{ job.description }}</p>
                </div>

                <div v-if="job.status === JOB_STATUS.OPEN" class="mt-3 pt-3 border-top border-secondary">
                    <button @click="closeConfirm = true" class="btn btn-danger">Close Job Drive</button>
                </div>
            </div>

            <!-- Applications Listing -->
            <div class="glass-card">
                <h3 class="border-bottom border-secondary pb-2 mb-3">Applications</h3>
                <div class="mb-3">
                    <label class="form-label">Search Candidates</label>
                    <input v-model="appSearch" type="text" class="form-control" placeholder="Search by student name...">
                </div>

                <h4 class="mb-3">Drives Applications ({{ filteredApplications.length }})</h4>
                <div v-if="filteredApplications.length > 0" class="custom-table-container">
                    <table class="table text-center table-hover">
                        <thead>
                            <tr>
                                <th>Student</th>
                                <th>CGPA</th>
                                <th>Branch</th>
                                <th>Status</th>
                                <th>Applied Date</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="app in filteredApplications" :key="app.id">
                                <td class="fw-bold text-white">{{ app.student_name }}</td>
                                <td>{{ app.cgpa }}</td>
                                <td>{{ app.branch || 'N/A' }}</td>
                                <td>
                                    <span :class="{
                                        'badge-custom badge-applied': app.status === 'applied',
                                        'badge-custom badge-shortlisted': app.status === 'shortlisted',
                                        'badge-custom badge-interview': app.status === 'interview_scheduled',
                                        'badge-custom badge-success': app.status === 'offer_released' || app.status === 'offer_accepted',
                                        'badge-custom badge-danger': app.status === 'rejected' || app.status === 'offer_rejected'
                                    }">{{ app.status }}</span>
                                </td>
                                <td>{{ formatDate(app.applied_at) }}</td>
                                <td>
                                    <button @click="router.push({name: 'company-application-details', params: {id: app.id}})" class="btn btn-primary btn-sm">View Profile</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <p v-else class="text-muted text-center py-4">No candidate applications found matching the search.</p>
            </div>
        </div>

        <!-- Close Confirmation Modal -->
        <div v-if="closeConfirm" class="modal d-block">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Confirm Close Job</h5>
                    </div>
                    <div class="modal-body text-light">
                        <p>Warning: Closing this job will automatically reject all pending applications (except those with accepted offers).</p>
                        <p>Are you sure you want to close <strong>{{ job.title }}</strong>?</p>
                    </div>
                    <div class="modal-footer">
                        <button @click="closeConfirm = false" class="btn btn-secondary">Cancel</button>
                        <button @click="closeJob" class="btn btn-danger">Close Job Drive</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
