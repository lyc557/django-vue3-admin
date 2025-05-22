import { request } from '/@/utils/service';
import { UserPageQuery, AddReq, EditReq, InfoReq, PageQuery } from '@fast-crud/fast-crud';

export const apiPrefix = '/api/kb/document/';

/**
 * 获取文档列表
 * @param query 查询参数
 */
export function GetList(query: UserPageQuery) {
  return request({
    url: apiPrefix,
    method: 'get',
    params: query,
  });
}

/**
 * 获取文档详情
 * @param id 文档ID
 */
export function GetObj(id: InfoReq) {
  return request({
    url: apiPrefix + id + '/',
    method: 'get',
  });
}

/**
 * 新增文档
 * @param obj 文档对象
 */
export function AddObj(obj: AddReq) {
  return request({
    url: apiPrefix,
    method: 'post',
    data: obj,
  });
}

/**
 * 更新文档
 * @param obj 文档对象
 */
export function UpdateObj(obj: EditReq) {
  return request({
    url: apiPrefix + obj.id + '/',
    method: 'put',
    data: obj,
  });
}

/**
 * 删除文档
 * @param id 文档ID
 */
export function DelObj(id: string) {
  return request({
    url: apiPrefix + id + '/',
    method: 'delete'
  });
}

/**
 * 获取文档分类列表
 */
export function GetCategoryList() {
  return request({
    url: '/api/kb/category/',
    method: 'get',
  });
}

/**
 * 获取文档标签列表
 */
export function GetTagList() {
  return request({
    url: '/api/kb/tag/',
    method: 'get',
  });
}