"""
文件管理模块
负责执行文件的删除、移动、备份等操作
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import config


class FileManager:
    """文件管理器"""

    def __init__(self):
        """初始化文件管理器"""
        self.backup_folder = config.BACKUP_FOLDER
        self.enable_backup = config.ENABLE_BACKUP

    def execute_suggestions(self, suggestions: List[Dict], progress_callback=None) -> Dict:
        """
        执行AI给出的建议

        :param suggestions: AI建议列表
        :param progress_callback: 进度回调函数，接收 (current, total, action, file_path) 参数
        :return: 执行结果统计
        """
        results = {
            'success': [],
            'failed': [],
            'skipped': [],
            'deleted_count': 0,
            'moved_count': 0,
            'kept_count': 0,
            'freed_space_mb': 0
        }

        total = len(suggestions)

        for i, suggestion in enumerate(suggestions):
            file_path = suggestion.get('file_path')
            action = suggestion.get('action', 'keep')

            if progress_callback:
                progress_callback(i + 1, total, action, file_path)

            try:
                if action == 'delete':
                    freed_space = self.delete_file(file_path, backup=self.enable_backup)
                    results['deleted_count'] += 1
                    results['freed_space_mb'] += freed_space
                    results['success'].append({
                        'file': file_path,
                        'action': 'deleted',
                        'freed_mb': freed_space
                    })

                elif action == 'move':
                    category = suggestion.get('category', 'Others')
                    new_path = self.move_file(file_path, category)
                    results['moved_count'] += 1
                    results['success'].append({
                        'file': file_path,
                        'action': 'moved',
                        'new_path': new_path
                    })

                elif action == 'keep':
                    results['kept_count'] += 1
                    results['skipped'].append(file_path)

            except Exception as e:
                results['failed'].append({
                    'file': file_path,
                    'error': str(e)
                })

        return results

    def delete_file(self, file_path: str, backup: bool = True) -> float:
        """
        删除文件

        :param file_path: 文件路径
        :param backup: 是否备份
        :return: 释放的空间（MB）
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 获取文件大小
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)

        # 备份
        if backup:
            self._backup_file(file_path)

        # 删除文件
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

        return round(file_size_mb, 2)

    def move_file(self, file_path: str, category: str) -> str:
        """
        移动文件到分类文件夹

        :param file_path: 文件路径
        :param category: 分类名称
        :return: 新的文件路径
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 创建分类文件夹（在原文件所在目录的父目录下）
        parent_dir = Path(file_path).parent
        category_folder = parent_dir / f"整理_{category}"
        category_folder.mkdir(exist_ok=True)

        # 移动文件
        file_name = os.path.basename(file_path)
        new_path = category_folder / file_name

        # 如果目标路径已存在，添加时间戳
        if new_path.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name_parts = os.path.splitext(file_name)
            new_name = f"{name_parts[0]}_{timestamp}{name_parts[1]}"
            new_path = category_folder / new_name

        shutil.move(file_path, str(new_path))
        return str(new_path)

    def _backup_file(self, file_path: str):
        """
        备份文件

        :param file_path: 文件路径
        """
        # 创建备份文件夹
        backup_folder = Path(self.backup_folder)
        backup_folder.mkdir(parents=True, exist_ok=True)

        # 创建带日期的子文件夹
        date_str = datetime.now().strftime('%Y%m%d')
        date_folder = backup_folder / date_str
        date_folder.mkdir(exist_ok=True)

        # 备份文件
        file_name = os.path.basename(file_path)
        backup_path = date_folder / file_name

        # 如果备份文件已存在，添加时间戳
        if backup_path.exists():
            timestamp = datetime.now().strftime('%H%M%S')
            name_parts = os.path.splitext(file_name)
            new_name = f"{name_parts[0]}_{timestamp}{name_parts[1]}"
            backup_path = date_folder / new_name

        shutil.copy2(file_path, str(backup_path))

    def create_category_folders(self, categories: Dict[str, List[str]], base_path: str):
        """
        根据分类创建文件夹并移动文件

        :param categories: 分类字典 {'分类名': ['文件1', '文件2']}
        :param base_path: 基础路径
        """
        for category, files in categories.items():
            category_folder = Path(base_path) / f"整理_{category}"
            category_folder.mkdir(exist_ok=True)

            for file_name in files:
                # 这里需要找到文件的完整路径
                # 在实际使用中，应该从扫描结果中获取完整路径
                pass

    def get_recycle_bin_size(self) -> float:
        """
        获取回收站大小（仅Windows）

        :return: 回收站大小（MB）
        """
        # 这个功能需要特定的系统API，暂时返回0
        return 0.0

    def empty_recycle_bin(self):
        """
        清空回收站（仅Windows）
        """
        # 这个功能需要特定的系统API
        # 可以使用 winshell 库（Windows）或其他系统命令
        pass


if __name__ == '__main__':
    # 测试代码
    manager = FileManager()

    # 测试创建备份文件夹
    print(f"备份文件夹: {manager.backup_folder}")

    # 测试建议执行（使用模拟数据）
    test_suggestions = [
        {
            'file_path': '/path/to/test.txt',
            'action': 'keep',
            'reason': '重要文件'
        }
    ]

    # 注意：实际运行前请确保测试文件存在
    # results = manager.execute_suggestions(test_suggestions)
    # print(f"执行结果: {results}")
