<template>
  <v-card rounded="xl" elevation="3">
    <v-card-title class="bg-amber-darken-2 text-white pa-4">
      <v-icon start>mdi-history</v-icon> ປະຫວັດການແກ້ໄຂຄະແນນ
    </v-card-title>

    <v-card-text class="pa-6">
      <v-timeline density="compact" align="start">
        <v-timeline-item
          v-for="log in logs"
          :key="log.id"
          dot-color="amber"
          size="x-small"
        >
          <div class="mb-4">
            <div class="d-flex justify-space-between align-center">
              <strong class="text-subtitle-1">
                ແກ້ໄຂ {{ log.score_type }}
              </strong>
              <span class="text-caption text-grey">{{ formatDate(log.updated_at) }}</span>
            </div>
            
            <div class="d-flex align-center my-2">
              <v-chip size="small" color="grey" variant="flat">{{ log.old_score }}</v-chip>
              <v-icon icon="mdi-arrow-right" class="mx-2" size="small"></v-icon>
              <v-chip size="small" color="success" variant="flat" class="font-weight-bold">
                {{ log.new_score }}
              </v-chip>
            </div>

            <div class="text-body-2 text-grey-darken-2">
              <strong>ເຫດຜົນ:</strong> {{ log.reason }}
            </div>
            <div class="text-caption font-italic text-primary mt-1">
              ໂດຍ: {{ log.updated_by_name }}
            </div>
          </div>
        </v-timeline-item>
      </v-timeline>

      <v-alert v-if="logs.length === 0" type="info" variant="tonal" class="mt-4">
        ຍັງບໍ່ມີປະຫວັດການແກ້ໄຂສຳລັບນັກຮຽນຄົນນີ້ໃນເດືອນນີ້.
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
// import ໃຫ້ຖືກຕ້ອງ
import { getGradeAuditLogs } from '../services/api';

const props = defineProps(['studentId', 'monthId']);
const logs = ref([]);

const fetchLogs = async () => {
  if (!props.studentId || !props.monthId) return;
  
  try {
    // ✅ ແກ້ໄຂ: ໃຊ້ Function getGradeAuditLogs ແທນ api.get
    const res = await getGradeAuditLogs(props.studentId, props.monthId);
    logs.value = res.data;
  } catch (error) {
    console.error("Error loading logs:", error);
  }
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('lo-LA', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
  });
};

onMounted(fetchLogs);

// ✅ ເພີ່ມ: ຖ້າ studentId ປ່ຽນ (ກົດເບິ່ງຄົນໃໝ່) ໃຫ້ໂຫຼດຂໍ້ມູນໃໝ່ທັນທີ
watch(() => props.studentId, fetchLogs);
</script>