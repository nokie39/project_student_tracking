<template>
  <v-container fluid class="bg-grey-lighten-5 fill-height align-start pa-0 pa-md-4">
    
    <v-card flat color="transparent" class="w-100" style="max-width: 900px; margin: 0 auto;">
      
      <div class="pa-4 pb-2">
        <div class="d-flex justify-space-between align-center mb-2">
          <div>
            <h1 class="text-h5 font-weight-bold text-primary">
              <v-icon start>mdi-school</v-icon> ວຽກບ້ານຂອງຂ້ອຍ
            </h1>
            <div class="text-body-2 text-grey">
              ຈັດການການສົ່ງວຽກ ແລະ ຕິດຕາມຄະແນນ
            </div>
          </div>
          <div class="text-right d-none d-sm-block">
             <v-chip color="error" variant="flat" class="font-weight-bold mr-2">
                ຄ້າງສົ່ງ: {{ pendingCount }}
             </v-chip>
             <v-chip color="success" variant="tonal" class="font-weight-bold">
                ສຳເລັດ: {{ completedCount }}
             </v-chip>
          </div>
        </div>

        <v-tabs
          v-model="activeTab"
          color="primary"
          bg-color="white"
          class="rounded-lg shadow-sm mt-4 border"
          grow
        >
          <v-tab value="pending">
            <v-icon start>mdi-clock-alert-outline</v-icon> 
            ຄ້າງສົ່ງ ({{ pendingCount }})
          </v-tab>
          <v-tab value="completed">
            <v-icon start>mdi-check-circle-outline</v-icon> 
            ສົ່ງແລ້ວ
          </v-tab>
          <v-tab value="all">
            ທັງໝົດ
          </v-tab>
        </v-tabs>
      </div>

      <div class="px-4 pb-10">
        
        <div v-if="loading" class="mt-4">
          <v-skeleton-loader v-for="n in 3" :key="n" type="article" class="mb-3 rounded-lg"></v-skeleton-loader>
        </div>

        <div v-else-if="filteredAssignments.length === 0" class="text-center py-10">
          <v-img 
            src="https://cdn-icons-png.flaticon.com/512/7486/7486744.png" 
            width="150" 
            class="mx-auto mb-4 opacity-50"
          ></v-img>
          <div class="text-h6 text-grey">ບໍ່ມີຂໍ້ມູນໃນໜ້ານີ້</div>
          <div class="text-body-2 text-grey-lighten-1">ພັກຜ່ອນໃຫ້ສະບາຍໃຈ! 😊</div>
        </div>

        <v-row v-else dense class="mt-2">
          <v-col cols="12" v-for="item in filteredAssignments" :key="item.id">
            
            <v-card 
              elevation="2" 
              rounded="lg" 
              class="mb-2 assignment-card border-s-lg"
              :style="{ 'border-left-color': getStatusColor(item) + ' !important' }"
              @click="openSubmitDialog(item)"
              v-ripple
            >
              <div class="pa-4">
                <div class="d-flex justify-space-between align-start">
                  <div class="d-flex align-start flex-grow-1" style="min-width: 0;">
                    <v-avatar :color="getStatusColor(item)" variant="tonal" rounded="lg" size="48" class="mr-3 d-none d-sm-flex">
                      <v-icon size="24">{{ getStatusIcon(item) }}</v-icon>
                    </v-avatar>

                    <div class="flex-grow-1 pr-2">
                      <div class="d-flex align-center flex-wrap gap-2 mb-1">
                        <span class="text-caption font-weight-bold text-primary px-2 py-0 bg-blue-lighten-5 rounded">
                          {{ item.class_name || 'General' }}
                        </span>
                        <span v-if="isOverdue(item)" class="text-caption font-weight-bold text-error bg-red-lighten-5 px-2 py-0 rounded">
                          <v-icon size="x-small" start>mdi-fire</v-icon> ກາຍກຳນົດ
                        </span>
                      </div>
                      
                      <div class="text-subtitle-1 font-weight-bold text-truncate-2 mb-1">
                        {{ item.title }}
                      </div>
                      
                      <div class="text-body-2 text-grey-darken-1 text-truncate mb-2">
                        {{ item.description || 'ບໍ່ມີລາຍລະອຽດເພີ່ມເຕີມ' }}
                      </div>

                      <div class="d-flex align-center text-caption">
                        <v-icon size="14" class="mr-1" :color="isOverdue(item) ? 'error' : 'grey'">mdi-calendar-clock</v-icon>
                        <span :class="isOverdue(item) ? 'text-error font-weight-bold' : 'text-grey'">
                          ສົ່ງກ່ອນ: {{ formatDate(item.due_date) }}
                        </span>
                        <span class="mx-2 text-grey-lighten-2">|</span>
                        <span class="text-grey">{{ getRelativeTime(item.due_date) }}</span>
                      </div>
                    </div>
                  </div>

                  <div class="d-flex flex-column align-end justify-space-between" style="height: 100%;">
                    
                    <v-chip 
                        size="small" 
                        :color="getStatusColor(item)" 
                        variant="flat" 
                        class="font-weight-bold mb-2"
                    >
                      {{ getStatusText(item) }}
                    </v-chip>

                    <div v-if="item.submission">
                        <div v-if="item.submission.score !== null" class="text-right">
                            <div class="text-h5 font-weight-bold text-success">{{ item.submission.score }}</div>
                            <div class="text-caption text-success font-weight-bold">ຄະແນນ</div>
                        </div>
                        <div v-else class="text-caption text-info font-italic">
                            <v-icon size="small" start>mdi-progress-clock</v-icon> ລໍຖ້າກວດ
                        </div>
                    </div>
                    
                    <v-btn v-else size="small" variant="tonal" color="primary" class="mt-2" prepend-icon="mdi-upload">
                        ສົ່ງວຽກ
                    </v-btn>

                  </div>
                </div>
              </div>

              <div v-if="item.submission?.feedback" class="bg-green-lighten-5 px-4 py-2 border-t d-flex align-start">
                 <v-icon color="success" size="small" class="mt-1 mr-2">mdi-comment-quote</v-icon>
                 <div>
                    <div class="text-caption font-weight-bold text-success-darken-1">ຄຳເຫັນຈາກຄູ:</div>
                    <div class="text-caption text-grey-darken-3">"{{ item.submission.feedback }}"</div>
                 </div>
              </div>

            </v-card>
          </v-col>
        </v-row>
      </div>
    </v-card>

    <v-dialog v-model="dialog" max-width="500" :fullscreen="mobile" transition="dialog-bottom-transition">
      <v-card rounded="xl">
        <v-toolbar color="white" density="comfortable" border>
          <v-btn icon @click="dialog = false"><v-icon>mdi-close</v-icon></v-btn>
          <v-toolbar-title class="text-subtitle-1 font-weight-bold">ລາຍລະອຽດການສົ່ງວຽກ</v-toolbar-title>
        </v-toolbar>

        <v-card-text class="bg-grey-lighten-5 pt-6">
          <v-sheet rounded="lg" class="pa-4 mb-4 border">
             <div class="text-caption text-primary font-weight-bold mb-1">{{ selectedItem?.class_name }}</div>
             <div class="text-h6 font-weight-bold mb-2">{{ selectedItem?.title }}</div>
             <div class="text-body-2 text-grey-darken-1 mb-4">{{ selectedItem?.description }}</div>
             
             <v-btn 
                v-if="selectedItem?.file_url" 
                :href="getFileUrl(selectedItem.file_url)" 
                target="_blank" 
                color="primary" 
                variant="outlined" 
                size="small"
                prepend-icon="mdi-file-eye"
                class="text-none"
             >
                ເປີດເບິ່ງໄຟລ໌ໂຈດ
             </v-btn>
          </v-sheet>

          <v-form ref="form" v-model="valid">
            <div class="text-subtitle-2 font-weight-bold mb-2 ml-1">
                {{ isGraded(selectedItem) ? 'ໄຟລ໌ທີ່ສົ່ງແລ້ວ' : 'ອັບໂຫລດຄຳຕອບ' }}
            </div>
            
            <div v-if="selectedItem?.submission" class="mb-4">
                <v-card variant="tonal" :color="isGraded(selectedItem) ? 'success' : 'info'" class="pa-3 d-flex align-center">
                    <v-icon start size="30">mdi-file-check</v-icon>
                    <div>
                        <div class="text-subtitle-2 font-weight-bold">ສົ່ງແລ້ວເມື່ອ:</div>
                        <div class="text-caption">{{ formatDate(selectedItem.submission.submitted_at, true) }}</div>
                    </div>
                    <v-spacer></v-spacer>
                    <v-btn 
                        variant="text" 
                        size="small" 
                        :href="getFileUrl(selectedItem.submission.file_url)" 
                        target="_blank"
                        icon="mdi-open-in-new"
                    ></v-btn>
                </v-card>
            </div>

            <v-file-input
              v-if="!isGraded(selectedItem)"
              v-model="fileToUpload"
              label="ເລືອກໄຟລ໌ (PDF, ຮູບພາບ, Word)..."
              variant="solo-filled"
              prepend-inner-icon="mdi-cloud-upload"
              prepend-icon=""
              show-size
              accept="image/*,.pdf,.doc,.docx"
              bg-color="white"
              :rules="[v => !!v || 'ກະລຸນາເລືອກໄຟລ໌']"
              class="mb-2"
            ></v-file-input>
          </v-form>

          <v-alert v-if="isGraded(selectedItem)" type="success" variant="tonal" border="start" density="compact" class="mt-4">
             <div class="text-subtitle-2 font-weight-bold">ວຽກນີ້ຖືກກວດແລ້ວ!</div>
             <div class="text-caption">ບໍ່ສາມາດແກ້ໄຂການສົ່ງໄດ້.</div>
          </v-alert>

        </v-card-text>

        <v-card-actions class="pa-4 bg-white border-t" v-if="!isGraded(selectedItem)">
          <v-btn 
            block 
            color="primary" 
            size="large" 
            rounded="lg" 
            variant="elevated" 
            :loading="submitting" 
            @click="handleSubmit"
            prepend-icon="mdi-send"
          >
            {{ selectedItem?.submission ? 'ສົ່ງໃໝ່ (Re-submit)' : 'ຢືນຢັນການສົ່ງ' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
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
const activeTab = ref('pending');

// --- Computed ---
const pendingCount = computed(() => assignments.value.filter(x => !x.submission).length);
const completedCount = computed(() => assignments.value.filter(x => x.submission).length);

const filteredAssignments = computed(() => {
    if (activeTab.value === 'pending') {
        // ເອົາອັນທີ່ຍັງບໍ່ສົ່ງ ແລະ ຮຽງຕາມ due_date (ໃກ້ໝົດກຳນົດຂຶ້ນກ່ອນ)
        return assignments.value
            .filter(x => !x.submission)
            .sort((a, b) => new Date(a.due_date) - new Date(b.due_date));
    } else if (activeTab.value === 'completed') {
        // ເອົາອັນສົ່ງແລ້ວ
        return assignments.value.filter(x => x.submission);
    }
    // All
    return assignments.value;
});

// --- API ---
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
  fileToUpload.value = null; // Reset file input
  dialog.value = true;
};

const handleSubmit = async () => {
  const { valid } = await form.value.validate();
  if (!valid) return;

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
    
    // ອັບເດດຂໍ້ມູນໃນໜ້າ Local ເລີຍ ບໍ່ຕ້ອງໂຫຼດໃໝ່ໝົດ
    const now = new Date().toISOString();
    // ດຶງຂໍ້ມູນໃໝ່ເພື່ອຄວາມຊົວ
    await fetchData();
    
    dialog.value = false;
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

const formatDate = (dateStr, withTime = false) => {
  if (!dateStr) return '';
  const opts = { day: 'numeric', month: 'short' };
  if(withTime) {
      opts.hour = '2-digit';
      opts.minute = '2-digit';
  }
  return new Date(dateStr).toLocaleDateString('lo-LA', opts);
};

const getRelativeTime = (dateStr) => {
    const due = new Date(dateStr);
    const now = new Date();
    const diff = due - now;
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));

    if (diff < 0) return 'ກາຍກຳນົດແລ້ວ';
    if (days === 0) return 'ມື້ນີ້';
    if (days === 1) return 'ມື້ອື່ນ';
    return `ອີກ ${days} ມື້`;
};

const isOverdue = (item) => {
  if (item.submission) return false;
  return new Date() > new Date(item.due_date);
};

const isGraded = (item) => item?.submission?.score !== null && item?.submission?.score !== undefined;

const getStatusColor = (item) => {
  if (item.submission) return item.submission.score !== null ? 'success' : 'info'; // Green if graded, Blue if submitted
  return isOverdue(item) ? 'error' : 'warning'; // Red if overdue, Orange if pending
};

const getStatusIcon = (item) => {
  if (item.submission) return item.submission.score !== null ? 'mdi-check-decagram' : 'mdi-send-check';
  return isOverdue(item) ? 'mdi-alert-circle' : 'mdi-clock-outline';
};

const getStatusText = (item) => {
  if (item.submission) return item.submission.score !== null ? 'ກວດແລ້ວ' : 'ສົ່ງແລ້ວ';
  return isOverdue(item) ? 'ກາຍກຳນົດ' : 'ຄ້າງສົ່ງ';
};

onMounted(fetchData);
</script>

<style scoped>
.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.gap-2 { gap: 8px; }
.border-s-lg { border-left-width: 6px !important; }
.assignment-card {
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
}
.assignment-card:active {
    transform: scale(0.98);
}
</style>