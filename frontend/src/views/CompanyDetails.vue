<script setup>
    import { ref, onMounted } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
    import api from '../services/api'
    import logout from '../services/logout'

    const router = useRouter()
    const route = useRoute()

    const company = ref(null)
    const error = ref(null)

    async function loadCompany(id) {
        try {
            company.value = (await api.get(`/admin/company/${id}`)).data
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to load company'
        }
    }

    async function jobApproval(id, status) {
        try {
            await api.patch(`/admin/job/${id}`, {status: status})
            await loadCompany(route.params.id)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to update job approval'
        }
    }

    const JOB_STATUS = {
        OPEN: 'open',
        CLOSED: 'closed',
        PENDING: 'pending',
        REJECTED: 'rejected',
    }

    const TOGGLE = {
        TRUE: true,
        FALSE: false
    }

    const APPROVAL_STATUS = {
        APPROVED: 'approved',
        REJECTED: 'rejected',
        PENDING: 'pending'
    }

    async function companyBlacklist(id, status) {
        try {
            await api.patch(`/admin/company/${id}/blacklist-status`, {is_blacklisted: status})
            loadCompany(route.params.id)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to update company blacklist status'
        }
    }

    async function companyApproval(id, status) {
        try {
            await api.patch(`/admin/company/${id}`, {approval_status :status})
            loadCompany(route.params.id)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to approve/reject company'
        }
    }

    function formatDate(dateStr) {
        return new Date(dateStr).toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'})
    }

    onMounted(async() => {
        await loadCompany(route.params.id)
    })
</script>

<template>
    <div class="container py-4">
        <div class="text-center">
            <h1>Company Details</h1>
        </div>

        <div v-if="error" class="alert alert-danger text-center">
            {{ error }}
            <button @click="logout" class="btn btn-danger">Login Again</button>
        </div>

        <div v-else class="text-end mb-3">
            <button @click="router.push({ name: 'admin-dashboard' })" class="btn btn-dark">Back to Dashboard</button>
            <button @click="logout" class="btn btn-danger">Logout</button>
        </div>

        <div v-if="company">
            <p><strong>ID:</strong> {{ company.id }}</p>
            <p><strong>Name:</strong> {{ company.name }}</p>
            <p><strong>HR Email:</strong> {{ company.hr_email }}</p>
            <p><strong>Description:</strong> {{ company.description }}</p>
            <p><strong>Industry:</strong> {{ company.industry }}</p>
            <p><strong>Location:</strong> {{ company.location }}</p>
            <p><strong>Website:</strong> {{ company.website_link }}</p>
            <p><strong>Approved:</strong> {{ company.is_approved }}</p>
            <p v-if="company.is_approved === APPROVAL_STATUS.PENDING">
                <button @click="companyApproval(route.params.id, APPROVAL_STATUS.APPROVED)" class="btn btn-success">Approve</button>
                <button @click="companyApproval(route.params.id, APPROVAL_STATUS.REJECTED)" class="btn btn-danger">Reject</button>
            </p>
            <p v-if="company.is_approved === APPROVAL_STATUS.APPROVED">
                <strong>Blacklisted:</strong> {{ company.is_blacklisted }}
                <button @click="companyBlacklist(route.params.id, TOGGLE.TRUE)" class="btn btn-dark" :disabled="company.is_blacklisted">Blacklist</button>
                <button @click="companyBlacklist(route.params.id, TOGGLE.FALSE)" class="btn btn-light" :disabled="!company.is_blacklisted">Whitelist</button>
            </p>
            <h4 class="mt-4">Jobs</h4>

            <div v-if="company.jobs?.length > 0">
                <table class="table text-center">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Status</th>
                            <th>Deadline</th>
                            <th>Vacancies</th>
                            <th>Details</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="job in company.jobs" :key="job.id">
                            <td>{{ job.id }}</td>
                            <td>{{ job.title }}</td>
                            <td>{{ job.status }}</td>
                            <td>{{ formatDate(job.deadline) }}</td>
                            <td>{{ job.vacancies }}</td>
                            <td>
                                <button @click="router.push({ name: 'job-details', params: { id: job.id } })" class="btn btn-primary">View</button>
                            </td>
                            <td>
                                <div v-if="job.status === JOB_STATUS.PENDING">
                                    <button class="btn btn-success" @click="jobApproval(job.id, JOB_STATUS.OPEN)">Approve</button>
                                    <button class="btn btn-danger" @click="jobApproval(job.id, JOB_STATUS.REJECTED)">Reject</button>
                                </div>
                                <p v-else class="text-muted">Action completed</p>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <p v-else class="text-muted">No jobs available</p>
        </div>
    </div>
</template>