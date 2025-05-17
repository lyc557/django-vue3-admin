<template>
  <div class="container">
    
    <div class="header-container">
      <h1>智能简历筛选--简历筛选对话</h1>
      
      <div class="actions">
        <el-button type="primary" @click="openHomePage">简历上传页面</el-button>
      </div>
    </div>

    <div class="chat-container">
      <div class="chat-messages" ref="chatContainer">
        <div v-for="(message, index) in chatMessages" :key="index" 
          :class="['message', message.role === 'user' ? 'user-message' : 'ai-message']">
          <div class="message-avatar">
            <img v-if="message.role === 'user'" src="../assets/user-avatar.png" alt="用户头像">
            <img v-else src="../assets/ai-avatar.png" alt="AI头像">
          </div>
          <div class="message-content" v-html="renderMarkdown(message.content)"></div>
        </div>
      </div>
      
      <div class="chat-input">
        <el-input
          v-model="userInput"
          placeholder="输入您的问题..."
          type="textarea"
          :rows="2"
          @keyup.enter.ctrl.native="sendMessage"
        />
        <el-button type="primary" @click="sendMessage" :loading="isLoading">
          发送
        </el-button>
      </div>
    </div>

    <el-table 
      :data="resumeList" 
      style="width: 100%" 
      name="简历列表"
      border
      class="resume-table"
    >
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="phone" label="电话" width="150" />
      <el-table-column prop="email" label="邮箱" width="200" />
      <el-table-column prop="education" label="教育背景" />
      <el-table-column label="AI评分" width="100">
        <template #default="{row}">
          <el-tag :type="getScoreType(row.score)">
            {{ row.score }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{row}">
          <el-button @click="viewDetail(row)">查看详情</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { marked } from 'marked'; // 添加Markdown解析器
import DOMPurify from 'dompurify';

const router = useRouter();
const resumeList = ref([]);

// 获取简历列表数据
const fetchResumes = async () => {
  try {
    const response = await axios.get('/api/resumes');
    // 从response.data.data获取数组数据
    resumeList.value = Array.isArray(response.data?.data) ? response.data.data : [];
  } catch (error) {
    console.error('获取简历列表失败:', error);
    resumeList.value = []; // Fallback to empty array
  }
};

// 根据评分获取标签类型
const getScoreType = (score) => {
  if (score >= 90) return 'success';
  if (score >= 60) return 'warning';
  return 'danger';
};

// 查看简历详情
const viewDetail = (resume) => {
  router.push(`/resume-detail/${resume.id}`);
};

const openHomePage = () => {
  window.location.href = '/';
};


const chatMessages = ref([]);
    const userInput = ref('');
    const isLoading = ref(false);
    const chatContainer = ref(null);

    // 组件挂载时推送AI助手的自我介绍消息
    chatMessages.value.push({
        role: 'assistant',
        content: '你好！我是你的AI助手，我可以帮你分析简历、回答招聘相关的问题。请随时向我提问。'
    });

    const sendMessage = async () => {
      if (!userInput.value.trim()) return;
      
      // 添加用户消息
      chatMessages.value.push({
        role: 'user',
        content: userInput.value
      });

      isLoading.value = true;

      try {
        // 调用AI接口
        const response = await axios.post('/api/chat', {
          message: userInput.value
        });


        // 处理AI回复
        if(response.data.error){ 
          chatMessages.value.push({
            role: 'assistant',
            content: response.data.error  // 修改为从data.reply获取回复内容
          });
        }else{
          // 判断是否需要更新简历列表
          if (response.data.need_search) {
            // 先清空简历列表
            resumeList.value = [];
            // 从response.data.data获取数组数据并更新简历列表

            resumeList.value = Array.isArray(response.data.data.data) ? response.data.data.data : [];
          }
          // 添加AI回复
          chatMessages.value.push({
            role: 'assistant',
            content: response.data.reply  // 修改为从data.reply获取回复内容
          });
        }

        // 清空输入
        userInput.value = '';

        // 滚动到底部
        await nextTick();
        if (chatContainer.value) {
          chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
        }
      } catch (error) { 
        console.error('发送消息失败:', error);
        chatMessages.value.push({
            role: 'assistant',
            content: error.response?.data.error || 'Message is required'
          });
      } finally {
        isLoading.value = false;
      }
    };

// 初始化获取数据
fetchResumes();

// 添加Markdown渲染方法
const renderMarkdown = (content) => {
  return DOMPurify.sanitize(marked(content || ''));
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

    .chat-container {
        margin: 20px 0;
        border: 1px solid #dcdfe6;
        border-radius: 4px;
        padding: 20px;
    }

    .chat-messages {
        height: 300px;
        overflow-y: auto;
        margin-bottom: 20px;
        padding: 10px;
        background-color: #fff; /* 添加背景色 */
        border: 1px solid #ebeef5; /* 添加边框 */
        border-radius: 4px; /* 统一圆角 */
    }

    .message {
        display: flex;
        align-items: flex-start;  /* 修改为flex-start确保顶部对齐 */
        gap: 10px;
        margin: 10px 0;
        padding: 10px;
        border-radius: 4px;
        max-width: 80%;
    }
    
    .message-avatar {
        display: flex;
        align-items: center;  /* 添加垂直居中 */
        height: 100%;  /* 确保头像容器高度与消息内容一致 */
    }
    
    .message-avatar img {
        width: 32px;
        height: 32px;
        border-radius: 50%;
    }
    
    .message-content {
        word-break: break-word;
        align-self: center;  /* 添加垂直居中 */
        & :deep(p) {
            margin-block-start: 0;
            margin-block-end: 0;
        }
    }

    .user-message {
        background-color: #ecf5ff;
        margin-left: auto;
        flex-direction: row-reverse;
    }
    
    .ai-message {
        background-color: #f4f4f5;
        margin-right: auto;
    }

    .message-content {
        word-break: break-word;
    }

    .chat-input {
        display: flex;
        gap: 10px;
    }

    .resume-table {
      border: 1px solid #ebeef5;
      border-radius: 4px;
      margin-top: 20px;
    }
</style>