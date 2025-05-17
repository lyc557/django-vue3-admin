import { request } from '/@/utils/service';

/**
 * 上传简历文件
 * @param {FormData} data - 包含文件和其他参数的表单数据
 * @returns {Promise} - 返回上传结果
 */
export function UploadResume(data) {
  return request({
    url: '/api/upload',
    method: 'post',
    data,
  });
}

/**
 * 分析简历内容
 * @param {Object} data - 分析参数
 * @returns {Promise} - 返回分析结果
 */
export function AnalyzeResume(data) {
  return request({
    url: '/api/analyze',
    method: 'post',
    data,
  });
}