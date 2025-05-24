<template>
  <div class="resume-upload-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>简历解析与评分</h2>
      <p class="subtitle">上传简历文件，获取AI智能解析和评分</p>
    </div>
    
    <el-row :gutter="20">
      <!-- 左侧：提示词和上传区域 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="10">
        <el-card class="prompt-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><document /></el-icon>
              <span>简历评分提示词</span>
              <el-tooltip content="自定义评分标准，AI将根据您的要求进行简历评分" placement="top">
                <el-icon class="info-icon"><info-filled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          
          <el-input
            v-model="jobDescription"
            :rows="8"
            type="textarea"
            maxlength="1000"
            show-word-limit
            :placeholder="'请输入简历基础评分提示词'"
            resize="none"
          />
          
          <div class="upload-section">
            <h4>
              <el-icon><upload /></el-icon>
              上传简历
            </h4>
            
            <el-upload
              class="resume-uploader"
              drag
              :auto-upload="true"
              :file-list="fileList"
              :on-change="handleFileChange"
              :before-upload="beforeUpload"
              :http-request="customUpload"
              :data="extraParams"
              multiple
              accept=".pdf,.docx"
              :loading="uploading"
            >
              <template #trigger>
                <div class="upload-trigger">
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                    拖拽简历文件到此处或<em>点击上传</em>
                  </div>
                  <div class="el-upload__tip">
                    支持PDF、DOCX格式文件
                  </div>
                </div>
              </template>
              
              <template #file="{ file }">
                <div class="uploaded-file">
                  <el-icon><document /></el-icon>
                  <span class="filename">{{ file.name }}</span>
                  <div class="file-status">
                    <el-tag v-if="file.status === 'success'" type="success" size="small">已上传</el-tag>
                    <el-tag v-else-if="file.status === 'uploading'" type="info" size="small">上传中</el-tag>
                    <el-tag v-else-if="file.status === 'error'" type="danger" size="small">上传失败</el-tag>
                  </div>
                </div>
              </template>
            </el-upload>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧：解析结果 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="14">
        <el-card v-if="resumeData.name" class="result-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div>
                <el-icon><data-analysis /></el-icon>
                <span>简历解析结果</span>
              </div>
              <div class="score-display" v-if="resumeData.score">
                <div class="score-circle" :class="getScoreClass(resumeData.score)">
                  <div class="score-value">{{ resumeData.score }}</div>
                  <div class="score-label">AI评分</div>
                </div>
              </div>
            </div>
          </template>
          
          <el-skeleton :loading="loading" animated :rows="6">
            <template #default>
              <div class="resume-content">
                <div class="resume-header">
                  <h3>{{ resumeData.name || '未知姓名' }}</h3>
                  <div class="contact-info">
                    <span v-if="resumeData.phone">
                      <el-icon><phone /></el-icon> {{ resumeData.phone }}
                    </span>
                    <span v-if="resumeData.email">
                      <el-icon><message /></el-icon> {{ resumeData.email }}
                    </span>
                  </div>
                </div>
                
                <el-divider content-position="left">
                  <el-icon><school /></el-icon> 教育背景
                </el-divider>
                <div class="section-content">
                  {{ resumeData.education || '无教育背景信息' }}
                </div>
                
                <el-divider content-position="left">
                  <el-icon><office-building /></el-icon> 工作经验
                </el-divider>
                <div class="section-content">
                  <el-empty v-if="!resumeData.experience || resumeData.experience.length === 0" description="无工作经验信息" :image-size="80" />
                  <ul v-else>
                    <li v-for="(exp, index) in resumeData.experience" :key="index" class="experience-item">
                      <div class="company">{{ exp.company }}</div>
                      <div class="position">{{ exp.position }}</div>
                      <div class="duration">{{ exp.duration }}</div>
                    </li>
                  </ul>
                </div>
                
                <el-divider content-position="left">
                  <el-icon><magic-stick /></el-icon> 技能
                </el-divider>
                <div class="section-content skills-section">
                  <el-empty v-if="!resumeData.skills || resumeData.skills.length === 0" description="无技能信息" :image-size="80" />
                  <el-tag 
                    v-for="(skill, index) in resumeData.skills" 
                    :key="index" 
                    :type="getTagType(index)" 
                    class="skill-tag"
                  >
                    {{ skill }}
                  </el-tag>
                </div>
                
                <el-divider content-position="left">
                  <el-icon><collection-tag /></el-icon> 项目经验
                </el-divider>
                <div class="section-content">
                  <el-empty v-if="!resumeData.projects || resumeData.projects.length === 0" description="无项目经验信息" :image-size="80" />
                  <el-collapse v-else accordion>
                    <el-collapse-item 
                      v-for="(project, index) in resumeData.projects" 
                      :key="index"
                      :title="project.name || '未命名项目'"
                    >
                      <div class="project-content">
                        <p v-if="project.role"><strong>角色：</strong>{{ project.role }}</p>
                        <p v-if="project.description"><strong>描述：</strong>{{ project.description }}</p>
                      </div>
                    </el-collapse-item>
                  </el-collapse>
                </div>
                
                <el-divider content-position="left" v-if="resumeData.other">
                  <el-icon><more-filled /></el-icon> 其他信息
                </el-divider>
                <div class="section-content" v-if="resumeData.other">
                  {{ resumeData.other }}
                </div>
                
                <div class="score-details" v-if="resumeData.scoreDetails">
                  <el-divider content-position="left">
                    <el-icon><histogram /></el-icon> 评分详情
                  </el-divider>
                  <div class="section-content">
                    <pre>{{ resumeData.scoreDetails }}</pre>
                  </div>
                </div>
              </div>
            </template>
          </el-skeleton>
        </el-card>
        
        <el-empty 
          v-else 
          class="empty-result" 
          description="上传简历后查看解析结果" 
          :image-size="200"
        >
          <template #image>
            <el-icon class="empty-icon"><document-checked /></el-icon>
          </template>
        </el-empty>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup name="resumeUpload">

import { ref, computed, watch, onMounted} from 'vue';
import { 
  UploadFilled, 
  Document, 
  Upload, 
  InfoFilled, 
  DataAnalysis,
  Phone, 
  Message, 
  School, 
  OfficeBuilding, 
  MagicStick,
  CollectionTag, 
  MoreFilled, 
  Histogram,
  DocumentChecked
} from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { debounce } from 'lodash-es';
import { UploadResume, AnalyzeResume } from './api';
import { successNotification } from '/@/utils/message';

// 状态定义
const jobDescription = ref(`你是一位经验丰富的 HR 招聘专家，请根据以下六个维度对上传的简历进行全面评分，总分为 100 分。请分别对每个维度进行打分，并在最后给出总评分及简要评语。
注意：无需参考任何具体岗位，仅从通用就业能力与简历质量角度进行评价。
评分维度如下：
1. 简历排版与清晰度（10 分）：版式是否清晰、有逻辑结构、有无明显错别字或排版混乱。
2. 教育背景（15 分）：学历层次、院校背景、是否为相关专业等。
3. 工作经验与成就（35 分）：工作年限、职位层级、是否有具体成果或量化成绩。
4. 技能与证书（20 分）：是否具备关键硬技能或软技能，有无权威证书支持。
5. 语言能力（10 分）：英语或其他语言能力如何，是否有官方考试成绩或实际应用经验。
6. 专业表达与语气（10 分）：语言是否专业、逻辑是否清晰、是否避免空话套话。
`);
const fileList = ref([]);
const loading = ref(false);
const uploading = ref(false);
const resumeData = ref({
  name: '',
  phone: '',
  email: '',
  education: '',
  experience: [],
  skills: [],
  projects: [],
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
const handleFileChange = debounce((file, files) => {
  console.log('file.status:', file.status);
  fileList.value = files;
  
  if (file.status === 'uploading') {
    uploading.value = true;
    loading.value = true;
  } else if (file.status === 'success') {
    uploading.value = false;
    
    // 检查响应是否符合API规范
    if (file.response && file.response.code === 2000 && file.response.data && file.response.data.parsed_data) {
      const parsedData = file.response.data.parsed_data;
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
      
      // 延迟关闭加载状态，让用户感知到变化
      setTimeout(() => {
        loading.value = false;
      }, 500);
    } else {
      // 处理错误情况
      loading.value = false;
      ElMessage.error(file.response?.msg || '简历解析失败');
    }
  } else if (file.status === 'error') {
    uploading.value = false;
    loading.value = false;
    ElMessage.error('文件上传失败，请重试');
  }
}, 300);

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
  
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过10MB');
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
    loading.value = true;
    const res = await AnalyzeResume({
      file_id: fileId,
      job_description: jobDescription.value
    });
    
    if (res.code === 2000) {
      const parsedData = res.data;
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
      successNotification(res.msg || '简历分析成功');
    } else {
      ElMessage.error(res.msg || '简历分析失败');
    }
  } catch (error) {
    console.error('分析简历时出错:', error);
    ElMessage.error('分析简历时出错');
  } finally {
    loading.value = false;
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

/**
 * 获取评分对应的CSS类名
 * @param {Number} score - 评分值
 * @returns {String} - 对应的CSS类名
 */
const getScoreClass = (score) => {
  if (score >= 90) return 'score-excellent';
  if (score >= 60) return 'score-qualified';
  return 'score-failed';
};

/**
 * 获取技能标签的类型
 * @param {Number} index - 标签索引
 * @returns {String} - 标签类型
 */
const getTagType = (index) => {
  const types = ['', 'success', 'warning', 'info', 'danger'];
  return types[index % types.length];
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
  uploading.value = true;
  
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
      console.log('上传响应:', response);
      onSuccess(response);
    })
    .catch(error => {
      console.error('上传错误:', error);
      onError(error);
      ElMessage.error('文件上传失败，请重试');
    })
    .finally(() => {
      uploading.value = false;
    });
};

const loadExampleData = () => {
  resumeData.value = {
    name: '案例：张三',
    phone: '1388888888',
    email: 'zhangsan@example.com',
    education: 'XX大学 计算机科学与技术 本科',
    experience: [
    { company: "北京宇信科技集团股份有限公司q", position: "UI自动化测试工程师", duration: "2022.09-至今" },
    { company: "北京宇信科技集团股份有限公司2", position: "UI自动化测试工程师2", duration: "2022.09-至今2" }
    ],

    skills: ['Vue3', 'TypeScript', 'Python'],
    projects: [
      {
        name: '开发了基于Vue3的管理系统',
        role: '前端开发',
        description: '负责前端架构设计和核心功能开发'
      },
      {
        name: '实现了自动化部署流程',
        role: 'DevOps工程师',
        description: '设计并实现了CI/CD流水线'
      }
    ],
    other: '获得2021年度优秀员工奖',
    score: 85,
    scoreDetails: '技术能力优秀，项目经验丰富'
  };
};

// 在组件挂载时或某个按钮点击时调用
onMounted(() => loadExampleData());
</script>

<style scoped>
:root {
  --primary-color: #1677ff;
  --primary-light: #69b1ff;
  --success-color: #67C23A;
  --warning-color: #E6A23C;
  --danger-color: #F56C6C;
  --text-primary: #303133;
  --text-regular: #606266;
  --text-secondary: #909399;
  --border-color: #DCDFE6;
  --bg-color: #f5f7fa;
  --card-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  --card-shadow-hover: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
}

.resume-upload-container {
  padding: 20px;
  background-color: var(--bg-color);
  min-height: calc(100vh - 120px);
}

.page-header {
  margin-bottom: 24px;
  text-align: center;
}

.page-header h2 {
  font-size: 24px;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 14px;
}

/* 卡片样式 */
.prompt-card,
.result-card {
  margin-bottom: 20px;
  border-radius: 8px;
  transition: box-shadow 0.3s ease;
}

.prompt-card:hover,
.result-card:hover {
  box-shadow: var(--card-shadow-hover);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: bold;
  color: var(--text-primary);
}

.card-header .el-icon {
  margin-right: 8px;
  font-size: 18px;
  color: var(--primary-color);
}

.info-icon {
  margin-left: 8px;
  color: var(--text-secondary);
  cursor: help;
}

/* 上传区域样式 */
.upload-section {
  margin-top: 20px;
}

.upload-section h4 {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  color: var(--text-regular);
}

.upload-section h4 .el-icon {
  margin-right: 8px;
  color: var(--primary-color);
}

.resume-uploader {
  width: 100%;
}

.upload-trigger {
  padding: 20px 0;
}

.el-icon--upload {
  font-size: 48px;
  color: var(--primary-color);
  margin-bottom: 16px;
}

.el-upload__text {
  color: var(--text-regular);
  font-size: 16px;
  margin-bottom: 8px;
}

.el-upload__text em {
  color: var(--primary-color);
  font-style: normal;
  font-weight: bold;
}

.el-upload__tip {
  font-size: 12px;
  color: var(--text-secondary);
}

.uploaded-file {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 4px;
  background-color: #f5f7fa;
  margin-bottom: 8px;
}

.uploaded-file .el-icon {
  margin-right: 8px;
  color: var(--primary-color);
}

.filename {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 12px;
}

/* 结果展示区域样式 */
.resume-content {
  padding: 0 12px;
}

.resume-header {
  text-align: center;
  margin-bottom: 24px;
}

.resume-header h3 {
  font-size: 22px;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.contact-info {
  display: flex;
  justify-content: center;
  gap: 16px;
  color: var(--text-regular);
  flex-wrap: wrap;
}

.contact-info span {
  display: flex;
  align-items: center;
}

.contact-info .el-icon {
  margin-right: 6px;
}

.section-content {
  padding: 8px 0 16px;
  color: var(--text-regular);
  line-height: 1.6;
}

.experience-item {
  margin-bottom: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
}
.company {
  font-weight: bold;
  font-size: 16px;
}
.position {
  color: #666;
  margin: 4px 0;
}
.duration {
  color: #999;
  font-size: 12px;
}

.skills-section {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag {
  margin-right: 0;
}

.project-content {
  padding: 8px;
  line-height: 1.6;
}

.score-details pre {
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-regular);
  background-color: #f8f8f8;
  padding: 12px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

/* 评分样式 */
.score-display {
  display: flex;
  align-items: center;
}

.score-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease;
}

.score-circle:hover {
  transform: scale(1.05);
}

.score-excellent {
  background: linear-gradient(135deg, #52c41a, #95de64);
}

.score-qualified {
  background: linear-gradient(135deg, #faad14, #ffd666);
}

.score-failed {
  background: linear-gradient(135deg, #f5222d, #ff7875);
}

.score-value {
  font-size: 24px;
  font-weight: bold;
  line-height: 1;
}

.score-label {
  font-size: 12px;
  margin-top: 4px;
  opacity: 0.9;
}

/* 空状态样式 */
.empty-result {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 40px 0;
}

.empty-icon {
  font-size: 80px;
  color: var(--primary-light);
  margin-bottom: 16px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .resume-upload-container {
    padding: 16px;
  }
  
  .page-header h2 {
    font-size: 20px;
  }
  
  .contact-info {
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
  
  .score-circle {
    width: 50px;
    height: 50px;
  }
  
  .score-value {
    font-size: 20px;
  }
  
  .score-label {
    font-size: 10px;
  }
}

@media (max-width: 480px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .score-display {
    margin-top: 12px;
    align-self: flex-end;
  }
}
</style>