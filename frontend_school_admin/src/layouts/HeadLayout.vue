<template>
  <v-layout>
    <v-navigation-drawer v-model="drawer" color="indigo-darken-3" elevation="3">
      <div class="pa-5 text-center">
        <v-avatar size="70" color="white" class="mb-3">
          <v-icon icon="mdi-account-star" size="40" color="indigo-darken-3"></v-icon>
        </v-avatar>
        <div class="text-white font-weight-bold text-h6">Head Teacher</div>
        <div class="text-indigo-lighten-4 text-caption text-uppercase">Management Portal</div>
      </div>

      <v-divider class="mx-4 border-opacity-25"></v-divider>

      <v-list density="compact" nav class="mt-3">
        <v-list-item to="/head/monitor" active-color="white" rounded="lg" class="mb-1">
          <template v-slot:prepend><v-icon icon="mdi-monitor-dashboard"></v-icon></template>
          <v-list-item-title>ຕິດຕາມການສອນ</v-list-item-title>
        </v-list-item>

        <v-list-item to="/head/reports" active-color="white" rounded="lg" class="mb-1">
          <template v-slot:prepend><v-icon icon="mdi-chart-bar"></v-icon></template>
          <v-list-item-title>ສະຖິຕິ ແລະ ລາຍງານ</v-list-item-title>
        </v-list-item>

        <v-list-item to="/head/teachers" active-color="white" rounded="lg" class="mb-1">
          <template v-slot:prepend><v-icon icon="mdi-account-group"></v-icon></template>
          <v-list-item-title>ຄູໃນສັງກັດ</v-list-item-title>
        </v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="pa-4">
          <v-btn block color="indigo-lighten-4" variant="outlined" prepend-icon="mdi-logout" @click="logout">
            ອອກຈາກລະບົບ
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-app-bar elevation="1" color="white">
      <v-app-bar-nav-icon @click="drawer = !drawer" color="indigo"></v-app-bar-nav-icon>
      <v-app-bar-title class="font-weight-medium text-indigo">
        ລະບົບຕິດຕາມການຮຽນ-ການສອນ
      </v-app-bar-title>
      
      <v-spacer></v-spacer>
      
      <div class="hidden-sm-and-down mr-4 text-grey-darken-1">
        {{ currentDate }}
      </div>
      
      <v-btn icon class="mr-2">
        <v-badge dot color="error">
          <v-icon icon="mdi-bell-outline" color="grey-darken-2"></v-icon>
        </v-badge>
      </v-btn>
    </v-app-bar>

    <v-main class="bg-grey-lighten-4">
      <v-container fluid>
        <router-view v-slot="{ Component }">
          <v-fade-transition mode="out-in">
            <component :is="Component" />
          </v-fade-transition>
        </router-view>
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const drawer = ref(true);
const router = useRouter();
const currentDate = ref('');

const logout = () => {
  localStorage.clear();
  router.push('/login');
};

onMounted(() => {
  currentDate.value = new Date().toLocaleDateString('lo-LA', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
});
</script>

<style scoped>
/* ປັບແຕ່ງ Font ໃຫ້ເປັນພາສາລາວທີ່ອ່ານງ່າຍ */
:deep(.v-list-item-title) {
  font-size: 0.95rem !important;
  font-weight: 500 !important;
}

.v-navigation-drawer {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>