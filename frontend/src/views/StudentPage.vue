<script setup>
    import { ref, onMounted } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
    import api from '../services/api'
    import logout from '../services/logout'

    const router = useRouter()
    const route = useRoute()

    const student = ref(null)
    const applications = ref([])
    const error = ref(null)

    const TOGGLE = {
        TRUE: true,
        FALSE: false
    }

    async function loadStudent(id) {
        try {
            student.value = (await api.get(`/admin/student/${id}`)).data
            await loadStudentApplications(id)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Failed to load student'
        }
    }

    async function loadStudentApplications(id) {
        try {
            const response = (await api.get(`/admin/student/${id}/applications`)).data
            applications.value = response.applicationData || []
        }
        catch (err) {
            console.error('Failed to load applications:', err)
            applications.value = []
        }
    }

    async function studentBlacklist(id, status) {
        try {
            await api.patch(`/admin/student/${id}`, {is_blacklisted: status})
            await loadStudent(route.params.id)
        }
        catch (err) {
            error.value = err.response?.data?.error || 'failed to update student blacklist status'
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
        return new Date(dateStr).toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'})
    }

    onMounted(async() => {
        const id = route.params.id;
        await loadStudent(id)
    })
</script>

<template>
    <div class="container py-4">
        <!-- Header -->
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary">
            <div>
                <h1 class="gradient-text fw-bold mb-0">Student Profile</h1>
                <p class="text-muted mb-0" v-if="student">Admin Candidate Review</p>
            </div>
            <div class="mt-3 mt-md-0 d-flex gap-2">
                <button @click="router.push({ name: 'admin-dashboard' })" class="btn btn-secondary">Back to Dashboard</button>
                <button @click="logout" class="btn btn-danger">Logout</button>
            </div>
        </div>

        <div v-if="error" class="alert alert-danger d-flex justify-content-between align-items-center mb-4">
            <span>{{ error }}</span>
            <button class="btn btn-danger btn-sm" @click="logout">Try login again</button>
        </div>

        <div v-if="student" class="glass-card" style="max-width: 900px; margin: 0 auto;">
            <h3 class="border-bottom border-secondary pb-2 mb-4 text-white">Student Information</h3>

            <div class="row mb-4">
                <div class="col-md-6 mb-3">
                    <p class="mb-2"><strong>Roll Number (Student ID):</strong> <span class="text-light ms-2">#{{ student.id }}</span></p>
                    <p class="mb-2"><strong>Full Name:</strong> <span class="text-light ms-2 text-white fw-bold">{{ student.name }}</span></p>
                    <p class="mb-2"><strong>Email Address:</strong> <span class="text-light ms-2">{{ student.email }}</span></p>
                    <p class="mb-2"><strong>Current CGPA:</strong> <span class="text-light ms-2 fw-bold text-white">{{ student.cgpa }}</span></p>
                </div>
                <div class="col-md-6 mb-3">
                    <p class="mb-2"><strong>Academic Branch:</strong> <span class="text-light ms-2">{{ student.branch }}</span></p>
                    <p class="mb-2"><strong>Graduation Year:</strong> <span class="text-light ms-2">{{ student.graduation_year }}</span></p>
                    <p class="mb-2"><strong>Key Skills:</strong> 
                        <span v-if="student.skills" class="text-light ms-2">{{ student.skills }}</span>
                        <span v-else class="text-muted ms-2 italic">No skills added</span>
                    </p>
                    <p class="mb-2"><strong>Resume Document:</strong> 
                        <button v-if="student.resume_path" @click="downloadResume(student.id)" class="btn btn-primary btn-sm ms-2">Download Resume</button>
                        <span v-else class="text-muted ms-2 italic">No resume uploaded</span>
                    </p>
                </div>
            </div>

            <!-- Blacklist / Whitelist Panel -->
            <div class="glass-panel mb-4">
                <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center">
                    <div>
                        <h5 class="text-white mb-1">Administrative Status</h5>
                        <p class="text-muted small mb-0">Blacklisted students are restricted from applying to active jobs.</p>
                    </div>
                    <div class="mt-2 mt-md-0 d-flex align-items-center gap-3">
                        <span :class="student.is_blacklisted ? 'badge-custom badge-danger' : 'badge-custom badge-success'">
                            {{ student.is_blacklisted ? 'Blacklisted' : 'Active / Approved' }}
                        </span>
                        <div class="d-flex gap-1">
                            <button @click="studentBlacklist(route.params.id, TOGGLE.TRUE)" class="btn btn-danger btn-sm" :disabled="student.is_blacklisted">Blacklist</button>
                            <button @click="studentBlacklist(route.params.id, TOGGLE.FALSE)" class="btn btn-success btn-sm" :disabled="!student.is_blacklisted">Whitelist</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Placement Status Panel -->
            <div class="glass-panel mb-4" :class="student.placement ? 'border border-success bg-opacity-10 bg-success' : ''">
                <h5 class="text-white mb-3">Placement Status</h5>
                <div v-if="student.placement">
                    <p class="mb-2"><strong class="text-success">Current Status:</strong> <span class="badge-custom badge-success ms-2">Placed 🎉</span></p>
                    <p class="mb-2"><strong>Company Name:</strong> <span class="text-light ms-2">{{ student.placement.company_name }}</span></p>
                    <p class="mb-2"><strong>Job Title:</strong> <span class="text-light ms-2">{{ student.placement.job_title }}</span></p>
                    <p class="mb-2"><strong>Annual Package:</strong> <span class="text-light ms-2">₹{{ student.placement.salary?.toLocaleString() }}</span></p>
                    <p class="mb-0" v-if="student.placement.joining_date"><strong>Joining Date:</strong> <span class="text-light ms-2">{{ formatDate(student.placement.joining_date) }}</span></p>
                </div>
                <div v-else>
                    <p class="mb-0"><strong>Current Status:</strong> <span class="badge-custom badge-danger ms-2">Unplaced</span></p>
                </div>
            </div>

            <!-- Applications History -->
            <div class="mt-4 pt-3 border-top border-secondary">
                <h4 class="text-white mb-3">Applications History ({{ applications.length || 0 }})</h4>
                
                <div v-if="applications.length > 0" class="custom-table-container">
                    <table class="table text-center table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Company Name</th>
                                <th>Job Title</th>
                                <th>Date Applied</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="application in applications" :key="application.id">
                                <td>{{ application.id }}</td>
                                <td class="fw-bold text-white">{{ application.company_name }}</td>
                                <td>{{ application.job_title }}</td>
                                <td class="text-warning">{{ formatDate(application.applied_at) }}</td>
                                <td>
                                    <span :class="{
                                        'badge-custom badge-applied': application.status === 'applied',
                                        'badge-custom badge-shortlisted': application.status === 'shortlisted',
                                        'badge-custom badge-interview': application.status === 'interview_scheduled',
                                        'badge-custom badge-success': application.status === 'offer_released' || application.status === 'offer_accepted',
                                        'badge-custom badge-danger': application.status === 'rejected' || application.status === 'offer_rejected'
                                    }">{{ application.status }}</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <p v-else class="text-muted py-3 text-center">No applications history found for this student.</p>
            </div>
        </div>
    </div>
</template>