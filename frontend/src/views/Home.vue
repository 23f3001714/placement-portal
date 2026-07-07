<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="home-page">
    <div class="overlay">
      <div class="hero-card">

        <h1 class="display-3 fw-bold mb-3">
          Campus Placement Portal
        </h1>

        <p class="lead text-light mb-5">
          Welcome to the official placement portal, please register/login.
        </p>

        <div class="button-group">
          <button
            class="btn btn-primary btn-lg action-btn"
            @click="router.push('/login')"
          >
            Login
          </button>

          <button
            class="btn btn-success btn-lg action-btn"
            @click="router.push('/register/student')"
          >
            Register as Student
          </button>

          <button
            class="btn btn-warning btn-lg action-btn"
            @click="router.push('/register/company')"
          >
            Register as Company
          </button>
        </div>

        <div class="image-container mt-5">
          <img
            src="/tempo_placement.jpeg"
            class="hero-image"
            alt="Campus Placement Portal"
          />
        </div>

        <hr class="my-4 text-light"/>

        <p class="text-light small">
          Need help?
          <a href="mailto:admin@mail.com" class="mail-link">
            admin@mail.com
          </a>
        </p>

      </div>
    </div>
  </div>
</template>

<style scoped>

.home-page{
    min-height:100vh;
    background:linear-gradient(135deg,#0f172a,#1e3a8a,#2563eb);
    display:flex;
    justify-content:center;
    align-items:center;
    padding:40px;
}

.overlay{
    width:100%;
    display:flex;
    justify-content:center;
}

.hero-card{
    max-width:1200px;
    width:100%;
    background:rgba(255,255,255,0.12);
    backdrop-filter:blur(12px);
    border-radius:24px;
    padding:50px;
    text-align:center;
    color:white;
    box-shadow:0 20px 40px rgba(0,0,0,0.35);
}

.button-group{
    display:flex;
    justify-content:center;
    flex-wrap:wrap;
    gap:20px;
}

.action-btn{
    min-width:220px;
    padding:14px 28px;
    border-radius:40px;
    font-size:18px;
    font-weight:600;
    transition:all .3s ease;
}

.action-btn:hover{
    transform:translateY(-5px);
    box-shadow:0 10px 20px rgba(0,0,0,.3);
}

.image-container{
    display:flex;
    justify-content:center;
}

.hero-image{
    width:100%;
    max-width:900px;
    border-radius:20px;
    box-shadow:0 20px 40px rgba(0,0,0,.35);
    transition:transform .4s ease;
}

.hero-image:hover{
    transform:scale(1.02);
}

.mail-link{
    color:#ffd43b;
    text-decoration:none;
    font-weight:bold;
}

.mail-link:hover{
    text-decoration:underline;
}

</style>