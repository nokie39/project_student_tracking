<template>
  <v-container fluid class="bg-grey-lighten-5 fill-height align-start pa-3">
    
    <v-row dense class="mb-4">
      <v-col cols="12" class="d-flex justify-space-between align-end">
        <div>
          <h2 class="text-h6 font-weight-bold text-grey-darken-3">
            ວຽກບ້ານທັງໝົດ
          </h2>
          <div class="text-caption text-grey">
            ລໍຖ້າສົ່ງ: {{ assignments.filter(x => !x.submission).length }} ວຽກ
          </div>
        </div>
        <v-chip color="primary" size="small" variant="flat" class="font-weight-bold">
          Total: {{ assignments.length }}
        </v-chip>
      </v-col>
    </v-row>

    <div v-if="loading">
      <v-skeleton-loader v-for="n in 3" :key="n" type="list-item-avatar-two-line" class="mb-2 rounded-lg bg-white"></v-skeleton-loader>
    </div>

    <div v-else-if="assignments.length === 0" class="text-center mt-10">
      <v-icon size="64" color="grey-lighten-2">mdi-clipboard-check</v-icon>
      <div class="text-grey mt-2">ບໍ່ມີວຽກບ້ານຄ້າງ</div>
    </div>

    <v-row v-else dense>
      <v-col cols="12" v-for="item in assignments" :key="item.id">
        
        <v-card elevation="0" border rounded="lg" class="mb-1" @click="openSubmitDialog(item)">
          <div class="d-flex flex-row align-center pa-3">
            
            <div class="mr-3">
              <v-avatar :color="getStatusColor(item)" variant="tonal" rounded="lg" size="48">
                <v-icon size="24">{{ getStatusIcon(item) }}</v-icon>
              </v-avatar>
            </div>

            <div class="flex-grow-1" style="min-width: 0;">
              <div class="d-flex justify-space-between align-start">
                <div class="text-subtitle-2 font-weight-bold text-truncate pr-2">
                  {{ item.title }}
                </div>
                <div class="text-caption font-weight-bold d-block d-sm-none" :class="`text-${getStatusColor(item)}`">
                  {{ getStatusText(item) }}
                </div>
              </div>

              <div class="text-caption text-grey text-truncate">
                {{ item.class_name }} • {{ item.description || 'No description' }}
              </div>
              
              <div class="d-flex align-center mt-1">
                <v-icon size="12" color="grey" start>mdi-clock-outline</v-icon>
                <span class="text-caption" :class="isOverdue(item) ? 'text-error font-weight-bold' : 'text-grey'">
                  {{ formatDate(item.due_date) }}
                </span>
              </div>
            </div>

            <div class="d-none d-sm-flex flex-column align-end ml-4 gap-1">
              <v-chip size="x-small" :color="getStatusColor(item)" variant="flat" class="font-weight-bold mb-1">
                {{ getStatusText(item) }}
              </v-chip>
              
              <div v-if="item.submission && item.submission.score !== null" class="text-h6 font-weight-bold text-success">
                {{ item.submission.score }} <span class="text-caption">ຄະແນນ</span>
              </div>
              <div v-else>
                 <v-btn size="x-small" variant="text" color="grey">ແຕະເພື່ອສົ່ງ</v-btn>
              </div>
            </div>

          </div>
          
          <div v-if="item.submission && item.submission.score !== null" class="bg-green-lighten-5 px-3 py-2 d-flex align-center border-t">
             <v-icon size="16" color="success" start>mdi-comment-check</v-icon>
             <span class="text-caption text-success font-weight-medium">
               "{{ item.submission.feedback || 'ດີຫຼາຍ' }}"
             </span>
          </div>
        </v-card>

      </v-col>
    </v-row>

    <v-dialog v-model="dialog" max-width="500" :fullscreen="mobile" transition="dialog-bottom-transition">
      <v-card rounded="xl">
        <v-toolbar color="white" density="compact" border>
          <v-btn icon @click="dialog = false"><v-icon>mdi-close</v-icon></v-btn>
          <v-toolbar-title class="text-subtitle-1 font-weight-bold">ສົ່ງວຽກ</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn v-if="selectedItem?.file_url" :href="getFileUrl(selectedItem.file_url)" target="_blank" color="primary" variant="text" prepend-icon="mdi-file-eye">
            ເບິ່ງໂຈດ
          </v-btn>
        </v-toolbar>

        <v-card-text class="pt-6 bg-grey-lighten-5">
          <div class="mb-4">
            <div class="text-h6 font-weight-bold">{{ selectedItem?.title }}</div>
            <div class="text-body-2 text-grey">{{ selectedItem?.description }}</div>
          </div>

          <v-form ref="form" v-model="valid">
            <div class="text-subtitle-2 font-weight-bold mb-2">ແນບໄຟລ໌ຄຳຕອບ</div>
            <v-file-input
              v-model="fileToUpload"
              label="ເລືອກໄຟລ໌ (PDF/Image)..."
              variant="solo-filled"
              prepend-inner-icon="mdi-paperclip"
              prepend-icon=""
              show-size
              accept="image/*,.pdf,.doc,.docx"
              bg-color="white"
              :rules="[v => !!v || 'Required']"
              :disabled="isGraded(selectedItem)"
            ></v-file-input>
          </v-form>

          <div v-if="isGraded(selectedItem)" class="text-center mt-4">
            <v-chip color="success" prepend-icon="mdi-check-circle">ກວດແລ້ວ! ບໍ່ສາມາດແກ້ໄຂໄດ້</v-chip>
          </div>
        </v-card-text>

        <v-card-actions class="pa-4 bg-white border-t" v-if="!isGraded(selectedItem)">
          <v-btn block color="primary" size="large" rounded="pill" variant="flat" :loading="submitting" @click="handleSubmit">
            ຢືນຢັນການສົ່ງ
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useDisplay } from 'vuetify';
import { getStudentAssignments, submitHomework } from '../../services/api'; 

const { mobile } = useDisplay();
const assignments = ref([]);
const loading = ref(true);
const dialog = ref(false);
const submitting = ref(false);
const selectedItem = ref(null);
const fileToUpload = ref(null);
const valid = ref(false);
const form = ref(null);

const fetchData = async () => {
  loading.value = true;
  try {
    const res = await getStudentAssignments();
    assignments.value = res.data;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const openSubmitDialog = (item) => {
  selectedItem.value = item;
  fileToUpload.value = null;
  dialog.value = true;
};

const handleSubmit = async () => {
  const { valid } = await form.value.validate();
  if (!valid) return;

  // File handling logic
  let actualFile = null;
  if (Array.isArray(fileToUpload.value) && fileToUpload.value.length > 0) actualFile = fileToUpload.value[0];
  else if (fileToUpload.value) actualFile = fileToUpload.value;

  if (!actualFile) return alert("Please select a file");

  submitting.value = true;
  try {
    const formData = new FormData();
    formData.append('assignment_id', selectedItem.value.id);
    formData.append('file', actualFile);
    await submitHomework(formData);
    dialog.value = false;
    fetchData(); 
  } catch (error) {
    alert("Error: " + (error.response?.data?.detail || error.message));
  } finally {
    submitting.value = false;
  }
};

// --- Helpers ---
const getFileUrl = (path) => {
  if (!path) return '#';
  if (path.startsWith('http')) return path;
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  return `${baseUrl}/${path}`;
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('lo-LA', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
};

const isOverdue = (item) => {
  if (item.submission) return false;
  return new Date() > new Date(item.due_date);
};

const isGraded = (item) => item?.submission?.score !== null && item?.submission?.score !== undefined;

const getStatusColor = (item) => {
  if (item.submission) return item.submission.score !== null ? 'success' : 'info';
  return isOverdue(item) ? 'error' : 'grey';
};

const getStatusIcon = (item) => {
  if (item.submission) return item.submission.score !== null ? 'mdi-check-decagram' : 'mdi-send-check';
  return isOverdue(item) ? 'mdi-alert-circle' : 'mdi-file-document-edit';
};

const getStatusText = (item) => {
  if (item.submission) return item.submission.score !== null ? 'ກວດແລ້ວ' : 'ສົ່ງແລ້ວ';
  return isOverdue(item) ? 'ກາຍກຳນົດ' : 'ຍັງບໍ່ສົ່ງ';
};

onMounted(fetchData);
</script>

<style scoped>
.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.gap-1 { gap: 4px; }
</style>