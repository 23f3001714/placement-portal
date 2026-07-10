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
    <!-- Header -->
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary">
      <div>
        <h1 class="gradient-text fw-bold mb-0">Application Details</h1>
        <p class="text-muted mb-0" v-if="application">Candidate Application Profile</p>
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

    <div v-if="application" class="glass-card" style="max-width: 850px; margin: 0 auto;">
      
      <!-- Top header / status info -->
      <div class="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary">
        <h3 class="mb-0 text-white">Application Status</h3>
        <span :class="{
          'badge-custom badge-applied': application.status === 'applied',
          'badge-custom badge-shortlisted': application.status === 'shortlisted',
          'badge-custom badge-interview': application.status === 'interview_scheduled',
          'badge-custom badge-success': application.status === 'offer_released' || application.status === 'offer_accepted',
          'badge-custom badge-danger': application.status === 'rejected' || application.status === 'offer_rejected'
        }">
          {{ application.status }}
        </span>
      </div>

      <!-- Student Details -->
      <div class="glass-panel mb-4">
        <h4 class="mb-3 text-info">Student Profile</h4>
        <div class="row">
          <div class="col-md-6 mb-2">
            <p class="mb-2"><strong>Name:</strong> <span class="text-light">{{ application.student_name }}</span></p>
            <p class="mb-2"><strong>Email:</strong> <span class="text-light">{{ application.student_email }}</span></p>
            <p class="mb-2"><strong>CGPA:</strong> <span class="text-light">{{ application.cgpa }}</span></p>
          </div>
          <div class="col-md-6 mb-2">
            <p class="mb-2"><strong>Branch:</strong> <span class="text-light">{{ application.branch }}</span></p>
            <p class="mb-2"><strong>Skills:</strong> <span class="text-light">{{ application.skills || 'N/A' }}</span></p>
            <p class="mb-0 mt-3 d-flex align-items-center">
              <button @click="downloadResume(application.student_id)" class="btn btn-primary btn-sm py-1 px-3">Download Resume</button>
            </p>
          </div>
        </div>
      </div>

      <!-- Application Info -->
      <div class="glass-panel mb-4">
        <h4 class="mb-3 text-info">Application Info</h4>
        <div class="row">
          <div class="col-md-6 mb-2">
            <p class="mb-2"><strong>Job Title:</strong> <span class="text-light">{{ application.job_title }}</span></p>
            <p class="mb-2"><strong>Applied On:</strong> <span class="text-light">{{ formatDate(application.applied_at) }}</span></p>
          </div>
          <div class="col-md-6 mb-2">
            <p class="mb-2" v-if="application.interview_date"><strong>Interview Schedule:</strong> <span class="text-light text-warning">{{ formatDateTime(application.interview_date) }}</span></p>
            <p class="mb-2" v-if="application.interview_location"><strong>Interview Venue:</strong> <span class="text-light">{{ application.interview_location }}</span></p>
            <p class="mb-2" v-if="application.feedback"><strong>Feedback Notes:</strong> <span class="text-light">{{ application.feedback }}</span></p>
          </div>
        </div>
      </div>

      <!-- Offer Details -->
      <div v-if="application.salary" class="glass-panel mb-4 border border-success">
        <h4 class="mb-3 text-success">Offer Information</h4>
        <div class="row mb-3">
          <div class="col-md-6 mb-2">
            <p class="mb-0"><strong>Offered Package:</strong> <span class="text-light">Rs. {{ application.salary?.toLocaleString() }}</span></p>
          </div>
          <div class="col-md-6 mb-2">
            <p class="mb-0"><strong>Joining Date:</strong> <span class="text-light">{{ formatDate(application.joining_date) }}</span></p>
          </div>
        </div>
        <button v-if="application.offer_letter_path" @click="downloadOfferLetter" class="btn btn-primary btn-sm">Download Offer Letter</button>
      </div>

      <!-- Actions -->
      <div v-if="!isFinalState" class="mt-4 pt-3 border-top border-secondary">
        <h4 class="mb-3 text-white">Application Operations</h4>

        <!-- Applied status actions -->
        <div v-if="canShortlist" class="d-flex gap-2">
          <button @click="shortlist" class="btn btn-success">Shortlist Candidate</button>
          <button @click="action = 'reject'" class="btn btn-danger">Reject Application</button>
        </div>

        <!-- Shortlisted actions -->
        <div v-if="canScheduleInterview">
          <div v-if="action !== 'interview'" class="d-flex gap-2">
            <button @click="action = 'interview'" class="btn btn-primary">Schedule Interview</button>
            <button @click="action = 'reject'" class="btn btn-danger">Reject Application</button>
          </div>
          <div class="glass-panel mt-3" v-else>
            <h5 class="mb-3 text-white">Schedule Interview</h5>
            <div class="row mb-3">
              <div class="col-md-6 mb-2">
                <label class="form-label">Interview Date & Time</label>
                <input v-model="interviewForm.interview_date" type="datetime-local" class="form-control" required>
              </div>
              <div class="col-md-6 mb-2">
                <label class="form-label">Location / Online Link</label>
                <input v-model="interviewForm.interview_location" type="text" class="form-control" placeholder="e.g. Google Meet Link" required>
              </div>
            </div>
            <div class="d-flex gap-2">
              <button @click="scheduleInterview" class="btn btn-success">Save Schedule</button>
              <button @click="action = null" class="btn btn-secondary">Cancel</button>
            </div>
          </div>
        </div>

        <!-- Interview Scheduled actions -->
        <div v-if="canReleaseOffer">
          <div v-if="action !== 'offer'" class="d-flex gap-2">
            <button @click="action = 'offer'" class="btn btn-success">Release Offer Letter</button>
            <button @click="action = 'reject'" class="btn btn-danger">Reject Application</button>
          </div>
          <div class="glass-panel mt-3 border border-success" v-else>
            <h5 class="mb-3 text-success">Release Offer Details</h5>
            <div class="row mb-3">
              <div class="col-md-6 mb-2">
                <label class="form-label">Annual Salary (INR)</label>
                <input v-model.number="offerForm.salary" type="number" min="1" class="form-control" placeholder="e.g. 1200000" required>
              </div>
              <div class="col-md-6 mb-2">
                <label class="form-label">Joining Date</label>
                <input v-model="offerForm.joining_date" type="date" class="form-control" required>
              </div>
            </div>
            <div class="d-flex gap-2">
              <button @click="releaseOffer" class="btn btn-success">Generate & Release Offer</button>
              <button @click="action = null" class="btn btn-secondary">Cancel</button>
            </div>
          </div>
        </div>

        <!-- Offer Released waiting text -->
        <div v-if="application.status === APPLICATION_STATUS.OFFER_RELEASED" class="alert alert-info py-2">
          Waiting for the student to accept or reject the released offer.
        </div>

        <!-- Offer Accepted placed status -->
        <div v-if="application.status === APPLICATION_STATUS.OFFER_ACCEPTED" class="alert alert-success py-3">
          <p class="mb-2"><strong>The student has accepted your offer!</strong> The candidate has been marked as placed.</p>
          <button @click="downloadPlacementLetter" class="btn btn-success btn-sm">Download Placement Letter</button>
        </div>

        <!-- Reject feedback block -->
        <div v-if="action === 'reject' && canReject" class="glass-panel mt-3 border border-danger">
          <h5 class="mb-3 text-danger">Reject Candidate</h5>
          <div class="mb-3">
            <label class="form-label">Rejection Feedback / Reason</label>
            <textarea v-model="rejectFeedback" class="form-control" rows="2" placeholder="Write feedback for the student..."></textarea>
          </div>
          <div class="d-flex gap-2">
            <button @click="reject" class="btn btn-danger">Confirm Rejection</button>
            <button @click="action=null; rejectFeedback = ''" class="btn btn-secondary">Cancel</button>
          </div>
        </div>
      </div>

      <div v-else class="mt-4 pt-3 border-top border-secondary text-muted text-center">
        This application has reached a final state (Rejected or Offer Rejected). No further actions can be taken.
      </div>

    </div>
  </div>
</template>
