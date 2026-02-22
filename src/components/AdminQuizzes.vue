<template>
  <div class="container mt-4">
    
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Admin Quizz</a>
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
    
    <h2>Manage Quizzes</h2>

    <!-- Filter Section -->
    <div class="row mb-3">
      <div class="col-md-4">
        <label>Subject</label>
        <select class="form-select" v-model="filterSubject" @change="fetchChaptersBySubject">
          <option value="">All Subjects</option>
          <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
      </div>
      <div class="col-md-4">
        <label>Chapter</label>
        <select class="form-select" v-model="filterChapter">
          <option value="">All Chapters</option>
          <option v-for="c in chapterOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div class="col-md-4 d-flex align-items-end">
        <button class="btn btn-primary w-100" @click="fetchQuizzes">Filter</button>
      </div>
    </div>

    <!-- Quiz Table -->
    <table class="table table-bordered">
      <thead>
        <tr>
          <!-- <th>Quiz ID</th> -->
          <th>Chapter</th>
          <th>Subject</th>
          <th>Date</th>
          <th>Time Duration</th>
          <th>Remarks</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="quiz in quizzes" :key="quiz.id">
          <template v-if="editingQuizId !== quiz.id">
            <!-- <td>{{ quiz.id }}</td> -->
            <td>{{ quiz.chapter_name }}</td>
            <td>{{ quiz.subject_name }}</td>
            <td>{{ quiz.date_of_quiz }}</td>
            <td>{{ quiz.time_duration }}</td>
            <td>{{ quiz.remarks }}</td>
            <td>
              <button class="btn btn-warning btn-sm" @click="startEditing(quiz)">Edit</button>
              <button class="btn btn-danger btn-sm" @click="deleteQuiz(quiz.id)">Delete</button>
            </td>
          </template>
          <template v-else>
            <td>
              <select class="form-select" v-model="editQuiz.chapter_id">
                <option v-for="c in chapterOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </td>
            <td>{{ quiz.subject_name }}</td>
            <td><input type="date" class="form-control" v-model="editQuiz.date_of_quiz"></td>
            <td><input type="text" class="form-control" v-model="editQuiz.time_duration"></td>
            <td><input type="text" class="form-control" v-model="editQuiz.remarks"></td>
            <td>
              <button class="btn btn-success btn-sm" @click="updateQuiz(quiz.id)">Update</button>
              <button class="btn btn-secondary btn-sm" @click="cancelEditing">Cancel</button>
            </td>
          </template>
        </tr>
      </tbody>
    </table>

    <!-- Add New Quiz -->
    <h4 class="mt-4">Add New Quiz</h4>
    <form @submit.prevent="addQuiz">
      <div class="row mb-2">
        <div class="col-md-6">
          <label>Subject</label>
          <select class="form-select" v-model="newQuiz.subject_id" @change="loadChapterOptions">
            <option value="">Select Subject</option>
            <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>
        <div class="col-md-6">
          <label>Chapter</label>
          <select class="form-select" v-model="newQuiz.chapter_id">
            <option value="">Select Chapter</option>
            <option v-for="c in chapterOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
      </div>

      <div class="mb-2">
        <label>Date of Quiz</label>
        <input type="date" class="form-control" v-model="newQuiz.date_of_quiz">
      </div>

      <div class="mb-2">
        <label>Time Duration</label>
        <input type="text" class="form-control" v-model="newQuiz.time_duration" placeholder="00:30">
      </div>

      <div class="mb-2">
        <label>Remarks</label>
        <input type="text" class="form-control" v-model="newQuiz.remarks">
      </div>

      <button class="btn btn-success">Add Quiz</button>
    </form>
    <h2>Manage Questions</h2>

    <!-- Select Quiz a kind of filter-->  
    <div class="row mb-3">
      <div class="col-md-6">
        <label>Select Quiz</label>
        <select class="form-select" v-model="selectedQuizId" @change="fetchQuestions">
          <option value="">Select Quiz</option>
          <option v-for="q in quizzes" :key="q.id" :value="q.id">
            Quiz {{ q.id }} ({{ q.date_of_quiz }})
          </option>
        </select>
      </div>
    </div>

    <!-- Questions Table -->
    <table class="table table-bordered">
      <thead>
        <tr>
          <th>Question</th>
          <th>Options</th>
          <th>Correct Option</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="q in questions" :key="q.id">
          <template v-if="editingQuestionId !== q.id">
            <td>{{ q.question_statement }}</td>
            <td>
              1. {{ q.option1 }}<br>
              2. {{ q.option2 }}<br>
              3. {{ q.option3 }}<br>
              4. {{ q.option4 }}
            </td>
            <td>{{ q.correct_option }}</td>
            <td>
              <button class="btn btn-warning btn-sm" @click="startEditQuestion(q)">Edit</button>
              <button class="btn btn-danger btn-sm" @click="deleteQuestion(q.id)">Delete</button>
            </td>
          </template>
          <template v-else>
            <td><input class="form-control" v-model="editQuestion.question_statement" /></td>
            <td>
              <input class="form-control mb-1" v-model="editQuestion.option1" placeholder="Option 1" />
              <input class="form-control mb-1" v-model="editQuestion.option2" placeholder="Option 2" />
              <input class="form-control mb-1" v-model="editQuestion.option3" placeholder="Option 3" />
              <input class="form-control mb-1" v-model="editQuestion.option4" placeholder="Option 4" />
            </td>
            <td><input class="form-control" type="number" min="1" max="4" v-model="editQuestion.correct_option" /></td>
            <td>
              <button class="btn btn-success btn-sm" @click="updateQuestion(q.id)">Update</button>
              <button class="btn btn-secondary btn-sm" @click="cancelEditQuestion">Cancel</button>
            </td>
          </template>
        </tr>
      </tbody>
    </table>

    <!-- Add New Question -->
    <h4 class="mt-4">Add New Question</h4>
    <form @submit.prevent="addQuestion">
      <div class="mb-2">
        <label>Question Statement</label>
        <input class="form-control" v-model="newQuestion.question_statement" required />
      </div>
      <div class="row mb-2">
        <div class="col">
          <input class="form-control" v-model="newQuestion.option1" placeholder="Option 1" required />
        </div>
        <div class="col">
          <input class="form-control" v-model="newQuestion.option2" placeholder="Option 2" required />
        </div>
        <div class="col">
          <input class="form-control" v-model="newQuestion.option3" placeholder="Option 3" required />
        </div>
        <div class="col">
          <input class="form-control" v-model="newQuestion.option4" placeholder="Option 4" required />
        </div>
      </div>
      <div class="mb-2">
        <label>Correct Option (1-4)</label>
        <input type="number" class="form-control" v-model="newQuestion.correct_option" min="1" max="4" required />
      </div>
      <button class="btn btn-primary">Add Question</button>
    </form>

    
    <div v-if="successMessage" class="floating-success">{{ successMessage }}</div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const quizzes = ref([])
const subjects = ref([])
const chapterOptions = ref([])
const filterSubject = ref('')
const filterChapter = ref('')
const successMessage = ref('')
const newQuiz = ref({ subject_id: '', chapter_id: '', date_of_quiz: '', time_duration: '', remarks: '' })
const editingQuizId = ref(null)
const editQuiz = ref({ chapter_id: '', date_of_quiz: '', time_duration: '', remarks: '' })
const selectedQuizId = ref('')
const questions = ref([])
const newQuestion = ref({
  quiz_id: '',
  question_statement: '',
  option1: '',
  option2: '',
  option3: '',
  option4: '',
  correct_option: ''
})
const editingQuestionId = ref(null)
const editQuestion = ref({})




const fetchSubjects = async () => {
  const res = await api.get('/api/subjects')
  subjects.value = res.data
}

const fetchQuizzes = async () => {
  const params = {}
  if (filterSubject.value) params.subject_id = filterSubject.value
  if (filterChapter.value) params.chapter_id = filterChapter.value
  const res = await api.get('/api/quizzes', { params })
  quizzes.value = res.data
}

const fetchChaptersBySubject = async () => {
  chapterOptions.value = []
  filterChapter.value = ''
  if (filterSubject.value) {
    const res = await api.get('/api/chapters/by_subject', { params: { subject_id: filterSubject.value } })
    chapterOptions.value = res.data
  }
}

const loadChapterOptions = async () => {
  newQuiz.value.chapter_id = ''
  chapterOptions.value = []
  if (newQuiz.value.subject_id) {
    const res = await api.get('/api/chapters/by_subject', { params: { subject_id: newQuiz.value.subject_id } })
    chapterOptions.value = res.data
  }
}

const addQuiz = async () => {
  await api.post('/api/quizzes', newQuiz.value)
  newQuiz.value = { subject_id: '', chapter_id: '', date_of_quiz: '', time_duration: '', remarks: '' }
  successMessage.value = '✅ Quiz added successfully!'
  fetchQuizzes()
  setTimeout(() => (successMessage.value = ''), 3000)
}

const deleteQuiz = async (id) => {
  await api.delete(`/api/quizzes/${id}`)
  fetchQuizzes()
}

const startEditing = (quiz) => {
  editingQuizId.value = quiz.id
  editQuiz.value = {
    chapter_id: quiz.chapter_id,
    date_of_quiz: quiz.date_of_quiz,
    time_duration: quiz.time_duration,
    remarks: quiz.remarks
  }
  fetchChaptersBySubject()
}

const cancelEditing = () => {
  editingQuizId.value = null
  editQuiz.value = { chapter_id: '', date_of_quiz: '', time_duration: '', remarks: '' }
}

const updateQuiz = async (id) => {
  await api.put(`/api/quizzes/${id}`, editQuiz.value)
  successMessage.value = '✅ Quiz updated successfully!'
  fetchQuizzes()
  cancelEditing()
  setTimeout(() => (successMessage.value = ''), 3000)
}

const fetchQuestions = async () => {
  if (!selectedQuizId.value) return
  const res = await api.get(`/api/questions/${selectedQuizId.value}`)
  questions.value = res.data
  newQuestion.value.quiz_id = selectedQuizId.value
}

const addQuestion = async () => {
  await api.post('/api/questions', newQuestion.value)
  successMessage.value = '✅ Question added successfully!'
  fetchQuestions()
  newQuestion.value = {
    quiz_id: selectedQuizId.value,
    question_statement: '',
    option1: '',
    option2: '',
    option3: '',
    option4: '',
    correct_option: ''
  }
  setTimeout(() => (successMessage.value = ''), 3000)
}

const deleteQuestion = async (id) => {
  await api.delete(`/api/questions/${id}`)
  fetchQuestions()
}

const startEditQuestion = (q) => {
  editingQuestionId.value = q.id
  editQuestion.value = { ...q }
}

const cancelEditQuestion = () => {
  editingQuestionId.value = null
  editQuestion.value = {}
}

const updateQuestion = async (id) => {
  await api.put(`/api/questions/${id}`, editQuestion.value)
  successMessage.value = '✅ Question updated successfully!'
  fetchQuestions()
  cancelEditQuestion()
  setTimeout(() => (successMessage.value = ''), 3000)
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('role')
  router.replace('/')
}

onMounted(() => {
  fetchSubjects()
  fetchQuizzes()
})
</script>
<style scoped>
.floating-success {
  position: fixed;
  top: 20px;
  left: 20px;
  background-color: #28a745;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  z-index: 9999;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
</style>
