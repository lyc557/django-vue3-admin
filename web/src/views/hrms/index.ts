/**
 * HRMS模块入口文件
 * 用于导出HRMS模块的组件和功能
 */
import { defineAsyncComponent } from 'vue';

// 导出HRMS模块的主要组件
export const HrmsEmployee = defineAsyncComponent(() => import('./employee/index.vue'));
export const HrmsDepartment = defineAsyncComponent(() => import('./department/index.vue'));
export const HrmsAttendance = defineAsyncComponent(() => import('./attendance/index.vue'));
export const HrmsLeave = defineAsyncComponent(() => import('./leave/index.vue'));
export const HrmsPayroll = defineAsyncComponent(() => import('./payroll/index.vue'));
export const HrmsPerformance = defineAsyncComponent(() => import('./performance/index.vue'));
export const HrmsRecruitment = defineAsyncComponent(() => import('./recruitment/index.vue'));