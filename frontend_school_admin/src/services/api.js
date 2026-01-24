import axios from 'axios';

// 1. ສ້າງ Instance ກ່ອນ (ປະກາດຕົວແປ api)
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 2. ຈາກນັ້ນຈຶ່ງໃສ່ Interceptors
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ⚠️ ຖ້າຢາກດັກຈັບ Error 401 (Token ໝົດອາຍຸ)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // ລຶບ Token ແລະ ດີດໄປໜ້າ Login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('role');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ==========================================
// 3. Export Functions
// ==========================================

// Authentication
export const requestOtp = (email) => api.post('/auth/login', { email });
export const verifyOtp = (email, otp_code) => api.post('/auth/verify', { email, otp_code });
export const getProfile = () => api.get('/users/me');

// User Management
export const getAllUsers = () => api.get('/users/');
export const createUser = (data) => api.post('/users/', data);
export const updateUser = (id, data) => api.put(`/users/${id}`, data);
export const deleteUser = (id) => api.delete(`/users/${id}`);

// Academic & Classes
export const getAcademicYears = () => api.get('/academic/years');
export const createAcademicYear = (data) => api.post('/academic/years', data);
export const updateAcademicYear = (id, data) => api.put(`/academic/years/${id}`, data);
export const deleteAcademicYear = (id) => api.delete(`/academic/years/${id}`);

export const getClasses = () => api.get('/academic/classes');
export const createClass = (data) => api.post('/academic/classes', data);
export const updateClass = (id, data) => api.put(`/academic/classes/${id}`, data);
export const deleteClass = (id) => api.delete(`/academic/classes/${id}`);
export const getTeachersForDropdown = () => api.get('/academic/teachers-list');

// Students
export const getAllStudents = () => api.get('/students/');
export const registerStudent = (data) => api.post('/students/register', data);
export const enrollStudent = (data) => api.post('/enrollments/', data);
export const getStudentsInClass = (classId) => api.get(`/students/class/${classId}`);
export const getStudentPortfolio = (id) => api.get(`/students/${id}/portfolio`);
export const getStudentDashboardData = () => api.get('/students/dashboard');
export const updateStudent = (id, data) => api.put(`/students/${id}`, data);
export const deleteStudent = (id) => api.delete(`/students/${id}`);

export const getMyGrades = () => api.get('/students/me/grades');

// Attendance
export const getAttendance = (classId, date) => api.get(`/attendance/class/${classId}?date_str=${date}`);
export const saveAttendance = (data) => api.post('/attendance/save', data);

// Grades
export const getClassGrades = (classId, monthId) => api.get(`/grades/view-class/${classId}/${monthId}`);
export const updateGrade = (data) => api.post('/grades/update', data);
export const getGradeAuditLogs = (studentId, monthId) => api.get(`/grades/logs/${studentId}/${monthId}`);

// Behavior
export const saveBehaviorLog = (data) => api.post('/behavior/add', data); 
export const updateStudentTalents = (id, talents) => api.put(`/behavior/talents/${id}`, { talents });
export const getStudentsForBehavior = (classId) => api.get(`/behavior/class/${classId}/students`);

// Head Teacher
export const getDailyStats = () => api.get('/head/daily-stats');
export const getAttendanceMonitor = () => api.get('/head/attendance-monitor');
export const getTeacherWorkStatus = () => api.get('/head/monitor/summary'); 
export const getAllTeachers = () => api.get('/head/teachers/list');

// LMS (Assignments & Grading)
export const createAssignment = (formData) => {
  return api.post('/lms/assignments', formData, {
    headers: {
      'Content-Type': 'multipart/form-data' // ✅ ຕ້ອງມີແຖວນີ້ສຳລັບການອັບໂຫລດໄຟລ໌
    }
  });
}; 
export const getAssignmentsByClass = (classId) => api.get(`/lms/assignments/class/${classId}`);
export const deleteAssignment = (id) => api.delete(`/lms/assignments/${id}`);
export const getAssignmentSubmissions = (assignmentId) => api.get(`/lms/assignments/${assignmentId}/submissions`);
export const gradeSubmission = (data) => api.post('/lms/grade', data);
export const getTeacherClasses = () => api.get('/lms/my-classes'); // ✅ ເພີ່ມ Function ນີ້

// Schedules
export const getClassSchedule = (classId) => api.get(`/lms/schedules/${classId}`);
export const createSchedule = (data) => api.post('/lms/schedules', data);
export const deleteSchedule = (id) => api.delete(`/lms/schedules/${id}`);

// Student Side LMS
export const getStudentAssignments = () => api.get('/lms/student/assignments');
export const submitHomework = (formData) => api.post('/lms/submissions/', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
});

// Parents
export const getMyChildren = () => api.get('/parents/children');
export const getChildDashboard = (studentId) => api.get(`/parents/student/${studentId}/dashboard`);
export const getChildGrades = (studentId) => api.get(`/parents/student/${studentId}/grades`);
export const getChildAssignments = (studentId) => api.get(`/parents/student/${studentId}/assignments`);

// Reports
export const getDashboardSummary = () => api.get('/reports/dashboard/summary');
export const getClassAttendanceStats = () => api.get('/reports/dashboard/class-attendance');

// ສຸດທ້າຍຈຶ່ງ export default
export default api;