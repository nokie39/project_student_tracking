<template>
  <v-app>
    <v-app-bar color="white" elevation="0" border="b" density="comfortable">
      <div class="d-flex align-center ml-2">
        <v-avatar color="indigo" variant="tonal" size="36" class="mr-2 rounded-lg">
          <v-icon icon="mdi-human-male-female-child" size="20"></v-icon>
        </v-avatar>
        <div v-if="!mobile">
          <div class="text-subtitle-2 font-weight-bold text-indigo" style="line-height: 1.2;">Parent Portal</div>
          <div class="text-caption text-grey" style="font-size: 10px;">Monitoring App</div>
        </div>
      </div>

      <v-spacer></v-spacer>

      <div style="width: 180px;" class="mr-2">
        <v-select
          v-model="selectedChildId"
          :items="children"
          item-title="name"
          item-value="id"
          label="ເລືອກລູກຫຼານ"
          variant="solo-filled"
          density="compact"
          hide-details
          bg-color="indigo-lighten-5"
          prepend-inner-icon="mdi-face-man-profile"
          class="rounded-lg text-caption"
          @update:model-value="changeChild"
        >
          <template v-slot:selection="{ item }">
             <span class="text-truncate font-weight-bold text-indigo">{{ item.title }}</span>
          </template>
        </v-select>
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
      <v-list density="compact" nav class="mt-2">
        <v-list-item prepend-icon="mdi-view-dashboard" title="ພາບລວມ" to="/parent/dashboard" active-color="indigo" rounded="lg" class="mb-1"></v-list-item>
        <v-list-item prepend-icon="mdi-book-open-variant" title="ວຽກບ້ານ" to="/parent/assignments" active-color="indigo" rounded="lg" class="mb-1"></v-list-item>
        <v-list-item prepend-icon="mdi-chart-line" title="ຜົນການຮຽນ" to="/parent/grades" active-color="indigo" rounded="lg" class="mb-1"></v-list-item>
        
        <v-list-item prepend-icon="mdi-calendar-clock" title="ຕາຕະລາງ" to="/parent/schedule" active-color="indigo" rounded="lg" class="mb-1"></v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="pa-2">
          <v-btn block variant="text" icon="mdi-chevron-left" @click.stop="rail = !rail"></v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-main class="bg-grey-lighten-5 pb-16">
      <router-view v-slot="{ Component }">
        <v-fade-transition mode="out-in">
          <component :is="Component" :key="selectedChildId" /> 
        </v-fade-transition>
      </router-view>
    </v-main>

    <v-bottom-navigation
      v-if="mobile"
      grow
      color="indigo"
      mode="shift"
      elevation="4"
      class="rounded-t-xl"
    >
      <v-btn to="/parent/dashboard">
        <v-icon>mdi-view-dashboard-outline</v-icon>
        <span>ພາບລວມ</span>
      </v-btn>

      <v-btn to="/parent/assignments">
        <v-icon>mdi-book-clock-outline</v-icon>
        <span>ວຽກບ້ານ</span>
      </v-btn>

      <v-btn to="/parent/grades">
        <v-icon>mdi-chart-bar</v-icon>
        <span>ຜົນຮຽນ</span>
      </v-btn>

      <v-btn to="/parent/schedule">
        <v-icon>mdi-calendar-month-outline</v-icon>
        <span>ຕາຕະລາງ</span>
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

const children = ref([]);
const selectedChildId = ref(null);

onMounted(async () => {
  try {
    const res = await getMyChildren();
    children.value = res.data;

    const storedId = localStorage.getItem('selectedChildId');
    
    if (storedId && children.value.find(c => c.id == storedId)) {
        selectedChildId.value = parseInt(storedId);
    } else if (children.value.length > 0) {
        selectedChildId.value = children.value[0].id;
        localStorage.setItem('selectedChildId', selectedChildId.value);
    }
  } catch (error) {
    console.error("Error fetching children:", error);
    if(error.response && error.response.status === 401) handleLogout();
  }
});

const changeChild = (newId) => {
    localStorage.setItem('selectedChildId', newId);
    window.location.reload(); 
};

const handleLogout = () => {
  localStorage.clear();
  router.push('/login');
};
</script>

<style scoped>
.v-app-bar {
    background-color: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(5px);
}
</style>