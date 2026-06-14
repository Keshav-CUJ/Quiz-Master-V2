<template>
  <div class="container mt-5">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Admin Summary</a>
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/dashboard">Home</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/quizzes">Quizzes</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/summary">Summary</router-link>
          </li>
          <li class="nav-item">
            <button class="nav-link" @click="logout">Logout</button>
          </li>
        </ul>
      </div>
    </nav>
    
    
     <div class="container mt-5">
    <h2 class="text-center mb-4">Admin Summary</h2>

    <div class="row">
      <!-- Top Scores Chart -->
      <div class="col-md-6 mb-4" v-if="topScoresLoaded">
        <Bar :data="topScoresChartData" :options="chartOptions" />
      </div>

      <!-- User Attempts Chart -->
      <div class="col-md-6 mb-4" v-if="userAttemptsLoaded">
        <Bar :data="userAttemptsChartData" :options="chartOptions" />
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Bar } from 'vue-chartjs'
import { useRouter } from 'vue-router'

import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'
import api from '../axios'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)
const router = useRouter()
const topScoresLoaded = ref(false)
const userAttemptsLoaded = ref(false)

const topScoresChartData = ref({
  labels: [],
  datasets: []
})

const userAttemptsChartData = ref({
  labels: [],
  datasets: []
})

const chartOptions = {
  responsive: true,
  plugins: {
    legend: {
      display: true
    },
    title: {
      display: true,
      text: ''
    }
  }
}

const fetchData = async () => {
  const res = await api.get('/api/admin/summary')

  // ✅ Top Scores
  const topScores = res.data.top_scores || []
  topScoresChartData.value = {
    labels: topScores.map(item => item.subject),
    datasets: [
      {
        label: 'Top Score',
        backgroundColor: '#4caf50',
        data: topScores.map(item => item.score)
      }
    ]
  }
  topScoresLoaded.value = true

  // ✅ User Attempts
  const attempts = res.data.user_attempts || []
  userAttemptsChartData.value = {
    labels: attempts.map(item => item.subject),
    datasets: [
      {
        label: 'Unique User Attempts',
        backgroundColor: '#2196f3',
        data: attempts.map(item => item.attempts)
      }
    ]
  }
  userAttemptsLoaded.value = true
}


const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('role')
  router.replace('/')
}

onMounted(() => {
  fetchData()
})
</script>


