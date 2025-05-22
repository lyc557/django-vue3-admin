# ... existing code ...
import os
import json
import traceback
import re
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from dvadmin.hrms.models import Resume
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from dvadmin.utils.viewset import CustomModelViewSet
       # 调用简历解析接口
from dvadmin.dputils.document_parser import parse_pdf, parse_docx
from dvadmin.dputils.deepseek_chat import chatToLLM4Analysis, chatToLLM
from dvadmin.dputils.es_vector_db import save_to_es, list_resume, search_resume



class ResumeSerializer(CustomModelSerializer):
    """简历序列化器"""
    
    class Meta:
        model = Resume
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]

class ResumeViewSet(CustomModelViewSet):
    """简历管理"""
    # permission_classes 用于指定访问视图所需的权限。当设置为空列表 [] 时，表示任何人都可以访问该接口，无需身份认证。
    permission_classes = []
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    


    def __parse_llm_response__(self, response):
        # 解析LLM返回的JSON字符串
        try:
            # 如果response已经是字典，直接使用
            if isinstance(response, dict):
                parsed_response = response
            else:
                # 否则按原逻辑处理字符串
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx == -1 or end_idx == 0:
                    raise ValueError('LLM返回的内容中未找到有效的JSON')
                    
                json_str = response[start_idx:end_idx]
                # 解析JSON字符串
                print("LLM返回的内容：", json_str)
                safe_json = re.sub(r'\bTrue\b', 'true', json_str)
                safe_json = re.sub(r'\bFalse\b', 'false', safe_json)
                safe_json = re.sub(r'\bNone\b', 'null', safe_json)
                parsed_response = json.loads(safe_json)
                print("解析后的内容：", parsed_response)
            # 验证必要字段是否存在
            required_fields = ['need_search', 'search_criteria', 'reply']
            for field in required_fields:
                if field not in parsed_response:
                    raise ValueError('LLM返回的内容中未找到有效的JSON')

            
            # 如果需要搜索，验证search_criteria的字段
            if parsed_response['need_search']:
                required_criteria = ['name', 'skills','projects', 'experience', 'education', 'score_range', 'gender']
                for field in required_criteria:
                    if field not in parsed_response['search_criteria']:
                        parsed_response['search_criteria'][field] = "" if field != 'skills' else []
                        if field == 'score_range':
                            parsed_response['search_criteria'][field] = [0, 100]
            return parsed_response
        except json.JSONDecodeError as e:
            print(f"解析LLM返回的JSON失败: {str(e)}")
            raise ValueError(f'解析LLM返回的JSON失败: {str(e)}')
        except Exception as e:
            raise ValueError(f'处理LLM返回内容时出错: {str(e)}')


    def __getfileid__(self,):
        """获取文件ID"""
        # 生成毫秒级时间戳加上随机4位编码作为file_id
        import time
        import random
        import string
        
        # 获取毫秒级时间戳
        timestamp = int(time.time() * 1000)
        # 生成随机4位编码
        random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        # 组合成file_id
        file_id = f"{timestamp}_{random_code}"
        return file_id
    
    
    def detail(self, request, *args, **kwargs):
        """获取简历详情"""
        # TODO: 从ES数据库获取完整的简历信息，包括解析后的结构化数据
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 2000,
            "msg": "获取成功",
            "data": serializer.data
        })
    
    @action(methods=["POST"], detail=False)
    def upload(self, request):
        """上传简历文件"""
        file = request.FILES.get("file")
        if not file:
            return Response({"code": 4000, "msg": "请上传文件"})
        
        # 简历评分要求
        # 修改为
        resume_description = request.data.get('job_description', '')
        # print("简历评分要求：", resume_description)

        # 获取文件信息
        file_id = self.__getfileid__()
        file_name = file_id + "." + file.name.split(".")[-1]
        file_size = round(file.size / 1024)
        file_type = file_name.split(".")[-1]
        # 重设置文件名
        file._set_name(file_name)
        
        # 保存文件
        resume = Resume.objects.create(
            file=file,
            file_id=file_id,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size
        )

        # 文件解析
        document_markdown = ''
        file_path = os.path.join(settings.MEDIA_ROOT, resume.file.name)
        print("文件路径：", file_path)

        if file.name.endswith('.pdf'):
        # 解析PDF 使用magicpdf 解析成Markdown文件
            document_markdown = parse_pdf(file_path)
        elif file.name.endswith('.docx'):
            # 解析DOCX
            document_markdown = parse_docx(file_path)
        else:
            return Response({"code": 4000, "msg": "不支持的文件格式"})

        if not document_markdown or len(document_markdown.strip()) < 50:  # 设置最小内容长度阈值为50个字符
            return Response({"code": 4000, "msg": "文件解析失败或内容过少，请检查上传的文件是否正确"})
            
        analysis = chatToLLM4Analysis(document_markdown, resume_description)

        # 从analysis中提取json字符串
        try:
            # 查找json字符串的起始和结束位置
            start_idx = analysis.find('{')
            end_idx = analysis.rfind('}') + 1
            if start_idx == -1 or end_idx == 0:
                return Response({"code": 4000, "msg": "No valid JSON found in LLM output"})
                
            json_str = analysis[start_idx:end_idx]
            # 解析JSON字符串
            parsed_data = json.loads(json_str)
            
            # 验证必要字段是否存在
            required_fields = ['name', 'phone', 'email', 'education', 'work_experience', 
                'skills', 'projects', 'other','score','score_details']
            for field in required_fields:
                if field not in parsed_data:
                    return Response({"code": 4000, "msg": f'Missing required field: {field}' })
                    
        except json.JSONDecodeError as e:
            return Response({"code": 4000, "msg": f'Failed to parse JSON from LLM output: {str(e)}'})
        except Exception as e:
            return Response({"code": 4000, "msg": f'Error processing LLM output: {str(e)}'})

        # 保存解析结果到es数据库
        save_to_es(file_name,document_markdown,parsed_data)

        print("解析结果：", parsed_data)

        return Response({
            "code": 2000,
            "msg": "上传成功",
            "data": {
                "id": file_id,
                "file_name": file_name,
                "parsed_data": parsed_data
            }
        })
    
    @action(methods=["POST"], detail=False)
    def analyze(self, request):
        """分析简历内容"""
        file_id = request.data.get("file_id")
        job_description = request.data.get("job_description", "")
        
        if not file_id:
            return Response({"code": 4000, "msg": "请提供文件ID"})
            
        try:
            resume = Resume.objects.get(id=file_id)
        except Resume.DoesNotExist:
            return Response({"code": 4000, "msg": "文件不存在"})
            
        # 这里可以添加简历解析逻辑
        # 例如：调用第三方API或使用NLP库解析简历内容
        
        # 示例分析结果
        analysis_result = {
            "name": "示例姓名",
            "education": "本科",
            "experience": "3年",
            "skills": ["Python", "Django", "Vue"],
            "match_score": 85
        }
        
        # 更新分析结果
        resume.analysis_result = analysis_result
        resume.save()
        
        return Response({
            "code": 2000,
            "msg": "分析成功",
            "data": analysis_result
        })

    def list(self, request, *args, **kwargs):
        """获取简历列表"""
        try:
            results = list_resume()
        except Exception as e:
            print(f"获取简历列表失败: {str(e)}\n错误类型: {type(e).__name__}\n完整堆栈: ")
            return Response({
                'code': 4000,
                'error': f'获取简历列表失败: {str(e)}',
                'error_type': type(e).__name__
            })
        
        if not results:
            return Response({
                'code': 4000,
                'error': '获取简历列表失败',
                'error_type': 'NoResumeFound'
            })
        
        # 打印查询结果
        # print("查询结果：", results)

        print(f"查到{results['hits']['total']['value']}条数据，本次返回{len(results['hits']['hits'])}条")

        # 处理返回结果
        resumes = []
        for hit in results['hits']['hits']:
            resume = {
                'id': hit['_id'],
                'name': hit['_source']['metadata']['name'],
                'phone': hit['_source']['metadata'].get('phone', ''),
                'email': hit['_source']['metadata'].get('email', ''),
                'education': hit['_source']['metadata'].get('education', ''),
                'work_experience': hit['_source']['metadata'].get('work_experience', ''),
                'skills': hit['_source']['metadata'].get('skills', ''),
                'projects': hit['_source']['metadata'].get('projects', []),
                'other': hit['_source']['metadata'].get('other', ''),
                'score': hit['_source']['metadata'].get('score', ''),
                'score_details': hit['_source']['metadata'].get('score_details', ''),
                'filename': hit['_source']['metadata']['filename'],
                'upload_time': hit['_source']['metadata'].get('upload_time', '')
            }
            resumes.append(resume)
        # 获取分页参数
        page = int(request.query_params.get('page', 1))
        size = int(request.query_params.get('size', 10))
        
        # 计算分页数据
        start = (page - 1) * size
        end = start + size
        paged_resumes = resumes[start:end]
        
        return Response({
            'code': 2000,
            'total': results['hits']['total']['value'],
            'page': page,
            'size': size,
            'data': paged_resumes
        })
        
    @action(methods=["POST"], detail=False, url_path="chat")
    def handle_chat(self, request, *args, **kwargs):
        try:
            # 修改这一行，使用request.data而不是request.get_json()
            data = request.data
            message = data.get('message', '')
            if not message:
                return Response({"code": 4000, "msg": "用户对话内容为空"})
            
            # 调用DeepSeekChat处理消息
            response = chatToLLM(message)

            # 解析LLM返回的内容
            try:
                parsed_response = self.__parse_llm_response__(response)
            except ValueError as e:
                return Response({"code": 4000, "msg": f'解析LLM返回内容时出错: {str(e)}'})
            # 如果需要搜索，连接ES并执行搜索 ,不需要连接ES时，直接返回
            if not parsed_response['need_search']:
                return Response({
                    'success': True,
                    'need_search': False,
                    'reply': parsed_response['reply']
                })
            # 简历列表
            candidates = []
            # 构建搜索条件
            query = {
                "bool": {
                    "must": []
                }
            }

            # 构建搜索条件
            search_criteria = parsed_response['search_criteria']
            # 添加各种搜索条件
            if 'name' in search_criteria and search_criteria['name']:
                query['bool']['must'].append({
                    "match": {"metadata.name": search_criteria['name']}
                })
            
            if 'email' in search_criteria and search_criteria['email']:
                query['bool']['must'].append({
                    "match": {"metadata.email": search_criteria['email']}
                })
            
            if 'phone' in search_criteria and search_criteria['phone']:
                query['bool']['must'].append({
                    "match": {"metadata.phone": search_criteria['phone']}
                })
            
            if 'skills' in search_criteria and search_criteria['skills']:
                # 处理skills作为列表的情况
                skill_queries = []
                for skill in search_criteria['skills']:
                    skill_queries.append({
                        "match": {"metadata.skills": skill}
                    })
                    
                if skill_queries:
                    query['bool']['must'].append({
                        "bool": {
                            "should": skill_queries,
                            "minimum_should_match": 1
                        }
                    })

            if 'experience' in search_criteria and search_criteria['experience']:
                query['bool']['must'].append({
                    "match": {"metadata.experience": search_criteria['experience']}
                })

            if 'education' in search_criteria and search_criteria['education']:
                query['bool']['must'].append({
                    "match": {"metadata.education": search_criteria['education']}
                })
            
            if 'projects' in search_criteria and search_criteria['projects']:
                # 处理projects作为列表的情况
                project_queries = []
                for project in search_criteria['projects']:
                    project_queries.append({
                        "match": {"metadata.projects": project}
                    })
                
                if project_queries:
                    query['bool']['must'].append({
                        "bool": {
                            "should": project_queries,
                            "minimum_should_match": 1
                        }
                    })

            if 'gender' in search_criteria and search_criteria['gender']:
                query['bool']['must'].append({
                    "match": {"metadata.gender": search_criteria['gender']}
                })
            
            if 'score_range' in search_criteria and search_criteria['score_range']:
                query['bool']['must'].append({
                    "range": {"metadata.score": {
                        "gte": search_criteria['score_range'][0],
                        "lte": search_criteria['score_range'][1]
                    }}
                })
            
            if 'other' in search_criteria and search_criteria['other']:
                query['bool']['must'].append({
                    "match": {"metadata.other": search_criteria['other']}
                })

            try:
                # 连接ES数据库
                # 执行搜索
                results = search_resume(
                    query=query
                )

                print(f"搜索到{results['hits']['total']['value']}条数据")
            except Exception as e:
                print(f"搜索候选人失败: {str(e)}")
                parsed_response['reply'] += "\n\n搜索数据库时发生错误，请稍后重试。"
            # 处理搜索结果
            for hit in results['hits']['hits']:
                candidate = {
                    'id': hit['_id'],
                    'name': hit['_source']['metadata']['name'],
                    'phone': hit['_source']['metadata'].get('phone', ''),
                    'email': hit['_source']['metadata'].get('email', ''),
                    'education': hit['_source']['metadata'].get('education', ''),
                    'score': hit['_source']['metadata'].get('score', ''),
                    'filename': hit['_source']['metadata']['filename'],
                    'upload_time': hit['_source']['metadata'].get('upload_time', '')
                }
                candidates.append(candidate)


            # 将搜索结果添加到回复中
            parsed_response['reply'] += f"\n\n找到以下{len(candidates)}位候选人：\n"
            for candidate in candidates:
                parsed_response['reply'] += f"\n- {candidate['name']} | {candidate['education']} | 评分：{candidate['score']}"
            
                    # 获取分页参数
            page = int(request.query_params.get('page', 1))
            size = int(request.query_params.get('size', 10))
            
            # 计算分页数据
            start = (page - 1) * size
            end = start + size
            paged_resumes = candidates[start:end]
            
            return Response({
                'success': True,
                'need_search': True,
                'reply': parsed_response['reply'],  # 按照要求将响应放在data.reply字段中
                'data': {
                    'total': len(paged_resumes),
                    'page': page,
                    'size': size,
                    'data': paged_resumes
                }
            })
            
       
        except Exception as e:
            print(f"聊天处理失败: {str(e)}\n错误类型: {type(e).__name__}\n完整堆栈: {traceback.format_exc()}")
            return Response({
                'error': f'聊天处理失败: {str(e)}',
                'error_type': type(e).__name__,
                'stack_trace': traceback.format_exc().splitlines()
            }, status=500)  # 使用status参数而不是元组