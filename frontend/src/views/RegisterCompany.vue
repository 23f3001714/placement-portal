<script setup>
    import { ref } from 'vue'
    import { useRouter } from 'vue-router'
    import api from '../services/api'

    const router = useRouter()

    const name = ref('')
    const email = ref('')
    const password = ref('')
    const hr_email = ref('')
    const industry = ref('')
    const description = ref('')
    const error = ref(null)

    // lookup after this - make sure fields match
    const register = async () => {
        error.value = null
        try {
            const res = await api.post('/auth/register/company', {
                name: name.value,
                email: email.value,
                password: password.value,
                hr_email: hr_email.value,
                industry: industry.value,
                description: description.value
            })
            
            localStorage.setItem('token', res.data.access_token)
            localStorage.setItem('role', res.data.role)
            
            router.push({name: 'login'})
        }
        catch (err) {
            error.value = err.response.data.error || 'Registration failed'
        }
    }

</script>

<template>
  <div class="d-flex align-items-center justify-content-center min-vh-100 p-3">
    <div class="glass-card w-100" style="max-width: 500px; border: 1px solid #333;">
      <div class="text-center mb-4">
        <h2 class="h3 mb-2 text-primary">Company Registration</h2>
        <p class="text-muted small">Enter details to register your company profile</p>
      </div>

      <form @submit.prevent="register">
        <div class="mb-3">
          <label for="name" class="form-label">Company Name</label>
          <input type="text" v-model="name" placeholder="Enter Company Name" id="name" class="form-control" required/>
        </div>

        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input type="email" v-model="email" placeholder="Enter Email" id="email" class="form-control" required/>
        </div>

        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input type="password" v-model="password" placeholder="Enter Password" id="password" class="form-control" required/>
        </div>

        <div class="mb-3">
          <label for="hr_email" class="form-label">HR Email</label>
          <input type="email" v-model="hr_email" placeholder="Enter HR Contact Email" id="hr_email" class="form-control" required/>
        </div>

        <div class="mb-3">
          <label for="industry" class="form-label">Industry</label>
          <input type="text" v-model="industry" placeholder="e.g. IT, Finance" id="industry" class="form-control" required/>
        </div>

        <div class="mb-3">
          <label for="description" class="form-label">Description</label>
          <textarea v-model="description" placeholder="Company Description" id="description" class="form-control" rows="2" required></textarea>
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
