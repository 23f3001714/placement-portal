<script setup>
    import { ref, onMounted } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
    import api from '../services/api'
    import logout from '../services/logout'

    const route = useRoute()
    const router = useRouter()

    const job = ref(null)
    const error = ref(null)
    const successMsg = ref(null)
    const hasApplied = ref(false)

    async function loadJob() {
        try {
            job.value = (await api.get(`/student/job/${route.params.id}`)).data
            hasApplied.value = job.value.applications?.status == 'applied' ? true : false
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to load job details'
        }
    }

    async function applyForJob() {
        try {
            successMsg.value = (await api.post('/student/job/apply', { job_id: job.value.id })).data.message
            await loadJob()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to apply for job'
        }
    }

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
                <h1 class="gradient-text fw-bold mb-0">Job Opportunity</h1>
                <p class="text-muted mb-0" v-if="job">Campus Recruitment Drive Details</p>
            </div>
            <div class="mt-3 mt-md-0 d-flex gap-2">
                <button @click="router.push({name: 'student-dashboard'})" class="btn btn-secondary">Back to Dashboard</button>
            </div>
        </div>

        <div v-if="error" class="alert alert-danger d-flex justify-content-between align-items-center mb-4">
            <span>{{ error }}</span>
            <button class="btn btn-danger btn-sm" @click="logout">Try login again</button>
        </div>
        <div v-if="successMsg" class="alert alert-success mb-4">
            {{ successMsg }}
        </div>

        <div v-if="job" class="glass-card" style="max-width: 800px; margin: 0 auto;">
            <div class="d-flex justify-content-between align-items-center border-bottom border-secondary pb-2 mb-3">
                <h3 class="mb-0 text-white">{{ job.title }}</h3>
                <span class="badge-custom badge-success" v-if="!hasApplied">Accepting Applications</span>
                <span class="badge-custom badge-applied" v-else>Applied</span>
            </div>
            
            <h5 class="text-info mb-4">at {{ job.company_name }}</h5>

            <!-- Grid info -->
            <div class="row mb-4">
                <div class="col-md-6 mb-2">
                    <p class="mb-2"><strong>Apply Before:</strong> <span class="text-light text-warning">{{ formatDateTime(job.deadline) }}</span></p>
                    <p class="mb-2"><strong>Vacancies:</strong> <span class="text-light">{{ job.vacancies }}</span></p>
                    <p class="mb-2"><strong>Minimum CGPA required:</strong> <span class="text-light fw-bold text-white">{{ job.min_cgpa }}</span></p>
                </div>
                <div class="col-md-6 mb-2">
                    <p class="mb-2"><strong>Eligible Branches:</strong> <span class="text-light">{{ job.eligible_branches }}</span></p>
                    <p class="mb-2"><strong>Graduation Years:</strong> <span class="text-light">{{ job.eligible_graduation_years }}</span></p>
                    <p class="mb-2"><strong>Drive Posted:</strong> <span class="text-light">{{ formatDate(job.created_at) }}</span></p>
                </div>
            </div>

            <p class="mb-3"><strong>Key Skills Required:</strong> <span class="text-light">{{ job.skills_required }}</span></p>
            
            <div class="glass-panel mb-4">
                <h6 class="text-white mb-2">Job Description</h6>
                <p class="text-light mb-0">{{ job.description }}</p>
            </div>

            <div class="mt-4 pt-3 border-top border-secondary">
                <div v-if="!hasApplied">
                    <button @click="applyForJob" class="btn btn-success px-4 py-2">Apply for Job Opportunity</button>
                </div>
                <div v-else class="d-flex align-items-center justify-content-between alert alert-info py-2 mb-0">
                    <span class="fw-bold">You have already applied for this job.</span>
                    <button @click="router.push({name: 'student-application-details', params: {id: job.applications.id}})" class="btn btn-light btn-sm">View Application</button>
                </div>
            </div>
        </div>
    </div>
</template>
