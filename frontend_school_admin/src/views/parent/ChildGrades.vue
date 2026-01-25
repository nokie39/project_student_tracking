<template>
  <v-container fluid class="bg-grey-lighten-5 fill-height align-start pa-0 pa-md-4">
    
    <div class="w-100 bg-teal-darken-1 pt-6 pb-12 px-6 rounded-b-xl shadow-lg position-relative text-center text-white">
       <div class="text-subtitle-1 opacity-90">ຜົນການຮຽນຂອງລູກ</div>
       <div class="text-h3 font-weight-bold mt-2">{{ averageScore }}</div>
       <div class="text-caption">ຄະແນນສະເລ່ຍລວມ (GPA)</div>
    </div>

    <v-container class="mt-n10 px-4 pb-16">
        <div v-if="loading" class="text-center mt-5">
            <v-progress-circular indeterminate color="teal"></v-progress-circular>
        </div>

        <div v-else-if="grades.length === 0" class="text-center py-10">
            <v-icon size="60" color="grey-lighten-2">mdi-chart-bar-off</v-icon>
            <div class="text-grey mt-2">ຍັງບໍ່ມີຂໍ້ມູນຄະແນນ</div>
        </div>

        <div v-else>
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
                            <v-avatar color="teal-lighten-5" class="mr-3 text-teal font-weight-bold rounded-lg">
                                {{ item.month_name.substring(0, 3) }}
                            </v-avatar>
                            <div class="flex-grow-1" style="min-width: 0;">
                                <div class="font-weight-bold text-truncate">{{ item.subject_name || item.month_name }}</div>
                                <div class="text-caption text-grey">
                                    <v-progress-linear :model-value="item.score" color="teal" height="4" rounded style="width: 50px;" class="d-inline-block mr-1"></v-progress-linear>
                                    {{ item.score }}%
                                </div>
                            </div>
                            <div class="text-right mr-2">
                                <v-chip size="small" :color="getGradeColor(item.grade)" class="font-weight-bold">
                                    {{ item.grade }}
                                </v-chip>
                            </div>
                        </div>
                    </v-expansion-panel-title>

                    <v-expansion-panel-text>
                        <v-row dense class="mt-1">
                            <v-col cols="6">
                                <div class="bg-grey-lighten-4 pa-2 rounded text-center">
                                    <div class="text-caption text-grey">ກາງພາກ</div>
                                    <div class="font-weight-bold">{{ item.midterm || 0 }}</div>
                                </div>
                            </v-col>
                            <v-col cols="6">
                                <div class="bg-grey-lighten-4 pa-2 rounded text-center">
                                    <div class="text-caption text-grey">ທ້າຍພາກ</div>
                                    <div class="font-weight-bold">{{ item.final || 0 }}</div>
                                </div>
                            </v-col>
                        </v-row>
                    </v-expansion-panel-text>
                </v-expansion-panel>
            </v-expansion-panels>
        </div>
    </v-container>

  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { getChildGrades } from '../../services/api';

const loading = ref(true);
const grades = ref([]);

const fetchData = async () => {
    const childId = localStorage.getItem('selectedChildId');
    if (!childId) return;

    loading.value = true;
    try {
        const res = await getChildGrades(childId);
        grades.value = res.data.grades || res.data; // Handle structure
    } catch (e) {
        console.error(e);
    } finally {
        loading.value = false;
    }
};

const averageScore = computed(() => {
    if (grades.value.length === 0) return '0.00';
    const sum = grades.value.reduce((a, b) => a + (b.score || 0), 0);
    return (sum / grades.value.length).toFixed(2);
});

const getGradeColor = (g) => {
    if (['A', 'B'].includes(g)) return 'success';
    if (['C', 'D'].includes(g)) return 'warning';
    return 'error';
};

onMounted(fetchData);
</script>