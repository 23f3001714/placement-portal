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
        <div class="text-center">
            <h1>Placement Details</h1>
        </div>

        <button @click="router.push({name: 'company-dashboard'})" class="btn btn-secondary mb-3">Back to Dashboard</button>

        <div v-if="error" class="alert alert-danger">
            {{ error }}
        </div>

        <div v-if="placement">
            <h3 class="mt-3">Student Information</h3>
            <div class="row mt-3">
                <div class="col-6">
                    <p><strong>Name:</strong> {{ placement.student_name }}</p>
                    <p><strong>Email:</strong> {{ placement.student_email }}</p>
                    <button @click="downloadResume(placement.student_id)" class="btn btn-primary">Download Resume</button>
                </div>
            </div>

            <h3 class="mt-5">Job Information</h3>
            <div class="row mt-3">
                <div class="col-6">
                    <p><strong>Position:</strong> {{ placement.job_title }}</p>
                </div>
            </div>

            <h3 class="mt-5">Placement Details</h3>
            <div class="row mt-3">
                <div class="col-4">
                    <p><strong>Salary:</strong> Rs. {{ placement.salary?.toLocaleString() || 'N/A' }}</p>
                </div>
                <div class="col-4">
                    <p><strong>Joining Date:</strong> {{ formatDate(placement.joining_date) }}</p>
                </div>
                <div class="col-4">
                    <p><strong>Placed On:</strong> {{ formatDateTime(placement.placed_at) }}</p>
                </div>
            </div>

            <h3 class="mt-5">Documents</h3>
            <div class="mt-3">
                <button v-if="placement.placement_letter_path" @click="downloadPlacementLetter" class="btn btn-primary">Download Placement Letter</button>
                <p v-else>No placement letter available.</p>
            </div>
        </div>
    </div>
</template>
