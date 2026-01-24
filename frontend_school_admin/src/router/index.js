import { createRouter, createWebHistory } from 'vue-router'

// --- Auth & Layouts ---
import Login from '../views/Login.vue'
import MainLayout from '../layouts/MainLayout.vue'
import StudentLayout from '../layouts/StudentLayout.vue'
import HeadLayout from '../layouts/HeadLayout.vue'
import TeacherLayout from '../layouts/TeacherLayout.vue' // ✅ Layout ໃໝ່ສຳລັບຄູ

// --- Admin / Shared Views ---
import Dashboard from '../views/admin/Dashboard.vue'
import Students from '../views/admin/Students.vue'
import Attendance from '../views/Attendance.vue' 
import Grades from '../views/Grades.vue'
import LMS from '../views/LMS.vue'
import ScheduleAdmin from '../views/ScheduleAdmin.vue'
import StudentDetail from '../views/student/StudentDetail.vue' 

// --- Teacher Specific Views ---
import TeacherDashboard from '../views/teacher/TeacherDashboard.vue'
import BehaviorEntry from '../views/teacher/BehaviorEntry.vue'

// --- Student Side Views ---
import MyAssignments from '../views/student/MyAssignments.vue'
import MySchedule from '../views/student/Schedule.vue'
import StudentDashboard from '../views/student/Dashboard.vue'

// --- Head Teacher Views ---
import TeacherMonitor from '../views/head/TeacherMonitor.vue'
import Reports from '../views/head/Reports.vue'

// --- Parent Views ---
const ParentSelectChild = () => import('../views/parent/SelectChild.vue')
const ParentDashboard = () => import('../views/parent/ParentDashboard.vue')

const routes = [
  // 0. ໜ້າ Login
  { path: '/login', component: Login, name: 'Login' },
  { path: '/', redirect: '/login' },

  // ==========================================
  // 1. ADMIN ROUTES (MainLayout)
  // ==========================================
  { 
    path: '/admin',
    component: MainLayout, 
    meta: { requiresAuth: true, roles: ['admin'] }, 
    children: [
      { path: 'dashboard', name: 'AdminDashboard', component: Dashboard },
      
      // ຈັດການຂໍ້ມູນພື້ນຖານ
      { 
        path: 'years', 
        name: 'AcademicYears', 
        component: () => import('../views/admin/AcademicYears.vue')
      },
      { 
        path: 'classes', 
        name: 'AdminClasses', 
        component: () => import('../views/admin/Classes.vue')
      },
      { 
        path: 'users', 
        name: 'AdminUsers', 
        component: () => import('../views/admin/Users.vue')
      },

      // ຈັດການນັກຮຽນ & ວິຊາການ
      { path: 'students', name: 'AdminStudents', component: Students },
      { path: 'student-detail/:id', name: 'StudentDetailAdmin', component: StudentDetail },
      { path: 'academic', name: 'AdminAcademic', component: ScheduleAdmin },
      
      // Admin ເບິ່ງໄດ້ທຸກຢ່າງ
      { path: 'attendance', name: 'AdminAttendance', component: Attendance },
      { path: 'grades', name: 'AdminGrades', component: Grades },
      { path: 'behavior', name: 'AdminBehavior', component: BehaviorEntry },
      { path: 'lms', name: 'AdminLMS', component: LMS },
    ]
  },

  // ==========================================
  // 2. TEACHER ROUTES (TeacherLayout)
  // ==========================================
  {
    path: '/teacher',
    component: TeacherLayout,
    meta: { requiresAuth: true, roles: ['teacher'] },
    children: [
      { 
        path: 'dashboard', 
        name: 'TeacherDashboard', 
        component: TeacherDashboard 
      },
      // ✅✅✅ ແກ້ໄຂຊື່ Route (name) ບໍ່ໃຫ້ຊ້ຳກັນກັບ Admin ✅✅✅
      { path: 'students', name: 'TeacherStudents', component: Students },
      { path: 'student-detail/:id', name: 'TeacherStudentDetail', component: StudentDetail },
      { path: 'academic', name: 'TeacherAcademic', component: ScheduleAdmin },
      
      { path: 'attendance', name: 'TeacherAttendance', component: Attendance },
      { path: 'grades', name: 'TeacherGrades', component: Grades },
      { path: 'behavior', name: 'TeacherBehavior', component: BehaviorEntry },
      { path: 'lms', name: 'TeacherLMS', component: LMS },
    ]
  },

  // ==========================================
  // 3. HEAD TEACHER ROUTES
  // ==========================================
  {
    path: '/head',
    component: HeadLayout,
    meta: { requiresAuth: true, roles: ['head_teacher'] },
    children: [
      { path: 'monitor', name: 'HeadMonitor', component: TeacherMonitor },
      { path: 'reports', name: 'HeadReports', component: Reports },
      { path: 'teachers', name: 'HeadTeachers', component: () => import('../views/head/TeachersList.vue') },
      { path: 'student-detail/:id', name: 'HeadStudentDetail', component: StudentDetail },
    ]
  },

  // ==========================================
  // 4. STUDENT ROUTES
  // ==========================================
  {
    path: '/student',
    component: StudentLayout,
    meta: { requiresAuth: true, roles: ['student'] },
    children: [
      { path: 'dashboard', name: 'StudentDashboard', component: StudentDashboard },
      { path: 'assignments', name: 'StudentAssignments', component: MyAssignments },
      { path: 'schedule', name: 'StudentSchedule', component: MySchedule },
      { path: 'my-portfolio', name: 'MyPortfolio', component: StudentDetail },
      { 
        path: 'profile', 
        name: 'StudentProfile', 
        component: () => import('../views/student/Profile.vue') 
      },
      { 
        path: 'grades', 
        name: 'StudentGrades', 
        component: () => import('../views/student/MyGrades.vue') 
      },
    ]
  },

  // ==========================================
  // 5. PARENT ROUTES
  // ==========================================
  {
    path: '/parent',
    component: StudentLayout,
    meta: { requiresAuth: true, roles: ['parent'] },
    children: [
      { 
        path: 'select-child', 
        name: 'ParentSelectChild', 
        component: ParentSelectChild,
        meta: { hideNavbar: true }
      },
      { 
        path: 'dashboard/:studentId', 
        name: 'ParentDashboard', 
        component: ParentDashboard 
      },
      { 
        path: 'grades/:studentId', 
        name: 'ParentChildGrades', 
        component: () => import('../views/parent/ChildGrades.vue') 
      },
      { 
        path: 'assignments/:studentId', 
        name: 'ParentChildAssignments', 
        component: () => import('../views/parent/ChildAssignments.vue') 
      },
    ]
  },

  // Catch-all
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// --- Security & Role Guard ---
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('role');

  if (to.meta.requiresAuth && !token) {
    return next('/login');
  }

  if (to.path === '/login' && token) {
    if (userRole === 'student') return next('/student/dashboard');
    if (userRole === 'teacher') return next('/teacher/dashboard');
    if (userRole === 'head_teacher') return next('/head/monitor');
    if (userRole === 'parent') return next('/parent/select-child');
    return next('/admin/dashboard');
  }

  if (to.meta.roles && !to.meta.roles.includes(userRole)) {
    if (userRole === 'student') return next('/student/dashboard');
    if (userRole === 'teacher') return next('/teacher/dashboard');
    if (userRole === 'head_teacher') return next('/head/monitor');
    if (userRole === 'parent') return next('/parent/select-child');
    return next('/admin/dashboard');
  }

  next();
});

export default router;