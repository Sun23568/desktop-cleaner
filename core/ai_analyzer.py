"""
AI分析模块
负责调用AI模型，分析文件并给出整理建议

支持多种AI提供商：
- tongyi: 通义千问
- rule_based: 规则引擎（不依赖AI）
- 可扩展：openai, ollama等
"""
import json
from typing import List, Dict, Optional
import config
from core.ai_providers import AIProviderFactory, AIProvider
from core.user_config import get_config_manager


class AIAnalyzer:
    """AI文件分析器（支持多提供商）"""

    def __init__(self, provider_type: str = None):
        """
        初始化AI分析器
        :param provider_type: AI提供商类型，不指定则使用用户配置
        """
        # 优先使用用户配置
        self.config_manager = get_config_manager()

        # 如果没有指定provider_type，从用户配置读取
        if provider_type is None:
            provider_type = self.config_manager.get('ai_provider', config.AI_PROVIDER)

        self.provider_type = provider_type
        self.fallback_enabled = self.config_manager.get('ai_fallback', config.AI_FALLBACK_TO_RULES)

        # 创建AI提供商
        self.provider = self._create_provider(self.provider_type)

    def _create_provider(self, provider_type: str) -> AIProvider:
        """创建AI提供商"""
        # 优先使用用户配置，如果没有则使用config.py的默认值
        provider_config = {
            'api_key': self.config_manager.get('tongyi_api_key', config.TONGYI_API_KEY),
            'model': self.config_manager.get('tongyi_model', config.TONGYI_MODEL),
            'timeout': self.config_manager.get('ai_timeout', config.AI_TIMEOUT),
            'max_retries': config.AI_MAX_RETRIES,
            'retry_delay': config.AI_RETRY_DELAY,
            'enable_detail_log': config.ENABLE_DETAIL_LOG,
            'old_file_days': self.config_manager.get('rule_old_file_days', config.RULE_OLD_FILE_DAYS),
            'temp_file_days': self.config_manager.get('rule_temp_file_days', config.RULE_TEMP_FILE_DAYS),
        }

        return AIProviderFactory.create_provider(provider_type, provider_config)

    def analyze_files(self, files: List[Dict], progress_callback=None) -> Dict:
        """
        分析文件列表，返回整理建议（支持分批处理）

        :param files: 文件信息列表，每个文件包含 name, path, extension, size_kb, modified_time 等字段
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
        batch_size = self.config_manager.get('max_files_per_request', config.MAX_FILES_PER_REQUEST)
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
                    print(f"      {idx}. {f['name']} ({f['size_kb']}KB)")
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

        # 调用AI提供商
        try:
            result = self.provider.analyze_files(files)

            # 解析成功日志
            suggestions_count = len(result.get('suggestions', []))
            print(f"✅ 批次 {batch_num} 解析成功，获得 {suggestions_count} 条建议")

            return result

        except Exception as e:
            print(f"❌ 批次 {batch_num} AI分析失败: {e}")

            # 如果启用了fallback且不是规则引擎
            if self.fallback_enabled and self.provider_type != 'rule_based':
                print(f"\n⚠️  正在切换到规则引擎作为fallback...")
                try:
                    fallback_provider = self._create_provider('rule_based')
                    result = fallback_provider.analyze_files(files)
                    print(f"✅ 规则引擎fallback成功")
                    return result
                except Exception as fallback_error:
                    print(f"❌ 规则引擎fallback也失败: {fallback_error}")

            return self._get_empty_result()

    def _get_empty_result(self) -> Dict:
        """返回空结果"""
        return {
            'suggestions': [],
            'categories': {}
        }


if __name__ == '__main__':
    # 测试代码
    print("="*80)
    print("AI分析器测试")
    print("="*80)

    # 模拟文件列表
    test_files = [
        {
            'name': 'temp_file.tmp',
            'path': '/home/user/Desktop/temp_file.tmp',
            'extension': '.tmp',
            'size_kb': 1536.0,
            'size_mb': 1.5,
            'modified_time': '2024-01-15 10:30:00'
        },
        {
            'name': 'important_doc.pdf',
            'path': '/home/user/Desktop/important_doc.pdf',
            'extension': '.pdf',
            'size_kb': 5324.8,
            'size_mb': 5.2,
            'modified_time': '2025-11-10 14:20:00'
        },
        {
            'name': 'photo.jpg',
            'path': '/home/user/Desktop/photo.jpg',
            'extension': '.jpg',
            'size_kb': 2048.0,
            'size_mb': 2.0,
            'modified_time': '2025-10-01 12:00:00'
        }
    ]

    # 测试不同的提供商
    print("\n测试1: 使用配置文件中的默认提供商")
    analyzer1 = AIAnalyzer()
    result1 = analyzer1.analyze_files(test_files)
    print("分析结果:")
    print(json.dumps(result1, indent=2, ensure_ascii=False))

    print("\n" + "="*80)
    print("测试2: 强制使用规则引擎")
    analyzer2 = AIAnalyzer(provider_type='rule_based')
    result2 = analyzer2.analyze_files(test_files)
    print("分析结果:")
    print(json.dumps(result2, indent=2, ensure_ascii=False))

    print("\n" + "="*80)
    print("测试完成！")
