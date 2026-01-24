<template>
  <v-container class="fill-height bg-grey-lighten-3" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12" rounded="xl">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title class="text-center font-weight-bold">
              <v-icon start>mdi-school</v-icon> ເຂົ້າສູ່ລະບົບ
            </v-toolbar-title>
          </v-toolbar>
          
          <v-card-text class="pa-6">
            <v-form v-if="step === 1" @submit.prevent="handleRequestOtp">
              <div class="text-center mb-4 text-grey-darken-1">
                ກະລຸນາໃສ່ Email ເພື່ອຮັບລະຫັດ OTP
              </div>
              <v-text-field
                v-model="email"
                label="Email Address"
                prepend-inner-icon="mdi-email"
                variant="outlined"
                type="email"
                required
                autofocus
              ></v-text-field>
              
              <v-btn
                block
                color="primary"
                size="large"
                type="submit"
                :loading="loading"
                class="mt-4"
              >
                ສົ່ງລະຫັດ OTP
              </v-btn>
            </v-form>

            <v-form v-else @submit.prevent="handleVerifyOtp">
              <div class="text-center mb-4">
                <div class="text-h6">ຢືນຢັນຕົວຕົນ</div>
                <div class="text-caption text-grey">
                  ລະຫັດ OTP ຖືກສົ່ງໄປທີ່: <strong>{{ email }}</strong>
                </div>
              </div>

              <v-otp-input
                v-model="otp"
                length="6"
                class="mb-4"
                autofocus
              ></v-otp-input>

              <v-btn
                block
                color="success"
                size="large"
                type="submit"
                :loading="loading"
              >
                ຢືນຢັນລະຫັດ
              </v-btn>

              <v-btn
                block
                variant="text"
                color="grey"
                class="mt-2"
                @click="step = 1"
              >
                ກັບໄປແກ້ໄຂ Email
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <v-snackbar v-model="snackbar" :color="snackbarColor">
      {{ snackbarText }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar = false">ປິດ</v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
// 🔥 ໃຊ້ Path ແບບ Relative (ຖອຍ 2 ຂັ້ນຖ້າຢູ່ໃນ views/auth ຫຼື 1 ຂັ້ນຖ້າຢູ່ໃນ views)
// ຖ້າໄຟລ໌ເຈົ້າຢູ່ src/views/Login.vue ໃຫ້ໃຊ້ '../services/api'
import { requestOtp, verifyOtp } from '../services/api'; 

const router = useRouter();
const step = ref(1);
const email = ref('');
const otp = ref('');
const loading = ref(false);
const snackbar = ref(false);
const snackbarText = ref('');
const snackbarColor = ref('error');

// 1. ຂໍ OTP
const handleRequestOtp = async () => {
  if (!email.value) return showNotify("ກະລຸນາໃສ່ Email", "warning");
  
  loading.value = true;
  try {
    await requestOtp(email.value);
    showNotify("ສົ່ງ OTP ສຳເລັດ! ກະລຸນາກວດ Email", "success");
    step.value = 2;
  } catch (error) {
    console.error(error);
    showNotify("ບໍ່ພົບ Email ນີ້ໃນລະບົບ ຫຼື ເກີດຂໍ້ຜິດພາດ", "error");
  } finally {
    loading.value = false;
  }
};

// 2. ຢືນຢັນ OTP
const handleVerifyOtp = async () => {
  if (otp.value.length < 6) return;
  
  loading.value = true;
  try {
    const res = await verifyOtp(email.value, otp.value);
    
    // ບັນທຶກ Token
    localStorage.setItem('token', res.data.access_token);
    localStorage.setItem('role', res.data.role);

    showNotify("ເຂົ້າສູ່ລະບົບສຳເລັດ!", "success");

    // ຍ້າຍໜ້າຕາມ Role
    setTimeout(() => {
      if (res.data.role === 'student') router.push('/student/dashboard');
      else if (res.data.role === 'head_teacher') router.push('/head/monitor');
      else router.push('/admin/dashboard'); // admin & teacher
    }, 1000);

  } catch (error) {
    console.error(error);
    showNotify("ລະຫັດ OTP ບໍ່ຖືກຕ້ອງ", "error");
  } finally {
    loading.value = false;
  }
};

const showNotify = (msg, color) => {
  snackbarText.value = msg;
  snackbarColor.value = color;
  snackbar.value = true;
};
</script>