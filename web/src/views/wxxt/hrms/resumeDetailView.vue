<template>
  <div class="container">
    <div class="header-container">
      <h1>简历详情</h1>
      <el-button type="primary" @click="goBack">返回列表</el-button>
    </div>

    <el-descriptions :column="1" border>
      <el-descriptions-item label="姓名">{{ resumeData.name }}</el-descriptions-item>
      <el-descriptions-item label="电话">{{ resumeData.phone }}</el-descriptions-item>
      <el-descriptions-item label="邮箱">{{ resumeData.email }}</el-descriptions-item>
      <el-descriptions-item label="教育背景">{{ resumeData.education }}</el-descriptions-item>
      <el-descriptions-item label="AI评分">
        <el-tag :type="getScoreType(resumeData.score)">{{ resumeData.score }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="工作经验">{{ resumeData.work_experience }}</el-descriptions-item>
      <el-descriptions-item label="技能">
        <el-tag v-for="(skill, index) in resumeData.skills" :key="index" type="info" style="margin-right: 5px;">{{ skill }}</el-tag>
      </el-descriptions-item>
    </el-descriptions>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const resumeData = ref({
  name: '',
  phone: '',
  email: '',
  education: '',
  experience: [],
  skills: [],
  score: 0
});

// 根据评分获取标签类型
const getScoreType = (score) => {
  if (score >= 90) return 'success';
  if (score >= 60) return 'warning';
  return 'danger';
};

// 获取简历详情数据
const fetchResumeDetail = async () => {
  try {
    const response = await axios.get(`/api/resumes/${route.params.id}`);
    resumeData.value = response.data.data.metadata;
  } catch (error) {
    console.error('获取简历详情失败:', error);
  }
};

// 返回列表
const goBack = () => {
  router.push('/resume-search');
};

onMounted(() => {
  fetchResumeDetail();
});
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
</style>