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
        <!-- Header -->
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary">
            <div>
                <h1 class="gradient-text fw-bold mb-0">Company Details</h1>
                <p class="text-muted mb-0" v-if="company">Admin view for {{ company.name }}</p>
            </div>
            <div class="mt-3 mt-md-0 d-flex gap-2">
                <button @click="router.push({ name: 'admin-dashboard' })" class="btn btn-secondary">Back to Dashboard</button>
                <button @click="logout" class="btn btn-danger">Logout</button>
            </div>
        </div>

        <div v-if="error" class="alert alert-danger d-flex justify-content-between align-items-center mb-4">
            <span>{{ error }}</span>
            <button @click="logout" class="btn btn-danger btn-sm">Login Again</button>
        </div>

        <div v-if="company" class="glass-card" style="max-width: 900px; margin: 0 auto;">
            <h3 class="border-bottom border-secondary pb-2 mb-4 text-white">Company Information</h3>

            <!-- Details Grid -->
            <div class="row mb-4">
                <div class="col-md-6 mb-3">
                    <p class="mb-2"><strong>Company ID:</strong> <span class="text-light ms-2">#{{ company.id }}</span></p>
                    <p class="mb-2"><strong>Company Name:</strong> <span class="text-light ms-2">{{ company.name }}</span></p>
                    <p class="mb-2"><strong>HR Email Address:</strong> <span class="text-light ms-2">{{ company.hr_email }}</span></p>
                    <p class="mb-2"><strong>Industry Sector:</strong> <span class="text-light ms-2">{{ company.industry }}</span></p>
                </div>
                <div class="col-md-6 mb-3">
                    <p class="mb-2"><strong>Location/Office:</strong> <span class="text-light ms-2">{{ company.location || 'N/A' }}</span></p>
                    <p class="mb-2"><strong>Website:</strong> 
                        <a :href="company.website_link" target="_blank" class="text-info ms-2" v-if="company.website_link">{{ company.website_link }}</a>
                        <span class="text-light ms-2" v-else>N/A</span>
                    </p>
                    <p class="mb-2">
                        <strong>Approval Status:</strong> 
                        <span :class="{
                            'badge-custom badge-success ms-2': company.is_approved === APPROVAL_STATUS.APPROVED,
                            'badge-custom badge-danger ms-2': company.is_approved === APPROVAL_STATUS.REJECTED,
                            'badge-custom badge-interview ms-2': company.is_approved === APPROVAL_STATUS.PENDING
                        }">{{ company.is_approved }}</span>
                    </p>
                    <p class="mb-2" v-if="company.is_approved === APPROVAL_STATUS.APPROVED">
                        <strong>Blacklist Status:</strong> 
                        <span :class="company.is_blacklisted ? 'badge-custom badge-danger ms-2' : 'badge-custom badge-success ms-2'">
                            {{ company.is_blacklisted ? 'Blacklisted' : 'Active' }}
                        </span>
                    </p>
                </div>
            </div>

            <div class="glass-panel mb-4">
                <h5 class="text-white mb-2">Company Description</h5>
                <p class="text-light mb-0">{{ company.description }}</p>
            </div>

            <!-- Approval / Blacklist Controls -->
            <div class="mb-4 pt-3 border-top border-secondary">
                <h5 class="text-white mb-3">Administrative Controls</h5>
                
                <div v-if="company.is_approved === APPROVAL_STATUS.PENDING" class="d-flex gap-2">
                    <button @click="companyApproval(route.params.id, APPROVAL_STATUS.APPROVED)" class="btn btn-success">Approve Company</button>
                    <button @click="companyApproval(route.params.id, APPROVAL_STATUS.REJECTED)" class="btn btn-danger">Reject Company</button>
                </div>
                
                <div v-if="company.is_approved === APPROVAL_STATUS.APPROVED" class="d-flex gap-2">
                    <button @click="companyBlacklist(route.params.id, TOGGLE.TRUE)" class="btn btn-danger" :disabled="company.is_blacklisted">Blacklist Company</button>
                    <button @click="companyBlacklist(route.params.id, TOGGLE.FALSE)" class="btn btn-success" :disabled="!company.is_blacklisted">Whitelist Company</button>
                </div>
            </div>

            <!-- Jobs Listing -->
            <div class="mt-4 pt-3 border-top border-secondary">
                <h4 class="text-white mb-3">Job Postings ({{ company.jobs?.length || 0 }})</h4>

                <div v-if="company.jobs?.length > 0" class="custom-table-container">
                    <table class="table text-center table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Job Title</th>
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
                                <td class="fw-bold text-white">{{ job.title }}</td>
                                <td>
                                    <span :class="{
                                        'badge-custom badge-success': job.status === JOB_STATUS.OPEN,
                                        'badge-custom badge-danger': job.status === JOB_STATUS.REJECTED || job.status === JOB_STATUS.CLOSED,
                                        'badge-custom badge-interview': job.status === JOB_STATUS.PENDING
                                    }">{{ job.status }}</span>
                                </td>
                                <td class="text-warning">{{ formatDate(job.deadline) }}</td>
                                <td>{{ job.vacancies }}</td>
                                <td>
                                    <button @click="router.push({ name: 'job-details', params: { id: job.id } })" class="btn btn-primary btn-sm">View</button>
                                </td>
                                <td>
                                    <div v-if="job.status === JOB_STATUS.PENDING" class="d-flex justify-content-center gap-1">
                                        <button class="btn btn-success btn-sm" @click="jobApproval(job.id, JOB_STATUS.OPEN)">Approve</button>
                                        <button class="btn btn-danger btn-sm" @click="jobApproval(job.id, JOB_STATUS.REJECTED)">Reject</button>
                                    </div>
                                    <span v-else class="text-muted small">No action required</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <p v-else class="text-muted py-3 text-center">No job drives have been posted by this company yet.</p>
            </div>

        </div>
    </div>
</template>