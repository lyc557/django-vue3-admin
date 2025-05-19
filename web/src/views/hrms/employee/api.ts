/**
 * 员工管理模块API
 * 包含员工数据的CRUD操作
 */
import { request } from '/@/utils/service';

export const apiPrefix = '/api/hrms/employee/';

/**
 * 获取员工列表数据
 * @param query 查询参数
 * @returns 员工列表数据
 */
export function GetList(query: any) {
  return request({
    url: apiPrefix,
    method: 'get',
    params: query
  });
}

/**
 * 添加员工
 * @param obj 员工数据
 * @returns 添加结果
 */
export function AddObj(obj: any) {
  return request({
    url: apiPrefix,
    method: 'post',
    data: obj
  });
}

/**
 * 更新员工信息
 * @param obj 员工数据
 * @returns 更新结果
 */
export function UpdateObj(obj: any) {
  return request({
    url: apiPrefix + obj.id + '/',
    method: 'put',
    data: obj
  });
}

/**
 * 删除员工
 * @param id 员工ID
 * @returns 删除结果
 */
export function DelObj(id: any) {
  return request({
    url: apiPrefix + id + '/',
    method: 'delete',
    data: { id }
  });
}

/**
 * 获取员工详情
 * @param id 员工ID
 * @returns 员工详情
 */
export function GetObj(id: any) {
  return request({
    url: apiPrefix + id + '/',
    method: 'get'
  });
}

/**
 * 获取员工列权限
 * @returns 列权限数据
 */
export function GetPermission() {
  return request({
    url: apiPrefix + 'permission/',
    method: 'get'
  });
}