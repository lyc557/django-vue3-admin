<template>
  <div class="document-container">
    <!-- 搜索和操作栏 - 优化布局和视觉效果 -->
    <div class="toolbar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索文档标题/内容/标签"
        class="search-input"
        @keyup.enter="handleSearch"
        clearable
      >
        <template #prefix>
          <el-icon class="search-icon"><Search /></el-icon>
        </template>
      </el-input>

      <div class="operation-buttons">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon> 新建文档
        </el-button>
        <el-button @click="handleBatchUpload">
          <el-icon><Upload /></el-icon> 批量上传
        </el-button>
      </div>
    </div>

    <!-- 文档列表 - 优化表格样式和响应性 -->
    <el-card shadow="hover" class="table-card">
      <el-table 
        :data="documents" 
        v-loading="loading"
        border
        stripe
        highlight-current-row
        row-key="id"
        :header-cell-style="{backgroundColor: '#f5f7fa', color: '#606266'}"
      >
        <el-table-column type="index" label="序号" width="60" align="center"/>
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="title-cell">
              <el-icon><Document /></el-icon>
              <span>{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" width="120" align="center" />
        <el-table-column prop="tags" label="标签" width="180" align="center">
          <template #default="{ row }">
            <div class="tag-container">
              <el-tag 
                v-for="tag in row.tags" 
                :key="tag" 
                size="small" 
                class="mx-1"
                effect="light"
                round
              >
                {{ tag }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === '0' ? 'warning' : 'success'" effect="dark" round>
              {{ row.status === '0' ? '草稿' : '已发布' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator_name" label="创建人" width="120" align="center" />
        <el-table-column prop="create_datetime" label="创建时间" width="180" align="center">
          <template #default="{ row }">
            <div class="time-cell">
              <el-icon><Calendar /></el-icon>
              <span>{{ formatDateTime(row.create_datetime) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="handlePreview(row)">
              <el-icon><View /></el-icon> 预览
            </el-button>
            <el-button link type="primary" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
            <el-button link type="info" @click="showHistory(row)" v-if="false">
              <el-icon><Timer /></el-icon> 历史
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 - 优化样式 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          background
        />
      </div>
    </el-card>

    <!-- 文档编辑对话框 - 优化表单布局和交互 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '新建文档' : '编辑文档'"
      width="80%"
      destroy-on-close
      top="5vh"
    >
      <el-form 
        :model="documentForm" 
        label-width="80px"
        :rules="formRules"
        ref="documentFormRef"
        class="document-form"
      >
        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="标题" prop="title">
              <el-input v-model.trim="documentForm.title" placeholder="请输入文档标题" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="分类" prop="category">
              <el-select 
                v-model="documentForm.category"
                placeholder="请选择分类"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="item in categories"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="标签" prop="tags">
          <el-select
            v-model="documentForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择标签"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="item in tags"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="内容" prop="content">
          <MdEditor 
            v-model="documentForm.content"
            height="400px"
            :toolbars="{
              bold: true,
              underline: true,
              italic: true,
              strikeThrough: true,
              title: true,
              sub: true,
              sup: true,
              quote: true,
              unorderedList: true,
              orderedList: true,
              task: true,
              codeRow: true,
              code: true,
              link: true,
              image: true,
              table: true,
              mermaid: true,
              katex: true,
              revoke: true,
              next: true,
              save: true,
              preview: true,
              htmlPreview: true,
              catalog: true,
              github: true
            }"
          />
        </el-form-item>
        
        <el-form-item label="附件">
          <el-upload
            :action="getBaseURL() + '/api/kb/attachment/'"
            :headers="uploadHeaders"
            :auto-upload="false"
            multiple
            :limit="50"
            :file-list="documentForm.attachments"
            class="attachment-upload"
            :on-change="handleAttachmentChange" 
            ref="attachmentUploader"
          >
            <el-button type="primary">
              <el-icon><UploadFilled /></el-icon>
              上传附件
            </el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持任意格式文件，单个文件不超过10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-radio-group v-model="documentForm.status">
            <el-radio label="0">草稿</el-radio>
            <el-radio label="1">发布</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 预览对话框 - 优化样式和阅读体验 -->
    <el-dialog
      v-model="previewVisible"
      title="文档预览"
      width="80%"
      destroy-on-close
      top="5vh"
      class="preview-dialog"
    >
      <div class="preview-content">
        <h1 class="preview-title">{{ previewData.title }}</h1>
        <div class="meta-info">
          <el-tag size="small" effect="plain" class="meta-tag">
            <el-icon><User /></el-icon> 作者: {{ previewData.creator_name }}
          </el-tag>
          <el-tag size="small" effect="plain" class="meta-tag">
            <el-icon><Calendar /></el-icon> 创建时间: {{ formatDateTime(previewData.create_datetime) }}
          </el-tag>
          <el-tag size="small" effect="plain" class="meta-tag" v-if="previewData.category_name">
            <el-icon><Folder /></el-icon> 分类: {{ previewData.category_name }}
          </el-tag>
        </div>
        <div class="tag-list" v-if="previewData.tags && previewData.tags.length > 0">
          <el-tag 
            v-for="tag in previewData.tags" 
            :key="tag" 
            size="small"
            effect="light"
            round
            class="preview-tag"
          >
            {{ tag }}
          </el-tag>
        </div>
        <div class="preview-divider"></div>
        <MdPreview :modelValue="previewData.content" class="md-preview" />
      </div>
    </el-dialog>

    <!-- 历史版本对话框 -->
    <el-dialog
      v-model="historyVisible"
      title="历史版本"
      width="60%"
      destroy-on-close
    >
      <el-timeline>
        <el-timeline-item
          v-for="(history, index) in documentHistory"
          :key="index"
          :timestamp="history.updateTime"
          :type="index === 0 ? 'primary' : ''"
        >
          <p>修改人: {{ history.editor }}</p>
          <div class="history-actions">
            <el-button link type="primary" @click="previewVersion(history)">
              <el-icon><View /></el-icon> 查看此版本
            </el-button>
            <el-button link type="success" @click="restoreVersion(history)">
              <el-icon><RefreshRight /></el-icon> 恢复此版本
            </el-button>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>

    <!-- 批量上传对话框 - 优化上传体验 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="批量上传文档"
      width="60%"
      destroy-on-close
    >
      <el-form :model="uploadForm" label-width="80px">
        <el-form-item label="分类" required>
          <el-select
            v-model="uploadForm.category"
            placeholder="请选择分类"
            style="width: 100%"
          >
            <el-option
              v-for="item in categories"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <fileUploader
        :upload-url="'/api/kb/document/batch-upload/'"
        :multiple="true"
        :drag="true"
        :auto-upload="false"
        :accept="'.doc,.docx,.pdf,.md,.txt'"
        :max-size="10"
        :tip-text="'支持Word、PDF、Markdown和文本文件，单个文件不超过10MB'"
        :show-file-list="false"
        :show-upload-list="true"
        @upload-success="handleBatchUploadSuccess"
        @upload-error="handleBatchUploadError"
        ref="uploaderRef"
      />
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitBatchUpload" :disabled="!uploadForm.category">
            开始上传
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup name="document">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, UploadFilled, Plus, Upload, Document, Calendar, 
  View, Edit, Delete, Timer, User, Folder, RefreshRight 
} from '@element-plus/icons-vue'
import { MdEditor, MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import fileUploader from '/@/components/upload/index.vue'
import { apiPrefix, GetList, AddObj, UpdateObj, GetCategoryList, GetTagList, DelObj } from './api'
import { getBaseURL } from '/@/utils/baseUrl';
import { Session } from '/@/utils/storage'


// 表单校验规则
const formRules = {
  title: [
    { required: true, message: '请输入文档标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度在2-100个字符之间', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择文档分类', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入文档内容', trigger: 'blur' }
  ]
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const documents = ref([])
const pagination = ref({
  currentPage: 1,
  pageSize: 10
})
const total = ref(0)
const searchQuery = ref('')
const dialogVisible = ref(false)
const dialogType = ref('create')
const previewVisible = ref(false)
const historyVisible = ref(false)
const documentHistory = ref([])
const categories = ref([])
const tags = ref([])
const tagData = ref([])
const uploadDialogVisible = ref(false)
const documentFormRef = ref(null)
const uploaderRef = ref(null)

// 表单数据
const documentForm = ref({
  title: '',
  category: '',
  tags: [],
  content: '',
  status: '0',
  attachments: []
})

// 预览数据
const previewData = ref({
  title: '',
  content: '',
  creator_name: '',
  create_datetime: '',
  category_name: '',
  tags: []
})

// 上传表单
const uploadForm = ref({
  category: ''
})

/**
 * 格式化日期时间
 * @param {string} datetime - 日期时间字符串
 * @returns {string} - 格式化后的日期时间
 */
const formatDateTime = (datetime) => {
  if (!datetime) return ''
  const date = new Date(datetime)
  return date.toLocaleString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 处理搜索
 */
const handleSearch = async () => {
  pagination.value.currentPage = 1
  await fetchDocuments()
}

/**
 * 处理创建文档
 */
const handleCreate = () => {
  dialogType.value = 'create'
  documentForm.value = {
    title: '',
    category: '',
    tags: [],
    content: '',
    status: '0',
    attachments: []
  }
  dialogVisible.value = true
}

/**
 * 处理编辑文档
 * @param {Object} row - 文档行数据
 */
const handleEdit = (row) => {
  dialogType.value = 'edit'
  documentForm.value = { ...row }
  dialogVisible.value = true
}

/**
 * 处理删除文档
 * @param {Object} row - 文档行数据
 */
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确认删除该文档?', '提示', {
      type: 'warning',
      confirmButtonText: '确认',
      cancelButtonText: '取消'
    })
    loading.value = true
    const res = await DelObj(row.id)
    if (res?.code === 2000) {
      ElMessage.success('删除成功')
      await fetchDocuments()
    } else {
      ElMessage.error(res?.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文档失败:', error)
      ElMessage.error('删除失败')
    }
  } finally {
    loading.value = false
  }
}

/**
 * 处理预览文档
 * @param {Object} row - 文档行数据
 */
const handlePreview = (row) => {
  previewData.value = { ...row }
  previewVisible.value = true
}

/**
 * 提交表单
 */
const submitForm = async () => {
  if (!documentFormRef.value) return
  
  await documentFormRef.value.validate(async (valid) => {
    // 校验表单
    if (valid) {
      try {
        submitting.value = true
        const formData = { ...documentForm.value }
        
        // 处理标签数据
        formData.tags = formData.tags.map(tagName => {
          const tagItem = tagData.value.find(item => item.name === tagName)
          return tagItem ? tagItem.id : null
        }).filter(Boolean)

        // 根据是否有ID判断是新增还是更新
        const res = formData.id ? 
          await UpdateObj(formData) : 
          await AddObj(formData)
        console.log('res', res)
        if (res?.code === 2000) { debugger
          // 新增成功，获取文档ID
          const docId = res.data.id 

          // 上传附件
          if (documentForm.value.attachments.length > 0) {
            // 创建FormData对象用于上传附件
            const attachmentPromises = documentForm.value.attachments.map(async (attachment) => {
              // 如果已经有URL，说明是已上传的附件，跳过
              if (attachment.url) return;
              
              // 创建FormData
              const formData = new FormData();
              formData.append('file', attachment.raw); // 原始文件对象
              formData.append('document_id', docId); // 关联到文档ID
              
              try {
                // 发送上传请求
                const response = await fetch(getBaseURL() + '/api/kb/attachment/', {
                  method: 'POST',
                  headers: {
                    'Authorization': uploadHeaders.Authorization
                  },
                  body: formData
                });
                
                const result = await response.json();
                if (result && result.url) {
                  console.log('附件上传成功:', attachment.name);
                } else {
                  console.error('附件上传失败:', result);
                  ElMessage.warning(`附件 ${attachment.name} 上传失败`);
                }
              } catch (error) {
                console.error('附件上传异常:', error);
                ElMessage.warning(`附件 ${attachment.name} 上传失败`);
              }
            });
            
            // 等待所有附件上传完成
            await Promise.all(attachmentPromises);
            ElMessage.success('所有附件上传完成');
          }

          ElMessage.success('保存成功')
          dialogVisible.value = false
          await fetchDocuments()
        } else {
          ElMessage.error(res?.message || '保存失败，请重试')
        }
      } catch (error) {
        console.error('保存文档失败:', error)
        ElMessage.error('保存失败，请重试')
      } finally {
        submitting.value = false
      }
    }else {
      ElMessage.error('请检查表单输入')
    }
  })
}

/**
 * 上传前检查
 * @param {File} file - 文件对象
 * @returns {boolean} - 是否允许上传
 */
const beforeUpload = (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('上传文件大小不能超过 10MB!')
  }
  return isLt10M
}

/**
 * 处理上传成功
 * @param {Object} response - 响应对象
 * @param {File} file - 文件对象
 * @param {Array} fileList - 文件列表
 */
const handleUploadSuccess = (response, file, fileList) => {
  if (response && response.url) {
    documentForm.value.attachments.push({
      name: file.name,
      url: response.url
    })
    ElMessage.success('上传成功')
  } else {
    ElMessage.error('上传失败：响应数据格式错误')
  }
}

/**
 * 处理上传失败
 * @param {Error} error - 错误对象
 */
const handleUploadError = (error) => {
  console.error('上传失败:', error)
  ElMessage.error('上传失败，请重试')
}

/**
 * 处理页面大小变化
 * @param {number} val - 新的页面大小
 */
const handleSizeChange = async (val) => {
  pagination.value.pageSize = val
  await fetchDocuments()
}

/**
 * 处理当前页变化
 * @param {number} val - 新的当前页
 */
const handleCurrentChange = async (val) => {
  pagination.value.currentPage = val
  await fetchDocuments()
}

/**
 * 获取文档列表
 */
const fetchDocuments = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.currentPage,
      pageSize: pagination.value.pageSize,
      search: searchQuery.value
    }
    const res = await GetList(params)
    
    if (res?.code === 2000) {
      documents.value = res.data.map(item => ({
        ...item,
        category_name: categories.value.find(c => c.value === item.category)?.label || '',
        tags: item.tags.map(tagId => {
          const tagItem = tagData.value.find(t => t.id === tagId)
          return tagItem ? tagItem.name : ''
        }).filter(Boolean),
        status: item.status == 0 ? '0' : '1'
      }))
      total.value = res.total
    } else {
      ElMessage.error(res?.message || '获取文档列表失败')
    }
  } catch (error) {
    console.error('获取文档列表失败:', error)
    ElMessage.error('获取文档列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 获取分类和标签数据
 */
const loadData = async () => {
  try {
    const [categoryRes, tagRes] = await Promise.all([
      GetCategoryList(),
      GetTagList()
    ])

    if (categoryRes?.code === 2000) {
      categories.value = categoryRes.data.map(item => ({
        value: item.id,
        label: item.name
      }))
    } else {
      ElMessage.error(categoryRes?.message || '获取分类数据失败')
    }

    if (tagRes?.code === 2000) {
      tagData.value = tagRes.data
      tags.value = tagRes.data.map(item => item.name)
    } else {
      ElMessage.error(tagRes?.message || '获取标签数据失败')
    }
  } catch (error) {
    console.error('获取基础数据失败:', error)
    ElMessage.error('获取基础数据失败')
  }
}

/**
 * 处理批量上传
 */
const handleBatchUpload = () => {
  // 检查是否有可用的分类
  if (!categories.value || categories.value.length === 0) {
    ElMessage.warning('请等待分类数据加载完成')
    return
  }
  
  // 打开批量上传对话框，并添加分类选择
  uploadForm.value.category = ''
  uploadDialogVisible.value = true
}

/**
 * 提交批量上传
 */
const submitBatchUpload = () => {
  if (!uploadForm.value.category) {
    ElMessage.warning('请选择文档分类')
    return
  }
  
  if (uploaderRef.value) {
    // 添加分类参数
    const uploadParams = {
      category: uploadForm.value.category
    }
    
    // 调用上传组件的提交方法，并传递额外参数
    uploaderRef.value.submitUpload(uploadParams)
  }
}

/**
 * 处理批量上传成功
 * @param {Object} data - 响应数据
 */
const handleBatchUploadSuccess = (data) => {
  ElMessage.success('文档上传成功')
  uploadDialogVisible.value = false
  // 刷新文档列表
  fetchDocuments()
}

/**
 * 处理批量上传失败
 * @param {Error} error - 错误对象
 */
const handleBatchUploadError = (error) => {
  console.error('批量上传失败:', error)
  ElMessage.error(`上传失败: ${error.message || '未知错误'}`)
}

/**
 * 显示历史版本
 * @param {Object} row - 文档行数据
 */
const showHistory = (row) => {
  // 这里应该调用获取历史版本的API
  // 目前使用模拟数据
  documentHistory.value = [
    { id: 1, updateTime: '2023-06-01 10:00', editor: '管理员' },
    { id: 2, updateTime: '2023-05-28 15:30', editor: '测试用户' },
    { id: 3, updateTime: '2023-05-25 09:15', editor: '管理员' }
  ]
  historyVisible.value = true
}

/**
 * 预览历史版本
 * @param {Object} history - 历史版本数据
 */
const previewVersion = (history) => {
  // 这里应该调用获取历史版本详情的API
  ElMessage.info(`预览历史版本: ${history.id}`)
}

/**
 * 恢复历史版本
 * @param {Object} history - 历史版本数据
 */
const restoreVersion = (history) => {
  // 这里应该调用恢复历史版本的API
  ElMessage.success(`已恢复到版本: ${history.updateTime}`)
  historyVisible.value = false
}

const uploadHeaders = {
  Authorization: Session.get('token') ? 'JWT ' + Session.get('token') : ''
}

const handleAttachmentChange = (file, fileList) => {
  documentForm.value.attachments = fileList.map(item => ({
    name: item.name,
    url: item.url || '',
    status: item.status,
    uid: item.uid,
    raw: item.raw // 保存原始文件对象，用于后续上传
  }))
}


onMounted(() => {
  loadData()
  fetchDocuments()
})
</script>

<style scoped>
.document-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background-color: #fff;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.search-input {
  width: 350px;
}

.operation-buttons {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.preview-content {
  padding: 20px;
}

.meta-info {
  margin: 10px 0;
  display: flex;
  gap: 10px;
}

.history-actions {
  margin-top: 8px;
}

:deep(.el-table) {
  margin-top: 16px;
}

:deep(.el-form-item) {
  margin-bottom: 22px;
}

:deep(.el-upload__tip) {
  line-height: 1.2;
  margin-top: 8px;
  color: #909399;
}
</style>