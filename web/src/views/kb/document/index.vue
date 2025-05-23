<template>
  <div class="document-container">
    <!-- 搜索和操作栏 -->
    <div class="toolbar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索文档标题/内容/标签"
        class="search-input"
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>

      <div class="operation-buttons">
        <el-button type="primary" @click="handleCreate">新建文档</el-button>
        <el-button @click="handleBatchUpload">批量上传</el-button>
      </div>
    </div>

    <!-- 文档列表 -->
    <el-table 
      :data="documents" 
      v-loading="loading"
      border
      stripe
      highlight-current-row
    >
      <el-table-column type="index" label="序号" width="60"/>
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="category_name" label="分类" width="120" align="center" />
      <el-table-column prop="tags" label="标签" width="150" align="center">
        <template #default="{ row }">
          <el-tag 
            v-for="tag in row.tags" 
            :key="tag" 
            size="small" 
            class="mx-1"
            effect="plain"
          >
            {{ tag }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === '0' ? 'warning' : 'success'" effect="plain">
            {{ row.status === '0' ? '草稿' : '已发布' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="创建人" width="120" align="center" />
      <el-table-column prop="create_datetime" label="创建时间" width="180" align="center" />
      <el-table-column label="操作" width="220" fixed="right" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="handlePreview(row)">预览</el-button>
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          <el-button link type="info" @click="showHistory(row)" v-if="false">历史</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 文档编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '新建文档' : '编辑文档'"
      width="80%"
      destroy-on-close
    >
      <el-form 
        :model="documentForm" 
        label-width="80px"
        :rules="formRules"
        ref="documentFormRef"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model.trim="documentForm.title" placeholder="请输入文档标题" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select 
            v-model="documentForm.category"
            placeholder="请选择分类"
            clearable
          >
            <el-option
              v-for="item in categories"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="标签" prop="tags">
          <el-select
            v-model="documentForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择标签"
            clearable
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
          />
        </el-form-item>
        <el-form-item label="附件">
          <el-upload
            action="/api/upload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            multiple
            :limit="5"
            :file-list="documentForm.attachments"
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
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      title="文档预览"
      width="80%"
      destroy-on-close
    >
      <div class="preview-content">
        <h2>{{ previewData.title }}</h2>
        <div class="meta-info">
          <el-tag size="small" effect="plain">
            作者: {{ previewData.creator }}
          </el-tag>
          <el-tag size="small" effect="plain">
            创建时间: {{ previewData.create_datetime }}
          </el-tag>
        </div>
        <MdPreview :modelValue="previewData.content" />
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
              查看此版本
            </el-button>
            <el-button link type="success" @click="restoreVersion(history)">
              恢复此版本
            </el-button>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>

    <!-- 批量上传对话框 -->
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
        v-model="uploadedFiles"
        :upload-url="'/api/kb/document/batch-upload/'"
        :multiple="true"
        :drag="true"
        :auto-upload="false"
        :accept="'.doc,.docx,.pdf,.md,.txt'"
        :max-size="100"
        :tip-text="'支持Word、PDF、Markdown和文本文件，单个文件不超过10MB'"
        :show-file-list="false"
        :show-upload-list="true"
        @upload-success="handleBatchUploadSuccess"
        @upload-error="handleBatchUploadError"
      />
    </el-dialog>
  </div>
</template>

<script lang="ts" setup name="document">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, UploadFilled } from '@element-plus/icons-vue'
import { MdEditor, MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import fileUploader from '/@/components/upload/index.vue'
import { GetList, AddObj, UpdateObj, GetCategoryList, GetTagList, DelObj } from './api'
import type { APIResponseData } from '/@/api/interface'

const uploadedFiles = ref([])
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
  creator: '',
  create_datetime: ''
})

// 方法定义
const handleSearch = async () => {
  pagination.value.currentPage = 1
  await fetchDocuments()
}

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

const handleEdit = (row) => {
  dialogType.value = 'edit'
  documentForm.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确认删除该文档?', '提示', {
      type: 'warning'
    })
    const res = await DelObj(row.id)
    if (res?.code === 2000) {
      ElMessage.success('删除成功')
      await fetchDocuments()
    }
  } catch (error) {
    console.error('删除文档失败:', error)
    ElMessage.error('删除失败')
  }
}

const handlePreview = (row) => {
  previewData.value = { ...row }
  previewVisible.value = true
}

const submitForm = async () => {
  if (!documentFormRef.value) return
  
  await documentFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const formData = { ...documentForm.value }
        formData.tags = formData.tags.map(tagName => {
          const tagItem = tagData.value.find(item => item.name === tagName)
          return tagItem ? tagItem.id : null
        }).filter(Boolean)

        const res = formData.id ? 
          await UpdateObj(formData) : 
          await AddObj(formData)

        if (res?.code === 2000) {
          ElMessage.success('保存成功')
          dialogVisible.value = false
          await fetchDocuments()
        }
      } catch (error) {
        console.error('保存文档失败:', error)
        ElMessage.error('保存失败，请重试')
      }
    }
  })
}

const beforeUpload = (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('上传文件大小不能超过 10MB!')
  }
  return isLt10M
}

const handleUploadSuccess = (response, file, fileList) => {
  documentForm.value.attachments.push({
    name: file.name,
    url: response.url
  })
  ElMessage.success('上传成功')
}

const handleUploadError = () => {
  ElMessage.error('上传失败，请重试')
}

const handleSizeChange = async (val) => {
  pagination.value.pageSize = val
  await fetchDocuments()
}

const handleCurrentChange = async (val) => {
  pagination.value.currentPage = val
  await fetchDocuments()
}

// 获取文档列表
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
        }),
        status: item.status == 0 ? '0' : '1'
      }))
      total.value = res.total
    }
  } catch (error) {
    console.error('获取文档列表失败:', error)
    ElMessage.error('获取文档列表失败')
  } finally {
    loading.value = false
  }
}

// 获取分类和标签数据
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
    }

    if (tagRes?.code === 2000) {
      tagData.value = tagRes.data
      tags.value = tagRes.data.map(item => item.name)
    }
  } catch (error) {
    console.error('获取基础数据失败:', error)
    ElMessage.error('获取基础数据失败')
  }
}

// 在方法定义部分添加
const handleBatchUpload = () => {
  // 检查是否有可用的分类
  if (!categories.value || categories.value.length === 0) {
    ElMessage.warning('请等待分类数据加载完成')
    return
  }
  
  // 打开批量上传对话框，并添加分类选择
  uploadDialogVisible.value = true
}

// 在状态定义部分添加
const uploaderRef = ref(null)

const handleBatchUploadSuccess = (data) => {
  ElMessage.success('文档上传成功')
  // 可以在这里处理上传成功后的逻辑，例如刷新文档列表
  fetchDocuments()
}

const handleBatchUploadError = (error) => {
  ElMessage.error(`上传失败: ${error.message || '未知错误'}`)
}

// 在状态定义部分添加
const uploadForm = ref({
  category: ''
})

onMounted(() => {
  loadData()
  fetchDocuments()
})
</script>

<style scoped>
.document-container {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-input {
  width: 300px;
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
