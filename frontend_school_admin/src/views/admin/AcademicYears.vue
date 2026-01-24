<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h2 class="text-primary mb-4">
          <v-icon icon="mdi-calendar-range" class="mr-2"></v-icon>
          ຈັດການປີການສຶກສາ (Academic Years)
        </h2>
      </v-col>
    </v-row>

    <v-card elevation="2" rounded="lg">
      <v-card-title class="d-flex align-center py-3">
        <span>ລາຍການປີການສຶກສາ</span>
        <v-spacer></v-spacer>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openDialog()">
          ເພີ່ມປີໃໝ່
        </v-btn>
      </v-card-title>

      <v-data-table :headers="headers" :items="years" :loading="loading">
        <template v-slot:item.is_active="{ item }">
          <v-chip v-if="item.is_active" color="success" size="small" prepend-icon="mdi-check-circle">
            ປະຈຸບັນ
          </v-chip>
          <v-chip v-else color="grey" size="small">
            ເກົ່າ
          </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn icon="mdi-pencil" size="small" color="primary" variant="text" @click="openDialog(item)"></v-btn>
          <v-btn icon="mdi-delete" size="small" color="error" variant="text" @click="deleteItem(item)"></v-btn>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="dialog" max-width="400px">
      <v-card rounded="lg">
        <v-card-title class="bg-primary text-white">
          {{ editedId ? 'ແກ້ໄຂປີການສຶກສາ' : 'ເພີ່ມປີການສຶກສາໃໝ່' }}
        </v-card-title>
        <v-card-text class="pa-4">
          <v-form @submit.prevent="save">
            <v-text-field 
                v-model="editedItem.name" 
                label="ຊື່ປີການສຶກສາ (ຕົວຢ່າງ: 2025-2026)" 
                variant="outlined"
                autofocus
            ></v-text-field>
            <v-switch 
                v-model="editedItem.is_active" 
                label="ຕັ້ງເປັນປີປະຈຸບັນ (Active Year)" 
                color="success"
                inset
            ></v-switch>
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
import { getAcademicYears, createAcademicYear, updateAcademicYear, deleteAcademicYear } from '../../services/api';

const years = ref([]);
const loading = ref(false);
const dialog = ref(false);
const editedId = ref(null);
const editedItem = ref({ name: '', is_active: false });

const headers = [
  { title: 'ຊື່ປີການສຶກສາ', key: 'name', align: 'start' },
  { title: 'ສະຖານະ', key: 'is_active', align: 'center' },
  { title: 'ຈັດການ', key: 'actions', align: 'end', sortable: false },
];

const fetchData = async () => {
  loading.value = true;
  try {
    const res = await getAcademicYears();
    years.value = res.data;
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
    editedItem.value = { name: '', is_active: false };
  }
  dialog.value = true;
};

const save = async () => {
  try {
    if (editedId.value) {
      await updateAcademicYear(editedId.value, editedItem.value);
    } else {
      await createAcademicYear(editedItem.value);
    }
    dialog.value = false;
    fetchData(); // ໂຫຼດຂໍ້ມູນໃໝ່
  } catch (error) {
    alert("ເກີດຂໍ້ຜິດພາດ: " + (error.response?.data?.detail || error.message));
  }
};

const deleteItem = async (item) => {
  if (confirm(`ຕ້ອງການລຶບປີ ${item.name} ແທ້ບໍ່?`)) {
    try {
      await deleteAcademicYear(item.id);
      fetchData();
    } catch (error) {
      alert("ລຶບບໍ່ໄດ້: " + (error.response?.data?.detail || "ມີການໃຊ້ງານປີນີ້ຢູ່"));
    }
  }
};

onMounted(fetchData);
</script>