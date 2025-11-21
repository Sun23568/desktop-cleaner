"""
文件扫描模块
负责扫描指定目录，收集文件信息
"""
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import config


class FileInfo:
    """文件信息类"""
    def __init__(self, file_path: str):
        self.path = file_path
        self.name = os.path.basename(file_path)
        self.extension = os.path.splitext(file_path)[1].lower()
        self.size = os.path.getsize(file_path)  # 字节
        self.size_kb = round(self.size / 1024, 2)  # KB
        self.size_mb = round(self.size / (1024 * 1024), 2)  # MB
        self.modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        self.created_time = datetime.fromtimestamp(os.path.getctime(file_path))
        self.is_file = os.path.isfile(file_path)

    def to_dict(self) -> Dict:
        """转换为字典格式，方便传递给AI"""
        return {
            'name': self.name,
            'path': self.path,
            'extension': self.extension,
            'size_kb': self.size_kb,
            'size_mb': self.size_mb,
            'modified_time': self.modified_time.strftime('%Y-%m-%d %H:%M:%S'),
            'created_time': self.created_time.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def __repr__(self):
        return f"FileInfo(name={self.name}, size={self.size_mb}MB, modified={self.modified_time})"


class FileScanner:
    """文件扫描器"""

    def __init__(self, scan_paths: List[str] = None):
        """
        初始化扫描器
        :param scan_paths: 要扫描的路径列表
        """
        self.scan_paths = scan_paths or config.DEFAULT_SCAN_PATHS
        self.scanned_files: List[FileInfo] = []

    def scan(self, progress_callback=None) -> List[FileInfo]:
        """
        扫描文件
        :param progress_callback: 进度回调函数，接收 (current, total, file_path) 参数
        :return: 文件信息列表
        """
        self.scanned_files = []
        total_files = 0

        # 先计算总文件数
        for scan_path in self.scan_paths:
            if not os.path.exists(scan_path):
                print(f"路径不存在: {scan_path}")
                continue
            total_files += sum(1 for _ in self._walk_path(scan_path))

        # 开始扫描
        current = 0
        for scan_path in self.scan_paths:
            if not os.path.exists(scan_path):
                continue

            for file_path in self._walk_path(scan_path):
                try:
                    file_info = FileInfo(file_path)

                    # 过滤条件
                    if self._should_include(file_info):
                        self.scanned_files.append(file_info)

                    current += 1
                    if progress_callback:
                        progress_callback(current, total_files, file_path)

                except (PermissionError, OSError) as e:
                    print(f"无法访问文件: {file_path}, 错误: {e}")
                    current += 1
                    continue

        return self.scanned_files

    def _walk_path(self, path: str):
        """遍历路径下的第一层文件（不递归）"""
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)

                # 只扫描文件，跳过文件夹
                if os.path.isfile(item_path):
                    yield item_path
        except (PermissionError, OSError):
            pass

    def _should_include(self, file_info: FileInfo) -> bool:
        """判断文件是否应该被包含"""
        # 忽略指定扩展名
        if file_info.extension in config.IGNORE_EXTENSIONS:
            return False

        # 忽略太小的文件
        if config.MIN_FILE_SIZE > 0 and file_info.size_mb < config.MIN_FILE_SIZE:
            return False

        return True

    def get_statistics(self) -> Dict:
        """获取扫描统计信息"""
        if not self.scanned_files:
            return {
                'total_files': 0,
                'total_size_mb': 0,
                'file_types': {}
            }

        file_types = {}
        total_size = 0

        for file_info in self.scanned_files:
            # 统计文件类型
            ext = file_info.extension or 'no_extension'
            file_types[ext] = file_types.get(ext, 0) + 1
            total_size += file_info.size_mb

        return {
            'total_files': len(self.scanned_files),
            'total_size_mb': round(total_size, 2),
            'file_types': file_types
        }

    def get_files_for_ai(self) -> List[Dict]:
        """
        获取用于AI分析的文件列表（简化格式）
        """
        return [f.to_dict() for f in self.scanned_files]


if __name__ == '__main__':
    # 测试代码
    scanner = FileScanner()

    def progress(current, total, path):
        print(f"扫描进度: {current}/{total} - {path}")

    files = scanner.scan(progress_callback=progress)
    stats = scanner.get_statistics()

    print(f"\n扫描完成！")
    print(f"总文件数: {stats['total_files']}")
    print(f"总大小: {stats['total_size_mb']} MB")
    print(f"文件类型分布: {stats['file_types']}")
