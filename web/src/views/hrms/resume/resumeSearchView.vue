<template>
  <div class="resume-search-container">
    <el-row :gutter="20">
      <!-- 左侧聊天区域 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card class="chat-card" shadow="hover">
          <template #header>
            <div class="chat-header">
              <h2><i class="el-icon-chat-dot-round"></i> 智能简历筛选助手</h2>
              <el-tag type="success" effect="dark" size="small">在线</el-tag>
            </div>
          </template>
          
          <div class="chat-body">
            <div class="chat-messages" ref="chatContainer">
              <template v-if="chatMessages.length > 0">
                <div v-for="(message, index) in chatMessages" :key="index" 
                  :class="['message', message.role === 'user' ? 'user-message' : 'ai-message']">
                  <div class="message-avatar">
                    <el-avatar :size="36" v-if="message.role === 'user'" icon="el-icon-user" />
                    <el-avatar :size="36" v-else src="/src/assets/ai-avatar.png" />
                  </div>
                  <div class="message-bubble">
                    <div class="message-content" v-html="renderMarkdown(message.content)"></div>
                    <div class="message-time">{{ formatTime(message.time || new Date()) }}</div>
                  </div>
                </div>
              </template>
              <div v-else class="empty-chat">
                <el-empty description="暂无对话记录" :image-size="100">
                  <template #description>
                    <p>开始向AI助手提问，获取简历筛选帮助</p>
                  </template>
                </el-empty>
              </div>
            </div>
            
            <div class="chat-input-container">
              <el-input
                v-model="userInput"
                placeholder="输入您的问题，例如：'帮我找出Java开发相关的简历'..."
                type="textarea"
                :rows="2"
                :disabled="isLoading"
                @keyup.enter.ctrl.native="sendMessage"
                class="chat-textarea"
              />
              <div class="input-actions">
                <span class="input-tip">按Ctrl+Enter发送</span>
                <el-button type="primary" @click="sendMessage" :loading="isLoading" :disabled="!userInput.trim()">
                  <i class="el-icon-s-promotion mr-1"></i> 发送
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧简历列表区域 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card class="resume-card" shadow="hover">
          <template #header>
            <div class="resume-header">
              <h2><i class="el-icon-document"></i> 简历列表</h2>
              <div class="resume-actions">
                <el-input 
                  v-model="searchKeyword" 
                  placeholder="搜索简历..."
                  prefix-icon="el-icon-search"
                  clearable
                  size="small"
                  class="search-input"
                />
                <el-button type="primary" size="small" @click="fetchResumes" icon="el-icon-refresh">刷新</el-button>
              </div>
            </div>
          </template>
          
          <el-table 
            :data="filteredResumeList" 
            style="width: 100%" 
            border
            v-loading="tableLoading"
            class="resume-table"
            :header-cell-style="{backgroundColor: '#f5f7fa'}"
            empty-text="暂无简历数据"
            highlight-current-row
            @row-click="viewDetail"
          >
            <el-table-column prop="name" label="姓名" min-width="90">
              <template #default="{row}">
                <div class="name-cell">
                  <el-avatar :size="24" icon="el-icon-user" class="mr-1"></el-avatar>
                  <span>{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="phone" label="联系方式" min-width="120" show-overflow-tooltip />
            <el-table-column prop="education" label="教育背景" min-width="120" show-overflow-tooltip />
            <el-table-column label="AI评分" min-width="90" align="center">
              <template #default="{row}">
                <el-progress 
                  :percentage="row.score" 
                  :color="getScoreColor(row.score)"
                  :stroke-width="16"
                  :format="(p) => p + '分'"
                  class="score-progress"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right" align="center">
              <template #default="{row}">
                <el-button type="primary" size="small" @click.stop="viewDetail(row)" icon="el-icon-view">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="table-footer">
            <el-pagination
              :current-page="currentPage"
              :page-sizes="[10, 20, 30, 50]"
              :page-size="pageSize"
              layout="total, sizes, prev, pager, next, jumper"
              :total="resumeList.length"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              background
              hide-on-single-page
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 简历详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="简历详情"
      width="70%"
      :before-close="handleClose"
      destroy-on-close
      top="5vh"
    >
      <div v-if="currentResume" class="resume-detail">
        <div class="resume-detail-header">
          <div class="resume-person-info">
            <el-avatar :size="64" icon="el-icon-user" class="person-avatar"></el-avatar>
            <div class="person-meta">
              <h2>{{ currentResume.name }}</h2>
              <div class="meta-items">
                <span v-if="currentResume.phone"><i class="el-icon-phone"></i> {{ currentResume.phone }}</span>
                <span v-if="currentResume.email"><i class="el-icon-message"></i> {{ currentResume.email }}</span>
              </div>
            </div>
          </div>
          <div class="resume-score">
            <div class="score-label">AI评分</div>
            <el-progress type="dashboard" :percentage="currentResume.score" :color="getScoreColor(currentResume.score)" />
          </div>
        </div>
        
        <el-divider content-position="left">详细信息</el-divider>
        
        <el-tabs type="border-card">
          <el-tab-pane label="基本信息">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="姓名">{{ currentResume.name }}</el-descriptions-item>
              <el-descriptions-item label="电话">{{ currentResume.phone }}</el-descriptions-item>
              <el-descriptions-item label="邮箱">{{ currentResume.email }}</el-descriptions-item>
              <el-descriptions-item label="教育背景">{{ currentResume.education }}</el-descriptions-item>
              <el-descriptions-item label="工作经验" :span="2">
                {{ currentResume.work_experience || '暂无工作经验' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane label="技能与专长">
            <div class="skills-container">
              <template v-if="currentResume.skills && currentResume.skills.length > 0">
                <el-tag 
                  v-for="(skill, index) in currentResume.skills" 
                  :key="index" 
                  :type="getRandomTagType()"
                  effect="light"
                  class="skill-tag"
                >
                  {{ skill }}
                </el-tag>
              </template>
              <el-empty v-else description="暂无技能信息" :image-size="80" />
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="AI评价">
            <div class="ai-evaluation">
              <div class="evaluation-header">
                <i class="el-icon-s-opportunity"></i>
                <span>AI智能评价</span>
              </div>
              <div class="evaluation-content">
                {{ currentResume.ai_evaluation || '暂无AI评价' }}
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="handleDownloadResume">下载简历</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup name="resumeSearch">
import { ref, computed, nextTick, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { GetList, GetInfo, SendChatMessage } from './api';
import { APIResponseData } from '../types';

// 路由
const router = useRouter();

// 简历列表相关
const resumeList = ref([]);
const tableLoading = ref(false);
const searchKeyword = ref('');
const currentPage = ref(1);
const pageSize = ref(10);

// 聊天相关
const chatMessages = ref([]);
const userInput = ref('');
const isLoading = ref(false);
const chatContainer = ref(null);

// 详情对话框相关
const dialogVisible = ref(false);
const currentResume = ref(null);

/**
 * 过滤后的简历列表
 */
const filteredResumeList = computed(() => {
  if (!searchKeyword.value) {
    // 分页处理
    const startIndex = (currentPage.value - 1) * pageSize.value;
    return resumeList.value.slice(startIndex, startIndex + pageSize.value);
  }
  
  // 搜索过滤
  const keyword = searchKeyword.value.toLowerCase();
  const filtered = resumeList.value.filter(resume => {
    return resume.name?.toLowerCase().includes(keyword) ||
           resume.phone?.toLowerCase().includes(keyword) ||
           resume.email?.toLowerCase().includes(keyword) ||
           resume.education?.toLowerCase().includes(keyword) ||
           resume.work_experience?.toLowerCase().includes(keyword) ||
           (resume.skills && resume.skills.some(skill => skill.toLowerCase().includes(keyword)));
  });
  
  // 分页处理
  const startIndex = (currentPage.value - 1) * pageSize.value;
  return filtered.slice(startIndex, startIndex + pageSize.value);
});

/**
 * 从后端获取简历列表
 */
const fetchResumes = async () => {
  tableLoading.value = true;
  try {
    let res: APIResponseData = await GetList({});

    if (res?.code === 2000 && Array.isArray(res.data)) {
      resumeList.value = res.data as Array<any>;
      // 重置分页
      currentPage.value = 1;
    } else {
      ElMessage.error('获取简历列表失败');
    }
  } catch (error) {
    console.error('获取简历列表失败:', error);
    ElMessage.error('获取简历列表失败，请检查网络连接');
  } finally {
    tableLoading.value = false;
  }
};

/**
 * 根据评分获取标签颜色
 */
const getScoreColor = (score) => {
  if (score >= 90) return '#67c23a';
  if (score >= 75) return '#409eff';
  if (score >= 60) return '#e6a23c';
  return '#f56c6c';
};

/**
 * 随机获取标签类型，用于技能标签展示
 */
const getRandomTagType = () => {
  const types = ['', 'success', 'info', 'warning', 'danger'];
  return types[Math.floor(Math.random() * types.length)];
};

/**
 * 查看简历详情
 */
const viewDetail = (resume) => { 
  currentResume.value = resume;
  dialogVisible.value = true;
};

/**
 * 关闭详情对话框
 */
const handleClose = () => {
  dialogVisible.value = false;
};

/**
 * 下载简历
 */
const handleDownloadResume = () => {
  if (!currentResume.value) return;
  
  ElMessage({
    message: '简历下载功能正在开发中',
    type: 'info'
  });
  // 这里可以实现简历下载逻辑
};

/**
 * 获取简历详情
 */
const getResumeDetail = async (id) => {
  try {
    let res: APIResponseData = await GetInfo(id.toString());
    return res.data;
  } catch (error) {
    console.error('获取简历详情失败:', error);
    const resume = resumeList.value.find(item => item.id === id);
    return resume || null;
  }
};

/**
 * 发送聊天消息
 */
const sendMessage = async () => {
  if (!userInput.value.trim()) return;
  
  // 添加用户消息
  chatMessages.value.push({
    role: 'user',
    content: userInput.value,
    time: new Date()
  });

  // 滚动到底部
  await scrollToBottom();
  
  // 保存用户输入并清空输入框
  const message = userInput.value;
  userInput.value = '';
  isLoading.value = true;

  try {
    // 调用AI接口
    const response = await SendChatMessage({
      message: message
    });
    
    // 处理AI回复
    if (response.error) { 
      chatMessages.value.push({
        role: 'assistant',
        content: `发生错误: ${response.error}`,
        time: new Date()
      });
    } else {
      // 判断是否需要更新简历列表
      if (response.need_search) {
        // 更新简历列表
        if (Array.isArray(response.data?.data)) {
          resumeList.value = response.data.data;
          // 重置分页
          currentPage.value = 1;
        }
      }
      
      // 添加AI回复
      chatMessages.value.push({
        role: 'assistant',
        content: response.reply,
        time: new Date()
      });
    }

    // 滚动到底部
    await scrollToBottom();
  } catch (error) { 
    console.error('发送消息失败:', error);
    chatMessages.value.push({
      role: 'assistant',
      content: `发送消息失败: ${error.message || '未知错误'}`,
      time: new Date()
    });
  } finally {
    isLoading.value = false;
  }
};

/**
 * 滚动聊天容器到底部
 */
const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

/**
 * 格式化时间
 */
const formatTime = (date) => {
  if (!date) return '';
  const d = new Date(date);
  const hours = d.getHours().toString().padStart(2, '0');
  const minutes = d.getMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
};

/**
 * 渲染Markdown内容
 */
const renderMarkdown = (content) => {
  return DOMPurify.sanitize(marked(content || ''));
};

/**
 * 处理分页大小变化
 */
const handleSizeChange = (size) => {
  pageSize.value = size;
  currentPage.value = 1; // 重置到第一页
};

/**
 * 处理页码变化
 */
const handleCurrentChange = (page) => {
  currentPage.value = page;
};

// 组件挂载时初始化
onMounted(() => {
  // 获取简历列表
  fetchResumes();
  
  // 添加AI助手的欢迎消息
  chatMessages.value.push({
    role: 'assistant',
    content: '你好！我是你的AI助手，我可以帮你分析简历、回答招聘相关的问题，还可以根据你的需求筛选合适的简历。请随时向我提问。',
    time: new Date()
  });
});
</script>

<style scoped>
/* 全局容器 */
.resume-search-container {
  --primary-color: #409eff;
  --success-color: #67c23a;
  --warning-color: #e6a23c;
  --danger-color: #f56c6c;
  --info-color: #909399;
  --border-color: #ebeef5;
  --bg-color: #f5f7fa;
  --text-color: #303133;
  --text-color-secondary: #606266;
  --text-color-placeholder: #c0c4cc;
  --border-radius: 4px;
  --transition-duration: 0.3s;
  --box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  
  padding: 20px;
  min-height: calc(100vh - 120px);
}

/* 卡片样式 */
.chat-card, .resume-card {
  height: 100%;
  margin-bottom: 20px;
  transition: all var(--transition-duration);
}

.chat-card:hover, .resume-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

/* 卡片头部 */
.chat-header, .resume-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h2, .resume-header h2 {
  margin: 0;
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.resume-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-input {
  width: 200px;
}

/* 聊天区域 */
.chat-body {
  display: flex;
  flex-direction: column;
  height: 600px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: var(--bg-color);
  border-radius: var(--border-radius);
  margin-bottom: 16px;
}

.empty-chat {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.message {
  display: flex;
  margin-bottom: 16px;
  max-width: 85%;
}

.user-message {
  flex-direction: row-reverse;
  margin-left: auto;
}

.ai-message {
  margin-right: auto;
}

.message-avatar {
  margin: 0 8px;
}

.message-bubble {
  padding: 12px;
  border-radius: 12px;
  position: relative;
}

.user-message .message-bubble {
  background-color: var(--primary-color);
  color: white;
  border-top-right-radius: 2px;
}

.ai-message .message-bubble {
  background-color: white;
  border: 1px solid var(--border-color);
  border-top-left-radius: 2px;
}

.message-content {
  word-break: break-word;
}

.message-content :deep(p) {
  margin-block-start: 0;
  margin-block-end: 0.5em;
}

.message-content :deep(p:last-child) {
  margin-block-end: 0;
}

.message-time {
  font-size: 12px;
  margin-top: 4px;
  text-align: right;
  opacity: 0.7;
}

.user-message .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.chat-input-container {
  padding: 16px;
  background-color: white;
  border-radius: var(--border-radius);
  border: 1px solid var(--border-color);
}

.chat-textarea {
  margin-bottom: 10px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-tip {
  font-size: 12px;
  color: var(--text-color-placeholder);
}

/* 简历表格 */
.resume-table {
  margin-bottom: 16px;
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-progress {
  margin: 0;
}

.table-footer {
  padding-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* 简历详情 */
.resume-detail {
  padding: 0 16px;
}

.resume-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.resume-person-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.person-meta {
  display: flex;
  flex-direction: column;
}

.person-meta h2 {
  margin: 0 0 8px 0;
}

.meta-items {
  display: flex;
  gap: 16px;
  color: var(--text-color-secondary);
}

.meta-items span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.resume-score {
  text-align: center;
}

.score-label {
  margin-bottom: 8px;
  font-weight: bold;
  color: var(--text-color-secondary);
}

.skills-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 16px;
}

.skill-tag {
  padding: 8px 16px;
  font-size: 14px;
}

.ai-evaluation {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: var(--border-radius);
  border-left: 4px solid var(--primary-color);
}

.evaluation-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  margin-bottom: 12px;
  color: var(--primary-color);
}

.evaluation-content {
  line-height: 1.6;
  color: var(--text-color);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .chat-body {
    height: 400px;
  }
  
  .resume-detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .resume-score {
    align-self: center;
    width: 100%;
  }
  
  .meta-items {
    flex-direction: column;
    gap: 8px;
  }
}
</style>