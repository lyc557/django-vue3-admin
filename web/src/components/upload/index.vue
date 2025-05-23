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
      :before-upload="handleBeforeUpload"
      :on-success="handleUploadSuccess"
      :on-error="handleUploadError"
      :on-progress="handleUploadProgress"
      :on-exceed="handleExceed"
      :file-list="fileList"
      :http-request="customUploadRequest"
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

<script setup>
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
    default: true
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

// 上传前检查
const handleBeforeUpload = (file) => {
  // 检查文件大小
  const isLtMaxSize = file.size / 1024 / 1024 < props.maxSize
  if (!isLtMaxSize) {
    ElMessage.error(`文件大小不能超过 ${props.maxSize}MB!`)
    return false
  }
  
  // 如果有自定义的beforeUpload函数，则调用
  if (props.beforeUpload) {
    return props.beforeUpload(file)
  }
  
  return true
}

// 自定义上传请求
const customUploadRequest = (options) => {
  const { file, onProgress, onSuccess, onError } = options
  
  // 创建FormData对象
  const formData = new FormData()
  formData.append('file', file)
  
  // 创建XMLHttpRequest对象
  const xhr = new XMLHttpRequest()
  
  // 监听上传进度
  xhr.upload.addEventListener('progress', (e) => {
    if (e.lengthComputable) {
      const percentage = Math.round((e.loaded * 100) / e.total)
      onProgress({ percent: percentage })
    }
  })
  
  // 请求完成
  xhr.addEventListener('load', () => {
    if (xhr.status >= 200 && xhr.status < 300) {
      try {
        const response = JSON.parse(xhr.responseText)
        onSuccess(response)
      } catch (e) {
        onSuccess({ url: xhr.responseText })
      }
    } else {
      onError({ status: xhr.status, message: xhr.statusText })
    }
  })
  
  // 请求错误
  xhr.addEventListener('error', () => {
    onError({ status: xhr.status, message: '上传失败' })
  })
  
  // 请求超时
  xhr.addEventListener('timeout', () => {
    onError({ message: '上传超时' })
  })


  // 发送请求
  xhr.open('POST', getBaseURL(props.uploadUrl), true)
  // 添加认证头
  let uploadHeaders = ref({
    Authorization: 'JWT ' + Session.get('token'),
  });

  xhr.setRequestHeader('Authorization', uploadHeaders.value.Authorization);
  xhr.setRequestHeader('Content-Type', 'multipart/form-data');
  xhr.send(formData)
  
  // 返回上传取消函数
  return {
    abort: () => {
      xhr.abort()
    }
  }
}

// 上传成功处理
const handleUploadSuccess = (response, file, fileList) => {
  // 获取上传成功后的文件URL
  const fileUrl = response.url || response.data?.url || ''
  
  if (fileUrl) {
    // 更新当前文件的URL
    const currentFile = fileList.value.find(item => item.uid === file.uid)
    if (currentFile) {
      currentFile.url = fileUrl
    }
    
    // 更新modelValue
    const successFiles = fileList.value
      .filter(file => file.status === 'success' && file.url)
      .map(file => file.url)
    
    emit('update:modelValue', successFiles)
    emit('upload-success', { file, response })
  }
  
  ElMessage.success(`文件 ${file.name} 上传成功`)
}

// 上传错误处理
const handleUploadError = (error, file, fileList) => {
  ElMessage.error(`文件 ${file.name} 上传失败: ${error.message || '未知错误'}`)
  emit('upload-error', { file, error })
}

// 上传进度处理
const handleUploadProgress = (event, file, fileList) => {
  emit('upload-progress', { file, event })
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