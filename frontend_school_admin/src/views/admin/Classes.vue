<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h2 class="text-primary mb-4">
          <v-icon icon="mdi-google-classroom" class="mr-2"></v-icon>
          ຈັດການຫ້ອງຮຽນ (Class Management)
        </h2>
      </v-col>
    </v-row>

    <v-card elevation="2" rounded="lg">
      <v-card-title class="d-flex align-center py-3">
        <span>ລາຍຊື່ຫ້ອງຮຽນ</span>
        <v-spacer></v-spacer>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openDialog()">
          ສ້າງຫ້ອງຮຽນ
        </v-btn>
      </v-card-title>

      <v-data-table :headers="headers" :items="classes" :loading="loading">
        <template v-slot:item.year_id="{ item }">
          <v-chip color="info" size="small" variant="outlined">
            {{ getYearName(item.year_id) }}
          </v-chip>
        </template>
        
        <template v-slot:item.teacher_id="{ item }">
           {{ getTeacherName(item.teacher_id) }}
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn icon="mdi-pencil" size="small" color="primary" variant="text" @click="openDialog(item)"></v-btn>
          <v-btn icon="mdi-delete" size="small" color="error" variant="text" @click="deleteItem(item)"></v-btn>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="dialog" max-width="500px">
      <v-card rounded="lg">
        <v-card-title class="bg-primary text-white">
          {{ editedId ? 'ແກ້ໄຂຫ້ອງຮຽນ' : 'ສ້າງຫ້ອງຮຽນໃໝ່' }}
        </v-card-title>
        <v-card-text class="pa-4">
          <v-form @submit.prevent="save">
            
            <v-text-field 
                v-model="editedItem.name" 
                label="ຊື່ຫ້ອງຮຽນ (ຕົວຢ່າງ: ມ.1/1)" 
                variant="outlined"
                class="mb-2"
            ></v-text-field>

            <v-select
                v-model="editedItem.year_id"
                :items="years"
                item-title="name"
                item-value="id"
                label="ປີການສຶກສາ"
                variant="outlined"
                class="mb-2"
            ></v-select>

            <v-select
                v-model="editedItem.teacher_id"
                :items="teachers"
                item-title="full_name"
                item-value="id"
                label="ຄູປະຈຳຫ້ອງ"
                variant="outlined"
            ></v-select>

          </v-form>
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn text @click="dialog = false">ຍົກເລີກ</v-btn>
          <v-btn color="primary" variant="elevated" @click="save">ບັນທຶກ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { 
    getClasses, createClass, updateClass, deleteClass, 
    getAcademicYears, getTeachersForDropdown 
} from '../../services/api';

const classes = ref([]);
const years = ref([]);
const teachers = ref([]);
const loading = ref(false);
const dialog = ref(false);
const editedId = ref(null);
const editedItem = ref({ name: '', year_id: null, teacher_id: null });

const headers = [
  { title: 'ຊື່ຫ້ອງຮຽນ', key: 'name', align: 'start' },
  { title: 'ປີການສຶກສາ', key: 'year_id', align: 'start' },
  { title: 'ຄູປະຈຳຫ້ອງ', key: 'teacher_id', align: 'start' },
  { title: 'ຈັດການ', key: 'actions', align: 'end', sortable: false },
];

// Helper Functions ຫາຊື່ຈາກ ID
const getYearName = (id) => years.value.find(y => y.id === id)?.name || id;
const getTeacherName = (id) => teachers.value.find(t => t.id === id)?.full_name || 'ບໍ່ລະບຸ';

const fetchData = async () => {
  loading.value = true;
  try {
    // ດຶງຂໍ້ມູນ 3 ຢ່າງພ້ອມກັນ: ຫ້ອງຮຽນ, ປີການສຶກສາ, ລາຍຊື່ຄູ
    const [classesRes, yearsRes, teachersRes] = await Promise.all([
        getClasses(),
        getAcademicYears(),
        getTeachersForDropdown()
    ]);
    
    classes.value = classesRes.data;
    years.value = yearsRes.data;
    teachers.value = teachersRes.data;

  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const openDialog = (item = null) => {
  if (item) {
    editedId.value = item.id;
    editedItem.value = { ...item };
  } else {
    editedId.value = null;
    editedItem.value = { name: '', year_id: null, teacher_id: null };
    
    // Auto Select ປີປະຈຸບັນ (Active Year)
    const activeYear = years.value.find(y => y.is_active);
    if (activeYear) editedItem.value.year_id = activeYear.id;
  }
  dialog.value = true;
};

const save = async () => {
  try {
    if (editedId.value) {
      await updateClass(editedId.value, editedItem.value);
    } else {
      await createClass(editedItem.value);
    }
    dialog.value = false;
    fetchData(); 
  } catch (error) {
    alert("ເກີດຂໍ້ຜິດພາດ: " + (error.response?.data?.detail || error.message));
  }
};

const deleteItem = async (item) => {
  if (confirm(`ຕ້ອງການລຶບຫ້ອງ ${item.name} ແທ້ບໍ່?`)) {
    try {
      await deleteClass(item.id);
      fetchData();
    } catch (error) {
      alert("ລຶບບໍ່ໄດ້: " + (error.response?.data?.detail || "ມີນັກຮຽນໃນຫ້ອງນີ້"));
    }
  }
};

onMounted(fetchData);
</script>