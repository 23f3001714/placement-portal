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
        <div class="text-center">
            <h1>Application Details</h1>
        </div>

        <div v-if="error" class="alert alert-danger">
            {{ error }}
            <button class="btn btn-danger" @click="logout">Try login again</button>
        </div>

        <div v-if="application">
            <div class="text-end mb-3">
                <button @click="router.push({ name: 'admin-dashboard' })" class="btn btn-dark">Back to Dashboard</button>
                <button @click="logout" class="btn btn-danger">Logout</button>
            </div>

            <p><strong>Student:</strong>
                <button @click="router.push({ name: 'student-details', params: { id: application.student_id } })" class="btn btn-link">{{ application.student_name }}</button>
                <button @click="downloadResume(application.student_id)" class="btn btn-primary">Download Resume</button>
            </p>
            <p><strong>Job:</strong>
                <button @click="router.push({ name: 'job-details', params: { id: application.job_id } })" class="btn btn-link">{{ application.job_title }} @ {{ application.company_name }}</button>
            </p>
            <p><strong>Application ID:</strong> {{ application.id }}</p>
            <p><strong>Current Status:</strong> {{ application.status }}</p>
            <p><strong>Applied Date:</strong> {{ formatDate(application.applied_at) }}</p>

            <div v-if="application.interview_date">
                <p><strong>Interview Date:</strong> {{ formatDateTime(application.interview_date) }}</p>
                <p v-if="application.interview_location"><strong>Interview Location:</strong> {{ application.interview_location }}</p>
            </div>

            <div v-if="application.salary">
                <h5 class="mt-3">Offer Details</h5>
                <p><strong>Salary:</strong> Rs. {{ application.salary?.toLocaleString() }}</p>
                <p><strong>Joining Date:</strong> {{ formatDate(application.joining_date) }}</p>
                <button v-if="application.offer_letter_path" @click="downloadOfferLetter" class="btn btn-primary">Download Offer Letter</button>
                <button v-if="application.status == 'offer_accepted'" @click="downloadPlacementLetter" class="btn btn-primary">Download Placement Letter</button>
            </div>

            <div v-if="application.feedback">
                <h5 class="mt-3">Feedback</h5>
                <p>{{ application.feedback }}</p>
            </div>
        </div>
    </div>
</template>
