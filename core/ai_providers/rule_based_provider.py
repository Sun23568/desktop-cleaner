"""
基于规则的文件分析提供商
不依赖AI，纯规则判断
"""
from typing import List, Dict
from datetime import datetime, timedelta
from .base_provider import AIProvider


class RuleBasedProvider(AIProvider):
    """基于规则的文件分析提供商"""

    def __init__(self, config: Dict = None):
        super().__init__(config)

        # 规则配置
        self.temp_extensions = {'.tmp', '.temp', '.cache', '.log', '.bak', '.old'}
        self.doc_extensions = {'.doc', '.docx', '.pdf', '.txt', '.md', '.xlsx', '.xls', '.ppt', '.pptx'}
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'}
        self.video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
        self.audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'}
        self.archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'}
        self.installer_extensions = {'.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm'}

        # 时间阈值
        self.old_file_days = self.config.get('old_file_days', 90)  # 90天未修改视为旧文件
        self.temp_file_days = self.config.get('temp_file_days', 7)  # 7天未修改的临时文件可删除

    def get_provider_name(self) -> str:
        return "规则引擎 (Rule-Based)"

    def is_available(self) -> bool:
        """规则引擎始终可用"""
        return True

    def analyze_files(self, files: List[Dict], existing_categories: List[str] = None) -> Dict:
        """基于规则分析文件

        :param files: 文件列表
        :param existing_categories: 已存在的类别列表（规则引擎不使用，保持接口一致性）
        """
        print(f"\n{'='*80}")
        print(f"🔧 使用规则引擎分析文件")
        print(f"{'='*80}")

        suggestions = []
        categories = {
            '临时文件': [],
            '文档': [],
            '图片': [],
            '视频': [],
            '音频': [],
            '压缩包': [],
            '安装包': [],
            '其他': []
        }

        for file_info in files:
            file_name = file_info['name']
            file_path = file_info['path']
            extension = file_info.get('extension', '').lower()
            size_kb = file_info.get('size_kb', 0)
            modified_time_str = file_info.get('modified_time', '')

            # 解析修改时间
            try:
                modified_time = datetime.strptime(modified_time_str, '%Y-%m-%d %H:%M:%S')
                days_since_modified = (datetime.now() - modified_time).days
            except:
                days_since_modified = 0

            # 应用规则
            suggestion = self._apply_rules(
                file_name, file_path, extension,
                size_kb, days_since_modified, categories
            )

            if suggestion:
                suggestions.append(suggestion)

        print(f"✅ 规则引擎分析完成，生成 {len(suggestions)} 条建议")
        print(f"{'='*80}\n")

        return {
            'suggestions': suggestions,
            'categories': categories
        }

    def _apply_rules(self, file_name: str, file_path: str, extension: str,
                     size_kb: float, days_since_modified: int,
                     categories: Dict) -> Dict:
        """应用规则判断文件"""

        # 规则1: 临时文件
        if extension in self.temp_extensions:
            categories['临时文件'].append(file_name)

            if days_since_modified > self.temp_file_days:
                return {
                    'file_path': file_path,
                    'action': 'delete',
                    'reason': f'临时文件，已{days_since_modified}天未修改',
                    'category': '临时文件',
                    'confidence': 0.9
                }
            else:
                return {
                    'file_path': file_path,
                    'action': 'keep',
                    'reason': '临时文件，但最近修改过',
                    'category': '临时文件',
                    'confidence': 0.7
                }

        # 规则2: 文档
        elif extension in self.doc_extensions:
            categories['文档'].append(file_name)

            if days_since_modified > self.old_file_days:
                return {
                    'file_path': file_path,
                    'action': 'move',
                    'reason': f'文档，已{days_since_modified}天未修改，建议归档',
                    'category': '文档',
                    'confidence': 0.8
                }
            else:
                return {
                    'file_path': file_path,
                    'action': 'keep',
                    'reason': '最近使用的文档',
                    'category': '文档',
                    'confidence': 0.9
                }

        # 规则3: 图片
        elif extension in self.image_extensions:
            categories['图片'].append(file_name)
            return {
                'file_path': file_path,
                'action': 'move',
                'reason': '图片文件，建议移动到图片文件夹',
                'category': '图片',
                'confidence': 0.85
            }

        # 规则4: 视频
        elif extension in self.video_extensions:
            categories['视频'].append(file_name)

            if size_kb > 100 * 1024:  # 大于100MB
                return {
                    'file_path': file_path,
                    'action': 'move',
                    'reason': f'大视频文件({size_kb/1024:.1f}MB)，建议移动到专门目录',
                    'category': '视频',
                    'confidence': 0.9
                }
            else:
                return {
                    'file_path': file_path,
                    'action': 'move',
                    'reason': '视频文件，建议整理',
                    'category': '视频',
                    'confidence': 0.8
                }

        # 规则5: 音频
        elif extension in self.audio_extensions:
            categories['音频'].append(file_name)
            return {
                'file_path': file_path,
                'action': 'move',
                'reason': '音频文件，建议移动到音乐文件夹',
                'category': '音频',
                'confidence': 0.85
            }

        # 规则6: 压缩包
        elif extension in self.archive_extensions:
            categories['压缩包'].append(file_name)

            if days_since_modified > self.old_file_days:
                return {
                    'file_path': file_path,
                    'action': 'delete',
                    'reason': f'旧压缩包，已{days_since_modified}天未使用',
                    'category': '压缩包',
                    'confidence': 0.7
                }
            else:
                return {
                    'file_path': file_path,
                    'action': 'keep',
                    'reason': '最近的压缩包',
                    'category': '压缩包',
                    'confidence': 0.8
                }

        # 规则7: 安装包
        elif extension in self.installer_extensions:
            categories['安装包'].append(file_name)

            if days_since_modified > 30:
                return {
                    'file_path': file_path,
                    'action': 'delete',
                    'reason': f'安装包，已{days_since_modified}天未使用，可能已安装',
                    'category': '安装包',
                    'confidence': 0.75
                }
            else:
                return {
                    'file_path': file_path,
                    'action': 'keep',
                    'reason': '最近的安装包',
                    'category': '安装包',
                    'confidence': 0.8
                }

        # 其他文件
        else:
            categories['其他'].append(file_name)

            if days_since_modified > self.old_file_days * 2:  # 180天
                return {
                    'file_path': file_path,
                    'action': 'move',
                    'reason': f'长时间未使用({days_since_modified}天)，建议归档',
                    'category': '其他',
                    'confidence': 0.6
                }
            else:
                return {
                    'file_path': file_path,
                    'action': 'keep',
                    'reason': '普通文件',
                    'category': '其他',
                    'confidence': 0.7
                }
