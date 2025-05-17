<template>
    <div class="container">
      <div class="job-description-input">
        <h3>简历基础评分提示词</h3>
        <el-input
          v-model="jobDescription"
          :rows="8"
          type="textarea"
          maxlength="1000"
          show-word-limit
          :placeholder="'请输入简历基础评分提示词'"
        />
      </div>
      <el-upload
        class="upload-demo"
        drag
        :auto-upload="true"
        :file-list="fileList"
        :on-change="handleFileChange"
        :before-upload="beforeUpload"
        :http-request="customUpload"
        multiple
        accept=".pdf,.docx"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽简历文件到此处或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持PDF、DOCX格式文件
          </div>
        </template>
      </el-upload>
  
      <div v-show="resumeData" class="resume-result">
        <h3 class="resume-title">简历解析结果
            <div class="score-display" v-if="resumeData.score">
                <div class="score-circle">
                    <div class="score-value" :style="{color: getScoreColor(resumeData.score)}">{{ resumeData.score }}</div>
                    <div class="score-label">AI评分</div>
                </div>
            </div>
        </h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="姓名">{{ resumeData.name }}</el-descriptions-item>
          <el-descriptions-item label="联系方式">
            <p>{{ resumeData.phone }}</p>
            <p>{{ resumeData.email }}</p>
          </el-descriptions-item>
          <el-descriptions-item label="教育背景">{{ resumeData.education }}</el-descriptions-item>
          <el-descriptions-item label="工作经验">
            <ul>
              <li v-for="(exp, index) in resumeData.experience" :key="index">{{ exp }}</li>
            </ul>
          </el-descriptions-item>
          <el-descriptions-item label="技能">
            <el-tag v-for="(skill, index) in resumeData.skills" :key="index" type="info" style="margin-right: 5px;">{{ skill }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="项目">
            <ul>
              <li v-for="(project, index) in resumeData.projects" :key="index" class="project-item">
                <div>
                  <p><strong>项目名称:</strong> {{ project.name }}</p>
                  <p><strong>项目角色:</strong> {{ project.role }}</p>
                  <p><strong>项目描述:</strong> {{ project.description }}</p>
                </div>
              </li>
            </ul>
          </el-descriptions-item>
          <el-descriptions-item label="其他">
            <p>{{ resumeData.other }}</p>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
  </template>
  
  <script lang="ts" setup name="resumeUpload">
  import { ref, computed, watch } from 'vue';
  import { UploadFilled } from '@element-plus/icons-vue';
  import { ElMessage, ElMessageBox } from 'element-plus';
  import { debounce } from 'lodash-es';
  import { UploadResume, AnalyzeResume } from './api';
  import { successNotification } from '/@/utils/message';
  
  import { getBaseURL } from '/@/utils/baseUrl';

  // 从环境变量获取后端地址
  const UPLOAD_API = `${getBaseURL()}api/hrms/resume/upload/`;  // 使用getBaseURL方法获取基础URL
  
  const jobDescription = ref(`你是一位经验丰富的 HR 招聘专家，请根据以下六个维度对上传的简历进行全面评分，总分为 100 分。请分别对每个维度进行打分，并在最后给出总评分及简要评语。
注意：无需参考任何具体岗位，仅从通用就业能力与简历质量角度进行评价。
评分维度如下：
1. 简历排版与清晰度（10 分）：版式是否清晰、有逻辑结构、有无明显错别字或排版混乱。
2. 教育背景（15 分）：学历层次、院校背景、是否为相关专业等。
3. 工作经验与成就（35 分）：工作年限、职位层级、是否有具体成果或量化成绩。
4. 技能与证书（20 分）：是否具备关键硬技能或软技能，有无权威证书支持。
5. 语言能力（10 分）：英语或其他语言能力如何，是否有官方考试成绩或实际应用经验。
6. 专业表达与语气（10 分）：语言是否专业、逻辑是否清晰、是否避免空话套话。
请使用以下格式输出评分结果：
- 简历排版与清晰度：X/10  
- 教育背景：X/15  
- 工作经验与成就：X/35  
- 技能与证书：X/20  
- 语言能力：X/10  
- 专业表达与语气：X/10  
- 总评分：XX/100
简要评语：请总结简历的优点、不足，建议改进方向（100字以内）。`);
  const showResults = ref(false);
  const candidates = ref([]);
  const fileList = ref([]);
  const resumeData = ref({
    name: '',
    phone: '',
    email: '',
    education: '',
    experience: [],
    skills: [],
    projects: [] ,
    other: '',
    score: 0,
    scoreDetails: ''
  });
  
  // 计算属性，根据jobDescription的变化更新extraParams
  const extraParams = computed(() => {
    return {
      job_description: jobDescription.value
    };
  });
  
  /**
   * 处理文件变更事件
   * @param {Object} file - 上传的文件对象
   * @param {Array} files - 文件列表
   */
  const handleFileChange = debounce(async (file, files) => {
    console.log('file.status:', file.status);
    if (file.status === 'success') {
      fileList.value = files;
      
      // 检查响应是否符合API规范
      if (file.response && file.response.code === 2000 && file.response.data) {
        const parsedData = file.response.data;
        resumeData.value = {
          name: parsedData.name || '',
          phone: parsedData.phone || '',
          email: parsedData.email || '',
          education: parsedData.education || '',
          experience: parsedData.work_experience || [],
          skills: parsedData.skills || [],
          projects: parsedData.projects || [],
          other: parsedData.other || '',
          score: parsedData.score || 0,
          scoreDetails: parsedData.score_details || ''
        };
        
        // 显示成功通知
        successNotification('简历解析成功');
      } else {
        // 处理错误情况
        ElMessage.error(file.response?.msg || '简历解析失败');
      }
    } else if (file.status === 'error') {
      ElMessage.error('文件上传失败，请重试');
    }
  }, 500);
  
  /**
   * 上传前的文件验证
   * @param {Object} file - 待上传的文件
   * @returns {Boolean} - 是否允许上传
   */
  const beforeUpload = (file) => {
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];
    const isAllowed = allowedTypes.includes(file.type);
    
    if (!isAllowed) {
      ElMessage.error('只支持上传PDF、DOCX格式的文件');
      return false;
    }
    
    return true;
  };
  
  /**
   * 手动分析简历内容
   * @param {String} fileId - 文件ID
   */
  const analyzeResume = async (fileId) => {
    try {
      const res = await AnalyzeResume({
        file_id: fileId,
        job_description: jobDescription.value
      });
      
      if (res.code === 2000) {
        const parsedData = res.data;
        resumeData.value = {
          // ... 更新简历数据
          name: parsedData.name || '',
          phone: parsedData.phone || '',
          email: parsedData.email || '',
          education: parsedData.education || '',
          experience: parsedData.work_experience || [],
          skills: parsedData.skills || [],
          projects: parsedData.projects || [],
          other: parsedData.other || '',
          score: parsedData.score || 0,
          scoreDetails: parsedData.score_details || ''
        };
        successNotification(res.msg || '简历分析成功');
      } else {
        ElMessage.error(res.msg || '简历分析失败');
      }
    } catch (error) {
      console.error('分析简历时出错:', error);
      ElMessage.error('分析简历时出错');
    }
  };
  
  /**
   * 获取评分对应的颜色
   * @param {Number} score - 评分值
   * @returns {String} - 对应的颜色代码
   */
  const getScoreColor = (score) => {
    if (score >= 90) return '#67C23A'; // 优秀 - 绿色
    if (score >= 60) return '#E6A23C'; // 合格 - 黄色
    return '#F56C6C'; // 不合格 - 红色
  };
  
  // 监听jobDescription变化，更新extraParams
  watch(jobDescription, (newVal) => {
    console.log('jobDescription changed:', newVal);
  });
  /**
   * 自定义上传方法
   * @param {Object} options - 上传选项
   */
  const customUpload = (options) => {
    const { file, data, onSuccess, onError } = options;
    
    // 创建FormData对象
    const formData = new FormData();
    formData.append('file', file);
    
    // 添加额外参数
    if (extraParams.value) {
      Object.keys(extraParams.value).forEach(key => {
        formData.append(key, extraParams.value[key]);
      });
    }
    
    // 使用api.js中的方法上传，它会自动包含认证信息
    UploadResume(formData)
      .then(response => {
        console.log('上传响应:', response);  // 添加日志
        onSuccess(response);
      })
      .catch(error => {
        console.error('上传错误:', error);  // 添加错误日志
        onError(error);
        ElMessage.error('文件上传失败，请重试');
      });
  };
  </script>
  
  <style scoped>
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  
  .header-container h1 {
    margin: 0;
  }
  
  .upload-demo {
    margin: 20px 0;
  }
  
  .result-container {
    margin-top: 30px;
  }
  
  .job-description-input {
    margin-bottom: 20px;
  }
  .job-description-input h3 {
    margin-bottom: 10px;
    font-size: 16px;
    color: #606266;
  }
  
  /* 新增项目分隔样式 */
  .resume-result .project-item:not(:last-child) {
    border-bottom: 1px solid #ebeef5;
    padding-bottom: 15px;
    margin-bottom: 15px;
  }
  
  .resume-result .project-item div {
    padding: 0 10px;
  }
  
  .resume-result-container {
    position: relative;
    /* 其他样式 */
  }
  
  .resume-title {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .score-display {
    position: static;
    margin-left: 10px;
  }
  
  .score-circle {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1677ff, #69b1ff);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  .score-value {
    font-size: 28px;
    font-weight: bold;
    line-height: 1;
  }
  
  .score-label {
    font-size: 12px;
    margin-top: 4px;
    opacity: 0.9;
  }
  
  .score-details {
    margin-top: 5px;
    font-size: 12px;
    color: #666;
  }
  </style>