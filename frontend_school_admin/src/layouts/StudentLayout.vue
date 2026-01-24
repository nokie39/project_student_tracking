<template>
  <v-app>
    <v-app-bar color="success" elevation="0" density="comfortable">
      <v-app-bar-title class="text-white font-weight-bold">
        <v-icon start icon="mdi-school" class="mr-2"></v-icon>
        Student Portal
      </v-app-bar-title>

      <template v-slot:append>
        <v-menu>
          <template v-slot:activator="{ props }">
            <v-btn icon v-bind="props" color="white">
              <v-avatar color="white" size="32">
                <span class="text-success font-weight-bold text-caption">S</span>
              </v-avatar>
            </v-btn>
          </template>
          <v-list width="150" density="compact">
            <v-list-item prepend-icon="mdi-account" title="ໂປຣໄຟລ໌" to="/student/profile"></v-list-item>
            <v-divider></v-divider>
            <v-list-item prepend-icon="mdi-logout" title="ອອກຈາກລະບົບ" @click="logout" color="error"></v-list-item>
          </v-list>
        </v-menu>
      </template>
    </v-app-bar>

    <v-main class="bg-grey-lighten-5">
      <v-container fluid class="pa-4 pb-16 h-100">
        <router-view v-slot="{ Component }">
          <v-fade-transition mode="out-in">
            <component :is="Component" />
          </v-fade-transition>
        </router-view>
      </v-container>
    </v-main>

    <v-bottom-navigation
      v-model="activeTab"
      color="success"
      mode="shift"
      elevation="4"
      grow
    >
      <v-btn to="/student/dashboard" value="dashboard">
        <v-icon>mdi-view-dashboard</v-icon>
        <span>ໜ້າຫຼັກ</span>
      </v-btn>

      <v-btn to="/student/assignments" value="assignments">
        <v-icon>mdi-book-open-page-variant</v-icon>
        <span>ວຽກບ້ານ</span>
      </v-btn>

      <v-btn to="/student/schedule" value="schedule">
        <v-icon>mdi-calendar-clock</v-icon>
        <span>ຕາຕະລາງ</span>
      </v-btn>

      <v-btn to="/student/grades" value="grades">
        <v-icon>mdi-chart-line</v-icon>
        <span>ຄະແນນ</span>
      </v-btn>
      
      </v-bottom-navigation>
  </v-app>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const activeTab = ref('dashboard'); // Default tab

const logout = () => {
  if(confirm('ຕ້ອງການອອກຈາກລະບົບແທ້ບໍ່?')) {
    localStorage.clear();
    router.push('/login');
  }
};
</script>

<style scoped>
/* Optional: Makes the bottom nav sticky/fixed nicely */
.v-bottom-navigation {
  position: fixed;
  bottom: 0;
  width: 100%;
  z-index: 1000;
}
</style>