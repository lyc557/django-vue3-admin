import os
from typing import List, Dict, Any, Optional
from tqdm import tqdm
from elasticsearch import Elasticsearch
from langchain.docstore.document import Document
from langchain_core.embeddings import Embeddings
from logger_config import get_logger
import numpy as np
from langchain_core.embeddings import Embeddings
from embedding_model import EmbeddingModel
from dotenv import load_dotenv
# 初始化日志记录器
logger = get_logger(__name__)
load_dotenv()

ES_URL = os.getenv("ES_URL", "")
ES_USERNAME = os.getenv("ES_USERNAME", "")
ES_PASSWORD = os.getenv("ES_PASSWORD", "")
ES_VERIFY_CERTS = os.getenv("ES_VERIFY_CERTS", "False") == "True"


class ESVectorDB:
    """Elasticsearch 向量数据库类，用于文档向量化和检索"""
    
    def __init__(self, ES_URL: str = "http://localhost:9200",ES_USERNAME:str="elastic",ES_PASSWORD:str="your_password",ES_VERIFY_CERTS:bool=False):
        self.ES_URL = ES_URL
        self.ES_USERNAME = ES_USERNAME
        self.ES_PASSWORD = ES_PASSWORD
        self.ES_VERIFY_CERTS = ES_VERIFY_CERTS

        """初始化 Elasticsearch 向量数据库
        
        Args:
            es_url: Elasticsearch 服务器 URL
        """
        try:
            self.es_client = Elasticsearch(self.ES_URL,basic_auth=(self.ES_USERNAME, self.ES_PASSWORD), verify_certs=self.ES_VERIFY_CERTS)
            logger.info(f"成功连接到 Elasticsearch: {ES_URL}")
        except Exception as e:
            logger.error(f"连接 Elasticsearch 失败: {e}")
            self.es_client = None
    
    def create_index(self, index_name: str, dims: int = 1024, force_recreate: bool = False):
        """创建向量索引
        
        Args:
            index_name: 索引名称
            dims: 向量维度
            force_recreate: 是否强制重建索引
        
        Returns:
            创建是否成功
        """
        if self.es_client is None:
            logger.error("Elasticsearch 客户端未初始化")
            return False
            
        # 检查索引是否存在
        index_exists = self.es_client.indices.exists(index=index_name)
        
        # 如果索引存在且需要重建，则删除
        if index_exists and force_recreate:
            self.es_client.indices.delete(index=index_name)
            logger.info(f"已删除现有索引: {index_name}")
            index_exists = False
        
        # 如果索引不存在，则创建
        if not index_exists:
            # 定义索引映射
            mapping = {
                "mappings": {
                    "properties": {
                        "content": {"type": "text"},
                        "vector": {"type": "dense_vector", "dims": dims},
                        "metadata": {"type": "object"}
                    }
                }
            }
            
            try:
                # 注意：在 Elasticsearch 8.x 中，body 参数已更改为直接传递映射
                self.es_client.indices.create(index=index_name, mappings=mapping["mappings"])
                logger.info(f"成功创建索引: {index_name}")
                return True
            except Exception as e:
                logger.error(f"创建索引失败: {e}")
                if hasattr(e, 'info'):
                    logger.error(f"错误详情: {e.info}")
                return False
        else:
            logger.info(f"索引已存在: {index_name}")
            return True
    
    def index_documents(self, docs: List[Document], embedding_model: Embeddings, 
                       index_name: str, batch_size: int = 100):
        """索引文档
        
        Args:
            docs: 文档列表
            embedding_model: 嵌入模型
            index_name: 索引名称
            batch_size: 批处理大小
        
        Returns:
            索引是否成功
        """
        if self.es_client is None:
            logger.error("Elasticsearch 客户端未初始化")
            return False
            
        if not docs:
            logger.warning("没有文档需要索引")
            return False
            
        # 获取第一个文档的向量维度
        try:
            sample_embedding = embedding_model.embed_documents([docs[0].page_content])[0]
            dims = len(sample_embedding)
            logger.info(f"向量维度: {dims}")
            
            # 创建索引
            if not self.create_index(index_name, dims):
                return False
                
        except Exception as e:
            logger.error(f"获取向量维度失败: {e}")
            return False
        
        # 批量索引文档
        total_batches = (len(docs) + batch_size - 1) // batch_size
        success_count = 0
        
        for i in tqdm(range(0, len(docs), batch_size), total=total_batches, desc="索引文档"):
            batch_docs = docs[i:i+batch_size]
            batch_texts = [doc.page_content for doc in batch_docs]
            
            try:
                # 获取嵌入向量
                batch_embeddings = embedding_model.embed_documents(batch_texts)
                
                # 准备批量索引请求
                bulk_data = []
                for j, (doc, embedding) in enumerate(zip(batch_docs, batch_embeddings)):
                    # 使用metadata中的doc_id作为文档ID，如果没有则使用默认生成方式
                    doc_id = doc.metadata.get('doc_id', f"{i+j}")
                    print(f"文档ID: {doc_id}")
                    # 索引操作
                    bulk_data.append({"index": {"_index": index_name, "_id": doc_id}})
                    
                    # 文档内容
                    doc_data = {
                        "content": doc.page_content,
                        "vector": embedding,
                        "metadata": doc.metadata
                    }
                    bulk_data.append(doc_data)
                
                # 执行批量索引
                if bulk_data:
                    # 异步刷新配置（不立即刷新）
                    response = self.es_client.bulk(body=bulk_data, refresh=False)
                    if not response.get("errors", True):
                        success_count += len(batch_docs)
                    else:
                        logger.warning(f"批量索引部分失败: {response}")
                
            except Exception as e:
                logger.error(f"批量索引失败: {e}")
        
        logger.info(f"成功索引 {success_count}/{len(docs)} 个文档")
        return success_count > 0
    
    def search(self, query: str, embedding_model: Embeddings, index_name: str, 
              k: int = 5, metadata_filter: Optional[Dict[str, Any]] = None):
        """向量搜索
        
        Args:
            query: 查询文本
            embedding_model: 嵌入模型
            index_name: 索引名称
            k: 返回结果数量
            metadata_filter: 元数据过滤条件
            
        Returns:
            检索到的文档列表
        """
        if self.es_client is None:
            logger.error("Elasticsearch 客户端未初始化")
            return []
            
        try:
            # 获取查询向量
            query_vector = embedding_model.embed_query(query)
            
            # 构建查询
            search_query = {
                "size": k,
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                            "params": {"query_vector": query_vector}
                        }
                    }
                }
            }
            
            # 添加元数据过滤
            if metadata_filter:
                filter_conditions = []
                for key, value in metadata_filter.items():
                    filter_conditions.append({"term": {f"metadata.{key}": value}})
                
                search_query["query"] = {
                    "bool": {
                        "must": search_query["query"],
                        "filter": filter_conditions
                    }
                }
            
            # 执行搜索
            response = self.es_client.search(index=index_name, body=search_query)
            
            # 处理结果
            results = []
            for hit in response['hits']['hits']:
                source = hit['_source']
                content = source.get('content', '')
                metadata = source.get('metadata', {})
                score = hit['_score']
                
                doc = Document(page_content=content, metadata={**metadata, "score": score})
                results.append(doc)
            
            return results
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def get_all_metadatas(self, index_name: str):
        """获取索引中所有文档的元数据
        
        Args:
            index_name: 索引名称
            
        Returns:
            元数据列表
        """
        if self.es_client is None:
            logger.error("Elasticsearch 客户端未初始化")
            return []
            
        try:
            # 使用scroll API获取所有文档
            query = {"query": {"match_all": {}}, "_source": ["metadata"]}
            
            # 初始化scroll
            response = self.es_client.search(
                index=index_name,
                body=query,
                scroll="2m",
                size=1000
            )
            
            scroll_id = response["_scroll_id"]
            hits = response["hits"]["hits"]
            
            # 收集所有元数据
            all_metadatas = []
            while len(hits) > 0:
                # 处理当前批次的结果
                for hit in hits:
                    metadata = hit["_source"].get("metadata", {})
                    all_metadatas.append(metadata)
                
                # 获取下一批结果
                response = self.es_client.scroll(
                    scroll_id=scroll_id,
                    scroll="2m"
                )
                scroll_id = response["_scroll_id"]
                hits = response["hits"]["hits"]
            
            # 清理scroll
            self.es_client.clear_scroll(scroll_id=scroll_id)
            
            return all_metadatas
            
        except Exception as e:
            logger.error(f"获取元数据失败: {e}")
            return []

    def index(self, index: str, document: Dict[str, Any]):
        """将单个文档索引到Elasticsearch
        
        Args:
            index: 索引名称
            document: 文档内容，包含向量和元数据
            
        Returns:
            索引操作的响应
        """
        if self.es_client is None:
            logger.error("Elasticsearch 客户端未初始化")
            return None
            
        try:
            response = self.es_client.index(index=index, document=document)
            logger.info(f"成功索引文档到 {index}")
            return response
        except Exception as e:
            logger.error(f"索引文档失败: {e}")
            return None

    def search_documents(self, index_name, query, sort=None, size=10):
        """搜索ES文档"""
        try:
            # 构建查询体
            search_body = {
                "query": query,
                "size": size
            }
            
            # 添加排序条件
            if sort:
                search_body["sort"] = sort
                
            # 执行搜索 - 使用 es_client 直接查询
            response = self.es_client.search(
                index=index_name,
                body=search_body
            )
            
            return response
            
        except Exception as e:
            print(f"搜索文档失败: {str(e)}")
            return None

def _query_es_(query_text, index_name, top_k=10):
    """
    在 Elasticsearch 中执行查询并返回结果。
    Args:
        query_text (str): 查询文本。
        index_name (str): 索引名称。
        top_k (int): 返回的结果数量。
    Returns:
        list: 包含查询结果的列表。
    """
    # 初始化 Elasticsearch 客户端
    es = Elasticsearch(ES_URL, basic_auth=(ES_USERNAME, ES_PASSWORD), verify_certs=ES_VERIFY_CERTS)

    # 构建查询
    query = {
        "query": {
            "match": {
                "content": query_text
            }
        },
        "size": top_k
    }
    # 执行查询
    response = es.search(index=index_name, body=query)
    # 解析结果
    results = []
    for hit in response["hits"]["hits"]:
        source = hit["_source"]
        content = source.get("content", "")
        metadata = source.get("metadata", {})
        score = hit["_score"]
        results.append({"content": content, "metadata": metadata, "score": score})
    return results


def _main_4_one_docs_():
    # 连接 ES 实例
    es = ESVectorDB(ES_URL,ES_USERNAME,ES_PASSWORD,ES_VERIFY_CERTS)
    # 定义索引名称
    index_name = "vector_es01_index"
    # 创建索引，指定向量维度为1024
    es.create_index(index_name, dims=1024, force_recreate=True)
    embedding_model = EmbeddingModel()
    # 创建示例文档
    from langchain.docstore.document import Document 
    docs = [
        Document(page_content=f"这是第{i+1}个测试文档的内容...", 
                metadata={
                    "doc_id": f"doc_{i:03d}",
                    "filename": f"product_manual_{chr(65+i)}.pdf",
                    "doc_length": np.random.randint(500, 2000)
                })
        for i in range(20)
    ]

    print("开始索引文档...")

    # 使用index_documents方法批量索引文档
    es.index_documents(docs, embedding_model, index_name)

    # 测试查询
    query_text = "12"
    logger.info(f"执行查询: {query_text}")
    results = es.search(query_text, embedding_model, index_name, k=5)
    for doc in results:
        logger.info(f"文档内容: {doc.page_content}, 分数: {doc.metadata.get('score')}")



def _main_():
    # 只是向量数据库，没有向量模型。
    # 连接 ES 实例
    es = ESVectorDB(ES_URL,ES_USERNAME,ES_PASSWORD,ES_VERIFY_CERTS)
    
    # 定义索引名称
    index_name = "vector_test_index"
    
    # 创建索引，指定向量维度为3
    es.create_index(index_name, dims=3, force_recreate=True)
    
    # 创建示例文档
    from langchain.docstore.document import Document
    
    docs = [
        Document(page_content="这是文档1", metadata={"uuid": "doc1"}),
        Document(page_content="这是文档2", metadata={"uuid": "doc2"}),
        Document(page_content="这是文档3", metadata={"uuid": "doc3"}),
        Document(page_content="这是文档4", metadata={"uuid": "doc4"}),
        Document(page_content="这是文档5", metadata={"uuid": "doc5"}),
        Document(page_content="这是文档6", metadata={"uuid": "doc6"}),
        Document(page_content="这是文档7", metadata={"uuid": "doc7"}),
        Document(page_content="这是文档8", metadata={"uuid": "doc8"}),
        Document(page_content="这是文档9", metadata={"uuid": "doc9"}),
        Document(page_content="这是文档10", metadata={"uuid": "doc10"}),
    ]
    
    # 创建一个简单的嵌入模型用于测试
    from langchain_core.embeddings import Embeddings
    
    class SimpleEmbeddings(Embeddings):
        def embed_documents(self, texts):
            # 简单示例，为每个文档生成一个3维向量
            return [[0.1, 0.2, 0.3], [0.2, 0.1, 0.4], [0.4, 0.4, 0.2]]
            
        def embed_query(self, text):
            # 查询向量
            return [0.2, 0.2, 0.3]
    
    # 索引文档
    embedding_model = SimpleEmbeddings()
    es.index_documents(docs, embedding_model, index_name)
    
    # 执行搜索
    results = es.search("测试查询", embedding_model, index_name, k=3)
    
    print("搜索结果：")
    for doc in results:
        print(f"文档内容: {doc.page_content}, 分数: {doc.metadata.get('score')}")



if __name__ == "__main__":
    # 只测向量数据库
    _main_()
    # 文档向量化
    _main_4_one_docs_()
    ret = _query_es_("测试查询", "vector_es_index")
    print(ret)
