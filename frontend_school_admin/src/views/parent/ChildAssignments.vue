<template>
  <v-container fluid class="fill-height align-start bg-grey-lighten-5 pa-0">
    
    <v-card color="orange-darken-2" rounded="b-xl" class="pa-6 pb-12 w-100 mb-n10" elevation="4">
      <div class="d-flex align-center text-white">
        <v-btn icon="mdi-arrow-left" variant="text" color="white" @click="$router.back()"></v-btn>
        <span class="text-h6 font-weight-bold ml-2">ວຽກບ້ານຂອງລູກ</span>
      </div>
      <div class="text-center mt-2 text-white text-caption opacity-80">
        ຕິດຕາມການສົ່ງວຽກ ແລະ ຄວາມຮັບຜິດຊອບ
      </div>
    </v-card>

    <v-container class="px-4 mt-4">
      
      <v-tabs v-model="tab" color="orange-darken-2" align-tabs="center" class="mb-4 bg-white rounded-lg elevation-1">
        <v-tab value="ALL">ທັງໝົດ</v-tab>
        <v-tab value="PENDING">ຍັງບໍ່ສົ່ງ</v-tab>
        <v-tab value="SUBMITTED">ສົ່ງແລ້ວ</v-tab>
      </v-tabs>

      <div v-if="filteredAssignments.length > 0">
        <v-card 
          v-for="work in filteredAssignments" 
          :key="work.id" 
          class="mb-3 rounded-xl border-s-lg"
          :class="getStatusBorderColor(work.status)"
          elevation="1"
        >
          <v-card-item>
            <div class="d-flex justify-space-between mb-1">
              <v-chip size="x-small" :color="getStatusColor(work.status)" variant="flat" class="font-weight-bold">
                {{ getStatusText(work.status) }}
              </v-chip>
              <span class="text-caption text-grey">
                ກຳນົດ: {{ formatDate(work.due_date) }}
              </span>
            </div>
            
            <div class="text-subtitle-1 font-weight-bold text-grey-darken-3">{{ work.title }}</div>
            <div class="text-body-2 text-grey-darken-1 text-truncate">{{ work.description }}</div>
            
            <div v-if="work.score !== null" class="mt-2 text-right">
              <span class="text-caption font-weight-bold text-success">
                <v-icon size="small" color="success">mdi-check-circle</v-icon>
                ໄດ້ຄະແນນ: {{ work.score }}
              </span>
            </div>
          </v-card-item>
        </v-card>
      </div>

      <v-alert v-else type="info" variant="tonal" class="rounded-xl mt-4 text-center">
        ບໍ່ມີຂໍ້ມູນວຽກບ້ານໃນໝວດນີ້
      </v-alert>

    </v-container>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '../../services/api';

const route = useRoute();
const assignments = ref([]);
const tab = ref("ALL");

const fetchAssignments = async () => {
  try {
    const studentId = route.params.studentId;
    const res = await api.get(`/parents/student/${studentId}/assignments`);
    assignments.value = res.data;
  } catch (error) {
    console.error(error);
  }
};

// Filter ຕາມ Tab
const filteredAssignments = computed(() => {
  if (tab.value === 'ALL') return assignments.value;
  if (tab.value === 'PENDING') return assignments.value.filter(a => a.status === 'PENDING' || a.status === 'LATE');
  return assignments.value.filter(a => a.status === tab.value);
});

// Helpers
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('lo-LA', { day: 'numeric', month: 'short', year: 'numeric' });
};

const getStatusText = (status) => {
  if (status === 'SUBMITTED') return 'ສົ່ງແລ້ວ';
  if (status === 'LATE') return 'ກາຍກຳນົດ';
  return 'ລໍຖ້າສົ່ງ';
};

const getStatusColor = (status) => {
  if (status === 'SUBMITTED') return 'success';
  if (status === 'LATE') return 'error';
  return 'warning';
};

const getStatusBorderColor = (status) => {
  if (status === 'SUBMITTED') return 'border-success'; // ຕ້ອງຂຽນ class css ເພີ່ມ ຫຼື ໃຊ້ style
  return ''; 
};

onMounted(fetchAssignments);
</script>

<style scoped>
.border-s-lg {
  border-left-width: 6px !important;
}
/* Custom border colors */
.border-success { border-left-color: #4CAF50 !important; }
.border-warning { border-left-color: #FB8C00 !important; }
.border-error { border-left-color: #FF5252 !important; }
</style>