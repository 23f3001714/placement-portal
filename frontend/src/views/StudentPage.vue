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
        <div class="text-center">
            <h1>Student Details</h1>
        </div>

        <div v-if="error" class="alert alert-danger">
            {{ error }}
            <button class="btn btn-danger" @click="logout">Try login again</button>
        </div>

        <div v-if="student">
            <div class="text-end mb-3">
                <button @click="router.push({ name: 'admin-dashboard' })" class="btn btn-dark">Back to Dashboard</button>
                <button @click="logout" class="btn btn-danger">Logout</button>
            </div>

            <h3>Student Profile</h3>
            <p><strong>ID:</strong> {{ student.id }}</p>
            <p><strong>Full Name:</strong> {{ student.name }}</p>
            <p><strong>Email:</strong> {{ student.email }}</p>
            <p><strong>Branch:</strong> {{ student.branch }}</p>
            <p><strong>Current CGPA:</strong> {{ student.cgpa }}</p>
            <p><strong>Graduation Year:</strong> {{ student.graduation_year }}</p>
            <p><strong>Skills:</strong> 
                <span v-if="student.skills">
                    {{ student.skills }}
                </span>
                <span v-else class="text-muted">No skills added</span>
            </p>
            <p><strong>Resume:</strong> 
                <button v-if="student.resume_path" @click="downloadResume(student.id)" class="btn btn-primary">Download Resume</button>
                <span v-else class="text-muted">No resume uploaded</span>
            </p>
            <p><strong>Status:</strong> 
                <span v-if="student.is_blacklisted">Blacklisted</span>
                <span v-else>Active</span>
            </p>
            <button @click="studentBlacklist(route.params.id, TOGGLE.TRUE)" class="btn btn-dark" :disabled="student.is_blacklisted">Blacklist</button>
            <button @click="studentBlacklist(route.params.id, TOGGLE.FALSE)" class="btn btn-light" :disabled="!student.is_blacklisted">Whitelist</button>

            <h3 class="mt-3">Placement Status</h3>
            <div v-if="student.placement">
                <p><strong>Current Status:</strong> <span>Placed</span></p>
                <p><strong>Company Name:</strong> {{ student.placement.company_name }}</p>
                <p><strong>Job Title:</strong> {{ student.placement.job_title }}</p>
                <p><strong>Package:</strong> ₹{{ student.placement.salary }}</p>
                <p v-if="student.placement.joining_date"><strong>Joining Date:</strong> {{ formatDate(student.placement.joining_date) }}</p>
            </div>
            <div v-else>
                <p><strong>Current Status:</strong> Unplaced</p>
            </div>

            <h3 class="mt-3">Applications History: {{ applications.length || 0 }}</h3>
            <div v-if="applications.length > 0">
                <table class="table text-center">
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
                        <tr v-for="application in applications">
                            <td>{{ application.id }}</td>
                            <td>{{ application.company_name }}</td>
                            <td>{{ application.job_title }}</td>
                            <td>{{ formatDate(application.applied_at) }}</td>
                            <td>{{ application.status }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <p v-else class="text-muted">No applications history</p>
        </div>
    </div>
</template>