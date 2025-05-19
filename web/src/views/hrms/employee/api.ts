/**
 * 员工管理模块API
 * 包含员工数据的CRUD操作
 */
import { request } from '/@/utils/service';

export const apiPrefix = '/api/hrms/employee/';

export function GetList(query: any) {
  return request({
    url: apiPrefix,
    method: 'get',
    params: query
  });
}

export function AddObj(obj: any) {
  return request({
    url: apiPrefix,
    method: 'post',
    data: obj
  });
}

export function UpdateObj(obj: any) {
  return request({
    url: apiPrefix + obj.id + '/',
    method: 'put',
    data: obj
  });
}

export function DelObj(id: any) {
  return request({
    url: apiPrefix + id + '/',
    method: 'delete',
    data: { id }
  });
}

export function GetObj(id: any) {
  return request({
    url: apiPrefix + id + '/',
    method: 'get'
  });
}

// 添加 GetPermission 函数导出
export const GetPermission = () => {
  return request({
    url: apiPrefix + 'field_permission/',
    method: 'get',
  });
};