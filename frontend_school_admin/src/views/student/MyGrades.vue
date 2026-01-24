<template>
  <v-container class="pa-4">
    <div class="mb-4">
      <h2 class="text-h5 font-weight-bold text-success">
        <v-icon start>mdi-chart-line</v-icon> ຜົນການຮຽນ
      </h2>
      <div class="text-caption text-grey">ປະຫວັດຄະແນນປະຈຳເດືອນ</div>
    </div>

    <div v-if="loading" class="d-flex justify-center py-10">
      <v-progress-circular indeterminate color="success"></v-progress-circular>
    </div>

    <div v-else>
      <v-expansion-panels variant="inset" class="mb-6">
        <v-expansion-panel
          v-for="(item, i) in grades"
          :key="i"
          elevation="2"
          rounded="xl"
          class="mb-2"
        >
          <v-expansion-panel-title>
            <div class="d-flex align-center w-100 justify-space-between mr-2">
              <div class="font-weight-bold text-body-1">{{ item.month_name }}</div>
              <div class="d-flex align-center">
                <div class="text-h6 font-weight-bold mr-3">{{ item.total_score }}</div>
                <v-chip
                  :color="getGradeColor(item.grade)"
                  size="small"
                  class="font-weight-bold px-3"
                  variant="flat"
                >
                  {{ item.grade }}
                </v-chip>
              </div>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <v-divider class="mb-3"></v-divider>
            <v-row dense>
              <v-col cols="6">
                <div class="grade-detail-box bg-blue-lighten-5">
                  <div class="text-caption text-blue-darken-2">ມາຮຽນ</div>
                  <div class="text-h6 font-weight-bold text-blue">{{ item.details.attendance }}</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="grade-detail-box bg-orange-lighten-5">
                  <div class="text-caption text-orange-darken-2">ວຽກບ້ານ</div>
                  <div class="text-h6 font-weight-bold text-orange">{{ item.details.homework }}</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="grade-detail-box bg-purple-lighten-5">
                  <div class="text-caption text-purple-darken-2">ເສັງກາງພາກ</div>
                  <div class="text-h6 font-weight-bold text-purple">{{ item.details.midterm }}</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="grade-detail-box bg-teal-lighten-5">
                  <div class="text-caption text-teal-darken-2">ເສັງທ້າຍພາກ</div>
                  <div class="text-h6 font-weight-bold text-teal">{{ item.details.final }}</div>
                </div>
              </v-col>
            </v-row>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <div v-if="grades.length === 0" class="text-center py-10 text-grey">
        <v-icon size="64" color="grey-lighten-2" class="mb-2">mdi-notebook-off</v-icon>
        <div>ຍັງບໍ່ມີຂໍ້ມູນຄະແນນ</div>
      </div>
    </div>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getMyGrades } from '../../services/api';

const grades = ref([]);
const loading = ref(false);

const fetchData = async () => {
  loading.value = true;
  try {
    const res = await getMyGrades();
    grades.value = res.data;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const getGradeColor = (g) => {
  if (g === 'A') return 'success';
  if (g === 'B') return 'info';
  if (g === 'C') return 'warning';
  if (g === 'D' || g === 'F') return 'error';
  return 'grey';
};

onMounted(fetchData);
</script>

<style scoped>
.grade-detail-box {
  border-radius: 12px;
  padding: 10px;
  text-align: center;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
</style>