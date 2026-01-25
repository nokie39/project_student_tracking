<template>
  <v-container fluid class="bg-grey-lighten-5 fill-height align-start pa-0 pa-md-4">
    
    <v-card class="w-100 rounded-xl elevation-2">
      <v-toolbar color="white" class="px-2 border-b">
        <v-toolbar-title class="text-h6 font-weight-bold text-grey-darken-3">
           <v-icon start color="primary">mdi-google-classroom</v-icon> 
        </v-toolbar-title>
        <v-spacer></v-spacer>
        
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="ຄົ້ນຫາຫ້ອງຮຽນ..."
          single-line
          hide-details
          variant="outlined"
          density="compact"
          class="mr-2"
          style="max-width: 300px;"
          rounded="lg"
        ></v-text-field>

        <v-btn color="primary" variant="flat" prepend-icon="mdi-plus" class="text-capitalize" rounded="lg" @click="openDialog()">
           ເພີ່ມຫ້ອງຮຽນ
        </v-btn>
      </v-toolbar>

      <v-data-table
        :headers="headers"
        :items="classes"
        :search="search"
        :loading="loading"
        class="bg-transparent"
        hover
      >
        <template v-slot:item.teacher="{ item }">
           <div class="d-flex align-center">
              <v-avatar color="blue-lighten-5" size="30" class="mr-2">
                 <span class="text-caption font-weight-bold text-blue">{{ item.teacher?.full_name?.charAt(0) || 'T' }}</span>
              </v-avatar>
              {{ item.teacher?.full_name || 'ຍັງບໍ່ລະບຸ' }}
           </div>
        </template>

        <template v-slot:item.academic_year="{ item }">
           <v-chip size="small" color="purple" variant="tonal" class="font-weight-bold">
              {{ item.academic_year?.name || '-' }}
           </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn icon size="small" variant="text" color="blue" @click="openDialog(item)">
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn icon size="small" variant="text" color="red" @click="confirmDelete(item)">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>

        <template v-slot:no-data>
           <div class="pa-4 text-center">
              <v-icon size="40" color="grey-lighten-2">mdi-google-classroom</v-icon>
              <div class="text-grey mt-2">ຍັງບໍ່ມີຂໍ້ມູນຫ້ອງຮຽນ</div>
           </div>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="dialog" max-width="500px">
      <v-card rounded="xl">
        <v-toolbar color="primary" density="compact">
           <v-toolbar-title class="text-subtitle-1 font-weight-bold ml-4">
              {{ editedItem.id ? 'ແກ້ໄຂຂໍ້ມູນ' : 'ເພີ່ມຫ້ອງຮຽນໃໝ່' }}
           </v-toolbar-title>
           <v-btn icon @click="dialog = false"><v-icon>mdi-close</v-icon></v-btn>
        </v-toolbar>

        <v-card-text class="pt-6">
          <v-form ref="form" v-model="valid" @submit.prevent="save">
            <v-row dense>
              <v-col cols="12">
                <v-text-field
                  v-model="editedItem.name"
                  label="ຊື່ຫ້ອງຮຽນ (ຕົວຢ່າງ: ປ.1/1)"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-label"
                  :rules="[v => !!v || 'ກະລຸນາໃສ່ຊື່ຫ້ອງຮຽນ']"
                  bg-color="grey-lighten-5"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <v-select
                  v-model="editedItem.year_id"
                  :items="years"
                  item-title="name"
                  item-value="id"
                  label="ສົກຮຽນ (Academic Year)"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-calendar-range"
                  bg-color="grey-lighten-5"
                  :rules="[v => !!v || 'ກະລຸນາເລືອກສົກຮຽນ']"
                ></v-select>
              </v-col>

              <v-col cols="12">
                <v-autocomplete
                  v-model="editedItem.teacher_id"
                  :items="teachers"
                  item-title="full_name"
                  item-value="id"
                  label="ຄູປະຈຳຫ້ອງ (Homeroom Teacher)"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-account-tie"
                  bg-color="grey-lighten-5"
                  clearable
                ></v-autocomplete>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-card-actions class="pa-4 pt-0">
          <v-spacer></v-spacer>
          <v-btn variant="text" color="grey-darken-1" @click="dialog = false">ຍົກເລີກ</v-btn>
          <v-btn color="primary" variant="elevated" :loading="saving" @click="save" rounded="lg" class="px-6">
             ບັນທຶກ
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialogDelete" max-width="400px">
      <v-card rounded="xl" class="pa-4 text-center">
        <v-icon color="error" size="60" class="mb-3">mdi-alert-circle-outline</v-icon>
        <h3 class="text-h6 font-weight-bold mb-2">ຢືນຢັນການລຶບ?</h3>
        <p class="text-grey mb-4">ທ່ານຕ້ອງການລຶບຫ້ອງຮຽນ <strong>{{ editedItem.name }}</strong> ແທ້ບໍ່? <br>ການກະທຳນີ້ບໍ່ສາມາດຍ້ອນກັບໄດ້.</p>
        <div class="d-flex justify-center gap-2">
           <v-btn color="grey-lighten-3" variant="flat" @click="dialogDelete = false" class="flex-grow-1">ຍົກເລີກ</v-btn>
           <v-btn color="error" variant="flat" @click="deleteItemConfirm" class="flex-grow-1">ລຶບເລີຍ</v-btn>
        </div>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../../services/api';

const loading = ref(true);
const saving = ref(false);
const search = ref('');
const dialog = ref(false);
const dialogDelete = ref(false);
const valid = ref(false);
const form = ref(null);

const headers = [
  { title: 'ID', key: 'id', align: 'start', width: '80px' },
  { title: 'ຊື່ຫ້ອງຮຽນ', key: 'name' },
  { title: 'ສົກຮຽນ', key: 'academic_year' },
  { title: 'ຄູປະຈຳຫ້ອງ', key: 'teacher' },
  { title: 'ຈັດການ', key: 'actions', sortable: false, align: 'end' },
];

const classes = ref([]);
const teachers = ref([]);
const years = ref([]);

const editedItem = ref({
  id: null,
  name: '',
  teacher_id: null,
  year_id: null
});

// --- API Calls ---
const fetchData = async () => {
  loading.value = true;
  try {
    const [classRes, teacherRes, yearRes] = await Promise.all([
      api.get('/academic/classes'),       // 1. ດຶງຫ້ອງຮຽນ
      api.get('/academic/teachers-list'), // 2. ດຶງລາຍຊື່ຄູ (ສຳລັບ Dropdown)
      api.get('/academic/years')          // 3. ດຶງສົກຮຽນ
    ]);
    
    classes.value = classRes.data;
    teachers.value = teacherRes.data;
    years.value = yearRes.data.filter(y => y.is_active); // ເອົາສະເພາະປີທີ່ Active ມາໃຫ້ເລືອກ
    
    // ຖ້າບໍ່ມີປີ Active ໃຫ້ເອົາມາທັງໝົດ
    if (years.value.length === 0) years.value = yearRes.data;

  } catch (error) {
    console.error("Error fetching data:", error);
  } finally {
    loading.value = false;
  }
};

// --- Actions ---
const openDialog = (item = null) => {
  if (item) {
    editedItem.value = { 
        id: item.id, 
        name: item.name, 
        teacher_id: item.teacher_id, 
        year_id: item.year_id 
    };
  } else {
    // Auto select active year
    const activeYear = years.value.find(y => y.is_active);
    editedItem.value = { 
        id: null, 
        name: '', 
        teacher_id: null, 
        year_id: activeYear ? activeYear.id : null 
    };
  }
  dialog.value = true;
};

const save = async () => {
  const { valid } = await form.value.validate();
  if (!valid) return;

  saving.value = true;
  try {
    if (editedItem.value.id) {
      // Update
      await api.put(`/academic/classes/${editedItem.value.id}`, editedItem.value);
    } else {
      // Create
      await api.post('/academic/classes', editedItem.value);
    }
    await fetchData();
    dialog.value = false;
  } catch (error) {
    alert("Error: " + (error.response?.data?.detail || error.message));
  } finally {
    saving.value = false;
  }
};

const confirmDelete = (item) => {
  editedItem.value = { ...item };
  dialogDelete.value = true;
};

const deleteItemConfirm = async () => {
  try {
    await api.delete(`/academic/classes/${editedItem.value.id}`);
    await fetchData();
    dialogDelete.value = false;
  } catch (error) {
    alert("ບໍ່ສາມາດລຶບໄດ້: " + (error.response?.data?.detail || "ອາດມີນັກຮຽນຢູ່ໃນຫ້ອງນີ້"));
  }
};

onMounted(fetchData);
</script>

<style scoped>
.gap-2 { gap: 8px; }
</style>