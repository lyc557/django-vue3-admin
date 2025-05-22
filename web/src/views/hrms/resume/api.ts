import { request } from '/@/utils/service';
import { UserPageQuery, AddReq, EditReq, InfoReq, PageQuery } from '@fast-crud/fast-crud';

const apiPrefix = '/api/hrms/resume/';

/**
 * 上传简历文件
 * @param {FormData} data - 包含文件和其他参数的表单数据
 */
export function UploadResume(data: FormData){
  return request({
    url: apiPrefix+'upload/',
    method: 'post',
    data: data,
    timeout: 1000000, // 设置超时时间为100秒（100000毫秒）
    headers: {
      'Content-Type': 'multipart/form-data',
    }
  });
}


/**
 * 分析简历内容
 * @param {Object} data - 分析参数
 */
export function AnalyzeResume(data: { file_id: string; job_description?: string }){
  return request({
    url: apiPrefix+'analyze',
    method: 'post',
    data,
  });
}

/**
 * 获取简历列表
 * @param {Object} params - 查询参数
 */
export function GetList(params: any) {
  return request({
    url: apiPrefix,
    method: 'get',
    params,
  });
}

/**
 * 获取简历详情
 * @param {string} id - 简历ID
 */
export function GetInfo(id: string) {
  return request({
    url: apiPrefix + id + '/',
    method: 'get',
  });
}

/**
 * 发送聊天消息
 * @param {Object} data - 聊天消息数据
 */
export function SendChatMessage(data: { message: string }){
  return request({
    url: apiPrefix + 'chat'+ '/',
    method: 'post',
    data,
  });
}

