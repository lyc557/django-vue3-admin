import os
import time
from typing import List, Dict
from langchain_community.embeddings import SentenceTransformerEmbeddings
from sentence_transformers import SentenceTransformer
from langchain.docstore.document import Document
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger
from dotenv import load_dotenv  # 环境变量管理

class EmbeddingModel:
    """文本嵌入模型类"""
    def __init__(self):
        """初始化"""
        self.setup_environment()
        self.model = None
        self.embeddings = None
        self.similarity_matrix = None
        self.model = self.load_embedding_model(local_model_path='/data/models/BAAI/bge-large-zh-v1.5')
    
    def setup_environment(self):
        """设置环境变量和代理"""
        load_dotenv()
        # 从 .env 读取代理设置
        http_proxy = os.getenv('HTTP_PROXY')
        https_proxy = os.getenv('HTTPS_PROXY')

        if http_proxy:
            os.environ['HTTP_PROXY'] = http_proxy
        if https_proxy:
            os.environ['HTTPS_PROXY'] = https_proxy
        
        logger.info("环境设置完成")
        

    def load_embedding_model(self, model_name: str = "BAAI/bge-large-zh-v1.5", local_model_path=None):
        """加载文本嵌入模型
        
        Args:
            model_name: 模型名称
            local_model_path: 本地模型路径，用于离线加载
            
        Returns:
            加载的模型对象，加载失败则返回None
        """
        try:
            if local_model_path and os.path.exists(local_model_path):
                logger.info(f"从本地路径加载模型: {local_model_path}")
                model = SentenceTransformer(local_model_path)
            else:
                model = SentenceTransformer(model_name)
            logger.info(f"成功加载模型: {model_name}")
            return model
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            return None

    def calculate_embeddings(self, sentences):
        """计算文本的嵌入向量
        
        Args:
            sentences: 待编码的文本列表
            
        Returns:
            嵌入向量，计算失败则返回None
        """
        if not self.model or not sentences:
            return None
        
        try:
            embeddings = self.model.encode(sentences)
            logger.info(f"嵌入向量计算完成，形状: {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"嵌入向量计算失败: {e}")
            return None
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """将文档列表转换为嵌入向量列表
        
        Args:
            texts: 文档文本列表
            
        Returns:
            嵌入向量列表
        """
        if not texts:
            return []
        
        try:
            embeddings = self.model.encode(texts)
            # 将numpy数组转换为Python列表
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"文档嵌入向量计算失败: {e}")
            # 出错时返回空列表
            return []
    
    def embed_query(self, text: str) -> List[float]:
        """将查询文本转换为嵌入向量
        
        Args:
            text: 查询文本
            
        Returns:
            嵌入向量
        """
        if not text:
            return []
        
        try:
            embedding = self.model.encode(text)
            # 将numpy数组转换为Python列表
            return embedding.tolist()
        except Exception as e:
            logger.error(f"查询嵌入向量计算失败: {e}")
            # 出错时返回空列表
            return []


def main():
    """主函数"""
    # 初始化模型
    embedding_model = EmbeddingModel()
    # 示例文本
    sentences = [
        "这是一个示例句子。",
        "这是另一个示例句子。",
        "这是一个更长的示例句子。"
    ]
    # 计算嵌入向量
    embeddings = embedding_model.calculate_embeddings(sentences)
    # 打印嵌入向量
    print(embeddings)


def __download_model__():
    from modelscope import snapshot_download
    # 指定模型名称
    model_name = 'ppaanngggg/layoutreader'
    model_dir = snapshot_download(model_name,local_dir='/data/models/'+model_name)
    print(f"模型已下载至：{model_dir}")

if __name__ == "__main__":
    main()
    # __download_model__()
