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
        <div class="text-center">
            <h1>Job Details</h1>
        </div>

        <button @click="router.push({name: 'student-dashboard'})" class="btn btn-secondary">Back to Dashboard</button>

        <div v-if="error" class="alert alert-danger">
            {{ error }}
            <button class="btn btn-danger" @click="logout">Try login again</button>
        </div>
        <div v-if="successMsg" class="alert alert-success">
            {{ successMsg }}
        </div>

        <div v-if="job">
            <h3>{{ job.title }}</h3>
            <p><strong>Company:</strong> {{ job.company_name }}</p>

            <div class="row mt-3">
                <div class="col">
                    <p><strong>Deadline:</strong> {{ formatDateTime(job.deadline) }}</p>
                    <p><strong>Vacancies:</strong> {{ job.vacancies }}</p>
                    <p><strong>Min CGPA:</strong> {{ job.min_cgpa }}</p>
                </div>
                <div class="col">
                    <p><strong>Eligible Branches:</strong> {{ job.eligible_branches }}</p>
                    <p><strong>Graduation Years:</strong> {{ job.eligible_graduation_years }}</p>
                    <p><strong>Posted:</strong> {{ formatDate(job.created_at) }}</p>
                </div>
            </div>
            <p><strong>Skills Required:</strong> {{ job.skills_required }}</p>
            <p><strong>Description:</strong> {{ job.description }}</p>

            <div class="mt-3">
                <button v-if="!hasApplied" @click="applyForJob" class="btn btn-success">Apply for Job</button>
                <p v-else><strong>You have already applied for this job.</strong>
                    <button @click="router.push({name: 'student-application-details', params: {id: job.applications.id}})" class="btn btn-light">View Application</button>
                </p>
            </div>
        </div>
    </div>
</template>
