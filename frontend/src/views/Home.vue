<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="home-page d-flex align-items-center justify-content-center min-vh-100 p-4">
    <div class="glass-card text-center w-100" style="max-width: 800px; border: 1px solid #333;">
      <h1 class="display-5 fw-bold mb-3 text-white">
        Placement Portal Application
      </h1>

      <p class="lead text-light mb-4" style="max-width: 600px; margin: 0 auto 30px auto;">
        An efficient system to manage campus recruitment activities involving companies, students and the placement cell.
      </p>

      <div class="button-group mb-4">
        <button
          class="btn btn-primary action-btn"
          @click="router.push('/login')"
        >
          Login
        </button>

        <button
          class="btn btn-success action-btn"
          @click="router.push('/register/student')"
        >
          Register Student
        </button>

        <button
          class="btn btn-warning action-btn text-white"
          @click="router.push('/register/company')"
        >
          Register Company
        </button>
      </div>

      <div class="image-container mt-4 mb-4">
        <img
          src="/tempo_placement.jpeg"
          class="hero-image"
          alt="Placement Drive"
        />
      </div>

      <hr class="my-4 rgba-white-divider"/>

      <p class="text-muted small">
        Support Contact: 
        <a href="mailto:potato05jk@gmail.com" class="mail-link">
          potato05jk@gmail.com
        </a>
      </p>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.button-group {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 20px;
}

.action-btn {
  min-width: 220px;
  padding: 14px 28px;
}

.image-container {
  display: flex;
  justify-content: center;
}

.hero-image {
  width: 100%;
  max-width: 750px;
  border-radius: 16px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: transform .4s ease;
}

.hero-image:hover {
  transform: scale(1.015);
}

.rgba-white-divider {
  border-color: rgba(255, 255, 255, 0.1);
  opacity: 1;
}

.mail-link {
  color: #818cf8;
  text-decoration: none;
  font-weight: bold;
  transition: color 0.2s ease;
}

.mail-link:hover {
  color: #a5b4fc;
  text-decoration: underline;
}
</style>