<template>
  <v-container>
    <v-card elevation="0" class="bg-transparent mb-4">
      <div class="d-flex flex-wrap align-center justify-space-between gap-3">
        <div>
          <h2 class="text-h5 font-weight-bold text-primary">ສະບາຍດີ, ຜູ້ປົກຄອງ! 👋</h2>
          <div class="text-body-2 text-grey">ຕິດຕາມຜົນການຮຽນຂອງລູກຫຼານທ່ານ</div>
        </div>
        
        <v-select
          v-model="selectedChildId"
          :items="children"
          item-title="name" 
          item-value="id"
          label="ເລືອກນັກຮຽນ"
          variant="solo-filled"
          density="compact"
          hide-details
          prepend-inner-icon="mdi-face-man-shimmer"
          style="min-width: 250px;"
          class="rounded-lg"
          @update:model-value="loadChildData"
          :loading="loadingChildren"
        >
          <template v-slot:selection="{ item }">
             <span class="font-weight-bold text-primary">{{ item.title }}</span>
          </template>
          <template v-slot:item="{ props, item }">
            <v-list-item v-bind="props" :subtitle="item.raw.class_name"></v-list-item>
          </template>
        </v-select>
      </div>
    </v-card>

    <div v-if="loading" class="text-center py-10">
      <v-progress-circular indeterminate size="50" color="primary"></v-progress-circular>
      <div class="mt-2 text-grey">ກຳລັງໂຫຼດຂໍ້ມູນ...</div>
    </div>

    <div v-else-if="selectedChildId && dashboard">
      
      <v-row class="mb-4">
        <v-col cols="12" sm="4">
          <v-card class="rounded-xl pa-4" elevation="2">
            <div class="d-flex align-center">
              <v-avatar color="green-lighten-5" size="56" class="text-green">
                <v-icon size="32">mdi-star-face</v-icon>
              </v-avatar>
              <div class="ml-4">
                <div class="text-caption text-grey font-weight-bold">ຄະແນນພຶດຕິກຳ</div>
                <div class="text-h5 font-weight-bold text-green">
                  {{ dashboard.student_info?.total_points || 0 }}
                  <span class="text-body-2 text-grey">ຄະແນນ</span>
                </div>
              </div>
            </div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="4">
          <v-card class="rounded-xl pa-4" elevation="2">
            <div class="d-flex align-center">
              <v-avatar color="blue-lighten-5" size="56" class="text-blue">
                <v-icon size="32">mdi-google-classroom</v-icon>
              </v-avatar>
              <div class="ml-4">
                <div class="text-caption text-grey font-weight-bold">ຫ້ອງຮຽນປັດຈຸບັນ</div>
                <div class="text-h5 font-weight-bold text-blue">
                  {{ dashboard.student_info?.class_name || 'N/A' }}
                </div>
              </div>
            </div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="4">
          <v-card class="rounded-xl pa-4" elevation="2">
            <div class="d-flex align-center">
              <v-avatar color="orange-lighten-5" size="56" class="text-orange">
                <v-icon size="32">mdi-notebook-alert</v-icon>
              </v-avatar>
              <div class="ml-4">
                <div class="text-caption text-grey font-weight-bold">ວຽກບ້ານຄ້າງສົ່ງ</div>
                <div class="text-h5 font-weight-bold text-orange">
                  {{ dashboard.assignments?.length || 0 }} 
                  <span class="text-body-2 text-grey">ລາຍການ</span>
                </div>
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>

      <v-card rounded="xl" elevation="2" class="overflow-hidden">
        <v-tabs v-model="tab" color="primary" align-tabs="start" class="bg-grey-lighten-5 px-4">
          <v-tab value="GRADES" class="text-none font-weight-bold"><v-icon start>mdi-chart-bar</v-icon> ຜົນການຮຽນ</v-tab>
          <v-tab value="HOMEWORK" class="text-none font-weight-bold"><v-icon start>mdi-book-open-variant</v-icon> ປະຫວັດວຽກບ້ານ</v-tab>
          <v-tab value="SCHEDULE" class="text-none font-weight-bold"><v-icon start>mdi-calendar-clock</v-icon> ຕາຕະລາງຮຽນວັນນີ້</v-tab>
        </v-tabs>

        <v-divider></v-divider>

        <v-window v-model="tab" class="pa-0">
          
          <v-window-item value="GRADES">
            <v-table hover>
              <thead>
                <tr class="bg-grey-lighten-4">
                  <th>ເດືອນ</th>
                  <th class="text-center">ກາງພາກ</th>
                  <th class="text-center">ທ້າຍພາກ</th>
                  <th class="text-center">ຄະແນນລວມ</th>
                  <th class="text-center">ເກຣດ</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(g, i) in grades" :key="i">
                  <td class="font-weight-bold text-primary">{{ g.month_name }}</td>
                  <td class="text-center text-grey">{{ g.midterm || '-' }}</td>
                  <td class="text-center text-grey">{{ g.final || '-' }}</td>
                  <td class="text-center font-weight-bold">{{ g.score }}</td>
                  <td class="text-center">
                    <v-chip :color="getGradeColor(g.grade)" size="small" class="font-weight-bold px-3">
                      {{ g.grade }}
                    </v-chip>
                  </td>
                </tr>
                <tr v-if="grades.length === 0">
                  <td colspan="5" class="text-center py-8 text-grey">ຍັງບໍ່ມີຂໍ້ມູນຄະແນນ</td>
                </tr>
              </tbody>
            </v-table>
          </v-window-item>

          <v-window-item value="HOMEWORK">
            <v-list lines="two" class="pa-0">
              <template v-for="(hw, i) in assignments" :key="i">
                <v-list-item class="py-3">
                  <template v-slot:prepend>
                    <v-icon 
                      :color="hw.status === 'SUBMITTED' ? 'success' : (hw.status === 'LATE' ? 'error' : 'orange')" 
                      class="mr-3 bg-grey-lighten-4 rounded-circle pa-2"
                    >
                      {{ hw.status === 'SUBMITTED' ? 'mdi-check' : 'mdi-clock-outline' }}
                    </v-icon>
                  </template>
                  
                  <v-list-item-title class="font-weight-bold text-body-1">{{ hw.title }}</v-list-item-title>
                  <v-list-item-subtitle class="mt-1">
                    <v-icon size="small" start>mdi-calendar</v-icon> 
                    ສົ່ງກ່ອນ: {{ formatDate(hw.due_date) }}
                    <span v-if="hw.score" class="ml-3 text-success font-weight-bold">
                      (ໄດ້ຄະແນນ: {{ hw.score }})
                    </span>
                  </v-list-item-subtitle>
                  
                  <template v-slot:append>
                    <v-chip size="small" :color="getStatusColor(hw.status)" label class="font-weight-bold">
                      {{ getStatusText(hw.status) }}
                    </v-chip>
                  </template>
                </v-list-item>
                <v-divider v-if="i < assignments.length - 1"></v-divider>
              </template>
              
              <div v-if="assignments.length === 0" class="text-center py-8 text-grey">
                ບໍ່ມີປະຫວັດວຽກບ້ານ
              </div>
            </v-list>
          </v-window-item>

          <v-window-item value="SCHEDULE">
             <v-list>
                <v-list-item v-for="(sch, i) in dashboard.schedule" :key="i" :title="sch.subject_name" :subtitle="`${sch.start_time} - ${sch.end_time}`">
                    <template v-slot:prepend>
                        <v-avatar color="primary" variant="tonal" size="40" class="mr-2">
                            <span class="text-h6">{{ i + 1 }}</span>
                        </v-avatar>
                    </template>
                    <template v-slot:append>
                        <v-chip size="small">{{ sch.room || 'ບໍ່ລະບຸຫ້ອງ' }}</v-chip>
                    </template>
                </v-list-item>
                <div v-if="!dashboard.schedule || dashboard.schedule.length === 0" class="text-center py-8 text-grey">
                    ບໍ່ມີຕາຕະລາງຮຽນສຳລັບມື້ນີ້
                </div>
             </v-list>
          </v-window-item>

        </v-window>
      </v-card>
    </div>

    <div v-else class="text-center py-15 text-grey">
      <v-icon size="80" color="grey-lighten-2" class="mb-4">mdi-account-group-outline</v-icon>
      <div class="text-h6">ຍັງບໍ່ໄດ້ເລືອກນັກຮຽນ</div>
      <div class="text-body-2">ກະລຸນາເລືອກນັກຮຽນຈາກເມນູດ້ານເທິງເພື່ອເບິ່ງຂໍ້ມູນ</div>
    </div>

  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { 
  getMyChildren, 
  getChildDashboard, 
  getChildGrades, 
  getChildAssignments 
} from '../../services/api';

const children = ref([]);
const selectedChildId = ref(null);
const loading = ref(false);
const loadingChildren = ref(false);
const tab = ref("GRADES");

// Data States (Initialize structure to avoid null errors)
const dashboard = ref({ 
    student_info: { total_points: 0, class_name: '' }, 
    assignments: [],
    schedule: [] 
});
const grades = ref([]);
const assignments = ref([]);

// 1. Load Children List
const fetchChildren = async () => {
  loadingChildren.value = true;
  try {
    const res = await getMyChildren();
    children.value = res.data;
    
    // Auto-select first child if available
    if (children.value.length > 0) {
      selectedChildId.value = children.value[0].id;
      loadChildData();
    }
  } catch (error) {
    console.error("Error fetching children", error);
  } finally {
    loadingChildren.value = false;
  }
};

// 2. Load Selected Child Data
const loadChildData = async () => {
  if (!selectedChildId.value) return;
  
  loading.value = true;
  try {
    const id = selectedChildId.value;
    
    // Parallel Requests for better performance
    const [dashRes, gradeRes, assignRes] = await Promise.all([
      getChildDashboard(id),
      getChildGrades(id),
      getChildAssignments(id)
    ]);

    dashboard.value = dashRes.data;
    grades.value = gradeRes.data;
    assignments.value = assignRes.data;

  } catch (error) {
    console.error("Error loading child details", error);
    alert("ບໍ່ສາມາດໂຫຼດຂໍ້ມູນໄດ້ ກະລຸນາລອງໃໝ່");
  } finally {
    loading.value = false;
  }
};

// Helpers
const getGradeColor = (g) => {
  if(g === 'A') return 'success';
  if(g === 'B') return 'info';
  if(g === 'C') return 'warning';
  if(g === 'D' || g === 'F') return 'error';
  return 'grey';
};

const getStatusColor = (s) => {
  if(s === 'SUBMITTED') return 'success';
  if(s === 'PENDING') return 'warning';
  if(s === 'LATE') return 'error';
  return 'grey';
};

const getStatusText = (s) => {
    const map = {
        'SUBMITTED': 'ສົ່ງແລ້ວ',
        'PENDING': 'ລໍຖ້າສົ່ງ',
        'LATE': 'ສົ່ງຊ້າ'
    };
    return map[s] || s;
};

const formatDate = (d) => {
    if(!d) return '-';
    return new Date(d).toLocaleDateString('lo-LA', { day: 'numeric', month: 'long', year: 'numeric' });
};

onMounted(fetchChildren);
</script>

<style scoped>
.gap-3 {
    gap: 12px;
}
</style>