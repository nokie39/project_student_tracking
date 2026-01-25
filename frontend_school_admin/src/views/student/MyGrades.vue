<template>
  <v-container fluid class="bg-grey-lighten-5 fill-height align-start pa-0 pa-md-4">
    
    <v-card flat color="transparent" class="w-100" style="max-width: 800px; margin: 0 auto;">
      
      <div class="pa-4">
        <h1 class="text-h5 font-weight-bold text-primary mb-1">
          <v-icon start>mdi-chart-line-variant</v-icon> ຜົນການຮຽນຂອງຂ້ອຍ
        </h1>
        <div class="text-body-2 text-grey">
          ຕິດຕາມຄະແນນສະສົມ ແລະ ປະຫວັດການຮຽນ
        </div>
      </div>

      <div v-if="loading" class="px-4">
         <v-skeleton-loader type="image" class="mb-4 rounded-xl" height="150"></v-skeleton-loader>
         <v-skeleton-loader type="list-item-three-line" v-for="n in 3" :key="n" class="mb-2 rounded-lg"></v-skeleton-loader>
      </div>

      <div v-else class="px-4 pb-10">
        
        <v-card rounded="xl" elevation="4" class="mb-6 bg-gradient-primary text-white overflow-hidden">
           <div class="bg-pattern"></div>
           <v-card-text class="d-flex align-center justify-space-between pa-6 position-relative">
              <div>
                 <div class="text-subtitle-2 font-weight-medium opacity-90 mb-1">ຄະແນນສະເລ່ຍລວມ (Average)</div>
                 <div class="text-h2 font-weight-bold">{{ averageScore }}</div>
                 <div class="text-caption opacity-80 mt-1">ຈາກທັງໝົດ {{ grades.length }} ເດືອນ</div>
              </div>
              <div class="text-right">
                 <div class="text-h3 font-weight-bold mb-1">{{ calculateGrade(averageScore) }}</div>
                 <v-chip color="white" variant="flat" size="small" class="text-primary font-weight-bold">
                    Grade
                 </v-chip>
              </div>
           </v-card-text>
        </v-card>

        <div class="d-flex justify-space-between align-center mb-3 ml-1">
            <span class="text-subtitle-2 text-grey-darken-1 font-weight-bold">ລາຍລະອຽດແຕ່ລະເດືອນ</span>
            <v-chip size="x-small" color="grey" variant="text">ສົກຮຽນ 2025-2026</v-chip>
        </div>

        <v-expansion-panels variant="popout" class="grade-panels">
          <v-expansion-panel
            v-for="(item, i) in grades"
            :key="i"
            rounded="xl"
            elevation="1"
            bg-color="white"
            class="mb-2"
          >
            <v-expansion-panel-title class="py-3">
              <div class="d-flex align-center w-100">
                <v-avatar color="blue-lighten-5" class="mr-4 text-primary font-weight-bold rounded-lg" size="45">
                   {{ item.month_name.substring(0, 3) }}
                </v-avatar>
                
                <div class="flex-grow-1" style="min-width: 0;">
                   <div class="text-subtitle-1 font-weight-bold text-truncate">{{ item.month_name }}</div>
                   <div class="text-caption text-grey d-flex align-center">
                      <v-progress-linear 
                        :model-value="item.total_score" 
                        color="primary" 
                        height="4" 
                        rounded 
                        style="width: 60px;" 
                        class="mr-2"
                      ></v-progress-linear>
                      {{ item.total_score }}%
                   </div>
                </div>

                <div class="text-right mr-2">
                   <div class="text-h6 font-weight-bold text-grey-darken-3">{{ item.total_score }}</div>
                   <v-badge 
                      inline 
                      :color="getGradeColor(item.grade)" 
                      :content="item.grade"
                      class="font-weight-bold"
                   ></v-badge>
                </div>
              </div>
            </v-expansion-panel-title>

            <v-expansion-panel-text>
               <v-divider class="mb-4 border-dashed"></v-divider>
               
               <v-row dense>
                  <v-col cols="6" sm="3">
                     <div class="score-box bg-blue-lighten-5 pa-3 rounded-lg h-100">
                        <div class="d-flex justify-space-between align-center mb-2">
                            <v-icon color="blue" size="small">mdi-account-check</v-icon>
                            <span class="text-caption text-blue-darken-2 font-weight-bold">ມາຮຽນ</span>
                        </div>
                        <div class="text-h6 font-weight-bold text-blue-darken-3">{{ item.details.attendance }}</div>
                        <v-progress-linear :model-value="(item.details.attendance / 10) * 100" color="blue" height="4" rounded></v-progress-linear>
                        <div class="text-caption text-right text-grey mt-1">/10</div>
                     </div>
                  </v-col>

                  <v-col cols="6" sm="3">
                     <div class="score-box bg-orange-lighten-5 pa-3 rounded-lg h-100">
                        <div class="d-flex justify-space-between align-center mb-2">
                            <v-icon color="orange" size="small">mdi-book-edit</v-icon>
                            <span class="text-caption text-orange-darken-2 font-weight-bold">ວຽກບ້ານ</span>
                        </div>
                        <div class="text-h6 font-weight-bold text-orange-darken-3">{{ item.details.homework }}</div>
                        <v-progress-linear :model-value="(item.details.homework / 20) * 100" color="orange" height="4" rounded></v-progress-linear>
                        <div class="text-caption text-right text-grey mt-1">/20</div>
                     </div>
                  </v-col>

                  <v-col cols="6" sm="3">
                     <div class="score-box bg-purple-lighten-5 pa-3 rounded-lg h-100">
                        <div class="d-flex justify-space-between align-center mb-2">
                            <v-icon color="purple" size="small">mdi-file-percent</v-icon>
                            <span class="text-caption text-purple-darken-2 font-weight-bold">ກາງພາກ</span>
                        </div>
                        <div class="text-h6 font-weight-bold text-purple-darken-3">{{ item.details.midterm }}</div>
                        <v-progress-linear :model-value="(item.details.midterm / 30) * 100" color="purple" height="4" rounded></v-progress-linear>
                        <div class="text-caption text-right text-grey mt-1">/30</div>
                     </div>
                  </v-col>

                  <v-col cols="6" sm="3">
                     <div class="score-box bg-teal-lighten-5 pa-3 rounded-lg h-100">
                        <div class="d-flex justify-space-between align-center mb-2">
                            <v-icon color="teal" size="small">mdi-certificate</v-icon>
                            <span class="text-caption text-teal-darken-2 font-weight-bold">ທ້າຍພາກ</span>
                        </div>
                        <div class="text-h6 font-weight-bold text-teal-darken-3">{{ item.details.final }}</div>
                        <v-progress-linear :model-value="(item.details.final / 40) * 100" color="teal" height="4" rounded></v-progress-linear>
                        <div class="text-caption text-right text-grey mt-1">/40</div>
                     </div>
                  </v-col>
               </v-row>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>

        <div v-if="grades.length === 0" class="text-center py-10 mt-4">
           <v-icon size="80" color="grey-lighten-2" class="mb-4">mdi-chart-bar-off</v-icon>
           <div class="text-h6 text-grey">ຍັງບໍ່ມີຂໍ້ມູນຄະແນນ</div>
           <div class="text-caption text-grey-lighten-1">ຄະແນນຈະສະແດງເມື່ອຄູສອນບັນທຶກເຂົ້າລະບົບ</div>
        </div>

      </div>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { getMyGrades } from '../../services/api';

const grades = ref([]);
const loading = ref(true);

// Computed Average Score
const averageScore = computed(() => {
    if (grades.value.length === 0) return 0;
    const total = grades.value.reduce((sum, item) => sum + item.total_score, 0);
    return (total / grades.value.length).toFixed(2);
});

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

const calculateGrade = (score) => {
    if (score >= 80) return 'A';
    if (score >= 70) return 'B';
    if (score >= 60) return 'C';
    if (score >= 50) return 'D';
    return 'F';
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
.bg-gradient-primary {
    background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
}
.bg-pattern {
    position: absolute;
    top: -20px;
    right: -20px;
    width: 150px;
    height: 150px;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 20%, transparent 20%),
                radial-gradient(circle, rgba(255,255,255,0.1) 20%, transparent 20%);
    background-size: 30px 30px;
    border-radius: 50%;
    opacity: 0.5;
}
.grade-panels :deep(.v-expansion-panel-text__wrapper) {
    padding: 16px;
}
.score-box {
    transition: transform 0.2s;
}
.score-box:hover {
    transform: translateY(-2px);
}
.border-dashed {
    border-style: dashed;
}
</style>