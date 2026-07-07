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
    const interviewForm = ref({interview_date: '', interview_location: ''})
    const offerForm = ref({salary: '', joining_date: ''})
    const action = ref(null)
    const rejectFeedback = ref('')

    async function loadApplication() {
        try {
            application.value = (await api.get(`/company/application/${route.params.id}`)).data
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

    async function shortlist() {
        try {
            successMsg.value = (await api.patch(`/company/application/${application.value.id}`, {status: APPLICATION_STATUS.SHORTLISTED})).message
            await loadApplication()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to shortlist'
        }
    }

    async function scheduleInterview() {
        try {
            successMsg.value = (await api.patch(`/company/application/${application.value.id}/interview`, {interview_date: interviewForm.value.interview_date, interview_location: interviewForm.value.interview_location})).message
            action.value = null
            interviewForm.value = { interview_date: '', interview_location: '' }
            await loadApplication()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to schedule interview'
        }
    }

    async function releaseOffer() {
        try {
            successMsg.value = (await api.patch(`/company/application/${application.value.id}`, {status: APPLICATION_STATUS.OFFER_RELEASED, salary: parseInt(offerForm.value.salary), joining_date: offerForm.value.joining_date})).message
            action.value = null
            offerForm.value = { salary: '', joining_date: '' }
            await loadApplication()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to release offer'
        }
    }

    async function reject() {
        try {
            successMsg.value = (await api.patch(`/company/application/${application.value.id}`, {status: APPLICATION_STATUS.REJECTED, feedback: rejectFeedback.value || null})).message
            action.value = null
            rejectFeedback.value = ''
            await loadApplication()
            setTimeout(() => successMsg.value = null, 3000)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to reject'
        }
    }

    async function downloadOfferLetter() {
        try {
            const url = window.URL.createObjectURL(new Blob([(await api.get(`/company/application/${application.value.id}/offer-letter`, { responseType: 'blob' })).data]))
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
            const url = window.URL.createObjectURL(new Blob([(await api.get(`/company/placement/${application.value.student_id}/letter`, { responseType: 'blob' })).data]))
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

    async function downloadResume(studentId) {
        try {
            const url = window.URL.createObjectURL(new Blob([(await api.get(`/company/resume/${studentId}`, { responseType: 'blob' })).data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `resume_student_${studentId}.pdf`)
            document.body.appendChild(link)
            link.click()
            link.remove()
            window.URL.revokeObjectURL(url)
        }
        catch (err) {
            error.value = 'Failed to load resume/ Resume not uploaded'
        }
    }

    const canShortlist = computed(() => application.value?.status === APPLICATION_STATUS.APPLIED)
    const canScheduleInterview = computed(() => application.value?.status === APPLICATION_STATUS.SHORTLISTED)
    const canReleaseOffer = computed(() => application.value?.status === APPLICATION_STATUS.INTERVIEW_SCHEDULED)
    const canReject = computed(() => [APPLICATION_STATUS.APPLIED, APPLICATION_STATUS.SHORTLISTED, APPLICATION_STATUS.INTERVIEW_SCHEDULED].includes(application.value?.status))
    const isFinalState = computed(() => [APPLICATION_STATUS.REJECTED, APPLICATION_STATUS.OFFER_REJECTED].includes(application.value?.status))

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

        <button @click="router.push({name: 'company-dashboard'})" class="btn btn-secondary mb-3">Back to Dashboard</button>

        <div v-if="error" class="alert alert-danger">
            {{ error }}
            <button class="btn btn-danger" @click="logout">Try login again</button>
        </div>

        <div v-if="successMsg" class="alert alert-success">
            {{ successMsg }}
        </div>

        <div v-if="application">
            <p><strong>Status:</strong> {{ application.status }}</p>

            <h3 class="mt-3">Student Information</h3>
            <div class="row mt-3">
                <div class="col">
                    <p><strong>Name:</strong> {{ application.student_name }}</p>
                    <p><strong>Email:</strong> {{ application.student_email }}</p>
                    <p><strong>CGPA:</strong> {{ application.cgpa }}</p>
                </div>
                <div class="col">
                    <p><strong>Branch:</strong> {{ application.branch }}</p>
                    <p><strong>Skills:</strong> {{ application.skills || 'N/A' }}</p>
                    <button @click="downloadResume(application.student_id)" class="btn btn-primary">Download Resume</button>
                </div>
            </div>

            <h3 class="mt-5">Application Information</h3>
            <div class="row mt-3">
                <div class="col">
                    <p><strong>Job:</strong> {{ application.job_title }}</p>
                    <p><strong>Applied On:</strong> {{ formatDate(application.applied_at) }}</p>
                </div>
                <div class="col">
                    <p v-if="application.interview_date"><strong>Interview Date:</strong> {{ formatDateTime(application.interview_date) }}</p>
                    <p v-if="application.interview_location"><strong>Interview Location:</strong> {{ application.interview_location }}</p>
                    <p v-if="application.feedback"><strong>Feedback:</strong> {{ application.feedback }}</p>
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

            <div v-if="!isFinalState">
                <h3 class="mt-5">Actions</h3>

                <div v-if="canShortlist" class="mt-3">
                    <button @click="shortlist" class="btn btn-success">Shortlist</button>
                    <button @click="action = 'reject'" class="btn btn-danger">Reject</button>
                </div>

                <div v-if="canScheduleInterview" class="mt-3">
                    <div v-if="action !== 'interview'">
                        <button @click="action = 'interview'" class="btn btn-primary">Schedule Interview</button>
                        <button @click="action = 'reject'" class="btn btn-danger">Reject</button>
                    </div>
                    <div v-else class="mt-3">
                        <h4>Schedule Interview</h4>
                        <div class="row">
                            <div class="col mb-2">
                                <label>Date & Time</label>
                                <input v-model="interviewForm.interview_date" type="datetime-local" class="form-control" required>
                            </div>
                            <div class="col mb-2">
                                <label>Location</label>
                                <input v-model="interviewForm.interview_location" type="text" class="form-control" placeholder="Location/link for interview.." required>
                            </div>
                        </div>
                        <button @click="scheduleInterview" class="btn btn-success">Confirm</button>
                        <button @click="action = null" class="btn btn-secondary">Cancel</button>
                    </div>
                </div>

                <div v-if="canReleaseOffer" class="mt-3">
                    <div v-if="action !== 'offer'">
                        <button @click="action = 'offer'" class="btn btn-success">Release Offer</button>
                        <button @click="action = 'reject'" class="btn btn-danger">Reject</button>
                    </div>
                    <div v-else class="mt-3">
                        <h4>Release Offer</h4>
                        <div class="row">
                            <div class="col mb-2">
                                <label>Annual Salary INR</label>
                                <input v-model.number="offerForm.salary" type="number" min="1" class="form-control" required>
                            </div>
                            <div class="col mb-2">
                                <label>Joining Date</label>
                                <input v-model="offerForm.joining_date" type="date" class="form-control" required>
                            </div>
                        </div>
                        <button @click="releaseOffer" class="btn btn-success">Confirm Release</button>
                        <button @click="action = null" class="btn btn-secondary">Cancel</button>
                    </div>
                </div>

                <div v-if="application.status === APPLICATION_STATUS.OFFER_RELEASED" class="mt-3">
                    <p>Waiting for student to accept/reject the offer.</p>
                </div>

                <div v-if="application.status === APPLICATION_STATUS.OFFER_ACCEPTED" class="mt-3">
                    <p><strong>Student accepted the offer.</strong> Placement is created.</p>
                    <button @click="downloadPlacementLetter" class="btn btn-primary">Download Placement Letter</button>
                </div>

                <div v-if="action === 'reject' && canReject" class="mt-3">
                    <h4>Reject Application</h4>
                    <div class="mb-2">
                        <label>Feedback</label>
                        <textarea v-model="rejectFeedback" class="form-control" rows="2" placeholder="Reason for rejection.."></textarea>
                    </div>
                    <button @click="reject" class="btn btn-danger">Confirm Reject</button>
                    <button @click="action=null; rejectFeedback = ''" class="btn btn-secondary">Cancel</button>
                </div>
            </div>

            <div v-else class="mt-5">
                <p><strong>This application is in a final state.</strong> No further actions can be taken.</p>
            </div>
        </div>
    </div>
</template>
