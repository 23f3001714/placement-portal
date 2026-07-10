<script setup>
    import { ref, onMounted, computed } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
    import api from '../services/api'
    import logout from '../services/logout'

    const route = useRoute()
    const router = useRouter()

    const application = ref(null)
    const error = ref(null)
    const successMsg = ref(null)
    const action = ref(null)

    async function loadApplication() {
        try {
            application.value = (await api.get(`/student/application/${route.params.id}`)).data
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to load application'
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

    async function acceptOffer() {
        try {
            successMsg.value = (await api.patch(`/student/application/${application.value.id}`, {status: APPLICATION_STATUS.OFFER_ACCEPTED})).data.message
            action.value = null
            await loadApplication()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to accept offer'
        }
    }

    async function rejectOffer() {
        try {
            successMsg.value = (await api.patch(`/student/application/${application.value.id}`, {status: APPLICATION_STATUS.OFFER_REJECTED})).data.message
            action.value = null
            await loadApplication()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to reject offer'
        }
    }

    async function downloadOfferLetter() {
        try {
            const url = window.URL.createObjectURL(new Blob([(await api.get(`/student/application/${application.value.id}/offer-letter`, { responseType: 'blob' })).data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `offer_letter_app_${application.value.id}.pdf`)
            document.body.appendChild(link)
            link.click()
            link.remove()
            window.URL.revokeObjectURL(url)
        }
        catch (err) {
            error.value = 'Failed to download offer letter'
        }
    }

    async function downloadPlacementLetter() {
        try {
            const url = window.URL.createObjectURL(new Blob([(await api.get('/student/placement-letter', { responseType: 'blob' })).data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', 'placement_letter.pdf')
            document.body.appendChild(link)
            link.click()
            link.remove()
            window.URL.revokeObjectURL(url)
        }
        catch (err) {
            error.value = 'Failed to download placement letter'
        }
    }

    const canAcceptReject = computed(() => application.value?.status === APPLICATION_STATUS.OFFER_RELEASED)
    const isFinalState = computed(() => [APPLICATION_STATUS.REJECTED, APPLICATION_STATUS.OFFER_REJECTED, APPLICATION_STATUS.OFFER_ACCEPTED].includes(application.value?.status))

    function formatDate(dateStr) {
        if (!dateStr) return 'N/A'
        return new Date(dateStr).toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'})
    }

    function formatDateTime(dateStr) {
        if (!dateStr) return 'N/A'
        return new Date(dateStr).toLocaleString('en-GB', {day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'})
    }

    onMounted(async () => {
        await loadApplication()
    })
</script>

<template>
    <div class="container py-4">
        <!-- Header -->
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary">
            <div>
                <h1 class="gradient-text fw-bold mb-0">Application Details</h1>
                <p class="text-muted mb-0" v-if="application">Viewing details for Application #{{ application.id }}</p>
            </div>
            <div class="mt-3 mt-md-0 d-flex gap-2">
                <button @click="router.push({name: 'student-dashboard'})" class="btn btn-secondary">Back to Dashboard</button>
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

        <div v-if="application" class="glass-card" style="max-width: 850px; margin: 0 auto;">
            <!-- Top Status Indicator -->
            <div class="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary">
                <h3 class="mb-0 text-white">Application Profile</h3>
                <span :class="{
                    'badge-custom badge-applied': application.status === 'applied',
                    'badge-custom badge-shortlisted': application.status === 'shortlisted',
                    'badge-custom badge-interview': application.status === 'interview_scheduled',
                    'badge-custom badge-success': application.status === 'offer_released' || application.status === 'offer_accepted',
                    'badge-custom badge-danger': application.status === 'rejected' || application.status === 'offer_rejected'
                }">{{ application.status }}</span>
            </div>

            <!-- Job Info -->
            <div class="glass-panel mb-4">
                <h4 class="mb-3 text-info">Job Information</h4>
                <div class="row">
                    <div class="col-md-6 mb-2">
                        <p class="mb-2"><strong>Job Title:</strong> <span class="text-light">{{ application.job_title }}</span></p>
                        <p class="mb-2"><strong>Company:</strong> <span class="text-light">{{ application.company_name }}</span></p>
                    </div>
                    <div class="col-md-6 mb-2">
                        <p class="mb-2"><strong>Applied On:</strong> <span class="text-light">{{ formatDate(application.applied_at) }}</span></p>
                    </div>
                </div>
                <div class="mt-3 border-top border-secondary pt-3">
                    <h6 class="text-white mb-2">Role Description</h6>
                    <p class="text-light mb-0">{{ application.description }}</p>
                </div>
            </div>

            <!-- Interview Details -->
            <div v-if="application.interview_date || application.interview_location" class="glass-panel mb-4">
                <h4 class="mb-3 text-warning">Interview Details</h4>
                <div class="row">
                    <div class="col-md-6 mb-2" v-if="application.interview_date">
                        <p class="mb-0"><strong>Schedule Time:</strong> <span class="text-light">{{ formatDateTime(application.interview_date) }}</span></p>
                    </div>
                    <div class="col-md-6 mb-2" v-if="application.interview_location">
                        <p class="mb-0"><strong>Location/Link:</strong> <span class="text-light text-warning">{{ application.interview_location }}</span></p>
                    </div>
                </div>
            </div>

            <!-- Offer Details -->
            <div v-if="application.salary" class="glass-panel mb-4 border border-success">
                <h4 class="mb-3 text-success">Offer Package Released</h4>
                <div class="row mb-3">
                    <div class="col-md-6 mb-2">
                        <p class="mb-0"><strong>Salary (Annual):</strong> <span class="text-success fw-bold">Rs. {{ application.salary?.toLocaleString() }}</span></p>
                    </div>
                    <div class="col-md-6 mb-2">
                        <p class="mb-0"><strong>Joining Date:</strong> <span class="text-light">{{ formatDate(application.joining_date) }}</span></p>
                    </div>
                </div>
                <button v-if="application.offer_letter_path" @click="downloadOfferLetter" class="btn btn-primary btn-sm px-3">Download Offer Letter</button>
            </div>

            <!-- Feedback -->
            <div v-if="application.feedback" class="glass-panel mb-4">
                <h4 class="mb-2 text-info">Feedback</h4>
                <p class="text-light mb-0">{{ application.feedback }}</p>
            </div>

            <!-- Acceptance Actions -->
            <div v-if="canAcceptReject && !action" class="mt-4 pt-3 border-top border-secondary">
                <h4 class="text-white mb-3">Actions Required</h4>
                <div class="d-flex gap-2">
                    <button @click="action = 'accept'" class="btn btn-success">Accept Offer</button>
                    <button @click="action = 'reject'" class="btn btn-danger">Reject Offer</button>
                </div>
            </div>

            <!-- Accept Confirmation -->
            <div v-if="action === 'accept'" class="glass-panel mt-3 border border-success">
                <h5 class="text-success mb-2">Confirm Accept Offer</h5>
                <p class="text-light mb-3">Warning: Accepting this offer will automatically reject all your other pending applications.</p>
                <p class="text-white fw-bold mb-3">Are you sure you want to accept this offer?</p>
                <div class="d-flex gap-2">
                    <button @click="acceptOffer" class="btn btn-success">Confirm Accept</button>
                    <button @click="action = null" class="btn btn-secondary">Cancel</button>
                </div>
            </div>

            <!-- Reject Confirmation -->
            <div v-if="action === 'reject'" class="glass-panel mt-3 border border-danger">
                <h5 class="text-danger mb-2">Confirm Reject Offer</h5>
                <p class="text-light mb-3">Are you sure you want to reject this job offer?</p>
                <div class="d-flex gap-2">
                    <button @click="rejectOffer" class="btn btn-danger">Confirm Reject</button>
                    <button @click="action = null" class="btn btn-secondary">Cancel</button>
                </div>
            </div>

            <!-- Placement Confirmed Alert -->
            <div v-if="application.status === APPLICATION_STATUS.OFFER_ACCEPTED" class="glass-panel mt-4 border border-success bg-opacity-10 bg-success">
                <h4 class="text-success mb-2">Placement Confirmed 🎉</h4>
                <p class="text-light mb-3">Congratulations! You have accepted the offer, and your placement letter has been generated.</p>
                <button @click="downloadPlacementLetter" class="btn btn-success btn-sm px-3">Download Placement Letter</button>
            </div>

            <!-- Final State message -->
            <div v-if="isFinalState && application.status !== APPLICATION_STATUS.OFFER_ACCEPTED" class="mt-4 pt-3 border-top border-secondary text-muted text-center">
                This application is in a final state. No further actions can be taken.
            </div>
        </div>
    </div>
</template>
