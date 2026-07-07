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
        <div class="text-center">
            <h1>Application Details</h1>
        </div>

        <button @click="router.push({name: 'student-dashboard'})" class="btn btn-secondary mb-3">Back to Dashboard</button>

        <div v-if="error" class="alert alert-danger">
            {{ error }}
            <button class="btn btn-danger" @click="logout">Try login again</button>
        </div>

        <div v-if="successMsg" class="alert alert-success">
            {{ successMsg }}
        </div>

        <div v-if="application">
            <p><strong>Status:</strong> {{ application.status }}</p>

            <h3 class="mt-3">Job Information</h3>
            <div class="row mt-3">
                <div class="col">
                    <p><strong>Job Title:</strong> {{ application.job_title }}</p>
                    <p><strong>Company:</strong> {{ application.company_name }}</p>
                </div>
                <div class="col">
                    <p><strong>Applied On:</strong> {{ formatDate(application.applied_at) }}</p>
                </div>
                <p><strong>Description:</strong> {{ application.description }}</p>
            </div>

            <div v-if="application.interview_date || application.interview_location">
                <h3 class="mt-5">Interview Details</h3>
                <div class="row mt-3">
                    <div class="col">
                        <p v-if="application.interview_date"><strong>Interview Date:</strong> {{ formatDateTime(application.interview_date) }}</p>
                    </div>
                    <div class="col">
                        <p v-if="application.interview_location"><strong>Interview Location:</strong> {{ application.interview_location }}</p>
                    </div>
                </div>
            </div>

            <div v-if="application.salary">
                <h3 class="mt-5">Offer Details</h3>
                <div class="row mt-3">
                    <div class="col">
                        <p><strong>Salary:</strong> Rs. {{ application.salary?.toLocaleString() }}</p>
                    </div>
                    <div class="col">
                        <p><strong>Joining Date:</strong> {{ formatDate(application.joining_date) }}</p>
                    </div>
                </div>
                <button v-if="application.offer_letter_path" @click="downloadOfferLetter" class="btn btn-primary">Download Offer Letter</button>
            </div>

            <div v-if="application.feedback">
                <h3 class="mt-5">Feedback</h3>
                <p>{{ application.feedback }}</p>
            </div>

            <div v-if="canAcceptReject && !action">
                <h3 class="mt-5">Actions</h3>
                <div class="mt-3">
                    <button @click="action = 'accept'" class="btn btn-success">Accept Offer</button>
                    <button @click="action = 'reject'" class="btn btn-danger">Reject Offer</button>
                </div>
            </div>

            <div v-if="action === 'accept'" class="mt-3">
                <h4>Confirm Accept Offer</h4>
                <p>Warning: Accepting this offer will automatically reject all your other pending applications.</p>
                <p>Are you sure you want to accept this offer?</p>
                <button @click="acceptOffer" class="btn btn-success">Confirm Accept</button>
                <button @click="action = null" class="btn btn-secondary">Cancel</button>
            </div>

            <div v-if="action === 'reject'" class="mt-3">
                <h4>Confirm Reject Offer</h4>
                <p>Are you sure you want to reject this offer?</p>
                <button @click="rejectOffer" class="btn btn-danger">Confirm Reject</button>
                <button @click="action = null" class="btn btn-secondary">Cancel</button>
            </div>

            <div v-if="application.status === APPLICATION_STATUS.OFFER_ACCEPTED">
                <h3 class="mt-5">Placement Confirmed</h3>
                <p><strong>Congratulations! You have accepted the offer and placement has been created.</strong></p>
                <button @click="downloadPlacementLetter" class="btn btn-primary">Download Placement Letter</button>
            </div>

            <div v-if="isFinalState && application.status !== APPLICATION_STATUS.OFFER_ACCEPTED" class="mt-5">
                <p><strong>This application is in a final state.</strong> No further actions can be taken.</p>
            </div>
        </div>
    </div>
</template>
