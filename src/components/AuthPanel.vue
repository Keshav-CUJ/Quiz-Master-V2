<!-- src/components/AuthPanel.vue JWT token based auth -->
<template>
  <div class="container mt-5">
    <ul class="nav nav-tabs mb-3" role="tablist">
      <li class="nav-item" role="presentation">
        <button class="nav-link" :class="{active: activeTab === 'admin'}" @click="activeTab = 'admin'">Admin Login</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" :class="{active: activeTab === 'userLogin'}" @click="activeTab = 'userLogin'">User Login</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" :class="{active: activeTab === 'register'}" @click="activeTab = 'register'">User Register</button>
      </li>
    </ul>

    <div class="card p-4 shadow-sm" style="max-width: 500px; margin: auto">
      <!-- Admin Login -->
      <div v-if="activeTab === 'admin'">
        <h4>Admin Login</h4>
        <form @submit.prevent="loginAdmin">
          <input v-model="admin.username" type="text" class="form-control mb-2" placeholder="Username" required />
          <input v-model="admin.password" type="password" class="form-control mb-3" placeholder="Password" required />
          <button class="btn btn-primary w-100" type="submit">Login</button>
        </form>
        
        <div v-if="adminError" class="alert alert-danger mt-3">{{ adminError }}</div>
      </div>

      <!-- User Login -->
      <div v-if="activeTab === 'userLogin'">
        <h4>User Login</h4>
        <form @submit.prevent="loginUser">
          <input v-model="user.username" type="text" class="form-control mb-2" placeholder="Username" required />
          <input v-model="user.password" type="password" class="form-control mb-3" placeholder="Password" required />
          <button class="btn btn-success w-100" type="submit">Login</button>
        </form>
        <div v-if="userError" class="alert alert-danger mt-3">{{ userError }}</div>
      </div>

      <!-- User Register -->
      <div v-if="activeTab === 'register'">
        <h4>User Registration</h4>
        <form @submit.prevent="registerUser">
          <input v-model="reg.full_name" class="form-control mb-2" placeholder="Full Name" />
          <input v-model="reg.username" class="form-control mb-2" placeholder="Username" required />
          <input v-model="reg.password" type="password" class="form-control mb-2" placeholder="Password" required />
          <input v-model="reg.qualification" class="form-control mb-2" placeholder="Qualification" />
          <input v-model="reg.email" class="form-control mb-2" placeholder="Email" />
          <input v-model="reg.dob" type="date" class="form-control mb-3" placeholder="DOB" required />
          <button class="btn btn-warning w-100" type="submit">Register</button>
        </form>
        <div v-if="regSuccess" class="alert alert-success mt-3">🎉 Registered successfully</div>
        <div v-if="regError" class="alert alert-danger mt-3">{{ regError }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../axios'

const router = useRouter()
const activeTab = ref('admin')

// Admin login
const admin = ref({ username: '', password: '' })
const adminError = ref('')
const adminSuccess = ref(false)

const loginAdmin = async () => {
  adminError.value = ''
  try {
    const res = await api.post('/api/login/admin', admin.value)
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('role', 'admin')
    adminSuccess.value = true
    await router.push('/admin/dashboard')
  } catch (err) {
    adminError.value = err.response?.data?.message || 'Admin login failed'
  }
}

// User login
const user = ref({ username: '', password: '' })
const userError = ref('')
const userSuccess = ref(false)

const loginUser = async () => {
  userError.value = ''
  try {
    const res = await api.post('/api/login/user', user.value)
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('role', 'user')
    userSuccess.value = true
    await router.push('/user/dashboard')
  } catch (err) {
    userError.value = err.response?.data?.message || 'User login failed'
  }
}

// User registration
const reg = ref({ full_name: '', username: '', password: '', qualification: '', dob: '' })
const regError = ref('')
const regSuccess = ref(false)

const registerUser = async () => {
  regError.value = ''
  try {
    await api.post('/api/register', reg.value)
    regSuccess.value = true
  } catch (err) {
    regError.value = err.response?.data?.message || 'Registration failed'
  }
}
</script>
