<template>
  <div class="file-uploader">
    <el-upload
      ref="uploadRef"
      class="upload-container"
      :action="uploadUrl"
      :multiple="multiple"
      :limit="limit"
      :accept="accept"
      :directory="directory"
      :drag="drag"
      :auto-upload="autoUpload"
      :show-file-list="showFileList"
      :on-exceed="handleExceed"
      :file-list="fileList"
      :http-request="customUploadRequest"
      :on-change="handleFileChange"
    >
      <template #default>
        <slot>
          <div v-if="drag" class="el-upload__text">
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="upload-text">
              将文件拖到此处或<em>点击上传</em>
            </div>
          </div>
        </slot>
      </template>
      
      <template #tip>
        <slot name="tip">
          <div class="el-upload__tip">
            {{ tipText }}
          </div>
        </slot>
      </template>
      
      <template #file="{ file }">
        <slot name="file" :file="file"></slot>
      </template>
    </el-upload>
    
    <div v-if="showUploadList && fileList.length > 0" class="upload-list">
      <h4>上传文件列表</h4>
      <el-table :data="fileList" style="width: 100%">
        <el-table-column prop="name" label="文件名" />
        <el-table-column label="大小" width="120">
          <template #default="scope">
            {{ formatFileSize(scope.row.size) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="180">
          <template #default="scope">
            <el-progress 
              v-if="scope.row.status === 'uploading'" 
              :percentage="scope.row.percentage || 0" 
            />
            <span v-else-if="scope.row.status === 'success'">完成</span>
            <span v-else-if="scope.row.status === 'error'" class="error-message">
              {{ scope.row.response?.message || '上传失败' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button 
              link 
              type="danger" 
              @click="handleRemoveFile(scope.row)"
              :disabled="scope.row.status === 'uploading'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="upload-actions" v-if="!autoUpload">
        <el-button type="primary" @click="submitUpload">开始上传</el-button>
        <el-button @click="clearFiles">清空列表</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { getBaseURL } from '/@/utils/baseUrl';
import { Session } from '/@/utils/storage';

// 在props中添加apiBaseUrl
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  uploadUrl: {
    type: String,
    default: '/api/xxx/upload/'
  },
  multiple: {
    type: Boolean,
    default: true
  },
  drag: {
    type: Boolean,
    default: true
  },
  limit: {
    type: Number,
    default: 10
  },
  accept: {
    type: String,
    default: ''
  },
  directory: {
    type: Boolean,
    default: false
  },
  autoUpload: {
    type: Boolean,
    default: false
  },
  showFileList: {
    type: Boolean,
    default: false
  },
  showUploadList: {
    type: Boolean,
    default: true
  },
  beforeUpload: {
    type: Function,
    default: null
  },
  maxSize: {
    type: Number,
    default: 100 // 默认10MB
  },
  tipText: {
    type: String,
    default: '支持多种文件格式，单个文件不超过100MB'
  }
})

const emit = defineEmits(['update:modelValue', 'upload-success', 'upload-error', 'upload-progress', 'file-removed'])

const uploadRef = ref(null)
const fileList = ref([])

// 监听modelValue变化
watch(() => props.modelValue, (newVal) => {
  // 如果外部传入的值变化，更新内部的fileList
  if (newVal && Array.isArray(newVal)) {
    // 只处理URL字符串数组转换为文件对象数组
    const existingUrls = fileList.value
      .filter(file => file.status === 'success')
      .map(file => file.url)
    
    // 添加新的URL
    newVal.forEach(url => {
      if (!existingUrls.includes(url)) {
        fileList.value.push({
          name: getFileNameFromUrl(url),
          url: url,
          status: 'success'
        })
      }
    })
    
    // 移除已不存在的URL
    fileList.value = fileList.value.filter(file => 
      file.status !== 'success' || newVal.includes(file.url)
    )
  }
}, { deep: true })

// 从URL中提取文件名
const getFileNameFromUrl = (url) => {
  try {
    return url.substring(url.lastIndexOf('/') + 1)
  } catch (e) {
    return url
  }
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (!size) return '未知'
  
  if (size < 1024) {
    return size + ' B'
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + ' KB'
  } else {
    return (size / (1024 * 1024)).toFixed(2) + ' MB'
  }
}

// 获取状态类型
const getStatusType = (status) => {
  switch (status) {
    case 'success': return 'success'
    case 'error': return 'danger'
    default: return 'info'
  }
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'ready': return '待上传'
    case 'uploading': return '上传中'
    case 'success': return '成功'
    case 'error': return '失败'
    default: return '未知'
  }
}

// 自定义上传请求
const customUploadRequest = (options) => {
  console.log('customUploadRequest', options);
  const { file, onProgress, onSuccess, onError } = options;

  const formData = new FormData();
  formData.append('file', file);

  const xhr = new XMLHttpRequest();

  xhr.upload.addEventListener('progress', (e) => {
    if (e.lengthComputable) {
      const percentage = Math.round((e.loaded * 100) / e.total);
      onProgress({ percent: percentage });
      file.status = 'uploading';
      file.percentage = percentage;
      emit('upload-progress', percentage, file);
    }
  });

  xhr.addEventListener('load', () => {
    if (xhr.status >= 200 && xhr.status < 300) {
      let response;
      try {
        response = JSON.parse(xhr.responseText);
      } catch (e) {
        response = { url: xhr.responseText };
      }

      file.status = 'success';
      file.url = response.url || '';
      file.response = response;
      onSuccess(response);
      emit('upload-success', response, file);

      // 更新绑定的 v-model
      const successFiles = fileList.value
        .filter(f => f.status === 'success' && f.url)
        .map(f => f.url);
      emit('update:modelValue', successFiles);

    } else {
      const err = { status: xhr.status, message: xhr.statusText };
      file.status = 'error';
      file.response = err;
      onError(err);
      emit('upload-error', err, file);
    }
  });

  xhr.addEventListener('error', () => {
    const err = { status: xhr.status, message: '上传失败' };
    file.status = 'error';
    file.response = err;
    onError(err);
    emit('upload-error', err, file);
  });

  xhr.addEventListener('timeout', () => {
    const err = { message: '上传超时' };
    file.status = 'error';
    file.response = err;
    onError(err);
    emit('upload-error', err, file);
  });

  xhr.open('POST', getBaseURL(props.uploadUrl), true);

  let uploadHeaders = ref({
    Authorization: 'JWT ' + Session.get('token'),
  });
  xhr.setRequestHeader('Authorization', uploadHeaders.value.Authorization);

  // 不需要设置 Content-Type 为 multipart/form-data
  // 浏览器在 FormData 会自动设置合适的 Content-Type 和边界
  // xhr.setRequestHeader('Content-Type', 'multipart/form-data'); // ← 请移除这行

  xhr.send(formData);

  return {
    abort: () => {
      xhr.abort();
    }
  };
}


// 超出限制处理
const handleExceed = (files, fileList) => {
  ElMessage.warning(`最多只能上传 ${props.limit} 个文件，本次选择了 ${files.length} 个文件，共超出 ${files.length + fileList.length - props.limit} 个文件`)
}

// 移除文件
const handleRemoveFile = (file) => {
  fileList.value = fileList.value.filter(item => item !== file)
  
  // 更新modelValue
  const successFiles = fileList.value
    .filter(file => file.status === 'success' && file.url)
    .map(file => file.url)
  
  emit('update:modelValue', successFiles)
  emit('file-removed', file)
}

// 提交上传（用于非自动上传模式）
const submitUpload = () => {
  uploadRef.value.submit()
}

// 清空文件列表
const clearFiles = () => {
  fileList.value = []
  emit('update:modelValue', [])
}

const handleFileChange = (file, fileList) => {
  console.log('handleFileChange', file, fileList);
  console.log('props.beforeUpload', props.beforeUpload);
  // 1. 处理 before-upload 的功能
  if (props.beforeUpload) {

    const beforeResult = props.beforeUpload(file);
    if (beforeResult === false) {
      // 如果返回false，阻止文件添加
      return false;
    }
    if (beforeResult instanceof Promise) {
      beforeResult.then(res => {
        if (res === false) {
          // 异步返回false，从列表中移除文件
          fileList.splice(fileList.indexOf(file), 1);
        }
      });
    }
  }

  // 2. 设置文件状态为ready
  file.status = 'ready';
  
  // 3. 触发progress事件（如果需要）
  emit('upload-progress', 0, file);
  
  // 4. 返回true允许文件添加
  return true;
};


// 暴露方法给父组件
defineExpose({
  submitUpload,
  clearFiles,
  uploadRef
})

</script>

<style scoped>
.file-uploader {
  width: 100%;
}

.upload-container {
  width: 100%;
}

.upload-text {
  margin-top: 10px;
  color: #606266;
}

.upload-list {
  margin-top: 20px;
}

.upload-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.error-message {
  color: #F56C6C;
}

:deep(.el-upload-dragger) {
  width: 100%;
  height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

:deep(.el-icon--upload) {
  font-size: 48px;
  color: #909399;
  margin-bottom: 10px;
}
</style>