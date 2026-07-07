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
  <div class="text-center">
    <h1>Company Registration</h1>

    <form class="form-group" @submit.prevent="register">
      <label for="name">Company Name:</label>
      <input type="text" v-model="name" placeholder="Company Name" id="name" class="form-control my-2" required/>
      <label for="email">Email:</label>
      <input type="email" v-model="email" placeholder="Email" id="email" class="form-control my-2" required/>
      <label for="password">Password:</label>
      <input type="password" v-model="password" placeholder="Password" id="password" class="form-control my-2" required/>
      <label for="hr_email">HR Email:</label>
      <input type="email" v-model="hr_email" placeholder="HR email" id="hr_email" class="form-control my-2" required/>
      <label for="industry">Industry:</label>
      <input type="text" v-model="industry" placeholder="Industry" id="industry" class="form-control my-2" required/>
      <label for="description">Description:</label>
      <input type="text" v-model="description" placeholder="Description" id="description" class="form-control my-2" required/>

      <button type="submit" class="btn btn-primary">Register</button>
      <button type="button" class="btn btn-secondary ms-2" @click="router.push({ name: 'home' })">Back</button>
    </form>

    <p v-if="error" class="text-danger mt-2">{{ error }}</p>
  </div>
</template>
