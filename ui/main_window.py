"""
主窗口UI
"""
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QProgressBar,
    QLabel, QTextEdit, QSplitter, QHeaderView, QCheckBox,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
import config

# 导入核心模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.file_scanner import FileScanner
from core.ai_analyzer import AIAnalyzer
from core.file_manager import FileManager


class ScanThread(QThread):
    """文件扫描线程"""
    progress = pyqtSignal(int, int, str)  # current, total, path
    finished = pyqtSignal(list, dict)  # files, statistics

    def __init__(self, scanner):
        super().__init__()
        self.scanner = scanner

    def run(self):
        def progress_callback(current, total, path):
            self.progress.emit(current, total, path)

        files = self.scanner.scan(progress_callback=progress_callback)
        stats = self.scanner.get_statistics()
        self.finished.emit(files, stats)


class AnalyzeThread(QThread):
    """AI分析线程"""
    finished = pyqtSignal(dict)  # result
    error = pyqtSignal(str)  # error message

    def __init__(self, analyzer, files):
        super().__init__()
        self.analyzer = analyzer
        self.files = files

    def run(self):
        try:
            result = self.analyzer.analyze_files(self.files)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ExecuteThread(QThread):
    """执行操作线程"""
    progress = pyqtSignal(int, int, str, str)  # current, total, action, path
    finished = pyqtSignal(dict)  # results

    def __init__(self, manager, suggestions):
        super().__init__()
        self.manager = manager
        self.suggestions = suggestions

    def run(self):
        def progress_callback(current, total, action, path):
            self.progress.emit(current, total, action, path)

        results = self.manager.execute_suggestions(
            self.suggestions,
            progress_callback=progress_callback
        )
        self.finished.emit(results)


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.scanner = FileScanner()
        self.analyzer = AIAnalyzer()
        self.manager = FileManager()

        self.scanned_files = []
        self.ai_suggestions = []

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 顶部控制区
        control_layout = QHBoxLayout()

        self.scan_btn = QPushButton("开始扫描")
        self.scan_btn.clicked.connect(self.start_scan)
        control_layout.addWidget(self.scan_btn)

        self.analyze_btn = QPushButton("AI分析")
        self.analyze_btn.clicked.connect(self.start_analyze)
        self.analyze_btn.setEnabled(False)
        control_layout.addWidget(self.analyze_btn)

        self.execute_btn = QPushButton("执行操作")
        self.execute_btn.clicked.connect(self.execute_operations)
        self.execute_btn.setEnabled(False)
        control_layout.addWidget(self.execute_btn)

        control_layout.addStretch()

        self.stats_label = QLabel("准备扫描...")
        control_layout.addWidget(self.stats_label)

        main_layout.addLayout(control_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        main_layout.addWidget(self.progress_label)

        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：文件列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        files_label = QLabel("扫描到的文件:")
        left_layout.addWidget(files_label)

        self.files_table = QTableWidget()
        self.files_table.setColumnCount(5)
        self.files_table.setHorizontalHeaderLabels(
            ["文件名", "大小(MB)", "修改时间", "路径", "选择"]
        )
        self.files_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.files_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        left_layout.addWidget(self.files_table)

        splitter.addWidget(left_widget)

        # 右侧：AI建议
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        suggestions_label = QLabel("AI建议:")
        right_layout.addWidget(suggestions_label)

        self.suggestions_table = QTableWidget()
        self.suggestions_table.setColumnCount(5)
        self.suggestions_table.setHorizontalHeaderLabels(
            ["文件", "操作", "分类", "理由", "置信度"]
        )
        self.suggestions_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.suggestions_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        right_layout.addWidget(self.suggestions_table)

        splitter.addWidget(right_widget)

        main_layout.addWidget(splitter)

        # 底部日志区
        log_label = QLabel("日志:")
        main_layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        main_layout.addWidget(self.log_text)

    def log(self, message: str):
        """添加日志"""
        self.log_text.append(message)

    def start_scan(self):
        """开始扫描"""
        self.log("开始扫描文件...")
        self.scan_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)

        self.scan_thread = ScanThread(self.scanner)
        self.scan_thread.progress.connect(self.on_scan_progress)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.start()

    def on_scan_progress(self, current: int, total: int, path: str):
        """扫描进度更新"""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            self.progress_label.setText(f"扫描中: {current}/{total} - {os.path.basename(path)}")

    def on_scan_finished(self, files: list, stats: dict):
        """扫描完成"""
        self.scanned_files = files
        self.log(f"扫描完成！共找到 {stats['total_files']} 个文件，总大小 {stats['total_size_mb']} MB")

        self.stats_label.setText(
            f"文件: {stats['total_files']} | 大小: {stats['total_size_mb']} MB"
        )

        # 显示文件列表
        self.display_files(files)

        self.scan_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

    def display_files(self, files: list):
        """显示文件列表"""
        self.files_table.setRowCount(len(files))

        for i, file_info in enumerate(files):
            # 文件名
            self.files_table.setItem(i, 0, QTableWidgetItem(file_info.name))

            # 大小
            self.files_table.setItem(i, 1, QTableWidgetItem(str(file_info.size_mb)))

            # 修改时间
            self.files_table.setItem(
                i, 2, QTableWidgetItem(file_info.modified_time.strftime('%Y-%m-%d %H:%M'))
            )

            # 路径
            self.files_table.setItem(i, 3, QTableWidgetItem(file_info.path))

            # 选择框
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.addWidget(checkbox)
            cell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            self.files_table.setCellWidget(i, 4, cell_widget)

    def start_analyze(self):
        """开始AI分析"""
        # 获取选中的文件
        selected_files = []
        for i in range(self.files_table.rowCount()):
            checkbox_widget = self.files_table.cellWidget(i, 4)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_files.append(self.scanned_files[i])

        if not selected_files:
            QMessageBox.warning(self, "警告", "请至少选择一个文件进行分析！")
            return

        self.log(f"开始AI分析 {len(selected_files)} 个文件...")
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # 不确定进度
        self.progress_label.setText("AI分析中，请稍候...")
        self.progress_label.setVisible(True)

        # 转换为字典格式
        files_data = [f.to_dict() for f in selected_files]

        self.analyze_thread = AnalyzeThread(self.analyzer, files_data)
        self.analyze_thread.finished.connect(self.on_analyze_finished)
        self.analyze_thread.error.connect(self.on_analyze_error)
        self.analyze_thread.start()

    def on_analyze_finished(self, result: dict):
        """AI分析完成"""
        self.ai_suggestions = result.get('suggestions', [])
        self.log(f"AI分析完成！生成了 {len(self.ai_suggestions)} 条建议")

        # 显示建议
        self.display_suggestions(self.ai_suggestions)

        self.analyze_btn.setEnabled(True)
        self.execute_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

    def on_analyze_error(self, error: str):
        """AI分析出错"""
        self.log(f"AI分析失败: {error}")
        QMessageBox.critical(self, "错误", f"AI分析失败:\n{error}")
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

    def display_suggestions(self, suggestions: list):
        """显示AI建议"""
        self.suggestions_table.setRowCount(len(suggestions))

        for i, suggestion in enumerate(suggestions):
            file_path = suggestion.get('file_path', '')
            file_name = os.path.basename(file_path)

            # 文件名
            self.suggestions_table.setItem(i, 0, QTableWidgetItem(file_name))

            # 操作
            action = suggestion.get('action', 'keep')
            action_item = QTableWidgetItem(self._translate_action(action))
            if action == 'delete':
                action_item.setBackground(QColor(255, 200, 200))
            elif action == 'move':
                action_item.setBackground(QColor(200, 255, 200))
            self.suggestions_table.setItem(i, 1, action_item)

            # 分类
            self.suggestions_table.setItem(
                i, 2, QTableWidgetItem(suggestion.get('category', ''))
            )

            # 理由
            self.suggestions_table.setItem(
                i, 3, QTableWidgetItem(suggestion.get('reason', ''))
            )

            # 置信度
            confidence = suggestion.get('confidence', 0)
            self.suggestions_table.setItem(
                i, 4, QTableWidgetItem(f"{confidence:.2f}")
            )

    def _translate_action(self, action: str) -> str:
        """翻译操作类型"""
        translations = {
            'delete': '删除',
            'move': '移动',
            'keep': '保留'
        }
        return translations.get(action, action)

    def execute_operations(self):
        """执行操作"""
        if not self.ai_suggestions:
            QMessageBox.warning(self, "警告", "没有可执行的操作！")
            return

        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认执行",
            f"即将执行 {len(self.ai_suggestions)} 个操作，是否继续？\n"
            f"备份功能: {'开启' if config.ENABLE_BACKUP else '关闭'}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        self.log("开始执行操作...")
        self.execute_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(100)
        self.progress_label.setVisible(True)

        self.execute_thread = ExecuteThread(self.manager, self.ai_suggestions)
        self.execute_thread.progress.connect(self.on_execute_progress)
        self.execute_thread.finished.connect(self.on_execute_finished)
        self.execute_thread.start()

    def on_execute_progress(self, current: int, total: int, action: str, path: str):
        """执行进度更新"""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            self.progress_label.setText(
                f"执行中: {current}/{total} - {action} {os.path.basename(path)}"
            )

    def on_execute_finished(self, results: dict):
        """执行完成"""
        self.log(
            f"执行完成！\n"
            f"删除: {results['deleted_count']} 个文件\n"
            f"移动: {results['moved_count']} 个文件\n"
            f"保留: {results['kept_count']} 个文件\n"
            f"失败: {len(results['failed'])} 个\n"
            f"释放空间: {results['freed_space_mb']} MB"
        )

        # 显示详细结果
        message = (
            f"操作完成！\n\n"
            f"删除: {results['deleted_count']} 个文件\n"
            f"移动: {results['moved_count']} 个文件\n"
            f"释放空间: {results['freed_space_mb']} MB\n"
        )

        if results['failed']:
            message += f"\n失败: {len(results['failed'])} 个文件"

        QMessageBox.information(self, "完成", message)

        self.execute_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

        # 重新扫描
        self.start_scan()
