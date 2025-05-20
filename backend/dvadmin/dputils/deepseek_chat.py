import os
import json
import threading
import concurrent.futures
from typing import List, Dict, Any
import requests
import re  # 添加 re 模块的导入
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential
from conf.env import *

class DeepSeekChat:
    def __init__(self, api_key: str = None, api_base: str = None, model: str = None):
        """初始化 DeepSeek 聊天客户端
        
        Args:
            api_key: DeepSeek API密钥，如果为None则从配置或环境变量获取
            api_base: API基础URL，如果为None则从配置获取
            model: 使用的模型，如果为None则从配置获取
        """
        self.api_key = api_key or DEEPSEEK_API_KEY or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供 DEEPSEEK_API_KEY")
        
        self.api_base = api_base or DEEPSEEK_API_BASE
        self.model = model or DEEPSEEK_MODEL
        
    def chat_mock(self, prompt: str, temperature: float = 0.7, debug: bool = False) -> str:
        renturn = """
        ```json
{
    "name": "吴晓双",
    "phone": "15950868517",
    "email": "844817991@qq.com",
    "education": "安徽建筑大学城市建设学院 电子信息工程/本科 (2015.09-2019.06)",
    "work_experience": [
        "北京宇信科技集团股份有限公司 UI自动化测试工程师 (2022.09-至今)",
        "捷保有信信息技术有限公司 软件测试工程师 (2020.07-2022.08)",
        "信雅达科技股份有限公司 软件测试工程师 (2019.07-2020.07)"
    ],
    "skills": [
        "擅长UI自动化测试，可独立设计、执行测试用例",
        "熟悉综合管理平台流程类测试",
        "通晓金融方面开户、下单、合同签署等流程，熟悉相关 app、pc端测试",
        "熟悉 oracle ，可熟练使用 sql 语句增删改查",
        "有良好的Python编程基础，UI自动化流程测试脚本编写熟练",
        "英语水平cet4，掌握Python语言、sql 常用语句；熟练使用oracle、git、fiddler、postman等工具"
    ],
    "projects": [
        {
            "name": "大盈私享app测试",
            "role": "UI自动化测试工程师",
            "description": "万向信托移动私信系统提供客户账户管理、快速预约万向信托产品、查询账户资产概览、资产投资情况、交易流水及收益明细、资讯查看等功能。工作内容：根据需求编写测试点及用例，并标注优先级；提交缺陷报告，并对缺陷进行跟踪处理。针对系统兼容性等方面进行测试，在近期一次大版本更新中，累计发现 bug 近百个。"
        },
        {
            "name": "综合管理平台测试",
            "role": "UI自动化测试工程师",
            "description": "负责公司内部综合管理平台、信息填报系统、礼品卡兑换系统功能测试。涉及的重要功能会定期进行自动化测试。工作内容：根据需求编写测试用例、部署测试环境再进行详细测试，使用管理工具禅道提交bug ，对bug进行跟踪和监控、分析测试结果，编写测试报告。属于日常工作，着重流程测试、后台数据对比，参与该项目平均每月发现bug20+。"
        },
        {
            "name": "特殊资产服务信托小程序",
            "role": "UI自动化测试工程师",
            "description": "一款连接法官、债权人和管理人的工作平台。债权人可通过该小程序自行录入并上传证明材料，完成线上债权申报。管理人可通过小程序或后台管理端，协同开展债权审查工作。工作内容：小程序端、管理端功能测试，累计发现bug 80+。"
        }
    ],
    "other": "求职意向：软件测试工程师 | 生日：1996.09.23 | 现居：浙江杭州 | 学习能力强，对新事物充满探索精神，上手新内容速度快。",
    "score": "85",
    "score_details": "候选人具有扎实的软件测试经验，尤其在UI自动化测试方面表现突出。项目经历丰富，能够独立完成测试用例设计和执行，并发现大量bug。技能全面，熟悉多种测试工具和编程语言。教育背景与求职岗位匹配，工作经历连贯且有成长性。"
}
```
        """
        return renturn

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def chat(self, prompt: str, temperature: float = 0.7, debug: bool = False) -> str:
        """发送聊天请求到 DeepSeek API
        
        Args:
            prompt: 提示文本
            temperature: 温度参数，控制响应的随机性
            debug: 是否打印调试信息
            
        Returns:
            API 返回的响应文本
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        
        if debug:
            print(f"发送请求: {prompt[:100]}...")
            
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"API 调用失败: {str(e)}")
            raise
    
    @staticmethod
    def build_qa_prompt(prompt_tmpl: str, text: str) -> str:
        """构建QA提示
        
        Args:
            prompt_tmpl: 提示模板
            text: 要处理的文本
        """
        prompt = prompt_tmpl.replace('{{document}}', text).strip()
        return prompt

    @staticmethod
    def build_qa_scoring_prompt(prompt_teml: str,row):
        # QA质量检查prompt
        context = row['context']
        question = row['question']
        answer = row['answer']
        prompt = prompt_teml.replace('{{question}}', question).replace('{{answer}}', answer)
        return prompt

    
    

def main():
    # 使用示例
    chat = DeepSeekChat()
    
    # 从文件中读取简历内容
    with open('output/吴晓双-软件测试.md', 'r', encoding='utf-8') as f:
        document = f.read()

    PROMPT_TMPL = "你是一个专业的招聘助理，请从以下一份中文简历中提取结构化的关键信息，按如下格式输出：" + \
        "```json\n" + \
        "{\n" + \
        "    \"name\": \"姓名\",\n" + \
        "    \"phone\": \"手机号码\",\n" + \
        "    \"email\": \"邮箱\",\n" + \
        "    \"education\": \"教育经历\",\n" + \
        "    \"work_experience\": \"工作经历\"\n" + \
        "    \"skills\": \"技能描述\",\n" + \
        "    \"projects\": \"项目经历\"\n" + \
        "}\n" + \
        "```\n" + \
        "简历内容：{{document}}" + \
        "请确保输出的JSON格式正确，并且所有字段都有值。"
    prompt = PROMPT_TMPL.replace('{{document}}', document)
    response = chat.chat(prompt)
    print(f"问题: {prompt}")
    print(f"回答: {response}")

if __name__ == "__main__":
    main()