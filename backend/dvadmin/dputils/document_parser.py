# 标准库导入
import os
import traceback

# 第三方库导入
from docx import Document

# 本地模块导入
from pdftomarkdown import MarkdownConverter

def parse_docx(file_path):
    """解析docx文件并返回结构化数据"""
    try:
        # 确保文件存在且可读
        if not os.path.exists(file_path) or not os.access(file_path, os.R_OK):
            raise Exception("文件不存在或不可读")
            
        # 使用绝对路径
        abs_path = os.path.abspath(file_path)
        print("doc文件路径：", abs_path)

        # 加载 Word 文件
        doc = Document(abs_path)

        # 初始化空字符串用于拼接所有段落
        full_text = ""
        # 逐段读取并拼接
        for para in doc.paragraphs:
            full_text += para.text + "\n"  # 添加换行符分隔段落
        print("docfull_text：", full_text)
        return full_text.strip()  # 去除末尾多余换行
    except Exception as e:
        print(f"DOCX解析错误: {str(e)}")
        traceback.print_exc()  # 打印完整错误堆栈
        return ""


def parse_pdf(file_path):
    """解析PDF文件并返回结构化数据"""
    try:
        # 使用绝对路径并添加错误处理
        # 初始化PDF转Markdown转换器 
        converter = MarkdownConverter()
        result = converter.convert(os.path.abspath(file_path))
        converter.clear_gpu_memory()  # 清除GPU内存
        return result
    except Exception as e:
        print(f"PDF解析错误: {str(e)}")
        return ""

if __name__ == "__main__":
    print(parse_docx("../data/简历/20200706/程新磊3年.docx"))
    # print(parse_pdf("../data/简历/20200508/谭宗森 3年.pdf"))