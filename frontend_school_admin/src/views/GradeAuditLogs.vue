<template>
  <v-card rounded="xl" elevation="0">
    <v-card-title class="bg-grey-lighten-4 pa-4 d-flex align-center">
      <v-icon start color="primary">mdi-history</v-icon> 
      <span class="text-subtitle-1 font-weight-bold">ປະຫວັດການແກ້ໄຂຄະແນນ</span>
      <v-spacer></v-spacer>
      <v-btn icon="mdi-close" variant="text" density="compact" @click="$emit('close')"></v-btn>
    </v-card-title>

    <v-card-text class="pa-4" style="max-height: 400px; overflow-y: auto;">
      <div v-if="loading" class="text-center pa-4">
        <v-progress-circular indeterminate color="primary" size="24"></v-progress-circular>
      </div>

      <div v-else-if="logs.length === 0" class="text-center pa-8 text-grey">
        <v-icon size="40" class="mb-2">mdi-text-box-search-outline</v-icon>
        <p>ຍັງບໍ່ມີປະຫວັດການແກ້ໄຂ</p>
      </div>

      <v-timeline v-else density="compact" align="start" side="end">
        <v-timeline-item
          v-for="log in logs"
          :key="log.id"
          dot-color="amber-darken-2"
          size="x-small"
        >
          <div class="mb-1">
            <div class="d-flex justify-space-between align-center mb-1">
              <v-chip 
                size="x-small" 
                color="indigo-lighten-5" 
                class="text-indigo-darken-3 font-weight-bold" 
                variant="flat"
              >
                {{ log.subject_name }}
              </v-chip>
              <span class="text-caption text-grey">{{ formatDate(log.updated_at) }}</span>
            </div>
            
            <div class="d-flex align-center my-2">
              <v-chip size="x-small" color="grey-lighten-2" variant="flat" class="text-grey-darken-2">
                {{ log.old_score }}
              </v-chip>
              <v-icon icon="mdi-arrow-right" class="mx-1 text-grey-lighten-1" size="x-small"></v-icon>
              <v-chip size="x-small" color="green-lighten-4" variant="flat" class="text-green-darken-4 font-weight-bold">
                {{ log.new_score }}
              </v-chip>
            </div>

            <div class="bg-grey-lighten-5 pa-2 rounded mb-1">
              <div class="text-caption text-grey-darken-1">
                <v-icon start size="x-small">mdi-comment-quote-outline</v-icon>
                {{ log.reason }}
              </div>
            </div>
            
            <div class="text-caption text-primary d-flex align-center">
              <v-icon start size="x-small">mdi-account-edit</v-icon>
              {{ log.updated_by_name }}
            </div>
          </div>
        </v-timeline-item>
      </v-timeline>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { getGradeAuditLogs } from '../services/api';

const props = defineProps(['studentId', 'monthId']);
const logs = ref([]);
const loading = ref(false);

const fetchLogs = async () => {
  if (!props.studentId || !props.monthId) return;
  
  loading.value = true;
  try {
    const res = await getGradeAuditLogs(props.studentId, props.monthId);
    logs.value = res.data;
  } catch (error) {
    console.error("Error loading logs:", error);
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleString('lo-LA', {
    day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit'
  });
};

onMounted(fetchLogs);

// ໂຫຼດຂໍ້ມູນໃໝ່ທຸກຄັ້ງທີ່ ID ນັກຮຽນປ່ຽນ
watch(() => props.studentId, fetchLogs);
</script>

<style scoped>
::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-thumb {
  background: #e0e0e0; 
  border-radius: 4px;
}
</style>