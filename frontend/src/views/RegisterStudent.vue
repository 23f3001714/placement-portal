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
  <div class="text-center">
    <h1>Student Registration</h1>

    <form class="form-group" @submit.prevent="register">
      <label for="name">Name:</label>
      <input type="text" v-model="name" placeholder="Full Name" id="name" class="form-control my-2" required/>
      <label for="email">Email:</label>
      <input type="email" v-model="email" placeholder="Email" id="email" class="form-control my-2" required/>
      <label for="password">Password:</label>
      <input type="password" v-model="password" placeholder="Password" id="password" class="form-control my-2" required/>
      <label for="cgpa">CGPA:</label>
      <input type="number" step="0.01" v-model="cgpa" placeholder="CGPA" id="cgpa" class="form-control my-2" required/>
      <label for="branch">Branch:</label>
      <input type="text" v-model="branch" placeholder="Branch" id="branch" class="form-control my-2" required/>
      <label for="graduation_year">Graduation Year:</label>
      <input type="number" v-model="graduation_year" placeholder="Graduation Year" id="graduation_year" class="form-control my-2" required/>
      <button type="submit" class="btn btn-primary">Register</button>
      <button type="button" class="btn btn-secondary ms-2" @click="router.push({ name: 'home' })">Back</button>
    </form>

    <p v-if="error" class="text-danger mt-2">{{ error }}</p>
  </div>
</template>
