# hrms后台管理系统
## 平台简介

💡 [django-vue3-admin]是一套全部开源的快速开发平台，毫无保留给个人免费使用、团体授权使用。
    django-vue3-admin 基于RBAC模型的权限控制的一整套基础开发平台，权限粒度达到列级别，前后端分离，后端采用django + django-rest-framework，前端采用基于 vue3 + CompositionAPI + typescript + vite + element plus




* 🧑‍🤝‍🧑前端采用 Vue3+TS+pinia+fastcrud(感谢[vue-next-admin](https://lyt-top.gitee.io/vue-next-admin-doc-preview/))
* 👭后端采用 Python 语言 Django 框架以及强大的 [Django REST Framework](https://pypi.org/project/djangorestframework)。
* 👫权限认证使用[Django REST Framework SimpleJWT](https://pypi.org/project/djangorestframework-simplejwt)，支持多终端认证系统。
* 👬支持加载动态权限菜单，多方式轻松权限控制。
* 👬全新的列权限管控，粒度细化到每一列。
* 💏特别鸣谢：[vue-next-admin](https://lyt-top.gitee.io/vue-next-admin-doc-preview/)。
* 💡特别感谢[jetbrains](https://www.jetbrains.com/) 为本开源项目提供免费的 IntelliJ IDEA 授权。

#### 🏭 环境支持

| Edge      | Firefox      | Chrome      | Safari      |
| --------- | ------------ | ----------- | ----------- |
| Edge ≥ 79 | Firefox ≥ 78 | Chrome ≥ 64 | Safari ≥ 12 |

> 由于 Vue3 不再支持 IE11，故而 ElementPlus 也不支持 IE11 及之前版本。

## 内置功能

1.  👨‍⚕️菜单管理：配置系统菜单，操作权限，按钮权限标识、后端接口权限等。
2.  🧑‍⚕️部门管理：配置系统组织机构（公司、部门、角色）。
3.  👩‍⚕️角色管理：角色菜单权限分配、数据权限分配、设置角色按部门进行数据范围权限划分。
4.  🧑‍🎓按钮权限控制：授权角色的按钮权限和接口权限,可做到每一个接口都能授权数据范围。
5.  🧑‍🎓字段列权限控制：授权页面的字段显示权限，具体到某一列的显示权限。
7.  👨‍🎓用户管理：用户是系统操作者，该功能主要完成系统用户配置。
8.  👬接口白名单：配置不需要进行权限校验的接口。
9.  🧑‍🔧字典管理：对系统中经常使用的一些较为固定的数据进行维护。
10.  🧑‍🔧地区管理：对省市县区域进行管理。
11.  📁附件管理：对平台上所有文件、图片等进行统一管理。
12.  🗓️操作日志：系统正常操作日志记录和查询；系统异常信息日志记录和查询。

## 准备工作
~~~
Python >= 3.11.0 (最低3.9+版本)
nodejs >= 16.0
Mysql >= 8.0 (可选，默认数据库sqlite3，支持5.7+，推荐8.0版本)
Redis (可选，最新版)
~~~

## 前端♝

```bash
# 克隆项目
git clone https://gitee.com/huge-dream/django-vue3-admin.git

# 进入项目目录
cd web

# 安装依赖
npm install yarn
yarn install --registry=https://registry.npmmirror.com

# 启动服务
yarn build
yarn dev
# 浏览器访问 http://localhost:8080
# .env.development 文件中可配置启动端口等参数
# 构建生产环境
# yarn run build
```



## 后端💈

~~~bash
1. 进入项目目录 cd backend
2. 在项目根目录中，复制 ./conf/env.example.py 文件为一份新的到 ./conf 文件夹下，并重命名为 env.py
3. 在 env.py 中配置数据库信息
	mysql数据库版本建议：8.0
	mysql数据库字符集：utf8mb4
4. 安装依赖环境
	pip3 install -r requirements.txt
5. 执行迁移命令：
	python3 manage.py makemigrations
	python3 manage.py migrate
6. 初始化数据
	python3 manage.py init
7. 初始化省市县数据:
	python3 manage.py init_area
8. 启动项目
	# 开发环境执行
	python3 manage.py runserver 0.0.0.0:8000
	# 生产环境执行
	daphne -b 0.0.0.0 -p 8000 application.asgi:application
  	uvicorn application.asgi:application --port 8000 --host 0.0.0.0 --workers 4
~~~
## 开发建议
前后端backend与web各自单独一个窗口打开进行开发

### 访问项目

- 访问地址：[http://localhost:8080](http://localhost:8080) (默认为此地址，如有修改请按照配置文件)
- 账号：`superadmin` 密码：`admin123456`

# 杀相关进程
lsof -i :8000 | awk 'NR>1 {print $2}' | xargs kill -9      