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
        <div class="text-center">
            <h1>Job Details</h1>
        </div>

        <button @click="router.push({name: 'company-dashboard'})" class="btn btn-secondary">Back to Dashboard</button>

        <div v-if="error" class="alert alert-danger">
            {{ error }}
            <button class="btn btn-danger" @click="logout">Try login again</button>
        </div>
        <div v-if="successMsg" class="alert alert-success">
            {{ successMsg }}
        </div>

        <div v-if="job">
            <h3>{{ job.title }}</h3>
            <p><strong>Status:</strong> {{ job.status }}</p>

            <div class="row mt-3">
                <div class="col">
                    <p><strong>Deadline:</strong> {{ formatDateTime(job.deadline) }}</p>
                    <p><strong>Vacancies:</strong> {{ job.vacancies }}</p>
                    <p><strong>Min CGPA:</strong> {{ job.min_cgpa }}</p>
                </div>
                <div class="col">
                    <p><strong>Eligible Branches:</strong> {{ job.eligible_branches }}</p>
                    <p><strong>Graduation Years:</strong> {{ job.eligible_graduation_years }}</p>
                    <p><strong>Created:</strong> {{ formatDate(job.created_at) }}</p>
                </div>
            </div>
            <p><strong>Skills Required:</strong> {{ job.skills_required }}</p>
            <p><strong>Description:</strong> {{ job.description }}</p>

            <div v-if="job.status === JOB_STATUS.OPEN" class="mt-3">
                <button @click="closeConfirm = true" class="btn btn-danger">Close Job</button>
            </div>

            <h3 class="mt-5">Applications</h3>
            <div>
                <input v-model="appSearch" type="text" class="form-control" placeholder="Search by student name..">
            </div>

            <h4 class="mt-3">Applications: {{ filteredApplications.length }}</h4>
            <div v-if="filteredApplications.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>Student</th>
                            <th>CGPA</th>
                            <th>Branch</th>
                            <th>Status</th>
                            <th>Applied</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="app in filteredApplications">
                            <td>{{ app.student_name }}</td>
                            <td>{{ app.cgpa }}</td>
                            <td>{{ app.branch || 'N/A' }}</td>
                            <td>{{ app.status }}</td>
                            <td>{{ formatDate(app.applied_at) }}</td>
                            <td>
                                <button @click="router.push({name: 'company-application-details', params: {id: app.id}})" class="btn btn-primary">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div v-if="closeConfirm" class="modal d-block">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Confirm Close Job</h5>
                    </div>
                    <div class="modal-body">
                        <p>Warning: Closing this job will automatically reject all pending applications (except those with accepted offers).</p>
                        <p>Are you sure you want to close {{ job.title }}?</p>
                    </div>
                    <div class="modal-footer">
                        <button @click="closeConfirm = false" class="btn btn-secondary">Cancel</button>
                        <button @click="closeJob" class="btn btn-danger">Close Job</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
