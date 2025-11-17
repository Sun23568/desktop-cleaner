"""
AI分析模块
负责调用通义大模型，分析文件并给出整理建议

【重要】请在此文件中填写通义大模型的调用代码
"""
import json
from typing import List, Dict, Optional
import config

# TODO: 导入通义千问的SDK
# 示例: from dashscope import Generation
# 或者使用 OpenAI 兼容的 API


class AIAnalyzer:
    """AI文件分析器"""

    def __init__(self):
        """初始化AI分析器"""
        self.api_key = config.TONGYI_API_KEY
        self.model = config.TONGYI_MODEL

        # TODO: 初始化通义千问客户端
        # 示例:
        # import dashscope
        # dashscope.api_key = self.api_key

    def analyze_files(self, files: List[Dict], progress_callback=None) -> Dict:
        """
        分析文件列表，返回整理建议（支持分批处理）

        :param files: 文件信息列表，每个文件包含 name, path, extension, size_mb, modified_time 等字段
        :param progress_callback: 进度回调函数，接收 (current_batch, total_batches, batch_result) 参数
        :return: 分析结果，包含分类建议、删除建议等

        返回格式示例:
        {
            'suggestions': [
                {
                    'file_path': '/path/to/file1.txt',
                    'action': 'delete',  # delete 删除, move 移动, keep 保留
                    'reason': '这是一个临时文件，已超过30天未使用',
                    'category': '临时文件',
                    'confidence': 0.9  # 置信度 0-1
                },
                ...
            ],
            'categories': {
                '临时文件': ['file1.txt', 'file2.txt'],
                '重要文档': ['file3.docx'],
                ...
            }
        }
        """

        # 分批处理文件
        batch_size = config.MAX_FILES_PER_REQUEST
        total_files = len(files)

        if total_files > batch_size:
            print(f"\n" + "="*80)
            print(f"📦 批量处理模式")
            print(f"   总文件数: {total_files}")
            print(f"   每批大小: {batch_size} (可在config.py中调整MAX_FILES_PER_REQUEST)")
            total_batches = (total_files + batch_size - 1) // batch_size
            print(f"   分批数量: {total_batches}")
            print("="*80)

            # 分批处理并合并结果
            all_suggestions = []
            all_categories = {}

            for i in range(0, total_files, batch_size):
                batch = files[i:i + batch_size]
                batch_num = i // batch_size + 1

                print(f"\n" + "▶"*40)
                print(f"📋 处理批次 {batch_num}/{total_batches}")
                print(f"   文件范围: {i+1} - {min(i+batch_size, total_files)}")
                print(f"   本批文件数: {len(batch)}")
                print(f"   文件列表:")
                for idx, f in enumerate(batch[:5], 1):  # 只显示前5个
                    print(f"      {idx}. {f['name']} ({f['size_mb']}MB)")
                if len(batch) > 5:
                    print(f"      ... 还有 {len(batch)-5} 个文件")
                print("▶"*40 + "\n")

                batch_result = self._analyze_batch(batch, batch_num, total_batches)

                # 统计本批结果
                batch_suggestions_count = len(batch_result.get('suggestions', []))
                print(f"\n✔️  批次 {batch_num} 完成，获得 {batch_suggestions_count} 条建议\n")

                all_suggestions.extend(batch_result.get('suggestions', []))

                # 合并分类
                for category, file_list in batch_result.get('categories', {}).items():
                    if category in all_categories:
                        all_categories[category].extend(file_list)
                    else:
                        all_categories[category] = file_list

                # 调用进度回调，实时更新GUI
                if progress_callback:
                    progress_callback(batch_num, total_batches, batch_result)

            print(f"\n" + "="*80)
            print(f"🎉 所有批次处理完成！")
            print(f"   总建议数: {len(all_suggestions)}")
            print(f"   分类数: {len(all_categories)}")
            print("="*80 + "\n")

            return {
                'suggestions': all_suggestions,
                'categories': all_categories
            }
        else:
            # 文件数量不多，直接处理
            print(f"\n📋 单批处理模式 - 共 {total_files} 个文件\n")
            result = self._analyze_batch(files, 1, 1)

            # 调用进度回调
            if progress_callback:
                progress_callback(1, 1, result)

            return result

    def _analyze_batch(self, files: List[Dict], batch_num: int = 1, total_batches: int = 1) -> Dict:
        """
        分析一批文件（内部方法）

        :param files: 文件列表
        :param batch_num: 当前批次号
        :param total_batches: 总批次数
        """
        print(f"🔄 开始分析批次 {batch_num}/{total_batches}...")

        # 构造发送给AI的提示词
        prompt = self._build_prompt(files)

        # 调用通义大模型API
        try:
            response_text = self._call_tongyi_api(prompt)
            result = self._parse_response(response_text)

            # 解析成功日志
            suggestions_count = len(result.get('suggestions', []))
            print(f"✅ 批次 {batch_num} 解析成功，获得 {suggestions_count} 条建议")

            return result
        except Exception as e:
            print(f"❌ 批次 {batch_num} AI分析失败: {e}")
            return self._get_empty_result()

    def _build_prompt(self, files: List[Dict]) -> str:
        """
        构建发送给AI的提示词
        """
        # 限制文件数量，避免超过token限制
        if len(files) > config.MAX_FILES_PER_REQUEST:
            files = files[:config.MAX_FILES_PER_REQUEST]

        # 构造文件列表的描述
        files_description = "文件列表:\n"
        for i, file in enumerate(files, 1):
            files_description += f"{i}. {file['name']} - {file['size_mb']}MB - 修改时间:{file['modified_time']}\n"
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

    def _call_tongyi_api(self, prompt: str) -> str:
        """
        调用通义千问API

        【核心方法 - 请在这里实现通义大模型的调用】

        :param prompt: 发送给AI的提示词
        :return: AI的响应文本
        """

        # TODO: 在这里实现通义千问API调用
        # ====================================
        # 方法1: 使用 dashscope SDK
        # ====================================
        # import dashscope
        # from dashscope import Generation

        # # 设置API Key（重要！）
        # dashscope.api_key = self.api_key

        # response = Generation.call(
        #     model=self.model,
        #     prompt=prompt,
        #     result_format='message'  # 或 'text'
        # )
        
        # if response.status_code == 200:
        #     return response.output.text
        # else:
        #     raise Exception(f"API调用失败: {response.message}")

        # ====================================
        # 方法2: 使用 OpenAI 兼容的 HTTP 请求（带重试机制）
        # ====================================
        import requests
        import time
        import json

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

        # 使用配置中的重试次数
        max_retries = config.AI_MAX_RETRIES

        for attempt in range(max_retries):
            try:
                print(f"\n{'='*80}")
                print(f"📡 通义千问API调用 - 尝试 {attempt + 1}/{max_retries}")
                print(f"{'='*80}")

                # 记录请求参数
                if config.ENABLE_DETAIL_LOG and config.LOG_REQUEST_PARAMS:
                    print(f"\n📤 请求参数:")
                    print(f"   URL: {url}")
                    print(f"   模型: {self.model}")
                    print(f"   超时设置: {config.AI_TIMEOUT}秒")
                    print(f"   提示词长度: {len(prompt)} 字符")
                    print(f"\n   消息内容:")
                    # 截取前500字符预览
                    preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
                    print(f"   {preview}")
                    print(f"\n   完整请求体:")
                    print(f"   {json.dumps(data, ensure_ascii=False, indent=2)[:1000]}...")

                # 发送请求
                start_time = time.time()
                response = requests.post(url, headers=headers, json=data, timeout=config.AI_TIMEOUT)
                elapsed_time = time.time() - start_time

                # 检查HTTP错误
                response.raise_for_status()

                # 解析响应
                result = response.json()
                response_content = result['choices'][0]['message']['content']

                # 成功日志
                print(f"\n✅ API调用成功！")
                print(f"⏱️  耗时: {elapsed_time:.2f}秒")
                print(f"📊 响应长度: {len(response_content)} 字符")

                # 记录响应内容
                if config.ENABLE_DETAIL_LOG and config.LOG_RESPONSE_CONTENT:
                    print(f"\n📥 响应内容:")
                    print(f"   HTTP状态码: {response.status_code}")

                    # Token使用情况
                    if 'usage' in result:
                        usage = result['usage']
                        print(f"\n   Token使用:")
                        print(f"      输入tokens: {usage.get('prompt_tokens', 'N/A')}")
                        print(f"      输出tokens: {usage.get('completion_tokens', 'N/A')}")
                        print(f"      总计tokens: {usage.get('total_tokens', 'N/A')}")

                    # AI响应内容（截取预览）
                    print(f"\n   AI响应内容（前500字符）:")
                    preview = response_content[:500] + "..." if len(response_content) > 500 else response_content
                    print(f"   {preview}")

                    # 完整响应（如果不太长）
                    if len(response_content) <= 2000:
                        print(f"\n   完整AI响应:")
                        print(f"   {response_content}")

                print(f"{'='*80}\n")

                return response_content

            except requests.exceptions.Timeout as e:
                print(f"\n⚠️  请求超时（尝试 {attempt + 1}/{max_retries}）")
                print(f"   错误: {str(e)}")

                if attempt < max_retries - 1:
                    wait_time = config.AI_RETRY_DELAY * (attempt + 1)
                    print(f"   等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"API调用超时，已重试{max_retries}次: {str(e)}")

            except requests.exceptions.HTTPError as e:
                print(f"\n❌ HTTP错误（尝试 {attempt + 1}/{max_retries}）")
                print(f"   状态码: {response.status_code}")
                print(f"   错误: {str(e)}")
                print(f"   响应内容: {response.text[:500]}")

                # 某些错误不需要重试
                if response.status_code in [401, 403]:
                    raise Exception(f"认证错误: {response.text}")

                if attempt < max_retries - 1:
                    wait_time = config.AI_RETRY_DELAY * (attempt + 1)
                    print(f"   等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"HTTP请求失败: {str(e)}")

            except requests.exceptions.RequestException as e:
                print(f"\n❌ 网络请求错误（尝试 {attempt + 1}/{max_retries}）")
                print(f"   错误类型: {type(e).__name__}")
                print(f"   错误详情: {str(e)}")

                if attempt < max_retries - 1:
                    wait_time = config.AI_RETRY_DELAY * (attempt + 1)
                    print(f"   等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"API调用失败: {str(e)}")

            except (KeyError, ValueError, json.JSONDecodeError) as e:
                print(f"\n❌ 响应解析错误")
                print(f"   错误类型: {type(e).__name__}")
                print(f"   错误详情: {str(e)}")
                print(f"   响应文本: {response.text[:500] if 'response' in locals() else 'N/A'}")
                raise Exception(f"API响应格式错误: {str(e)}")

        # ====================================
        # 临时返回（用于测试，请替换为实际的API调用）
        # ====================================
        # print("警告: AI API未配置，返回模拟数据")
        # return self._get_mock_response()

    def _get_mock_response(self) -> str:
        """
        获取模拟响应（仅用于测试）
        实际使用时，这个方法不会被调用
        """
        mock_result = {
            "suggestions": [
                {
                    "file_path": "/path/to/example.tmp",
                    "action": "delete",
                    "reason": "这是一个临时文件",
                    "category": "临时文件",
                    "confidence": 0.85
                }
            ],
            "categories": {
                "临时文件": ["example.tmp"],
                "文档": [],
                "图片": []
            }
        }
        return json.dumps(mock_result, ensure_ascii=False)

    def _parse_response(self, response_text: str) -> Dict:
        """
        解析AI返回的JSON响应
        """
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

    def _get_empty_result(self) -> Dict:
        """返回空结果"""
        return {
            'suggestions': [],
            'categories': {}
        }


if __name__ == '__main__':
    # 测试代码
    analyzer = AIAnalyzer()

    # 模拟文件列表
    test_files = [
        {
            'name': 'temp_file.tmp',
            'path': '/home/user/Desktop/temp_file.tmp',
            'extension': '.tmp',
            'size_mb': 1.5,
            'modified_time': '2024-01-15 10:30:00'
        },
        {
            'name': 'important_doc.pdf',
            'path': '/home/user/Desktop/important_doc.pdf',
            'extension': '.pdf',
            'size_mb': 5.2,
            'modified_time': '2025-11-10 14:20:00'
        }
    ]

    result = analyzer.analyze_files(test_files)
    print("AI分析结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
