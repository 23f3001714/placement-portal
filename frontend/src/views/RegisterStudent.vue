<script setup>
    import { ref } from 'vue'
    import { useRouter } from 'vue-router'
    import api from '../services/api'

    const router = useRouter()

    const name = ref('')
    const email = ref('')
    const password = ref('')
    const cgpa = ref('')
    const branch = ref('')
    const graduation_year = ref('')
    const error = ref(null)
            
    // lookup after this - make sure fields match
    const register = async () => {
        error.value = null
        try {
            const res = await api.post('/auth/register/student', {
                name: name.value,
                email: email.value,
                password: password.value,
                cgpa: cgpa.value,
                branch: branch.value,
                graduation_year: graduation_year.value
            })
            
            localStorage.setItem('token', res.data.access_token)
            localStorage.setItem('role', res.data.role)
            
            router.push({name: 'login'})
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Registration failed'
        }
    }

</script>

<template>
  <div class="d-flex align-items-center justify-content-center min-vh-100 p-3">
    <div class="glass-card w-100" style="max-width: 500px; border: 1px solid #333;">
      <div class="text-center mb-4">
        <h2 class="h3 mb-2 text-primary">Student Registration</h2>
        <p class="text-muted small">Enter your details to create a student account</p>
      </div>

      <form @submit.prevent="register">
        <div class="mb-3">
          <label for="name" class="form-label">Full Name</label>
          <input type="text" v-model="name" placeholder="Enter Full Name" id="name" class="form-control" required/>
        </div>

        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input type="email" v-model="email" placeholder="Enter Email" id="email" class="form-control" required/>
        </div>

        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input type="password" v-model="password" placeholder="Enter Password" id="password" class="form-control" required/>
        </div>

        <div class="row">
          <div class="col-md-6 mb-3">
            <label for="branch" class="form-label">Branch</label>
            <input type="text" v-model="branch" placeholder="Branch (e.g. CSE)" id="branch" class="form-control" required/>
          </div>
          <div class="col-md-3 mb-3">
            <label for="cgpa" class="form-label">CGPA</label>
            <input type="number" step="0.01" min="0" max="10" v-model="cgpa" placeholder="0.0" id="cgpa" class="form-control" required/>
          </div>
          <div class="col-md-3 mb-3">
            <label for="graduation_year" class="form-label">Grad Year</label>
            <input type="number" v-model="graduation_year" placeholder="Year" id="graduation_year" class="form-control" required/>
          </div>
        </div>

        <div class="d-flex justify-content-between mt-3">
          <button type="button" class="btn btn-secondary" @click="router.push({ name: 'home' })">Go Back</button>
          <button type="submit" class="btn btn-primary">Register</button>
        </div>
      </form>

      <div v-if="error" class="alert alert-danger mt-3 text-center py-2">{{ error }}</div>
    </div>
  </div>
</template>
