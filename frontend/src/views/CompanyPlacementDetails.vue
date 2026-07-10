<script setup>
    import { ref, onMounted } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
    import api from '../services/api'

    const route = useRoute()
    const router = useRouter()

    const placement = ref(null)
    const error = ref(null)

    async function loadPlacement() {
        try {
            placement.value = (await api.get(`/company/placement/${route.params.id}`)).data
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to load placement'
        }
    }

    async function downloadPlacementLetter() {
        try {
            const url = window.URL.createObjectURL(new Blob([(await api.get(`/company/placement/${placement.value.id}/letter`, { responseType: 'blob' })).data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `placement_letter_${placement.value.id}.pdf`)
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

    onMounted(async () => {
        await loadPlacement()
    })
</script>

<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary">
      <div>
        <h1 class="gradient-text fw-bold mb-0">Placement Record</h1>
        <p class="text-muted mb-0" v-if="placement">Secured Campus Placement Details</p>
      </div>
      <div class="mt-3 mt-md-0 d-flex gap-2">
        <button @click="router.push({name: 'company-dashboard'})" class="btn btn-secondary">Back to Dashboard</button>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger mb-4">
      {{ error }}
    </div>

    <div v-if="placement" class="glass-card" style="max-width: 800px; margin: 0 auto;">
      <h3 class="border-bottom border-secondary pb-2 mb-4 text-success">Placement Details 🎉</h3>

      <!-- Student details panel -->
      <div class="glass-panel mb-4">
        <h5 class="text-white mb-3">Candidate Information</h5>
        <div class="row">
          <div class="col-md-6 mb-2">
            <p class="mb-2"><strong>Name:</strong> <span class="text-light">{{ placement.student_name }}</span></p>
            <p class="mb-2"><strong>Email:</strong> <span class="text-light">{{ placement.student_email }}</span></p>
          </div>
          <div class="col-md-6 mb-2 d-flex align-items-end">
            <button @click="downloadResume(placement.student_id)" class="btn btn-primary btn-sm px-3">Download Candidate Resume</button>
          </div>
        </div>
      </div>

      <!-- Job details panel -->
      <div class="glass-panel mb-4">
        <h5 class="text-white mb-3">Position Information</h5>
        <div class="row">
          <div class="col-md-12">
            <p class="mb-0"><strong>Job Title / Role:</strong> <span class="text-light fw-bold text-white">{{ placement.job_title }}</span></p>
          </div>
        </div>
      </div>

      <!-- Package and dates -->
      <div class="glass-panel mb-4 border border-success">
        <h5 class="text-success mb-3">Package & Schedule</h5>
        <div class="row">
          <div class="col-md-4 mb-2">
            <p class="mb-0"><strong>Salary (Annual):</strong> <span class="text-success fw-bold">Rs. {{ placement.salary?.toLocaleString() || 'N/A' }}</span></p>
          </div>
          <div class="col-md-4 mb-2">
            <p class="mb-0"><strong>Joining Date:</strong> <span class="text-light">{{ formatDate(placement.joining_date) }}</span></p>
          </div>
          <div class="col-md-4 mb-2">
            <p class="mb-0"><strong>Placed Date:</strong> <span class="text-light">{{ formatDateTime(placement.placed_at) }}</span></p>
          </div>
        </div>
      </div>

      <!-- Documents download section -->
      <div class="mt-4 pt-3 border-top border-secondary">
        <h5 class="text-white mb-3">Documents</h5>
        <div v-if="placement.placement_letter_path">
          <button @click="downloadPlacementLetter" class="btn btn-primary btn-sm py-2 px-3">Download Placement Letter</button>
        </div>
        <p v-else class="text-muted small">No placement letter has been generated for this record.</p>
      </div>

    </div>
  </div>
</template>
