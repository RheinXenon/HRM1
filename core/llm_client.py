"""
LLM客户端 - 封装对Qwen API的调用
"""

import os
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger
import json

# 加载环境变量
load_dotenv()


class LLMClient:
    """LLM客户端类，封装Qwen API调用"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        初始化LLM客户端
        
        Args:
            api_key: API密钥，默认从环境变量读取
            base_url: API基础URL，默认从环境变量读取
            model: 模型名称，默认从环境变量读取
        """
        self.api_key = api_key or os.getenv("QWEN_API_KEY")
        self.base_url = base_url or os.getenv("QWEN_API_URL")
        self.model = model or os.getenv("QWEN_MODEL", "qwen-max")
        
        if not self.api_key or self.api_key == "your_qwen_api_key_here":
            logger.warning("⚠️  QWEN_API_KEY未配置或使用默认值，请在.env中设置真实的API密钥")
        
        # 初始化OpenAI客户端（兼容Qwen API）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        logger.info(f"✅ LLM客户端初始化成功: {self.model}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        执行对话补全
        
        Args:
            messages: 消息列表，格式为 [{"role": "system/user/assistant", "content": "..."}]
            temperature: 温度参数，控制随机性
            max_tokens: 最大token数
            response_format: 响应格式，如 {"type": "json_object"}
            
        Returns:
            模型生成的响应文本
        """
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            if response_format:
                params["response_format"] = response_format
            
            response = self.client.chat.completions.create(**params)
            
            content = response.choices[0].message.content
            
            # 记录token使用情况
            if hasattr(response, 'usage'):
                logger.debug(
                    f"Token使用: prompt={response.usage.prompt_tokens}, "
                    f"completion={response.usage.completion_tokens}, "
                    f"total={response.usage.total_tokens}"
                )
            
            return content
            
        except Exception as e:
            logger.error(f"❌ LLM调用失败: {e}")
            raise
    
    def chat_with_system_prompt(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        使用系统提示词进行对话（简化版）
        
        Args:
            system_prompt: 系统提示词
            user_message: 用户消息
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            模型响应
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def chat_with_json_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Dict:
        """
        请求JSON格式的响应
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            
        Returns:
            解析后的JSON对象
        """
        try:
            # 请求JSON格式响应
            response_text = self.chat_completion(
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            
            # 解析JSON
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析失败: {e}")
            logger.error(f"原始响应: {response_text}")
            # 尝试提取JSON部分
            try:
                # 如果响应包含markdown代码块
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                    return json.loads(json_str)
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0].strip()
                    return json.loads(json_str)
            except:
                pass
            raise
