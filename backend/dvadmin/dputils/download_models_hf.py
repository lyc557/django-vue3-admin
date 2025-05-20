import json
import os
import shutil
import subprocess

import requests
from huggingface_hub import snapshot_download
# ===== 配置和工具 =====
from dotenv import load_dotenv  # 环境变量管理
import os  # 操作系统相关

def download_json(url):
    # 下载JSON文件
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功
    return response.json()


def download_and_modify_json(url, local_filename, modifications):
    if os.path.exists(local_filename):
        data = json.load(open(local_filename))
        config_version = data.get('config_version', '0.0.0')
        if config_version < '1.2.0':
            data = download_json(url)
    else:
        data = download_json(url)

    # 修改内容
    for key, value in modifications.items():
        data[key] = value

    # 保存修改后的内容
    with open(local_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# 先定义 setup_environment 函数
def setup_environment():
    """设置环境变量和代理"""
    load_dotenv()
    # 从 .env 读取代理设置
    http_proxy = os.getenv('HTTP_PROXY')
    https_proxy = os.getenv('HTTPS_PROXY')

    if http_proxy:
        os.environ['HTTP_PROXY'] = http_proxy
    if https_proxy:
        os.environ['HTTPS_PROXY'] = https_proxy
    
    print("环境变量和代理设置完成")


def install_dependencies():
    """安装必要的依赖"""
    print("安装必要的依赖...")
    # 安装 rapidocr_onnxruntime
    subprocess.run(["pip", "install", "rapidocr_onnxruntime"], check=True)
    # 安装 paddleocr 相关依赖
    subprocess.run(["pip", "install", "paddleocr", "--upgrade"], check=True)
    print("依赖安装完成")


if __name__ == '__main__':
    # 然后调用函数
    setup_environment()  # 加载环境变量
    install_dependencies()  # 安装依赖

    # 修复仓库ID格式
    repo_id = "opendatalab/PDF-Extract-Kit-1.0"
    mineru_patterns = [
        "models/Layout/YOLO/*",
        "models/MFD/YOLO/*",
        "models/MFR/unimernet_hf_small_2503/*",
        "models/OCR/paddleocr_torch/*",
    ]
    
    print(f"开始从 {repo_id} 下载模型...")
    # 使用正确的参数格式
    model_dir = snapshot_download(
        repo_id=repo_id,         # 仓库ID
        allow_patterns=mineru_patterns,  # 允许的文件模式
        repo_type="model",       # 指定为模型
        resume_download=True     # 支持断点续传
    )
    print(f"模型下载完成: {model_dir}")

    # 修复layoutreader仓库ID
    layoutreader_repo_id = "hantian/layoutreader"
    layoutreader_pattern = [
        "*.json",
        "*.safetensors",
    ]
    
    print(f"开始从 {layoutreader_repo_id} 下载模型...")
    layoutreader_model_dir = snapshot_download(
        repo_id=layoutreader_repo_id, 
        allow_patterns=layoutreader_pattern,
        repo_type="model",
        resume_download=True
    )
    print(f"layoutreader模型下载完成: {layoutreader_model_dir}")

    model_dir = model_dir + '/models'
    print(f'model_dir is: {model_dir}')
    print(f'layoutreader_model_dir is: {layoutreader_model_dir}')

    # 取消注释这部分代码，确保paddleocr模型正确复制
    paddleocr_model_dir = model_dir + '/OCR/paddleocr'
    user_paddleocr_dir = os.path.expanduser('~/.paddleocr')
    if os.path.exists(user_paddleocr_dir):
        shutil.rmtree(user_paddleocr_dir)
    if os.path.exists(paddleocr_model_dir):
        shutil.copytree(paddleocr_model_dir, user_paddleocr_dir)
    else:
        print(f"警告: paddleocr模型目录不存在: {paddleocr_model_dir}")
        os.makedirs(user_paddleocr_dir, exist_ok=True)

    json_url = 'https://github.com/opendatalab/MinerU/raw/master/magic-pdf.template.json'
    config_file_name = 'magic-pdf.json'
    home_dir = os.path.expanduser('~')
    config_file = os.path.join(home_dir, config_file_name)

    json_mods = {
        'models-dir': model_dir,
        'layoutreader-model-dir': layoutreader_model_dir,
        'device-mode': 'cpu',  # 添加设备模式设置
        'ocr-config': {
            'use_angle_cls': False,  # 禁用角度分类，减少依赖
            'lang': 'ch'  # 指定语言为中文
        }
    }

    download_and_modify_json(json_url, config_file, json_mods)
    print(f'配置文件已成功配置，路径为: {config_file}')
    print("现在可以运行 pdftomarkdown.py 了")
