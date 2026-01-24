<template>
  <v-container fluid class="pa-0 pa-md-4">
    <v-card elevation="0" class="bg-transparent">
      
      <v-card-title class="py-4 px-2 d-flex flex-column flex-md-row justify-space-between align-start align-md-center">
        <div class="d-flex align-center mb-3 mb-md-0">
          <v-avatar color="primary" class="mr-3" variant="tonal" rounded>
            <v-icon color="primary">mdi-book-open-variant</v-icon>
          </v-avatar>
          <div>
            <div class="text-h6 font-weight-bold text-primary">ຈັດການວຽກບ້ານ</div>
            <div class="text-caption text-grey">Assignments Management</div>
          </div>
        </div>

        <div class="d-flex flex-column flex-sm-row align-center w-100 w-md-auto gap-2">
          <v-select
            v-model="selectedClassId"
            :items="classes"
            item-title="name"
            item-value="id"
            label="ຫ້ອງຮຽນ"
            density="compact"
            variant="solo-filled"
            hide-details
            prepend-inner-icon="mdi-google-classroom"
            class="w-100 w-sm-auto"
            style="min-width: 180px;"
            @update:model-value="fetchAssignments"
          ></v-select>

          <v-btn 
            color="primary" 
            prepend-icon="mdi-plus" 
            elevation="2"
            class="w-100 w-sm-auto mt-2 mt-sm-0"
            height="44"
            @click="openCreateDialog"
          >
            ສັ່ງວຽກໃໝ່
          </v-btn>
        </div>
      </v-card-title>

      <v-card-text class="px-2 mt-2">
        <div v-if="loading" class="text-center py-10">
          <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
          <div class="mt-4 text-grey">ກຳລັງໂຫຼດຂໍ້ມູນ...</div>
        </div>

        <v-row v-else>
          <v-col cols="12" md="6" lg="4" v-for="item in assignments" :key="item.id">
            <v-card elevation="2" rounded="lg" class="h-100 border-s-lg border-primary">
              <v-card-item>
                <div class="d-flex justify-space-between align-start mb-2">
                  <v-chip size="x-small" color="primary" variant="tonal" label>
                    <v-icon start size="small">mdi-google-classroom</v-icon>
                    {{ getClassName(item.class_id) }}
                  </v-chip>
                  
                  <div class="d-flex flex-column align-end">
                    <span class="text-caption font-weight-medium" :class="isOverdue(item.due_date) ? 'text-error' : 'text-success'">
                      {{ formatDate(item.due_date) }}
                    </span>
                    <span v-if="isOverdue(item.due_date)" class="text-[10px] text-error">ກາຍກຳນົດ</span>
                  </div>
                </div>
                
                <div class="text-h6 font-weight-bold mb-1 line-clamp-2">{{ item.title }}</div>
                <div class="text-body-2 text-grey mb-3 line-clamp-3">{{ item.description || 'ບໍ່ມີລາຍລະອຽດ' }}</div>
              </v-card-item>

              <v-divider></v-divider>

              <v-card-actions class="pa-3">
                 <v-btn 
                  v-if="item.file_url" 
                  :href="getFileUrl(item.file_url)" 
                  target="_blank" 
                  color="primary" 
                  variant="text" 
                  size="small"
                  prepend-icon="mdi-file-eye"
                >
                  ເບິ່ງໂຈດ
                </v-btn>
                <span v-else class="text-caption text-grey ml-2">-- ບໍ່ມີໄຟລ໌ --</span>
                
                <v-spacer></v-spacer>
                
                <div class="d-flex gap-2">
                  <v-btn 
                    color="success" 
                    variant="flat" 
                    size="small"
                    prepend-icon="mdi-playlist-check"
                    @click="openGrading(item)"
                  >
                    ກວດວຽກ
                  </v-btn>

                  <v-btn 
                    color="error" 
                    variant="text" 
                    icon="mdi-delete" 
                    size="small"
                    @click="handleDelete(item.id)"
                  ></v-btn>
                </div>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>

        <v-alert v-if="!loading && assignments.length === 0" type="info" variant="tonal" class="mt-4 border-dashed" border>
          <div class="text-center">
            <v-icon size="40" class="mb-2">mdi-notebook-off</v-icon>
            <div>ຍັງບໍ່ມີການສັ່ງວຽກໃນຫ້ອງຮຽນນີ້</div>
          </div>
        </v-alert>
      </v-card-text>

      <v-dialog 
        v-model="createDialog" 
        max-width="600" 
        :fullscreen="mobile" 
        transition="dialog-bottom-transition"
      >
        <v-card rounded="xl">
          <v-toolbar color="primary" dark>
            <v-btn icon dark @click="createDialog = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
            <v-toolbar-title>ສ້າງວຽກບ້ານໃໝ່</v-toolbar-title>
            <v-toolbar-items>
              <v-btn variant="text" @click="handleSubmit" :loading="saving">
                ບັນທຶກ
              </v-btn>
            </v-toolbar-items>
          </v-toolbar>
          
          <v-card-text class="pt-4 bg-grey-lighten-5">
            <v-form ref="form" v-model="valid">
              <v-card elevation="0" class="pa-4 mb-4" border>
                <div class="text-subtitle-1 font-weight-bold mb-3">ຂໍ້ມູນທົ່ວໄປ</div>
                <v-select
                  v-model="newItem.class_id"
                  :items="classes"
                  item-title="name"
                  item-value="id"
                  label="ເລືອກຫ້ອງຮຽນ *"
                  variant="outlined"
                  bg-color="white"
                  prepend-inner-icon="mdi-google-classroom"
                  :rules="[v => !!v || 'ກະລຸນາເລືອກຫ້ອງຮຽນ']"
                ></v-select>

                <v-text-field 
                  v-model="newItem.title" 
                  label="ຫົວຂໍ້ວຽກບ້ານ *" 
                  variant="outlined"
                  bg-color="white"
                  placeholder="ຕົວຢ່າງ: ບົດເຝິກຫັດທີ 1"
                  :rules="[v => !!v || 'ກະລຸນາໃສ່ຫົວຂໍ້']"
                ></v-text-field>

                <v-textarea 
                  v-model="newItem.description" 
                  label="ລາຍລະອຽດ / ຄຳສັ່ງ" 
                  variant="outlined" 
                  bg-color="white"
                  rows="3"
                  auto-grow
                ></v-textarea>
              </v-card>

              <v-card elevation="0" class="pa-4" border>
                <div class="text-subtitle-1 font-weight-bold mb-3">ການສົ່ງງານ</div>
                <v-text-field 
                  v-model="newItem.due_date" 
                  type="datetime-local" 
                  label="ກຳນົດສົ່ງ *" 
                  variant="outlined"
                  bg-color="white"
                  :rules="[v => !!v || 'ກະລຸນາໃສ່ວັນທີສົ່ງ']"
                ></v-text-field>

                <v-file-input
                  v-model="newItem.file"
                  label="ແນບໄຟລ໌ໂຈດ (PDF/ຮູບພາບ)"
                  variant="outlined"
                  bg-color="white"
                  prepend-inner-icon="mdi-paperclip"
                  show-size
                  accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                ></v-file-input>
              </v-card>
            </v-form>
          </v-card-text>
        </v-card>
      </v-dialog>

      <v-dialog 
        v-model="gradeDialog" 
        max-width="1000" 
        :fullscreen="mobile"
        transition="dialog-bottom-transition"
        scrollable
      >
        <v-card rounded="xl">
          <v-toolbar color="success" dark>
             <v-btn icon dark @click="gradeDialog = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
            <v-toolbar-title class="text-subtitle-1">
              ກວດວຽກ: {{ selectedAssignment?.title }}
            </v-toolbar-title>
          </v-toolbar>
          
          <v-card-text class="pa-0">
            <v-data-table
              :headers="gradeHeaders"
              :items="submissions"
              :loading="loadingSubmissions"
              mobile-breakpoint="md"
            >
              <template v-slot:item.student_name="{ item }">
                <div class="d-flex align-center py-2">
                  <v-avatar color="grey-lighten-2" size="32" class="mr-2">
                    <span class="text-caption font-weight-bold">{{ item.full_name.charAt(0) }}</span>
                  </v-avatar>
                  <div>
                    <div class="font-weight-bold text-body-2">{{ item.full_name }}</div> 
                    <div class="text-caption text-grey">{{ item.student_code }}</div>
                  </div>
                </div>
              </template>

              <template v-slot:item.submitted_at="{ item }">
                <div v-if="item.status === 'SUBMITTED'" class="text-no-wrap">
                  <v-chip size="x-small" color="success" variant="tonal" class="mb-1">ສົ່ງແລ້ວ</v-chip>
                  <div class="text-caption">{{ formatDateTime(item.submitted_at) }}</div>
                </div>
                <div v-else>
                   <v-chip size="x-small" :color="item.status === 'LATE' ? 'error' : 'grey'" variant="flat">
                     {{ item.status }}
                   </v-chip>
                </div>
              </template>

              <template v-slot:item.file_url="{ item }">
                <v-btn 
                  v-if="item.file_url"
                  :href="getFileUrl(item.file_url)" 
                  target="_blank" 
                  size="x-small" 
                  variant="outlined" 
                  color="primary" 
                  prepend-icon="mdi-file-eye"
                >
                  ເບິ່ງ
                </v-btn>
                <span v-else class="text-caption text-grey">-</span>
              </template>

              <template v-slot:item.score="{ item }">
                <v-text-field
                  v-model.number="item.score"
                  type="number"
                  variant="outlined"
                  density="compact"
                  hide-details
                  bg-color="white"
                  style="min-width: 80px; max-width: 100px;"
                  :disabled="item.status === 'MISSING'"
                ></v-text-field>
              </template>

              <template v-slot:item.feedback="{ item }">
                 <v-textarea
                  v-model="item.feedback"
                  variant="outlined"
                  density="compact"
                  hide-details
                  rows="1"
                  auto-grow
                  bg-color="white"
                  placeholder="ຄຳເຫັນ..."
                  :disabled="item.status === 'MISSING'"
                ></v-textarea>
              </template>

              <template v-slot:item.actions="{ item }">
                <v-btn 
                  icon="mdi-content-save" 
                  size="small" 
                  color="success" 
                  variant="tonal"
                  @click="saveGrade(item)"
                  :loading="item.saving"
                  :disabled="item.status === 'MISSING'"
                ></v-btn>
              </template>

            </v-data-table>
          </v-card-text>
        </v-card>
      </v-dialog>

    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useDisplay } from 'vuetify'; // ✅ Import ສຳລັບ Responsive
import { 
  getAssignmentsByClass, 
  createAssignment, 
  deleteAssignment, 
  getTeacherClasses, 
  getAssignmentSubmissions, 
  gradeSubmission 
} from '../services/api';

const { mobile } = useDisplay(); // ✅ ກວດສອບໜ້າຈໍມືຖື

// --- State Variables ---
const assignments = ref([]);
const classes = ref([]);
const selectedClassId = ref(null);
const loading = ref(false);

const createDialog = ref(false);
const gradeDialog = ref(false);
const saving = ref(false);
const loadingSubmissions = ref(false);
const valid = ref(false);
const form = ref(null);

// Grading Data
const selectedAssignment = ref(null);
const submissions = ref([]);

const newItem = ref({
  class_id: null,
  title: '',
  description: '',
  due_date: '',
  file: null
});

// Table Headers
const gradeHeaders = [
  { title: 'ນັກຮຽນ', key: 'student_name', width: '200px' },
  { title: 'ສະຖານະ', key: 'submitted_at', width: '120px' },
  { title: 'ໄຟລ໌', key: 'file_url', sortable: false, width: '80px' },
  { title: 'ຄະແນນ', key: 'score', width: '100px', sortable: false },
  { title: 'Feedback', key: 'feedback', sortable: false, minWidth: '150px' },
  { title: '', key: 'actions', align: 'end', sortable: false, width: '50px' },
];

// --- 1. Load Classes ---
const fetchClasses = async () => {
  try {
    const res = await getTeacherClasses();
    classes.value = res.data;
    if (classes.value.length > 0) {
        selectedClassId.value = classes.value[0].id;
        fetchAssignments();
    }
  } catch (error) {
    console.error("Error fetching classes:", error);
  }
};

// --- 2. Load Assignments ---
const fetchAssignments = async () => {
  if (!selectedClassId.value) return;
  
  loading.value = true;
  try {
    const res = await getAssignmentsByClass(selectedClassId.value);
    assignments.value = res.data;
  } catch (error) {
    console.error("Error fetching assignments:", error);
  } finally {
    loading.value = false;
  }
};

const openCreateDialog = () => {
  newItem.value = { 
    class_id: selectedClassId.value, 
    title: '', 
    description: '', 
    due_date: '', 
    file: null 
  };
  createDialog.value = true;
};

// --- 3. Create Assignment (FormData) ---
const handleSubmit = async () => {
  const { valid } = await form.value.validate();
  if (!valid) return;

  saving.value = true;
  try {
    const formData = new FormData();
    formData.append('class_id', newItem.value.class_id);
    formData.append('title', newItem.value.title);
    formData.append('description', newItem.value.description || '');
    formData.append('due_date', newItem.value.due_date);
    
    // File Handling
    const fileInput = newItem.value.file;
    if (fileInput) {
      if (Array.isArray(fileInput) && fileInput.length > 0) {
         formData.append('file', fileInput[0]); 
      } else if (fileInput instanceof File) {
         formData.append('file', fileInput);
      } else if (fileInput.length && fileInput[0]) {
         formData.append('file', fileInput[0]);
      }
    }

    await createAssignment(formData);
    createDialog.value = false;
    
    if (newItem.value.class_id === selectedClassId.value) {
        fetchAssignments();
    }
    // alert("ສັ່ງວຽກສຳເລັດ!");
  } catch (error) {
    console.error(error);
    alert('Error: ' + (error.response?.data?.detail || error.message));
  } finally {
    saving.value = false;
  }
};

// --- 4. Delete ---
const handleDelete = async (id) => {
  if (!confirm("ຕ້ອງການລຶບວຽກນີ້ແທ້ບໍ່?")) return;
  try {
    await deleteAssignment(id);
    fetchAssignments();
  } catch (error) {
    alert("ເກີດຂໍ້ຜິດພາດໃນການລຶບ");
  }
};

// --- 5. Grading Logic ---
const openGrading = async (assignment) => {
  selectedAssignment.value = assignment;
  gradeDialog.value = true;
  loadingSubmissions.value = true;
  submissions.value = [];

  try {
    const res = await getAssignmentSubmissions(assignment.id);
    submissions.value = res.data.map(sub => ({ ...sub, saving: false }));
  } catch (error) {
    console.error("Error loading submissions:", error);
  } finally {
    loadingSubmissions.value = false;
  }
};

const saveGrade = async (item) => {
  item.saving = true;
  try {
    await gradeSubmission({
      submission_id: item.id,
      score: parseFloat(item.score) || 0,
      feedback: item.feedback || ''
    });
    // alert("ບັນທຶກຄະແນນສຳເລັດ");
  } catch (error) {
    alert("ບັນທຶກບໍ່ໄດ້: " + (error.response?.data?.detail || error.message));
  } finally {
    item.saving = false;
  }
};

// --- Utils ---
const getClassName = (id) => {
    const c = classes.value.find(x => x.id === id);
    return c ? c.name : 'Unknown Class';
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('lo-LA', { day: 'numeric', month: 'short' });
};

const formatDateTime = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleString('lo-LA', { 
    day: 'numeric', month: 'numeric', hour: '2-digit', minute: '2-digit' 
  });
};

const getFileUrl = (path) => {
  if (!path) return '#';
  if (path.startsWith('http')) return path;
  const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
  const cleanPath = path.startsWith('/') ? path.substring(1) : path;
  return `${baseUrl}/${cleanPath}`;
};

const isOverdue = (dueDate) => {
  return new Date() > new Date(dueDate);
};

onMounted(() => {
  fetchClasses();
});
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
.border-s-lg {
  border-left-width: 4px !important;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>