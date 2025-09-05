<template>
  <div class="container mt-4">
    <div class="text-center mb-4">
      <h2 class="mb-2">Quiz Panel</h2>
      <p> <strong>Quiz ID:</strong> {{ quizId }}</p>
    </div>
    <!-- attempt quiz -->
    <!-- Timer Display -->
    <div class="text-end mb-3">
      <strong>Time Left:</strong> {{ formattedTime }}
    </div>

    <!-- Question Panel -->
    <div v-if="currentQuestion">
      <h5 class="mb-3">Q{{ currentIndex + 1 }}. {{ currentQuestion.question_statement }}</h5>
      <div class="form-check mb-2" v-for="(option, idx) in options" :key="idx">
        <input
          class="form-check-input"
          type="radio"
          :id="`option${idx}`"
          :value="idx + 1"
          :checked="userAnswers[currentQuestion.id] === idx + 1"
          @change="selectOption(currentQuestion.id, idx + 1)"
        >
        <label class="form-check-label" :for="`option${idx}`">{{ option }}</label>
      </div>

      <!-- Response Buttons -->
      <div class="mt-3">
        <button class="btn btn-outline-danger me-2" @click="clearResponse">Clear Response</button>
        <button class="btn btn-outline-warning" @click="markForReview" :disabled="userAnswers[currentQuestion.id] === -1">Mark for Review</button>
      </div>
    </div>

    <!-- Navigation Buttons -->
    <div class="mt-4">
      <button class="btn btn-secondary me-2" @click="prevQuestion" :disabled="currentIndex === 0">Previous</button>
      <button class="btn btn-primary me-2" @click="nextQuestion" :disabled="currentIndex === questions.length - 1">Next</button>
      <button class="btn btn-success me-2" @click="submitQuiz">Submit Quiz</button>
      <button class="btn btn-danger" @click="leaveQuiz">Leave Quiz</button>
    </div>

    <!-- Question Status Panel -->
    <div class="mt-5">
      <h5 class="mb-2">Question Status</h5>
      <div class="d-flex flex-wrap gap-2">
        <button v-for="(q, index) in questions" :key="q.id" @click="goToQuestion(index)"
                class="btn btn-sm"
                :class="statusClass(q.id)">
          {{ index + 1 }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../axios'

const route = useRoute()
const router = useRouter()
const quizId = route.query.quiz_id
const duration = route.query.duration


const questions = ref([])
const currentIndex = ref(0)
const userAnswers = ref({})
const questionStatuses = ref({})
const timeLeft = ref(0)
let timerInterval = null

const currentQuestion = computed(() => questions.value[currentIndex.value])
const options = computed(() => currentQuestion.value ? [
  currentQuestion.value.option1,
  currentQuestion.value.option2,
  currentQuestion.value.option3,
  currentQuestion.value.option4
] : [])

const formattedTime = computed(() => {
  const minutes = Math.floor(timeLeft.value / 60)
  const seconds = timeLeft.value % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

const fetchQuestions = async () => {
  const res = await api.get(`/api/questions/${quizId}`)
  questions.value = res.data
  for (const q of res.data) {
    userAnswers.value[q.id] = -1
    questionStatuses.value[q.id] = 'Not-Answered'
  }
  startTimer()
}

const startTimer = () => {
  const [h, m] = duration.split(':').map(Number)
  timeLeft.value = h * 3600 + m * 60
  timerInterval = setInterval(() => {
    if (timeLeft.value > 0) {
      timeLeft.value--
    } else {
      clearInterval(timerInterval)
      submitQuiz()
    }
  }, 1000)
}

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
  }
}

const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

const goToQuestion = (index) => {
  currentIndex.value = index
}

const selectOption = (questionId, value) => {
  userAnswers.value[questionId] = value
  questionStatuses.value[questionId] = 'Answered'
}

const clearResponse = () => {
  const qid = currentQuestion.value.id
  userAnswers.value[qid] = -1
  questionStatuses.value[qid] = 'Not-Answered'
}

const markForReview = () => {
  const qid = currentQuestion.value.id
  if (userAnswers.value[qid] !== -1) {
    questionStatuses.value[qid] = 'Marked-for-Review'
  }
}

const leaveQuiz = () => {
  clearInterval(timerInterval)
  router.push('/user/dashboard')
}

const statusClass = (id) => {
  const status = questionStatuses.value[id]
  return {
    'btn-outline-secondary': status === 'Not-Answered',
    'btn-warning': status === 'Marked-for-Review',
    'btn-success': status === 'Answered'
  }
}

const submitQuiz = async () => {
  clearInterval(timerInterval)
  const timestamp = new Date().toISOString()
  const payload = {
    answers: userAnswers.value,
    statuses: questionStatuses.value,
    timestamp
  }
  const res = await api.post(`/api/submit_quiz/${quizId}`, payload)
  alert(`✅ Quiz submitted! Score: ${res.data.total_score}`)
  router.push('/user/dashboard')
}

onMounted(() => {
  fetchQuestions()
})
</script>

<style scoped>
button.btn.btn-sm {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-weight: bold;
  padding: 0;
}
</style>
