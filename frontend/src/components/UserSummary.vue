<template>
  <div class="container mt-5 text-center">
    <!-- Navigation Bar for user-->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">User Summary</a>
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/user/dashboard">Home</router-link>
          </li>
         
          <li class="nav-item">
            <router-link class="nav-link" to="/user/summary">Summary</router-link>
          </li>
          <li class="nav-item">
            <button class="nav-link" @click="logout">Logout</button>
          </li>
        </ul>
      </div>
    </nav>
  </div>
   <div class="container mt-4">
    <h2 class="text-center mb-4">User Quiz Summary</h2>

    <div class="row">
      <div class="col-md-6">
        <h4 class="text-center">Quizzes Attempted per Subject</h4>
        <Bar :data="quizCountData" :options="chartOptions" />
      </div>

      <div class="col-md-6">
        <h4 class="text-center">Top Scores per Subject</h4>
        <Bar :data="topScoresData" :options="chartOptions" />
      </div>
    </div>
  </div>

</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import { Bar } from 'vue-chartjs'
import api from '../axios'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const router = useRouter()


const quizCountData = ref({
  labels: [],
  datasets: []
})

const topScoresData = ref({
  labels: [],
  datasets: []
})

const chartOptions = {
  responsive: true,
  plugins: {
    legend: { position: 'top' },
    title: { display: false }
  }
}

const fetchSummaryData = async () => {
  try {
    const res = await api.get('/api/user/summary')
    const quizCount = res.data.quiz_count
    const topScores = res.data.top_scores

    quizCountData.value = {
      labels: quizCount.map(item => item.subject),
      datasets: [
        {
          label: 'Attempted Quizzes',
          data: quizCount.map(item => item.count),
          backgroundColor: '#42a5f5'
        }
      ]
    }

    topScoresData.value = {
      labels: topScores.map(item => item.subject),
      datasets: [
        {
          label: 'Top Score',
          data: topScores.map(item => item.score),
          backgroundColor: '#66bb6a'
        }
      ]
    }
  } catch (err) {
    console.error('❌ Error loading user summary:', err)
  }
}


const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('role')
  router.push('/')
}

onMounted(() => {
  fetchSummaryData()
})

</script>
