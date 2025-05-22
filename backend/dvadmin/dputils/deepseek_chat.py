import os
import json
import threading
import concurrent.futures
from typing import List, Dict, Any
import requests
import re  # 添加 re 模块的导入
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential
import os
import sys
from dotenv import load_dotenv
# 从 .env 文件中加载环境变量

load_dotenv()
# 直接设置配置变量，避免导入 conf.env
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "")
DEEPSEEK_MAX_WORKERS = int(os.getenv("DEEPSEEK_MAX_WORKERS", "2"))

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
            "description": "万向信托移动私信系统提供客户账户管理、快速预约万向信托产品、查询账户资产概览、资产投资情况、交易流水及收益明细、资讯查看等功能。工作内容：根据需求编写测试点及用例，并标注优先级；提交缺陷报告，并对缺陷进行跟踪处理。针对系统兼容性等方面进行测试，在近期一次大版本更新中，累计发现 bug 上百个。"
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

    
    # 使用示例
chat = DeepSeekChat()


def chatToLLM(message):
    # 调用chat获取回复
    PROMPT_TMPL = """请根据用户的问题判断是否需要查询简历数据库。你的任务是根据问题内容决定是否需要查询数据库，并给出查询条件。

    判断规则：
    1. 如果问题涉及具体求职者的信息（如姓名、技能、工作经验等），则需要查询
    2. 如果问题要求推荐或筛选候选人，则需要查询
    3. 如果是一般性问题或不需要具体简历数据的问题，则不需要查询

    请按以下JSON格式回答：
    {
        "need_search": true/false,  // 是否需要查询数据库
        "search_criteria": {        // 如果需要查询，提供查询条件
            "name": "",             // 姓名条件（如有）
            "email": "",            // 邮箱条件（如有）
            "phone": "",            // 手机号码条件（如有）
            "skills": [],           // 技能条件（如有）
            "experience": "",       // 工作经验条件（如有）
            "education": "",        // 教育背景条件（如有）
            "gender": "",           // 性别条件（如有）
            "projects": [],         // 项目条件（如有）
            "other": "",            // 其他条件（如有）
            "score_range": [0,100]  // 分数范围（如有）
        }
        "reply": ""                // 如不需要查询，或者其他信息，请在这里回复
    }
    当前用户问题：{{question}}"""

    # 使用时替换question变量
    prompt = PROMPT_TMPL.replace('{{question}}', message)
    # 调用chat方法
    print("提示词：", prompt)
    response = chat.chat(prompt)  # 调用chat方法
    # response = {
    #         "need_search": true,
    #         "search_criteria": {
    #             "name": "",
    #             "skills": [],
    #             "experience": "4年以上",
    #             "education": "985,211院校",
    #             "score_range": [0,100],
    #             "gender": "女"
    #         },
    #         "reply": ""
    #     }
    print("回复：", response)
    return response

def chatToLLM4Analysis(document, job_description):
    # 让大模型提取简历关键信息，获得标准格式的json以及评分
    document = document.strip()


    # 构建提示模板，可以加入岗位要求
    PROMPT_TMPL = "你是一个专业的招聘经理，请从以下一份中文简历中提取结构化的关键信息"
    
    if job_description:
        PROMPT_TMPL += "，并根据简历要求进行打分并给出得分详情：\n简历要求：{{job_description}}\n"
    PROMPT_TMPL += "评分维度如下：" + \
       "1. 简历排版与清晰度（10 分）：版式是否清晰、有逻辑结构、有无明显错别字或排版混乱。" + \
       "2. 教育背景（15 分）：学历层次、院校背景、是否为相关专业等。" + \
       "3. 工作经验与成就（35 分）：工作年限、职位层级、是否有具体成果或量化成绩。" + \
       "4. 技能与证书（20 分）：是否具备关键硬技能或软技能，有无权威证书支持。" + \
       "5. 语言能力（10 分）：英语或其他语言能力如何，是否有官方考试成绩或实际应用经验。" + \
       "6. 专业表达与语气（10 分）：语言是否专业、逻辑是否清晰、是否避免空话套话。\n"

    PROMPT_TMPL += "按如下格式输出：" + \
       "```json\n" + \
       "{\n" + \
       "    \"name\": \"姓名\",\n" + \
       "    \"phone\": \"手机号码\",\n" + \
       "    \"email\": \"邮箱\",\n" + \
       "    \"education\": \"教育经历\",\n" + \
       "    \"work_experience\": \"工作经历\"\n" + \
       "    \"skills\": \"技能列表\",\n" + \
       "    \"projects\": [{\n" + \
       "        \"name\": \"项目名称\",\n" + \
       "        \"role\": \"担任角色\",\n" + \
       "        \"description\": \"项目描述\"\n" + \
       "    }],\n" + \
       "    \"other\": \"其他信息\"\n" + \
       "    \"score\": \"综合得分\"\n" + \
       "    \"score_details\": \"得分详情\"\n" + \
       "}\n" + \
       "```\n" + \
       "简历内容：{{document}}" + \
       "请确保输出的JSON格式正确，并且所有字段都有值。"

    # 构建提示词
    prompt = PROMPT_TMPL.replace('{{document}}', document)
    if job_description:
        prompt = prompt.replace('{{job_description}}', job_description)
    
    print("提示词：", prompt)
    # 调用chat获取分析结果
    analysis = chat.chat(prompt)  # 调用chat方法
    return analysis
    
def main():
    # 从文件中读取简历内容
    with open('media/output/1745487393.md', 'r', encoding='utf-8') as f:
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