"""
通义千问AI提供商
"""
import json
import requests
import time
from typing import List, Dict
from .base_provider import AIProvider


class TongyiProvider(AIProvider):
    """通义千问AI提供商"""

    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.api_key = self.config.get('api_key', '')
        self.model = self.config.get('model', 'qwen-plus')
        self.timeout = self.config.get('timeout', 60)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 2)
        self.enable_detail_log = self.config.get('enable_detail_log', False)

    def get_provider_name(self) -> str:
        return "通义千问 (Tongyi)"

    def is_available(self) -> bool:
        """检查API Key是否配置"""
        return bool(self.api_key and self.api_key != 'your-api-key-here')

    def analyze_files(self, files: List[Dict]) -> Dict:
        """分析文件列表"""
        if not self.is_available():
            raise Exception("通义千问API Key未配置")

        prompt = self._build_prompt(files)

        try:
            response_text = self._call_api(prompt)
            result = self._parse_response(response_text)
            return result
        except Exception as e:
            print(f"❌ 通义千问分析失败: {e}")
            return self._get_empty_result()

    def _build_prompt(self, files: List[Dict]) -> str:
        """构建提示词"""
        files_description = "文件列表:\n"
        for i, file in enumerate(files, 1):
            files_description += f"{i}. {file['name']} - {file['size_kb']}KB - 修改时间:{file['modified_time']}\n"
            files_description += f"   路径: {file['path']}\n"

        prompt = f"""你是一个智能文件管理助手。请分析以下桌面和下载文件夹中的文件，并给出整理建议。

{files_description}

请按照以下JSON格式返回分析结果（只返回JSON，不要其他文字）：

{{
    "suggestions": [
        {{
            "file_path": "文件完整路径",
            "action": "delete/move/keep",
            "reason": "建议理由",
            "category": "文件分类（如：临时文件、重要文档、图片等）",
            "confidence": 0.9
        }}
    ],
    "categories": {{
        "临时文件": ["文件名1", "文件名2"],
        "重要文档": ["文件名3"]
    }}
}}

分析要点：
1. 识别临时文件、重复文件、过期文件，建议删除
2. 将文件按类型分类（文档、图片、视频、安装包等）
3. 标注每个建议的置信度
4. 给出清晰的理由

现在请开始分析。"""

        return prompt

    def _call_api(self, prompt: str) -> str:
        """调用通义千问API"""
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        for attempt in range(self.max_retries):
            try:
                print(f"\n{'='*80}")
                print(f"📡 通义千问API调用 - 尝试 {attempt + 1}/{self.max_retries}")
                print(f"{'='*80}")

                if self.enable_detail_log:
                    print(f"\n📤 请求参数:")
                    print(f"   URL: {url}")
                    print(f"   模型: {self.model}")
                    print(f"   超时设置: {self.timeout}秒")
                    preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
                    print(f"   提示词预览:\n   {preview}")

                start_time = time.time()
                response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
                elapsed_time = time.time() - start_time

                response.raise_for_status()
                result = response.json()
                response_content = result['choices'][0]['message']['content']

                print(f"\n✅ API调用成功！")
                print(f"⏱️  耗时: {elapsed_time:.2f}秒")
                print(f"📊 响应长度: {len(response_content)} 字符")
                print(f"{'='*80}\n")

                return response_content

            except requests.exceptions.Timeout as e:
                print(f"\n⚠️  请求超时（尝试 {attempt + 1}/{self.max_retries}）")
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    print(f"   等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"API调用超时，已重试{self.max_retries}次: {str(e)}")

            except requests.exceptions.HTTPError as e:
                print(f"\n❌ HTTP错误（尝试 {attempt + 1}/{self.max_retries}）")
                print(f"   状态码: {response.status_code}")
                print(f"   响应内容: {response.text[:500]}")

                if response.status_code in [401, 403]:
                    raise Exception(f"认证错误: {response.text}")

                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    print(f"   等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"HTTP请求失败: {str(e)}")

            except Exception as e:
                print(f"\n❌ API调用错误: {str(e)}")
                raise

    def _parse_response(self, response_text: str) -> Dict:
        """解析AI返回的JSON响应"""
        # 去除可能的markdown代码块标记
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        # 解析JSON
        result = json.loads(response_text)

        # 验证格式
        if 'suggestions' not in result:
            result['suggestions'] = []
        if 'categories' not in result:
            result['categories'] = {}

        return result
