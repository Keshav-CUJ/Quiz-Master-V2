<template>
  <div class="container mt-4">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Admin Dashboard</a>
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


    <div>
       <div class="card p-4 shadow-sm"> 
      <h2>Subjects</h2>
      <table class="table table-bordered">
        <thead>
          <tr>
            <th>Subject Name</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in subjects" :key="s.id">
            <td>
              <input v-if="editSubjectId === s.id" v-model="s.name" class="form-control" />
              <span v-else>{{ s.name }}</span>
            </td>
            <td>
              <input v-if="editSubjectId === s.id" v-model="s.description" class="form-control" />
              <span v-else>{{ s.description }}</span>
            </td>
            <td>
              <button class="btn btn-sm btn-warning" v-if="editSubjectId !== s.id" @click="editSubjectId = s.id">Edit</button>
              <button class="btn btn-sm btn-success" v-else @click="updateSubject(s)">Update</button>
              <button class="btn btn-sm btn-danger ms-2" @click="deleteSubject(s.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="successMessage === ' Subject updated'" class="alert alert-success mt-3">{{ successMessage }}</div>

      <h4>Add New Subject</h4>
      <form @submit.prevent="addSubject">
        <input v-model="newSubject.name" class="form-control mb-2" placeholder="Subject name" required>
        <input v-model="newSubject.description" class="form-control mb-2" placeholder="Subject description">
        <button class="btn btn-primary">Add Subject</button>
      </form>
      <div v-if="successMessage === ' Subject added successfully!'" class="alert alert-success mt-3">{{ successMessage }}</div>

      </div>
      <hr>
      <div class="card p-4 shadow-sm">
      <h2>Chapters</h2>
      <div class="mb-3">
        <label>Filter by Subject:</label>
        <select v-model="selectedSubjectFilter" class="form-select">
          <option value="">All Subjects</option>
          <option v-for="s in subjects" :key="s.id" :value="s.name">{{ s.name }}</option>
        </select>
      </div>

      <table class="table table-bordered">
        <thead>
          <tr>
            <th>Chapter Name</th>
            <th>Description</th>
            <th>Subject</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in filteredChapters" :key="c.id">
            <td>
              <input v-if="editChapterId === c.id" v-model="c.name" class="form-control" />
              <span v-else>{{ c.name }}</span>
            </td>
            <td>
              <input v-if="editChapterId === c.id" v-model="c.description" class="form-control" />
              <span v-else>{{ c.description }}</span>
            </td>
            <td>
              <select v-if="editChapterId === c.id" v-model="c.subject_id" class="form-select">
                <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
              <span v-else>{{ c.subject_name }}</span>
            </td>
            <td>
              <button class="btn btn-sm btn-warning" v-if="editChapterId !== c.id" @click="editChapterId = c.id">Edit</button>
              <button class="btn btn-sm btn-success" v-else @click="updateChapter(c)">Update</button>
              <button class="btn btn-sm btn-danger ms-2" @click="deleteChapter(c.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="successMessage === '✅ Chapter updated'" class="alert alert-success mt-3">{{ successMessage }}</div>
      <h4>Add New Chapter</h4>
      <form @submit.prevent="addChapter">
        <input v-model="newChapter.name" class="form-control mb-2" placeholder="Chapter name" required>
        <input v-model="newChapter.description" class="form-control mb-2" placeholder="Chapter description">
        <select v-model="newChapter.subject_id" class="form-select mb-2" required>
          <option disabled value="">Select Subject</option>
          <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
        <button class="btn btn-success">Add Chapter</button>
      </form>

      <div v-if="successMessage === '✅ Chapter added successfully!'" class="alert alert-success mt-3">{{ successMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../axios'

const router = useRouter()
const subjects = ref([])
const chapters = ref([])
const newSubject = ref({ name: '', description: '' })
const newChapter = ref({ name: '', description: '', subject_id: '' })
const selectedSubjectFilter = ref('')
const editSubjectId = ref(null)
const editChapterId = ref(null)
const successMessage = ref('')

const showSuccess = (msg) => {
  successMessage.value = msg
  setTimeout(() => successMessage.value = '', 3000)
}

const fetchSubjects = async () => {
  fetchChapters()
  const res = await api.get('/api/subjects')
  subjects.value = res.data
}

const fetchChapters = async () => {
  const res = await api.get('/api/chapters')
  chapters.value = res.data
}

const addSubject = async () => {
  try {
    await api.post('/api/subjects', newSubject.value)
    await fetchSubjects()
    newSubject.value = { name: '', description: '' }
    showSuccess('✅ Subject added successfully!')
  } catch (err) {
    console.error('Failed to add subject', err)
  }
}

const updateSubject = async (subject) => {
  await api.put(`/api/subjects/${subject.id}`, subject)
  editSubjectId.value = null
  fetchSubjects()
  showSuccess('✅ Subject updated')
}

const deleteSubject = async (id) => {
  await api.delete(`/api/subjects/${id}`)
  fetchSubjects()
}

const addChapter = async () => {
  await api.post('/api/chapters', newChapter.value)
  newChapter.value = { name: '', description: '', subject_id: '' }
  fetchChapters()
  showSuccess('✅ Chapter added successfully!')
}

const updateChapter = async (chapter) => {
  await api.put(`/api/chapters/${chapter.id}`, chapter)
  editChapterId.value = null
  fetchChapters()
  showSuccess('✅ Chapter updated')
}

const deleteChapter = async (id) => {
  await api.delete(`/api/chapters/${id}`)
  fetchChapters()
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('role')
  router.replace('/')
}

const filteredChapters = computed(() => {
  if (!selectedSubjectFilter.value) return chapters.value
  return chapters.value.filter(c => {
    const subject = subjects.value.find(s => s.id === c.subject_id)
    return subject && subject.name === selectedSubjectFilter.value
  })
})




onMounted(() => {
  fetchSubjects()
  
})
</script>