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
      :before-upload="handleBeforeUpload"
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
import { ref, watch, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { getBaseURL } from '/@/utils/baseUrl'
import { Session } from '/@/utils/storage'

/**
 * 定义文件状态类型
 */
type FileStatus = 'ready' | 'uploading' | 'success' | 'error'

/**
 * 定义文件项类型
 */
interface FileItem {
  uid?: string
  name: string
  size?: number
  status?: FileStatus
  percentage?: number
  url?: string
  response?: any
}

/**
 * 文件上传组件属性定义
 */
const props = defineProps({
  // 双向绑定的文件列表值
  modelValue: {
    type: Array,
    default: () => []
  },
  // 上传URL地址
  uploadUrl: {
    type: String,
    default: '/api/xxx/upload/'
  },
  // 是否支持多文件上传
  multiple: {
    type: Boolean,
    default: true
  },
  // 是否启用拖拽上传
  drag: {
    type: Boolean,
    default: true
  },
  // 最大上传文件数量
  limit: {
    type: Number,
    default: 10
  },
  // 接受的文件类型
  accept: {
    type: String,
    default: ''
  },
  // 是否支持文件夹上传
  directory: {
    type: Boolean,
    default: false
  },
  // 是否自动上传
  autoUpload: {
    type: Boolean,
    default: false
  },
  // 是否显示el-upload的文件列表
  showFileList: {
    type: Boolean,
    default: false
  },
  // 是否显示自定义的上传文件列表
  showUploadList: {
    type: Boolean,
    default: true
  },
  // 上传前的钩子函数
  beforeUpload: {
    type: Function,
    default: null
  },
  // 最大文件大小(MB)
  maxSize: {
    type: Number,
    default: 100
  },
  // 提示文本
  tipText: {
    type: String,
    default: '支持多种文件格式，单个文件不超过100MB'
  },
  // 额外的请求头
  headers: {
    type: Object,
    default: () => ({})
  },
  // 额外的请求参数
  data: {
    type: Object,
    default: () => ({})
  }
})

/**
 * 定义组件事件
 */
const emit = defineEmits([
  'update:modelValue',
  'update:showUploadList',
  'upload-success',
  'upload-error',
  'upload-progress',
  'file-removed',
  'file-added'
])

// 上传组件引用
const uploadRef = ref(null)
// 文件列表
const fileList = ref<FileItem[]>([])

/**
 * 监听modelValue变化，同步文件列表
 */
watch(() => props.modelValue, (newVal) => {
  if (newVal && Array.isArray(newVal)) {
    // 获取当前成功文件的URL列表
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
}, { deep: true, immediate: true })

/**
 * 从URL中提取文件名
 * @param {string} url - 文件URL
 * @returns {string} - 提取的文件名
 */
const getFileNameFromUrl = (url: string): string => {
  if (!url) return '未知文件'
  try {
    return url.substring(url.lastIndexOf('/') + 1)
  } catch (e) {
    return url
  }
}

/**
 * 格式化文件大小
 * @param {number} size - 文件大小（字节）
 * @returns {string} - 格式化后的文件大小
 */
const formatFileSize = (size?: number): string => {
  if (!size) return '未知'
  
  if (size < 1024) {
    return size + ' B'
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + ' KB'
  } else {
    return (size / (1024 * 1024)).toFixed(2) + ' MB'
  }
}

/**
 * 获取状态对应的类型
 * @param {string} status - 文件状态
 * @returns {string} - 对应的类型
 */
const getStatusType = (status?: FileStatus): string => {
  switch (status) {
    case 'success': return 'success'
    case 'error': return 'danger'
    case 'uploading': return 'primary'
    default: return 'info'
  }
}

/**
 * 获取状态对应的文本
 * @param {string} status - 文件状态
 * @returns {string} - 对应的文本
 */
const getStatusText = (status?: FileStatus): string => {
  switch (status) {
    case 'ready': return '待上传'
    case 'uploading': return '上传中'
    case 'success': return '成功'
    case 'error': return '失败'
    default: return '未知'
  }
}

/**
 * 验证文件类型
 * @param {File} file - 文件对象
 * @returns {boolean} - 是否通过验证
 */
const validateFileType = (file: File): boolean => {
  if (!props.accept) return true
  
  const fileName = file.name || ''
  const fileExt = '.' + fileName.split('.').pop()?.toLowerCase()
  const acceptTypes = props.accept.split(',').map(type => type.trim())
  
  // 检查文件扩展名是否在接受列表中
  return acceptTypes.some(type => {
    // 处理MIME类型 (如 image/png)
    if (type.includes('/')) {
      return file.type.match(type)
    }
    // 处理文件扩展名 (如 .png)
    return type === fileExt || type === '*'
  })
}

/**
 * 验证文件大小
 * @param {File} file - 文件对象
 * @returns {boolean} - 是否通过验证
 */
const validateFileSize = (file: File): boolean => {
  const maxBytes = props.maxSize * 1024 * 1024
  return file.size <= maxBytes
}

/**
 * 上传前的处理函数
 * @param {File} file - 文件对象
 * @returns {boolean|Promise} - 是否继续上传
 */
const handleBeforeUpload = (file: File) => {
  // 检查文件类型
  if (!validateFileType(file)) {
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase()
    ElMessage.error(`不支持的文件类型: ${fileExt}`)
    return false
  }
  
  // 检查文件大小
  if (!validateFileSize(file)) {
    ElMessage.error(`文件大小不能超过 ${props.maxSize}MB`)
    return false
  }
  
  // 如果提供了自定义的beforeUpload函数，执行它
  if (props.beforeUpload) {
    return props.beforeUpload(file)
  }
  
  return true
}

/**
 * 自定义上传请求
 * @param {Object} options - 上传选项
 * @returns {Object} - 上传控制对象
 */
const customUploadRequest = (options: any) => {
  const { file, onProgress, onSuccess, onError } = options

  // 设置文件状态为上传中
  const fileIndex = fileList.value.findIndex(item => item.uid === file.uid)
  if (fileIndex > -1) {
    fileList.value[fileIndex].status = 'uploading'
    fileList.value[fileIndex].percentage = 0
  }

  const formData = new FormData()
  formData.append('file', file)
  
  // 添加额外的数据
  if (props.data) {
    Object.keys(props.data).forEach(key => {
      formData.append(key, props.data[key])
    })
  }

  const xhr = new XMLHttpRequest()

  // 监听上传进度
  xhr.upload.addEventListener('progress', (e) => {
    if (e.lengthComputable) {
      const percentage = Math.round((e.loaded * 100) / e.total)
      onProgress({ percent: percentage })
      
      // 更新文件状态
      const fileIndex = fileList.value.findIndex(item => item.uid === file.uid)
      if (fileIndex > -1) {
        fileList.value[fileIndex].status = 'uploading'
        fileList.value[fileIndex].percentage = percentage
      }
      
      emit('upload-progress', percentage, file)
    }
  })

  // 监听请求完成
  xhr.addEventListener('load', () => {
    if (xhr.status >= 200 && xhr.status < 300) {
      let response
      try {
        response = JSON.parse(xhr.responseText)
      } catch (e) {
        response = { url: xhr.responseText }
      }

      // 更新文件状态
      const fileIndex = fileList.value.findIndex(item => item.uid === file.uid)
      if (fileIndex > -1) {
        fileList.value[fileIndex].status = 'success'
        fileList.value[fileIndex].url = response.url || ''
        fileList.value[fileIndex].response = response
      }
      
      onSuccess(response)
      emit('upload-success', response, file)

      // 更新绑定的 v-model
      updateModelValue()
    } else {
      let errMsg = '上传失败'
      let errResponse
      
      try {
        errResponse = JSON.parse(xhr.responseText)
        errMsg = errResponse.message || errResponse.detail || errMsg
      } catch (e) {
        // 解析失败，使用默认错误信息
      }
      
      const err = { 
        status: xhr.status, 
        message: errMsg,
        response: errResponse
      }
      
      // 更新文件状态
      const fileIndex = fileList.value.findIndex(item => item.uid === file.uid)
      if (fileIndex > -1) {
        fileList.value[fileIndex].status = 'error'
        fileList.value[fileIndex].response = err
      }
      
      onError(err)
      emit('upload-error', err, file)
    }
  })

  // 监听错误
  xhr.addEventListener('error', () => {
    const err = { status: xhr.status, message: '网络错误，上传失败' }
    
    // 更新文件状态
    const fileIndex = fileList.value.findIndex(item => item.uid === file.uid)
    if (fileIndex > -1) {
      fileList.value[fileIndex].status = 'error'
      fileList.value[fileIndex].response = err
    }
    
    onError(err)
    emit('upload-error', err, file)
  })

  // 监听超时
  xhr.addEventListener('timeout', () => {
    const err = { message: '上传超时' }
    
    // 更新文件状态
    const fileIndex = fileList.value.findIndex(item => item.uid === file.uid)
    if (fileIndex > -1) {
      fileList.value[fileIndex].status = 'error'
      fileList.value[fileIndex].response = err
    }
    
    onError(err)
    emit('upload-error', err, file)
  })

  // 打开连接并发送请求
  xhr.open('POST', getBaseURL(props.uploadUrl), true)

  // 设置请求头
  const token = Session.get('token')
  if (token) {
    xhr.setRequestHeader('Authorization', 'JWT ' + token)
  }
  
  // 添加自定义请求头
  if (props.headers) {
    Object.keys(props.headers).forEach(key => {
      xhr.setRequestHeader(key, props.headers[key])
    })
  }

  xhr.send(formData)

  // 返回取消上传的方法
  return {
    abort: () => {
      xhr.abort()
      
      // 更新文件状态
      const fileIndex = fileList.value.findIndex(item => item.uid === file.uid)
      if (fileIndex > -1) {
        fileList.value[fileIndex].status = 'error'
        fileList.value[fileIndex].response = { message: '上传已取消' }
      }
    }
  }
}

/**
 * 更新modelValue值
 */
const updateModelValue = () => {
  // 防御性检查，确保fileList.value存在且是数组
  if (!fileList.value || !Array.isArray(fileList.value)) {
    emit('update:modelValue', [])
    return
  }
  
  const successFiles = fileList.value
    .filter(file => file.status === 'success' && file.url)
    .map(file => file.url)
  
  emit('update:modelValue', successFiles)
}

/**
 * 处理超出限制
 * @param {Array} files - 选择的文件
 * @param {Array} uploadFiles - 已上传的文件
 */
const handleExceed = (files: File[], uploadFiles: any[]) => {
  ElMessage.warning(`最多只能上传 ${props.limit} 个文件，本次选择了 ${files.length} 个文件，共超出 ${files.length + uploadFiles.length - props.limit} 个文件`)
}

/**
 * 处理文件变化
 * @param {Object} file - 变化的文件
 * @param {Array} uploadFiles - 所有文件
 */
const handleFileChange = (file: any, uploadFiles: any[]) => {
  // 设置文件状态为ready
  if (file.status === 'ready') {
    // 检查文件是否已存在
    if (fileList.value.some(item => item.name === file.name && item.status === 'success')) {
      ElMessage.warning('文件已上传成功')
      // 从上传列表中移除
      const index = uploadFiles.findIndex(item => item.uid === file.uid)
      if (index !== -1) {
        uploadFiles.splice(index, 1)
      }
      return
    }
    
    // 触发文件添加事件
    emit('file-added', file)
  }
  
  // 同步上传文件列表到组件内部的fileList
  fileList.value = uploadFiles
}

/**
 * 移除文件
 * @param {Object} file - 要移除的文件
 */
const handleRemoveFile = (file: any) => {
  // 从文件列表中移除
  fileList.value = fileList.value.filter(item => item !== file)
  
  // 如果上传组件引用存在，也从el-upload组件中移除
  if (uploadRef.value) {
    uploadRef.value.handleRemove(file)
  }
  
  // 更新modelValue
  updateModelValue()
  
  // 触发文件移除事件
  emit('file-removed', file)
}

/**
 * 提交上传（用于非自动上传模式）
 */
const submitUpload = () => {
  if (uploadRef.value) {
    uploadRef.value.submit()
  }
}

/**
 * 清空文件列表
 */
const clearFiles = () => {
  fileList.value = []
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  emit('update:modelValue', [])
}

/**
 * 获取当前上传状态
 */
const getUploadStatus = computed(() => {
  if (!fileList.value || fileList.value.length === 0) return 'empty'
  if (fileList.value.some(file => file.status === 'uploading')) return 'uploading'
  if (fileList.value.some(file => file.status === 'error')) return 'error'
  if (fileList.value.every(file => file.status === 'success')) return 'success'
  return 'ready'
})

/**
 * 组件挂载时初始化
 */
onMounted(() => {
  // 初始化时确保fileList是空数组
  if (!fileList.value) {
    fileList.value = []
  }
})

// 暴露方法给父组件
defineExpose({
  submitUpload,
  clearFiles,
  uploadRef,
  fileList,
  getUploadStatus
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