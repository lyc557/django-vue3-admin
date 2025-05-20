import { request } from '/@/utils/service';
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