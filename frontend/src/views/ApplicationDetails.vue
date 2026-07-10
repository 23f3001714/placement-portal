<script setup>
    import { ref, onMounted } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
    import api from '../services/api'
    import logout from '../services/logout'

    const router = useRouter()
    const route = useRoute()

    const application = ref(null)
    const error = ref(null)

    async function loadApplication(id) {
        try {
            application.value = (await api.get(`/admin/application/${id}`)).data
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to load application'
        }
    }

    async function downloadOfferLetter() {
        try {
            const url = window.URL.createObjectURL(new Blob([(await api.get(`/admin/application/${application.value.id}/offer-letter`, { responseType: 'blob' })).data]))
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
            const url = window.URL.createObjectURL(new Blob([(await api.get(`/admin/placement/${application.value.student_id}/letter`, { responseType: 'blob' })).data]))
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
            const url = window.URL.createObjectURL(new Blob([(await api.get(`/admin/student/${studentId}/resume`, { responseType: 'blob' })).data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `resume_student_${studentId}.pdf`)
            document.body.appendChild(link)
            link.click()
            link.remove()
            window.URL.revokeObjectURL(url)
        }
        catch (err) {
            error.value = 'Failed to load resume'
        }
    }

    function formatDate(dateStr) {
        if (!dateStr) return 'N/A'
        return new Date(dateStr).toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'})
    }

    function formatDateTime(dateStr) {
        if (!dateStr) return 'N/A'
        return new Date(dateStr).toLocaleString('en-GB', {day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'})
    }

    onMounted(async() => {
        await loadApplication(route.params.id)
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
        <button @click="router.push({ name: 'admin-dashboard' })" class="btn btn-secondary">Back to Dashboard</button>
        <button class="btn btn-danger" @click="logout">Logout</button>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger d-flex justify-content-between align-items-center mb-4">
      <span>{{ error }}</span>
      <button class="btn btn-danger btn-sm" @click="logout">Try login again</button>
    </div>

    <div v-if="application" class="glass-card" style="max-width: 800px; margin: 0 auto;">
      <h3 class="border-bottom border-secondary pb-2 mb-4 text-white">Application Information</h3>
      
      <div class="row mb-4">
        <div class="col-md-6 mb-3">
          <label class="form-label">Student Name</label>
          <div class="d-flex align-items-center gap-2">
            <button @click="router.push({ name: 'student-details', params: { id: application.student_id } })" class="btn btn-link text-info fw-bold p-0 border-0" style="text-decoration:none;">
              {{ application.student_name }}
            </button>
            <button @click="downloadResume(application.student_id)" class="btn btn-primary btn-sm ms-2">Download Resume</button>
          </div>
        </div>

        <div class="col-md-6 mb-3">
          <label class="form-label">Job Opening</label>
          <div>
            <button @click="router.push({ name: 'job-details', params: { id: application.job_id } })" class="btn btn-link text-info fw-bold p-0 border-0 text-start" style="text-decoration:none;">
              {{ application.job_title }} @ {{ application.company_name }}
            </button>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-md-4 mb-3">
          <label class="form-label">Application ID</label>
          <p class="text-white fw-bold">#{{ application.id }}</p>
        </div>
        <div class="col-md-4 mb-3">
          <label class="form-label">Current Status</label>
          <div>
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
        </div>
        <div class="col-md-4 mb-3">
          <label class="form-label">Applied Date</label>
          <p class="text-light">{{ formatDate(application.applied_at) }}</p>
        </div>
      </div>

      <!-- Interview Details -->
      <div v-if="application.interview_date" class="glass-panel mb-4">
        <h5 class="text-warning mb-3">Interview Details</h5>
        <div class="row">
          <div class="col-md-6 mb-2">
            <p class="mb-0"><strong>Schedule Time:</strong> <span class="text-light">{{ formatDateTime(application.interview_date) }}</span></p>
          </div>
          <div class="col-md-6 mb-2" v-if="application.interview_location">
            <p class="mb-0"><strong>Location / Link:</strong> <span class="text-light">{{ application.interview_location }}</span></p>
          </div>
        </div>
      </div>

      <!-- Offer Details -->
      <div v-if="application.salary" class="glass-panel mb-4 border border-success">
        <h5 class="text-success mb-3">Offer & Placement Package</h5>
        <div class="row mb-3">
          <div class="col-md-6 mb-2">
            <p class="mb-0"><strong>Salary Offered:</strong> <span class="text-light">Rs. {{ application.salary?.toLocaleString() }}</span></p>
          </div>
          <div class="col-md-6 mb-2">
            <p class="mb-0"><strong>Expected Joining Date:</strong> <span class="text-light">{{ formatDate(application.joining_date) }}</span></p>
          </div>
        </div>
        <div class="d-flex gap-2 flex-wrap">
          <button v-if="application.offer_letter_path" @click="downloadOfferLetter" class="btn btn-primary btn-sm">Download Offer Letter</button>
          <button v-if="application.status == 'offer_accepted'" @click="downloadPlacementLetter" class="btn btn-success btn-sm">Download Placement Letter</button>
        </div>
      </div>

      <!-- Feedback -->
      <div v-if="application.feedback" class="glass-panel mb-3">
        <h5 class="text-info mb-2">Feedback & Comments</h5>
        <p class="mb-0 text-light">{{ application.feedback }}</p>
      </div>
    </div>
  </div>
</template>
