import os
import json
import torch
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod

class MarkdownConverter:
    def __init__(self, output_dir: str = "output"):
        """
        初始化PDF转Markdown转换器
        :param output_dir: 输出目录
        """
        self.output_dir = output_dir
        self.image_dir = os.path.join(output_dir, "images")
        
        # 初始化输出目录
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # 初始化写入器
        self.image_writer = FileBasedDataWriter(self.image_dir)
        self.md_writer = FileBasedDataWriter(output_dir)
        self.ds = None  # 延迟初始化

    def clear_gpu_memory(self):
        '''
        clear GPU memory
        '''
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
            print("MPS GPU memory cleared.")
        else:
            print("MPS not available, skipping memory clearing.")
        torch.cuda.empty_cache()
        print("GPU memory cleared.")

    def doc_convert(self, doc_path: str):
        """
        执行PDF到Markdown的转换
        :param doc_path: PDF文件路径
        :return: Markdown内容
        """
        # 读取PDF内容
        if not os.path.exists(doc_path):
            raise FileNotFoundError(f"PDF文件不存在: {doc_path}")
        self.file_bytes = FileBasedDataReader("").read(doc_path)
        self.ds = PymuDocDataset(self.file_bytes)
        # 清空GPU内存
        self.clear_gpu_memory()

        # 判断处理模式
        if self.ds.classify() == SupportedPdfParseMethod.OCR:
            infer_result = self.ds.apply(doc_analyze, ocr=True)
            pipe_result = infer_result.pipe_ocr_mode(self.image_writer)
        else:
            infer_result = self.ds.apply(doc_analyze, ocr=False)
            pipe_result = infer_result.pipe_txt_mode(self.image_writer)

        # 生成各种输出文件
        self._generate_output_files(infer_result, pipe_result)
        # 返回Markdown内容
        return pipe_result.get_markdown(os.path.basename(self.image_dir))


    def convert(self, pdf_path: str):
        """执行PDF到Markdown的转换"""
        # 读取PDF内容
        pdf_path = os.path.abspath(pdf_path)  # 转换为绝对路径
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
            
        self.name_without_ext = os.path.splitext(os.path.basename(pdf_path))[0]
        self.pdf_bytes = FileBasedDataReader("").read(pdf_path)
        self.ds = PymuDocDataset(self.pdf_bytes)

        # 清空GPU内存
        self.clear_gpu_memory()
        
        # 判断处理模式
        if self.ds.classify() == SupportedPdfParseMethod.OCR:
            infer_result = self.ds.apply(doc_analyze, ocr=True)
            pipe_result = infer_result.pipe_ocr_mode(self.image_writer)
        else:
            infer_result = self.ds.apply(doc_analyze, ocr=False)
            pipe_result = infer_result.pipe_txt_mode(self.image_writer)
        
        # 生成各种输出文件
        self._generate_output_files(infer_result, pipe_result)
        
        # 返回Markdown内容
        return pipe_result.get_markdown(os.path.basename(self.image_dir))
    
    def _generate_output_files(self, infer_result, pipe_result):
        """生成所有输出文件"""
        # 绘制模型结果
        infer_result.draw_model(self._get_output_path("_model.pdf"))
        
        # 绘制布局结果
        pipe_result.draw_layout(self._get_output_path("_layout.pdf"))
        
        # 绘制文本块结果
        pipe_result.draw_span(self._get_output_path("_spans.pdf"))
        
        # 保存Markdown文件
        pipe_result.dump_md(self.md_writer, f"{self.name_without_ext}.md", 
                           os.path.basename(self.image_dir))
        
        # 保存内容列表
        pipe_result.dump_content_list(self.md_writer, 
                                    f"{self.name_without_ext}_content_list.json",
                                    os.path.basename(self.image_dir))
        
        # 保存中间JSON
        pipe_result.dump_middle_json(self.md_writer, 
                                    f"{self.name_without_ext}_middle.json")
    
    def _get_output_path(self, suffix: str) -> str:
        """获取输出文件路径"""
        return os.path.join(self.output_dir, f"{self.name_without_ext}{suffix}")

# 使用示例
if __name__ == "__main__":
    converter = MarkdownConverter()  # 初始化时不传pdf_path
    pdf_path = "/Users/luyangcai/trae/django-vue3-admin/backend/media/output/1745491266.pdf"
    print("开始转换PDF到Markdown...")
    markdown_content = converter.convert(pdf_path)  # 只调用一次convert并传入参数
    converter.clear_gpu_memory()
    
    print("转换完成，Markdown内容已保存到输出目录")
