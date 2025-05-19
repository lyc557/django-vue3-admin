/**
 * 员工管理CRUD配置
 * 定义表格字段、搜索条件、表单等配置
 */
import * as api from './api';
import { useI18n } from 'vue-i18n';
import { dictionary } from '/@/utils/dictionary';
import { AddReq, DelReq, EditReq, PageQuery, GetObj } from '../types';

export const createCrudOptions = async () => {
  const { t } = useI18n();
  const genderOptions = await dictionary('gender');
  const statusOptions = await dictionary('status');
  const departmentOptions = await dictionary('department');
  
  return {
    crudOptions: {
      request: {
        pageRequest: api.GetList,
        addRequest: api.AddObj,
        editRequest: api.UpdateObj,
        delRequest: api.DelObj,
        infoRequest: api.GetObj
      },
      actionbar: {
        buttons: {
          add: {
            show: true,
            auth: 'employee:Create'
          }
        }
      },
      rowHandle: {
        width: 240,
        buttons: {
          edit: {
            show: true,
            auth: 'employee:Update'
          },
          remove: {
            show: true,
            auth: 'employee:Delete'
          }
        }
      },
      columns: {
        id: {
          title: 'ID',
          key: 'id',
          type: 'number',
          column: {
            width: 50
          },
          form: {
            show: false
          }
        },
        avatar: {
          title: '头像',
          key: 'avatar',
          type: 'file-uploader',
          column: {
            width: 80,
            component: {
              name: 'fs-column-cell'
            }
          },
          form: {
            component: {
              multiple: false,
              uploader: {
                type: 'form'
              }
            }
          }
        },
        employee_id: {
          title: '工号',
          key: 'employee_id',
          type: 'text',
          search: {
            show: true
          },
          column: {
            width: 120
          },
          form: {
            rules: [{ required: true, message: '请输入工号' }]
          }
        },
        name: {
          title: '姓名',
          key: 'name',
          type: 'text',
          search: {
            show: true
          },
          form: {
            rules: [{ required: true, message: '请输入姓名' }]
          }
        },
        gender: {
          title: '性别',
          key: 'gender',
          type: 'dict-select',
          dict: genderOptions,
          search: {
            show: true
          },
          form: {
            value: '',
            rules: [{ required: true, message: '请选择性别' }]
          }
        },
        mobile: {
          title: '手机号',
          key: 'mobile',
          type: 'text',
          search: {
            show: true
          },
          form: {
            rules: [
              { required: true, message: '请输入手机号' },
              { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }
            ]
          }
        },
        email: {
          title: '邮箱',
          key: 'email',
          type: 'text',
          form: {
            rules: [
              { type: 'email', message: '请输入正确的邮箱地址' }
            ]
          }
        },
        department: {
          title: '部门',
          key: 'department',
          type: 'dict-select',
          dict: departmentOptions,
          search: {
            show: true
          },
          form: {
            rules: [{ required: true, message: '请选择部门' }]
          }
        },
        position: {
          title: '职位',
          key: 'position',
          type: 'text',
          form: {
            rules: [{ required: true, message: '请输入职位' }]
          }
        },
        hire_date: {
          title: '入职日期',
          key: 'hire_date',
          type: 'date',
          form: {
            rules: [{ required: true, message: '请选择入职日期' }]
          }
        },
        status: {
          title: '状态',
          key: 'status',
          type: 'dict-select',
          dict: statusOptions,
          search: {
            show: true
          },
          form: {
            value: 1,
            rules: [{ required: true, message: '请选择状态' }]
          }
        },
        remark: {
          title: '备注',
          key: 'remark',
          type: 'textarea',
          column: {
            show: false
          }
        },
        create_datetime: {
          title: '创建时间',
          key: 'create_datetime',
          type: 'datetime',
          column: {
            width: 180
          },
          form: {
            show: false
          }
        }
      }
    }
  };
};