<template>
  <v-container fluid class="bg-grey-lighten-5 fill-height align-start pa-0 pa-md-4">
    
    <v-card flat color="transparent" class="w-100" style="max-width: 900px; margin: 0 auto;">
      
      <div class="pa-4 pb-2">
        <h1 class="text-h5 font-weight-bold text-indigo">
          <v-icon start>mdi-book-clock</v-icon> ວຽກບ້ານຂອງລູກ
        </h1>
        <div class="text-body-2 text-grey">
          ຕິດຕາມການສົ່ງວຽກ (Read Only)
        </div>

        <v-tabs
          v-model="activeTab"
          color="indigo"
          bg-color="white"
          class="rounded-lg shadow-sm mt-4 border"
          grow
        >
          <v-tab value="pending">
            <v-badge color="error" :content="pendingCount" v-if="pendingCount > 0" inline>
              ຄ້າງສົ່ງ
            </v-badge>
            <span v-else>ຄ້າງສົ່ງ</span>
          </v-tab>
          <v-tab value="completed">ສົ່ງແລ້ວ</v-tab>
        </v-tabs>
      </div>

      <div class="px-4 pb-16">
        <div v-if="loading" class="mt-4 text-center">
          <v-progress-circular indeterminate color="indigo"></v-progress-circular>
        </div>

        <div v-else-if="filteredAssignments.length === 0" class="text-center py-10">
          <v-icon size="60" color="grey-lighten-2">mdi-checkbox-multiple-marked-outline</v-icon>
          <div class="text-grey mt-2">ບໍ່ມີຂໍ້ມູນໃນສ່ວນນີ້</div>
        </div>

        <v-row v-else dense class="mt-2">
          <v-col cols="12" v-for="item in filteredAssignments" :key="item.id">
            
            <v-card 
              elevation="1" 
              rounded="lg" 
              class="mb-2 border-s-lg"
              :style="{ 'border-left-color': getStatusColor(item) + ' !important' }"
              @click="openDetail(item)"
              v-ripple
            >
              <div class="pa-3 d-flex justify-space-between align-start">
                <div class="d-flex align-start" style="min-width: 0;">
                    <div class="mr-3 mt-1">
                        <v-icon :color="getStatusColor(item)">{{ getStatusIcon(item) }}</v-icon>
                    </div>
                    <div>
                        <div class="text-subtitle-2 font-weight-bold text-truncate">{{ item.title }}</div>
                        <div class="text-caption text-grey">{{ item.class_name || 'General' }}</div>
                        <div class="text-caption mt-1" :class="isOverdue(item) ? 'text-error font-weight-bold' : 'text-grey-darken-1'">
                            <v-icon size="x-small" start>mdi-calendar-clock</v-icon> 
                            ກຳນົດ: {{ formatDate(item.due_date) }}
                        </div>
                    </div>
                </div>

                <div class="text-right">
                    <v-chip size="x-small" :color="getStatusColor(item)" variant="flat" class="font-weight-bold">
                        {{ getStatusText(item) }}
                    </v-chip>
                    <div v-if="item.score !== null" class="text-h6 text-success font-weight-bold mt-1">
                        {{ item.score }}
                    </div>
                </div>
              </div>
            </v-card>

          </v-col>
        </v-row>
      </div>

    </v-card>

    <v-dialog v-model="dialog" max-width="500">
        <v-card rounded="xl">
            <v-toolbar :color="getStatusColor(selectedItem)" dark density="compact">
                <v-btn icon @click="dialog = false"><v-icon>mdi-close</v-icon></v-btn>
                <v-toolbar-title class="text-subtitle-1 font-weight-bold">ລາຍລະອຽດວຽກບ້ານ</v-toolbar-title>
            </v-toolbar>
            
            <v-card-text class="bg-grey-lighten-5 pt-4">
                <v-card variant="outlined" class="bg-white mb-3 border-indigo">
                    <v-card-text>
                        <h3 class="text-h6 font-weight-bold mb-1">{{ selectedItem?.title }}</h3>
                        <p class="text-body-2 text-grey-darken-1">{{ selectedItem?.description || 'ບໍ່ມີລາຍລະອຽດເພີ່ມເຕີມ' }}</p>
                    </v-card-text>
                </v-card>

                <div v-if="selectedItem?.submission" class="mb-4">
                    <v-alert type="success" variant="tonal" border="start" density="compact">
                        <div class="text-subtitle-2 font-weight-bold">ສົ່ງແລ້ວເມື່ອ:</div>
                        <div class="text-caption">{{ formatDate(selectedItem.submission.submitted_at, true) }}</div>
                        <div v-if="selectedItem.submission.feedback" class="mt-2 pt-2 border-t">
                            <strong>ຄຳເຫັນຄູ:</strong> "{{ selectedItem.submission.feedback }}"
                        </div>
                    </v-alert>
                </div>
                <div v-else>
                    <v-alert type="warning" variant="tonal" border="start" density="compact">
                        ຍັງບໍ່ທັນສົ່ງວຽກ
                    </v-alert>
                </div>
            </v-card-text>
        </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { getChildAssignments } from '../../services/api';

const loading = ref(true);
const assignments = ref([]);
const activeTab = ref('pending');
const dialog = ref(false);
const selectedItem = ref(null);

const fetchAssignments = async () => {
    const childId = localStorage.getItem('selectedChildId');
    if (!childId) return;

    loading.value = true;
    try {
        const res = await getChildAssignments(childId);
        // Map data 
        assignments.value = res.data.map(a => ({
            ...a,
            submission: a.status === 'SUBMITTED' ? { score: a.score, submitted_at: new Date().toISOString() } : null 
        }));
    } catch (e) {
        console.error(e);
    } finally {
        loading.value = false;
    }
};

const pendingCount = computed(() => assignments.value.filter(x => !x.submission).length);
const filteredAssignments = computed(() => {
    if (activeTab.value === 'pending') {
        return assignments.value.filter(x => !x.submission).sort((a, b) => new Date(a.due_date) - new Date(b.due_date));
    }
    return assignments.value.filter(x => x.submission);
});

const isOverdue = (item) => !item.submission && new Date() > new Date(item.due_date);
const getStatusColor = (item) => item.submission ? 'success' : (isOverdue(item) ? 'error' : 'warning');
const getStatusIcon = (item) => item.submission ? 'mdi-check-circle' : (isOverdue(item) ? 'mdi-alert' : 'mdi-clock');
const getStatusText = (item) => item.submission ? 'ສົ່ງແລ້ວ' : (isOverdue(item) ? 'ກາຍກຳນົດ' : 'ຄ້າງສົ່ງ');
const formatDate = (d, t=false) => d ? new Date(d).toLocaleDateString('lo-LA', {day:'numeric', month:'short', hour: t?'2-digit':undefined, minute: t?'2-digit':undefined}) : '';

const openDetail = (item) => {
    selectedItem.value = item;
    dialog.value = true;
};

onMounted(fetchAssignments);
</script>

<style scoped>
.border-s-lg { border-left-width: 5px !important; }
.border-indigo { border-color: #3F51B5 !important; }
</style>