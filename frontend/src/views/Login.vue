<script setup>
    import { ref } from 'vue'
    import { useRouter } from 'vue-router'
    import api from '../services/api'

    const router = useRouter()

    const email = ref('')
    const password = ref('')
    const error = ref(null)

    async function login () {
        try {
            const res = await api.post('/auth/login', {
                email: email.value,
                password: password.value
            })
            
            localStorage.setItem('token', res.data.access_token)
            localStorage.setItem('role', res.data.role)

            if (res.data.role === 'student') {
                router.push({name: 'student-dashboard'})
            }
            else if (res.data.role === 'company') {
                router.push({name: 'company-dashboard'})
            }
            else if (res.data.role === 'admin') {
                router.push({name: 'admin-dashboard'})
            }
            else {
                error.value = 'Invalid user role'
            }
        }
        catch (err) {
            error.value = err.response?.data?.error || 'Login failed'
        }
    }

</script>

<template>
  <div class="d-flex align-items-center justify-content-center min-vh-100 p-3">
    <div class="glass-card w-100" style="max-width: 400px; border: 1px solid #333;">
      <div class="text-center mb-4">
        <h2 class="h3 mb-2 text-primary">Placement Portal Login</h2>
        <p class="text-muted small">Enter your credentials to enter the application</p>
      </div>

      <form @submit.prevent="login">
        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input
            type="email"
            v-model="email"
            placeholder="Enter Email"
            id="email"
            class="form-control"
            required
          />
        </div>

        <div class="mb-4">
          <label for="password" class="form-label">Password</label>
          <input
            type="password"
            v-model="password"
            placeholder="Enter Password"
            id="password"
            class="form-control"
            required
          />
        </div>

        <div class="d-grid gap-2">
          <button type="submit" class="btn btn-primary">Login</button>
          <button
            type="button"
            class="btn btn-secondary btn-sm"
            @click="router.push({name: 'home'})"
          >
            Go Back
          </button>
        </div>
      </form>

      <div v-if="error" class="alert alert-danger mt-3 text-center py-2">
        {{ error }}
      </div>
    </div>
  </div>
</template>