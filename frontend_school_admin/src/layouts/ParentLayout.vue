<template>
  <v-app>
    <v-app-bar color="white" elevation="1" density="comfortable">
      <div class="d-flex align-center ml-4">
        <v-avatar color="indigo" variant="tonal" size="36" class="mr-2 rounded-lg">
          <v-icon icon="mdi-human-male-female-child" size="24"></v-icon>
        </v-avatar>
        <div v-if="!mobile">
          <div class="text-subtitle-2 font-weight-bold text-indigo">Parent Portal</div>
        </div>
      </div>

      <v-spacer></v-spacer>

      <div style="width: 200px;" class="mr-4">
        <v-select
          v-model="selectedChildId"
          :items="children"
          item-title="name"
          item-value="id"
          label="ກະລຸນາເລືອກລູກ"
          variant="outlined"
          density="compact"
          hide-details
          color="indigo"
          prepend-inner-icon="mdi-account-child-circle"
          class="text-body-2"
          @update:model-value="changeChild"
        ></v-select>
      </div>
      
      <v-btn icon color="grey" variant="text" class="d-none d-sm-flex" @click="handleLogout">
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </v-app-bar>

    <v-navigation-drawer
      v-if="!mobile"
      v-model="drawer"
      :rail="rail"
      permanent
      @click="rail = false"
      elevation="1"
    >
      <v-list density="compact" nav class="mt-4">
        <v-list-item
            prepend-icon="mdi-view-dashboard"
            title="ພາບລວມ"
            to="/parent/dashboard"
            active-color="indigo"
            rounded="lg"
            class="mb-1"
        ></v-list-item>
        
        <v-list-item
            prepend-icon="mdi-book-clock"
            title="ວຽກບ້ານ"
            to="/parent/assignments"
            active-color="indigo"
            rounded="lg"
            class="mb-1"
        ></v-list-item>

        <v-list-item
            prepend-icon="mdi-chart-line"
            title="ຜົນການຮຽນ"
            to="/parent/grades"
            active-color="indigo"
            rounded="lg"
            class="mb-1"
        ></v-list-item>

        <v-list-item
            prepend-icon="mdi-calendar-month"
            title="ຕາຕະລາງຮຽນ"
            to="/parent/schedule"
            active-color="indigo"
            rounded="lg"
            class="mb-1"
        ></v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="pa-2">
           <v-btn block variant="text" icon="mdi-chevron-left" @click.stop="rail = !rail"></v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-main class="bg-grey-lighten-5">
      <div v-if="loading" class="d-flex justify-center align-center h-100">
         <v-progress-circular indeterminate color="indigo"></v-progress-circular>
      </div>
      
      <div v-else-if="children.length === 0" class="text-center mt-10 text-grey">
         <v-icon size="60">mdi-account-off</v-icon>
         <h3>ບໍ່ພົບຂໍ້ມູນລູກຫຼານໃນລະບົບ</h3>
         <p>ກະລຸນາຕິດຕໍ່ຫ້ອງການໂຮງຮຽນ</p>
         <v-btn color="error" class="mt-4" @click="handleLogout">ອອກຈາກລະບົບ</v-btn>
      </div>

      <router-view v-else v-slot="{ Component }">
         <v-fade-transition mode="out-in">
            <component :is="Component" :key="selectedChildId" />
         </v-fade-transition>
      </router-view>
    </v-main>

    <v-bottom-navigation
      v-if="mobile"
      grow
      color="indigo"
      bg-color="white"
      elevation="5"
    >
      <v-btn to="/parent/dashboard">
        <v-icon>mdi-view-dashboard</v-icon>
        <span class="text-caption">ພາບລວມ</span>
      </v-btn>

      <v-btn to="/parent/assignments">
        <v-icon>mdi-book-clock</v-icon>
        <span class="text-caption">ວຽກບ້ານ</span>
      </v-btn>

      <v-btn to="/parent/grades">
        <v-icon>mdi-chart-bar</v-icon>
        <span class="text-caption">ຜົນຮຽນ</span>
      </v-btn>

      <v-btn to="/parent/schedule">
        <v-icon>mdi-calendar</v-icon>
        <span class="text-caption">ຕາຕະລາງ</span>
      </v-btn>
    </v-bottom-navigation>

  </v-app>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useDisplay } from 'vuetify';
import { getMyChildren } from '../services/api';

const router = useRouter();
const { mobile } = useDisplay();
const drawer = ref(true);
const rail = ref(false);
const loading = ref(true);

const children = ref([]);
const selectedChildId = ref(null);

onMounted(async () => {
  try {
    const res = await getMyChildren();
    children.value = res.data;

    // Logic ເລືອກລູກ
    const storedId = localStorage.getItem('selectedChildId');
    
    // ກວດສອບວ່າ ID ທີ່ເກັບໄວ້ຍັງຖືກຕ້ອງບໍ່?
    const validChild = storedId ? children.value.find(c => c.id == storedId) : null;

    if (validChild) {
        selectedChildId.value = parseInt(storedId);
    } else if (children.value.length > 0) {
        // ຖ້າບໍ່ມີ ຫຼື ID ບໍ່ຖືກ -> ເລືອກຄົນທຳອິດ
        selectedChildId.value = children.value[0].id;
        localStorage.setItem('selectedChildId', selectedChildId.value);
    }
  } catch (error) {
    console.error("Error fetching children:", error);
    if(error.response && error.response.status === 401) {
        handleLogout();
    }
  } finally {
    loading.value = false;
  }
});

const changeChild = (newId) => {
    if(!newId) return;
    localStorage.setItem('selectedChildId', newId);
    // Reload ໜ້າເພື່ອບັງຄັບໃຫ້ Component ລູກໂຫລດຂໍ້ມູນໃໝ່
    window.location.reload(); 
};

const handleLogout = () => {
  localStorage.clear();
  router.push('/login');
};
</script>