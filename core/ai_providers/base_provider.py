"""
AI提供商基类
定义统一的AI接口，支持多种AI提供商
"""
from abc import ABC, abstractmethod
from typing import List, Dict


class AIProvider(ABC):
    """AI提供商抽象基类"""

    def __init__(self, config: Dict = None):
        """
        初始化AI提供商
        :param config: 配置字典
        """
        self.config = config or {}

    @abstractmethod
    def analyze_files(self, files: List[Dict], existing_categories: List[str] = None) -> Dict:
        """
        分析文件列表，返回整理建议

        :param files: 文件信息列表，每个文件包含 name, path, extension, size_kb, modified_time 等字段
        :param existing_categories: 已存在的类别列表（用于保持一致性）
        :return: 分析结果

        返回格式:
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
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """获取提供商名称"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        pass

    def _get_empty_result(self) -> Dict:
        """返回空结果"""
        return {
            'suggestions': [],
            'categories': {}
        }
