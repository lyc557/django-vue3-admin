import { request } from '/@/utils/service';

/**
 * 简历文件上传响应接口
 */
interface ResumeUploadResponse {
  code: number;
  data: any;
  msg: string;
}

/**
 * 简历分析响应接口
 */
interface ResumeAnalyzeResponse {
  code: number;
  data: {
    name?: string;
    phone?: string;
    email?: string;
    education?: string;
    work_experience?: any[];
    skills?: string[];
    projects?: any[];
    other?: string;
    score?: number;
    score_details?: string;
  };
  msg: string;
}

/**
 * 上传简历文件
 * @param {FormData} data - 包含文件和其他参数的表单数据
 * @returns {Promise<ResumeUploadResponse>} - 返回上传结果
 */
export function UploadResume(data: FormData): Promise<ResumeUploadResponse> {
  return request({
    url: '/api/hrms/resume/upload/',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data',
    }
  });
}

/**
 * 分析简历内容
 * @param {Object} data - 分析参数
 * @returns {Promise<ResumeAnalyzeResponse>} - 返回分析结果
 */
export function AnalyzeResume(data: { file_id: string; job_description?: string }): Promise<ResumeAnalyzeResponse> {
  return request({
    url: '/api/hrms/resume/analyze',
    method: 'post',
    data,
  });
}