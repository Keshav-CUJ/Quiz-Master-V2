<template>
  <div class="container mt-5 text-center">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">User Dashboard</a>
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
  <h2>Attempted Quizzes</h2>
  <table class="table table-bordered">
    <thead>
      <tr>
        <th>Quiz ID</th>
        <th>Subject</th>
        <th>Chapter</th>
        <th>Total Questions</th>
        <th>Score</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="quiz in attemptedQuizzes" :key="quiz.id">
        <td>{{ quiz.id }}</td>
        <td>{{ quiz.subject }}</td>
        <td>{{ quiz.chapter }}</td>
        <td>{{ quiz.total_questions }}</td>
        <td>{{ quiz.score }}</td>
      </tr>
    </tbody>
  </table>
</div>

    
    <!-- Monthly Report Export Section -->
<!-- Monthly Report Export Section -->
<div class="card p-5 container mt-4 shadow-sm">
  <h4>📁 Generate Monthly Report (CSV)</h4>
  <button
    class="btn btn-outline-primary"
    :disabled="exporting || attemptedQuizzes.length === 0"
    @click="triggerCSVExport"
  >
    {{ exporting ? 'Generating...' : 'Generate CSV' }}
  </button>

  <div v-if="csvReady" class="mt-3">
    <a :href="csvDownloadLink" class="btn btn-success" download>⬇ Download Report</a>
  </div>

  <div v-if="exportError" class="alert alert-danger mt-2">{{ exportError }}</div>

  <div v-if="attemptedQuizzes.length === 0 && !exporting" class="text-danger mt-2">
    ⚠️ You haven't attempted any quizzes yet.
  </div>
</div>

<!-- kind of filter -->
  <div class="container mt-4">
    <h2>Your Subjects</h2>
    <table class="table table-bordered">
      <thead>
        <tr>
          <th>ID</th>
          <th>Subject Name</th>
          <th>Description</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="subject in subjects" :key="subject.id">
          <td>{{ subject.id }}</td>
          <td>{{ subject.name }}</td>
          <td>{{ subject.description }}</td>
          <td>
            <button class="btn btn-sm btn-primary" @click="fetchChapters(subject.id)">View Chapters</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="chapters.length">
      <h2>Chapters</h2>
      <table class="table table-bordered">
        <thead>
          <tr>
            <th>ID</th>
            <th>Chapter Name</th>
            <th>Description</th>
            <th>Subject ID</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="chapter in chapters" :key="chapter.id">
            <td>{{ chapter.id }}</td>
            <td>{{ chapter.name }}</td>
            <td>{{ chapter.description }}</td>
            <td>{{ chapter.subject_id }}</td>
            <td>
              <button class="btn btn-sm btn-info" @click="fetchQuizzes(chapter.id)">View Quizzes</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="quizzes.length">
      <h2>Quizzes</h2>
      <table class="table table-bordered">
        <thead>
          <tr>
            <th>Quiz ID</th>
            <th>Chapter ID</th>
            <th>Date</th>
            <th>Time Duration</th>
            <th>Remarks</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="quiz in quizzes" :key="quiz.id">
            <td>{{ quiz.id }}</td>
            <td>{{ quiz.chapter_id }}</td>
            <td>{{ quiz.date_of_quiz }}</td>
            <td>{{ quiz.time_duration }}</td>
            <td>{{ quiz.remarks }}</td>
            <td>
              <button class="btn btn-sm btn-success" @click="attemptQuiz(quiz.id)">Attempt</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>


</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import api from '../axios'

const router = useRouter()
const subjects = ref([])
const chapters = ref([])
const quizzes = ref([])
const attemptedQuizzes = ref([])

const fetchAttemptedQuizzes = async () => {
  try {
    const res = await api.get('/api/user_attempted_quizzes')
    attemptedQuizzes.value = res.data.quizzes
  } catch (error) {
    console.error("Failed to fetch attempted quizzes:", error)
  }
}

const fetchSubjects = async () => {
  const res = await api.get('/api/subjects')
  subjects.value = res.data
}

const fetchChapters = async (subjectId) => {
  const res = await api.get(`/api/chapters/by_subject?subject_id=${subjectId}`)
  chapters.value = res.data
  quizzes.value = []
}

const fetchQuizzes = async (chapterId) => {
  const res = await api.get(`/api/quizzes/by_chapter?chapter_id=${chapterId}`)
  quizzes.value = res.data
}

const attemptQuiz = async (quizId) => {
  try {
    const res = await api.get(`/api/user/quiz/${quizId}`)
    if (res.data.attempted) {
      alert("You have already attempted this quiz!")
    } else {
      router.push({ path: `/user/quiz`, query: { quiz_id: res.data.quiz_id, duration: res.data.duration } })
    }
  } catch (err) {
    if (err.response && err.response.status === 403 && err.response.data.message) {
      alert(err.response.data.message)
    } else {
      alert("Something went wrong while starting the quiz.")
    }
  }
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('role')
  router.push('/')
}
// CSV Exporting 
const exporting = ref(false)
const csvReady = ref(false)
const exportError = ref('')
const csvDownloadLink = ref('')
const taskId = ref(null)

const triggerCSVExport = async () => {
  try {
    exporting.value = true
    csvReady.value = false
    exportError.value = ''

    const res = await api.post('/api/user/export-csv')
    taskId.value = res.data.task_id

    // Start polling for result
    pollExportStatus()
  } catch (err) {
    exportError.value = 'Failed to trigger export.'
    exporting.value = false
  }
}

const pollExportStatus = async () => {
  const interval = setInterval(async () => {
    try {
      const res = await api.get(`/api/user/export-status/${taskId.value}`)
      if (res.data.status === 'SUCCESS') {
        clearInterval(interval)
        const filename = res.data.download_url.split('/').pop();
        csvDownloadLink.value = `http://127.0.0.1:5000/download/${filename}`
        csvReady.value = true
        exporting.value = false
      } else if (res.data.status === 'FAILURE') {
        clearInterval(interval)
        exportError.value = 'Export failed.'
        exporting.value = false
      }
    } catch (err) {
      clearInterval(interval)
      exportError.value = 'Error checking export status.'
      exporting.value = false
    }
  }, 3000)
}

onMounted(() => {
  fetchSubjects()
  fetchAttemptedQuizzes()
})


</script>
