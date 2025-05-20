# -*- coding: utf-8 -*-

"""
@author: yangcailu
@Created on: 简历解析工具
@Remark: 提供简历解析相关功能
"""
import json
import requests
from django.conf import settings
from dvadmin.utils.json_response import DetailResponse, ErrorResponse


def parse_resume(file_path, file_type=None):
    """
    调用简历解析接口，解析上传的简历文件
    
    :param file_path: 简历文件路径
    :param file_type: 文件类型，如pdf、doc、docx等，如果为None则自动从文件路径推断
    :return: 解析结果
    """
    try:
        # 如果未指定文件类型，则从文件路径推断
        if file_type is None:
            file_extension = file_path.split('.')[-1].lower()
            file_type = file_extension
        
        # 这里可以根据实际情况调用第三方简历解析API
        # 以下为示例代码，实际使用时需要替换为真实的API调用
        resume_api_url = getattr(settings, 'RESUME_PARSE_API_URL', None)
        api_key = getattr(settings, 'RESUME_PARSE_API_KEY', None)
        
        if not resume_api_url:
            return ErrorResponse(msg="未配置简历解析API地址")
        
        # 准备请求数据
        with open(file_path, 'rb') as file:
            files = {'resume': (file_path.split('/')[-1], file, f'application/{file_type}')}
            headers = {}
            
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            
            # 发送请求到简历解析API
            response = requests.post(
                resume_api_url,
                files=files,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return DetailResponse(data=result, msg="简历解析成功")
            else:
                return ErrorResponse(msg=f"简历解析失败: {response.text}")
    
    except Exception as e:
        return ErrorResponse(msg=f"简历解析出错: {str(e)}")


def extract_resume_info(resume_data):
    """
    从解析结果中提取关键信息
    
    :param resume_data: 简历解析返回的原始数据
    :return: 提取后的关键信息
    """
    try:
        # 根据实际API返回的数据结构进行处理
        # 以下为示例代码，需要根据实际使用的API返回格式调整
        extracted_info = {
            'basic_info': {
                'name': resume_data.get('name', ''),
                'phone': resume_data.get('phone', ''),
                'email': resume_data.get('email', ''),
                'gender': resume_data.get('gender', ''),
                'age': resume_data.get('age', ''),
                'education': resume_data.get('education', ''),
            },
            'work_experience': resume_data.get('work_experience', []),
            'education_experience': resume_data.get('education_experience', []),
            'skills': resume_data.get('skills', []),
            'projects': resume_data.get('projects', []),
        }
        
        return DetailResponse(data=extracted_info, msg="简历信息提取成功")
    
    except Exception as e:
        return ErrorResponse(msg=f"简历信息提取出错: {str(e)}")