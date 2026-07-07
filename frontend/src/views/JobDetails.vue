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
        <div class="text-center">
            <h1>Job Details</h1>
        </div>

        <div v-if="error" class="alert alert-danger">
            {{ error }}
            <button class="btn btn-danger" @click="logout">Try login again</button>
        </div>

        <div v-if="job">
            <div class="text-end mb-3">
                <button @click="router.push({ name: 'admin-dashboard' })" class="btn btn-dark">Back to Dashboard</button>
                <button @click="logout" class="btn btn-danger">Logout</button>
            </div>

            <p><strong>ID:</strong> {{ job.id }}</p>
            <p><strong>Title:</strong> {{ job.title }}</p>
            <p><strong>Company:</strong>
                <button @click="router.push({ name: 'company-details', params: { id: job.company_id } })" class="btn btn-link p-0">{{ job.company_name }}</button>
            </p>
            <p><strong>Description:</strong> {{ job.description }}</p>
            <p><strong>Deadline:</strong> {{ formatDate(job.deadline) }}</p>
            <p><strong>Vacancies:</strong> {{ job.vacancies }}</p>
            <p><strong>Skills Required:</strong> {{ job.skills_required }}</p>
            <p><strong>Min CGPA:</strong> {{ job.min_cgpa }}</p>
            <p><strong>Eligible Branches:</strong> {{ job.eligible_branches }}</p>
            <p><strong>Eligible Graduation Years:</strong> {{ job.eligible_graduation_years }}</p>
            <p><strong>Status:</strong> {{ job.status }}</p>
            <div v-if="job.status === JOB_STATUS.PENDING">
                <button @click="jobApproval(route.params.id, JOB_STATUS.REJECTED)" class="btn btn-danger">Reject</button>
                <button @click="jobApproval(route.params.id, JOB_STATUS.OPEN)" class="btn btn-success">Approve</button>
            </div>

            <div v-if="job.status !== JOB_STATUS.REJECTED && job.status !== JOB_STATUS.PENDING">
                <div v-if="stats">
                    <h4 class="mt-4">Stats</h4>
                    <p><strong>Total Applications:</strong> {{ stats.total_applications }}</p>
                    <p><strong>Accepted:</strong> {{ stats.accepted_applications }}</p>
                    <p><strong>Total Placements:</strong> {{ stats.total_placements }}</p>
                </div>

                <select v-model="applicationState" class="form-select mb-3">
                    <option value="">All Applications</option>
                    <option v-for="(value, key) in APPLICATION_STATUS" :key="key" :value="value">
                        {{ key }}
                    </option>
                </select>

                <h3 class="mt-3">Applications: {{ getFilteredApplications.length }}</h3>
                <div v-if="getFilteredApplications.length > 0">
                    <table class="table text-center">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Student Name</th>
                                <th>CGPA</th>
                                <th>Applied Date</th>
                                <th>Status</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="application in getFilteredApplications">
                                <td>{{ application.id }}</td>
                                <td>
                                    <button @click="router.push({ name: 'student-details', params: { id: application.student_id } })" class="btn btn-link p-0">{{ application.student_name }}</button>
                                </td>
                                <td>{{ application.cgpa }}</td>
                                <td>{{ formatDate(application.applied_at) }}</td>
                                <td>{{ application.status }}</td>
                                <td>
                                    <button @click="router.push({ name: 'application-details', params: { id: application.id } })" class="btn btn-primary">View</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <p v-else class="text-muted">No applications available</p>
            </div>
        </div>
    </div>
</template>