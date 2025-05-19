<template>
  <fs-page>
    <fs-crud ref="crudRef" v-bind="crudBinding">
      <template #actionbar-right>
        <importExcel api="api/hrms/employee/" v-auth="'employee:Import'">导入</importExcel>
      </template>
      <template #cell_avatar="scope">
        <div v-if="scope.row.avatar" style="display: flex; justify-content: center; align-items: center;">
          <el-image 
            style="width: 50px; height: 50px; border-radius: 50%; aspect-ratio: 1 /1 ; " 
            :src="getBaseURL(scope.row.avatar)"
            :preview-src-list="[getBaseURL(scope.row.avatar)]" 
            :preview-teleported="true" />
        </div>
      </template>
    </fs-crud>
  </fs-page>
</template>

<script lang="ts" setup name="hrmsEmployee">
import { useExpose, useCrud, useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { GetPermission } from './api';
import { ref, onMounted } from 'vue';
import importExcel from '/@/components/importExcel/index.vue';
import { getBaseURL } from '/@/utils/baseUrl';
import { handleColumnPermission } from '/@/utils/columnPermission';

// 创建CRUD对象
const { crudBinding, crudRef, crudExpose, crudOptions, resetCrudOptions } = useFs({ createCrudOptions });


// 页面加载时
// 页面打开后获取列表数据
onMounted(async () => {
	// 设置列权限
	const newOptions = await handleColumnPermission(GetPermission, crudOptions);
	//重置crudBinding
	resetCrudOptions(newOptions);
	// 刷新
	crudExpose.doRefresh();
});
</script>