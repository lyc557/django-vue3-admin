<template>
  <div class="document-container">
    <!-- 搜索和操作栏 -->
    <div class="search-bar">
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
    </div>

    <div class="operation-bar">
      <el-button type="primary" @click="handleCreate">
        新建文档
      </el-button>
      <el-button @click="uploadDialogVisible = true">
        批量上传
      </el-button>
    </div>

    <!-- 文档列表 -->
    <el-table :data="documents" v-loading="loading">
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column prop="category" label="分类" width="120" />
      <el-table-column prop="tags" label="标签" width="150">
        <template #default="{ row }">
          <el-tag v-for="tag in row.tags" :key="tag" size="small" class="mx-1">
            {{ tag }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'published' ? 'success' : 'info'">
            {{ row.status === 'published' ? '已发布' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="creator" label="创建人" width="120" />
      <el-table-column prop="createTime" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link @click="handlePreview(row)">预览</el-button>
          <el-button 
            link 
            @click="handleEdit(row)"
          >编辑</el-button>
          <el-button 
            link 
            type="danger" 
            @click="handleDelete(row)"
          >删除</el-button>
          <el-button link @click="showHistory(row)">历史</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 文档编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '新建文档' : '编辑文档'"
      width="80%"
    >
      <el-form :model="documentForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="documentForm.title" />
        </el-form-item>
        <el-form-item label="分类" required>
          <el-select v-model="documentForm.category">
            <el-option
              v-for="item in categories"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="documentForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择标签"
          >
            <el-option
              v-for="item in tags"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" required>
          <MdEditor v-model="documentForm.content" />
        </el-form-item>
        <el-form-item label="附件">
          <el-upload
            action="/api/upload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            multiple
          >
            <el-button type="primary">上传附件</el-button>
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
        <el-button type="primary" @click="() => handleSave(documentForm)">保存</el-button>
      </template>
    </el-dialog>
    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      title="文档预览"
      width="80%"
    >
      <div class="preview-content">
        <h2>{{ previewData.title }}</h2>
        <div class="meta-info">
          <span>作者: {{ previewData.creator }}</span>
          <span>创建时间: {{ previewData.createTime }}</span>
        </div>
        <MdPreview :modelValue="previewData.content" />
      </div>
    </el-dialog>

    <!-- 历史版本对话框 -->
    <el-dialog
      v-model="historyVisible"
      title="历史版本"
      width="60%"
    >
      <el-timeline>
        <el-timeline-item
          v-for="(history, index) in documentHistory"
          :key="index"
          :timestamp="history.updateTime"
        >
          <p>修改人: {{ history.editor }}</p>
          <el-button link @click="previewVersion(history)">查看此版本</el-button>
          <el-button link type="primary" @click="restoreVersion(history)">
            恢复此版本
          </el-button>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>

    <!-- 批量上传对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="批量上传文档"
      width="60%"
    >
      <fileUploader
        v-model="uploadedFiles"
        :upload-url="'/api/documents/batch-upload'"
        :multiple="true"
        :drag="true"
        :auto-upload="true"
        :accept="'.doc,.docx,.pdf,.md,.txt'"
        :max-size="10"
        :tip-text="'支持Word、PDF、Markdown和文本文件，单个文件不超过100MB'"
        :show-upload-list="true"
        @upload-success="handleBatchUploadSuccess"
        @upload-error="handleBatchUploadError"
        @upload-progress="handleUploadProgress"
        @file-removed="handleFileRemoved"
      />
      
      <template #footer>
        <el-button @click="uploadDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleClearUploadList">清空列表</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup name="document">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, UploadFilled } from '@element-plus/icons-vue'
import { MdEditor, MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import fileUploader from '/@/components/upload/index.vue'
import { GetList,  AddObj, GetCategoryList, GetTagList} from './api'
import { APIResponseData } from '/@/api/interface'

// 状态定义
const loading = ref(false)
const documents = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchQuery = ref('')
const dialogVisible = ref(false)
const dialogType = ref('create')
const previewVisible = ref(false)
const historyVisible = ref(false)
const documentHistory = ref([])
const categories = ref([])
const tags = ref([])
let tagData  = ref([])

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
  createTime: ''
})



// 方法定义
const handleSearch = async () => {
  currentPage.value = 1
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
    await ElMessageBox.confirm('确认删除该文档?', '提示')
    // TODO: 调用删除API
    ElMessage.success('删除成功')
    await fetchDocuments()
  } catch (error) {
    console.error(error)
  }
}

const handlePreview = (row) => {
  previewData.value = { ...row }
  previewVisible.value = true
}

// 保存文档方法
/**
 * 调用文档新增API，保存文档数据
 * @param {object} formData - 表单数据对象
 */
const handleSave = async (formData) => {
  // 确保formData已正确传递
  console.log('表单数据:', formData);
  try {

    console.log("formData.tags",formData.tags)

    // 将标签名称转换为对应的tag_id
    const tagIds = formData.tags.map(tagName => {
      const tagItem = tagData.value.find(item => item.name === tagName);
      return tagItem ? tagItem.id : null;
    }).filter(id => id !== null); // 过滤掉未找到对应id的标签
    // 更新表单数据
    formData.tags = tagIds;

    const res = await AddObj(formData);
    // 根据实际业务处理保存成功后的逻辑
    ElMessage.success('保存成功')
    // 可选：刷新列表或关闭弹窗等
    dialogVisible.value = false;
    await fetchDocuments();

  } catch (error) {
    // 错误处理
    ElMessage.error('保存失败，请重试');
  }
};

const showHistory = async (row) => {
  // TODO: 获取历史版本数据
  historyVisible.value = true
}

const previewVersion = (version) => {
  previewData.value = { ...version }
  previewVisible.value = true
}

const restoreVersion = async (version) => {
  try {
    // TODO: 调用恢复版本API
    ElMessage.success('版本恢复成功')
    historyVisible.value = false
    await fetchDocuments()
  } catch (error) {
    console.error(error)
  }
}

const handleUploadSuccess = (response) => {
  documentForm.value.attachments.push(response.url)
  ElMessage.success('上传成功')
}

const handleUploadError = () => {
  ElMessage.error('上传失败')
}

const handleSizeChange = async (val) => {
  pageSize.value = val
  await fetchDocuments()
}

const handleCurrentChange = async (val) => {
  currentPage.value = val
  await fetchDocuments()
}

// 获取文档列表
const fetchDocuments = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      pageSize: pageSize.value,
      search: searchQuery.value
    }
    let res: APIResponseData = await GetList(params);

    documents.value = data.items
    total.value = data.total
    // 模拟数据
    // documents.value = [
    //   {
    //     id: 1,
    //     title: '示例文档',
    //     category: '技术文档',
    //     tags: ['Vue', 'JavaScript'],
    //     status: 'published',
    //     creator: 'admin',
    //     createTime: '2023-01-01 12:00:00',
    //     content: '# 示例文档\n这是一个示例文档内容'
    //   }
    // ]
    // total.value = 1
    loading.value = false
  } catch (error) {
    console.error(error)
    loading.value = false
  }
}

// 获取分类和标签数据
const loadData = async () => {
  try {
    // 获取分类数据
    const categoryRes = await GetCategoryList()
    categories.value = categoryRes.data.map(item => ({
      value: item.id,
      label: item.name
    }))
    
    // 获取标签数据
    const tagRes = await GetTagList()
    tagData.value = tagRes.data
    tags.value = tagRes.data.map(item => item.name)

  } catch (error) {
    console.error('获取分类或标签数据失败:', error)
  }
}

// 在组件挂载时调用
onMounted(() => {
  loadData()
})

</script>

<style scoped>
.document-container {
  padding: 20px;
}

.search-bar {
  display: flex;
  margin-bottom: 20px;
  gap: 10px;
}

.operation-bar {
  display: flex;
  margin-bottom: 20px;
  gap: 10px;
}

.search-input {
  width: 300px;
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
  color: #666;
  margin: 10px 0;
  display: flex;
  gap: 20px;
}

.upload-demo {
  margin-bottom: 20px;
}

.upload-status {
  margin-top: 20px;
}

.error-message {
  color: #F56C6C;
}
</style>
