/**
 * HRMS模块类型定义
 */

// 通用请求类型
export interface PageQuery {
  page: number;
  limit: number;
  [key: string]: any;
}

export interface AddReq {
  [key: string]: any;
}

export interface EditReq {
  id: string | number;
  [key: string]: any;
}

export interface DelReq {
  id: string | number;
}

export interface GetObj {
  id: string | number;
}

// 员工类型
export interface Employee {
  id: number;
  employee_id: string;
  name: string;
  gender: number;
  mobile: string;
  email: string;
  department: number;
  position: string;
  hire_date: string;
  status: number;
  avatar: string;
  remark: string;
  create_datetime: string;
}

// 部门类型
export interface Department {
  id: number;
  name: string;
  parent: number | null;
  status: number;
  order_num: number;
  create_datetime: string;
}

// 考勤类型
export interface Attendance {
  id: number;
  employee: number;
  date: string;
  check_in: string;
  check_out: string;
  status: number;
  remark: string;
}

// 请假类型
export interface Leave {
  id: number;
  employee: number;
  type: number;
  start_date: string;
  end_date: string;
  days: number;
  reason: string;
  status: number;
  approver: number;
  approve_datetime: string;
  create_datetime: string;
}

// API响应数据类型
export interface APIResponseData<T = any> {
  code: number;
  data: T;
  msg: string;
}