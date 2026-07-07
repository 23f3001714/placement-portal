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
    <div class="text-center">
        <h1>Login Page</h1>
        <form class="form-group" @submit.prevent="login">
            <label for="email">Email:</label>
            <input type="email" v-model="email" placeholder="Email" id="email" class="form-control my-2" required/>
            <label for="password">Password:</label>
            <input type="password" v-model="password" placeholder="Password" id="password" class="form-control my-2" required/>
            <button type="submit" class="btn btn-primary">Login</button>
            <button class="btn btn-secondary" @click="router.push({name: 'home'})">Back</button>
        </form>
        <p v-if="error" class="text-danger mt-2">{{ error }}</p>
    </div>
</template>