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
from PyQt6.QtGui import QColor, QPixmap, QPainter, QPen, QPainterPath
import config
import os
import tempfile

# 导入核心模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.file_scanner import FileScanner
from core.ai_analyzer import AIAnalyzer
from core.file_manager import FileManager
from core.user_config import get_config_manager
from ui.settings_dialog import SettingsDialog


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
    batch_progress = pyqtSignal(int, int, dict)  # current_batch, total_batches, batch_result
    finished = pyqtSignal(dict)  # result
    error = pyqtSignal(str)  # error message

    def __init__(self, analyzer, files):
        super().__init__()
        self.analyzer = analyzer
        self.files = files

    def run(self):
        try:
            # 批次进度回调函数
            def on_batch_progress(current_batch, total_batches, batch_result):
                self.batch_progress.emit(current_batch, total_batches, batch_result)

            # 调用分析，传入进度回调
            result = self.analyzer.analyze_files(self.files, progress_callback=on_batch_progress)
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
        self.config_manager = get_config_manager()
        self.scanner = FileScanner()
        self.analyzer = self.create_analyzer()
        self.manager = FileManager()

        self.scanned_files = []
        self.ai_suggestions = []

        # 创建对勾图标
        self.checkmark_icon_path = self.create_checkmark_icon()

        self.init_ui()
        self.update_window_title()

        # 首次运行检查
        self.check_first_run()

    def create_checkmark_icon(self):
        """创建对勾图标PNG文件"""
        temp_dir = tempfile.gettempdir()
        check_pixmap = QPixmap(18, 18)
        check_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(check_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制对勾（调整位置和大小以适配18x18）
        path = QPainterPath()
        path.moveTo(3, 9)
        path.lineTo(7, 13)
        path.lineTo(15, 5)

        pen = QPen(QColor(255, 255, 255), 2.2)  # 白色对勾
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)
        painter.end()

        check_path = os.path.join(temp_dir, 'main_checkmark.png')
        check_pixmap.save(check_path)
        return check_path

    def create_analyzer(self):
        """根据用户配置创建AI分析器"""
        provider_type = self.config_manager.get('ai_provider', 'tongyi')
        return AIAnalyzer(provider_type=provider_type)

    def update_window_title(self):
        """更新窗口标题，显示当前使用的AI引擎"""
        provider = self.config_manager.get('ai_provider', 'tongyi')
        provider_name = "通义千问" if provider == 'tongyi' else "规则引擎"
        self.setWindowTitle(f"{config.WINDOW_TITLE} - 当前引擎: {provider_name}")

    def check_first_run(self):
        """检查是否首次运行，如果是则提示配置"""
        provider = self.config_manager.get('ai_provider', 'tongyi')
        api_key = self.config_manager.get('tongyi_api_key', '')

        # 如果选择了通义千问但没有配置API Key
        if provider == 'tongyi' and not api_key:
            self.log("⚠️  检测到你还没有配置API Key")
            self.log("💡 提示：点击右上角的'⚙ 设置'按钮进行配置")
            self.log("   你可以选择：")
            self.log("   1. 通义千问（需要API Key，智能分析）")
            self.log("   2. 规则引擎（无需API Key，完全离线）")
            self.log("")

            # 弹出提示对话框
            reply = QMessageBox.question(
                self,
                "欢迎使用",
                "👋 欢迎使用智能桌面清理工具！\n\n"
                "检测到你还没有配置AI引擎，请选择：\n\n"
                "📌 通义千问（需要API Key）\n"
                "   • 智能分析，理解上下文\n"
                "   • 需要网络连接\n\n"
                "📌 规则引擎（无需API Key）\n"
                "   • 完全离线，快速\n"
                "   • 基于规则判断\n\n"
                "是否现在打开设置？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.open_settings()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        # 应用现代化样式
        self.apply_modern_style()

        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 顶部控制区
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)

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
        self.stats_label.setObjectName("stats_label")
        control_layout.addWidget(self.stats_label)

        # 设置按钮
        self.settings_btn = QPushButton("⚙ 设置")
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setToolTip("配置AI引擎和API Key")
        control_layout.addWidget(self.settings_btn)

        main_layout.addLayout(control_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        main_layout.addWidget(self.progress_label)

        # 分割器
        splitter = QSplitter(Qt.Orientation.Vertical)

        # 上部：文件列表
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)

        files_label = QLabel("📁 扫描到的文件")
        files_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2d5266; padding: 5px 0px;")
        top_layout.addWidget(files_label)

        self.files_table = QTableWidget()
        self.files_table.setColumnCount(5)
        self.files_table.setHorizontalHeaderLabels(
            ["文件名", "大小(KB)", "修改时间", "路径", "选择"]
        )
        self.files_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.files_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        # 设置默认行高，让表格更舒适，能完美容纳复选框
        self.files_table.verticalHeader().setDefaultSectionSize(40)
        self.files_table.verticalHeader().setMinimumSectionSize(40)
        top_layout.addWidget(self.files_table)

        splitter.addWidget(top_widget)

        # 下部：AI建议
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)

        suggestions_label = QLabel("🤖 AI建议")
        suggestions_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2d5266; padding: 5px 0px;")
        bottom_layout.addWidget(suggestions_label)

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
        # 设置默认行高，保持与文件表格一致
        self.suggestions_table.verticalHeader().setDefaultSectionSize(40)
        self.suggestions_table.verticalHeader().setMinimumSectionSize(40)
        bottom_layout.addWidget(self.suggestions_table)

        splitter.addWidget(bottom_widget)

        # 设置分割器的默认大小比例
        splitter.setSizes([400, 300])

        main_layout.addWidget(splitter)

        # 底部日志区
        log_label = QLabel("📝 运行日志")
        log_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2d5266; padding: 5px 0px;")
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
            name_item = QTableWidgetItem(file_info.name)
            name_item.setToolTip(f"文件名: {file_info.name}\n完整路径: {file_info.path}")
            self.files_table.setItem(i, 0, name_item)

            # 大小
            size_item = QTableWidgetItem(str(file_info.size_kb))
            size_item.setToolTip(f"文件大小: {file_info.size_kb} KB ({file_info.size_mb} MB)")
            self.files_table.setItem(i, 1, size_item)

            # 修改时间
            time_str = file_info.modified_time.strftime('%Y-%m-%d %H:%M')
            time_item = QTableWidgetItem(time_str)
            time_item.setToolTip(f"最后修改时间: {file_info.modified_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
            self.files_table.setItem(i, 2, time_item)

            # 路径
            path_item = QTableWidgetItem(file_info.path)
            path_item.setToolTip(f"完整路径:\n{file_info.path}")
            self.files_table.setItem(i, 3, path_item)

            # 选择框
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.setToolTip("勾选以包含在AI分析中")
            # 设置固定尺寸确保复选框不被拉伸，保持正方形
            checkbox.setFixedSize(18, 18)
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
        self.progress_bar.setMaximum(100)  # 确定进度（百分比）
        self.progress_bar.setValue(0)
        self.progress_label.setText("正在准备分析...")
        self.progress_label.setVisible(True)

        # 清空之前的建议
        self.ai_suggestions = []
        self.suggestions_table.setRowCount(0)

        # 转换为字典格式
        files_data = [f.to_dict() for f in selected_files]

        self.analyze_thread = AnalyzeThread(self.analyzer, files_data)
        self.analyze_thread.batch_progress.connect(self.on_batch_progress)  # 连接批次进度信号
        self.analyze_thread.finished.connect(self.on_analyze_finished)
        self.analyze_thread.error.connect(self.on_analyze_error)
        self.analyze_thread.start()

    def on_batch_progress(self, current_batch: int, total_batches: int, batch_result: dict):
        """批次处理进度更新"""
        # 更新进度条
        progress = int((current_batch / total_batches) * 100)
        self.progress_bar.setValue(progress)

        # 更新进度文本
        self.progress_label.setText(f"AI分析中: 批次 {current_batch}/{total_batches} ({progress}%)")

        # 获取批次建议并累加到总建议列表
        batch_suggestions = batch_result.get('suggestions', [])
        self.ai_suggestions.extend(batch_suggestions)

        # 实时更新建议表格
        self.display_suggestions(self.ai_suggestions)

        # 记录日志
        self.log(f"批次 {current_batch}/{total_batches} 完成，本批获得 {len(batch_suggestions)} 条建议")

    def on_analyze_finished(self, result: dict):
        """AI分析完成"""
        # ai_suggestions 已经在 on_batch_progress 中更新过了
        # 这里只做最终确认（防止没有批次的情况）
        if not self.ai_suggestions:
            self.ai_suggestions = result.get('suggestions', [])
            self.display_suggestions(self.ai_suggestions)

        self.log(f"✅ 所有批次分析完成！共生成 {len(self.ai_suggestions)} 条建议")

        self.analyze_btn.setEnabled(True)
        self.execute_btn.setEnabled(True if self.ai_suggestions else False)
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
            file_item = QTableWidgetItem(file_name)
            file_item.setToolTip(f"完整路径:\n{file_path}")
            self.suggestions_table.setItem(i, 0, file_item)

            # 操作
            action = suggestion.get('action', 'keep')
            action_item = QTableWidgetItem(self._translate_action(action))
            action_item.setToolTip(f"操作: {self._translate_action(action)}")
            if action == 'delete':
                action_item.setBackground(QColor(255, 220, 220))
            elif action == 'move':
                action_item.setBackground(QColor(220, 245, 220))
            self.suggestions_table.setItem(i, 1, action_item)

            # 分类
            category = suggestion.get('category', '')
            category_item = QTableWidgetItem(category)
            category_item.setToolTip(f"分类: {category}")
            self.suggestions_table.setItem(i, 2, category_item)

            # 理由
            reason = suggestion.get('reason', '')
            reason_item = QTableWidgetItem(reason)
            reason_item.setToolTip(f"详细理由:\n{reason}")
            self.suggestions_table.setItem(i, 3, reason_item)

            # 置信度
            confidence = suggestion.get('confidence', 0)
            confidence_item = QTableWidgetItem(f"{confidence:.2f}")
            confidence_item.setToolTip(f"AI置信度: {confidence:.2%}")
            self.suggestions_table.setItem(i, 4, confidence_item)

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

    def open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # 用户点击了保存，重新加载配置
            self.log("⚙️  设置已更新，重新初始化AI分析器...")

            # 重新创建analyzer
            self.analyzer = self.create_analyzer()

            # 更新窗口标题
            self.update_window_title()

            provider = self.config_manager.get('ai_provider', 'tongyi')
            provider_name = "通义千问" if provider == 'tongyi' else "规则引擎"
            self.log(f"✅ 当前使用: {provider_name}")

    def apply_modern_style(self):
        """应用现代化样式"""
        style = """
        /* 主窗口样式 */
        QMainWindow {
            background-color: #fafafa;
        }

        /* 中心部件 */
        QWidget {
            background-color: #fafafa;
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
            font-size: 13px;
        }

        /* 按钮样式 */
        QPushButton {
            background-color: #5b8ba8;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 500;
            min-width: 100px;
            font-size: 13px;
        }

        QPushButton:hover {
            background-color: #4a7a97;
        }

        QPushButton:pressed {
            background-color: #3a6a85;
        }

        QPushButton:disabled {
            background-color: #c8c8c8;
            color: #888888;
        }

        /* 标签样式 */
        QLabel {
            color: #424242;
            font-size: 13px;
            padding: 5px;
        }

        /* 统计标签 */
        QLabel#stats_label {
            background-color: white;
            border: 1px solid #c0c0c0;
            border-radius: 6px;
            padding: 8px 15px;
            font-weight: 500;
            color: #2d5266;
        }

        /* 表格样式 */
        QTableWidget {
            background-color: white;
            border: 1px solid #dcdcdc;
            border-radius: 8px;
            gridline-color: #f0f0f0;
            selection-background-color: #e8f0f7;
            selection-color: #424242;
        }

        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #f5f5f5;
        }

        QTableWidget::item:selected {
            background-color: #e8f0f7;
            color: #424242;
        }

        QHeaderView::section {
            background-color: #5b8ba8;
            color: #ffffff;
            padding: 10px;
            border: none;
            font-weight: 500;
            font-size: 13px;
        }

        QHeaderView::section:first {
            border-top-left-radius: 8px;
        }

        QHeaderView::section:last {
            border-top-right-radius: 8px;
        }

        /* 进度条样式 */
        QProgressBar {
            border: 1px solid #c0c0c0;
            border-radius: 8px;
            background-color: white;
            text-align: center;
            color: #2d5266;
            font-weight: 500;
            height: 25px;
        }

        QProgressBar::chunk {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #5b8ba8,
                stop:1 #7aa3ba
            );
            border-radius: 7px;
        }

        /* 文本编辑框（日志）样式 */
        QTextEdit {
            background-color: white;
            border: 1px solid #dcdcdc;
            border-radius: 8px;
            padding: 10px;
            color: #424242;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 12px;
        }

        /* 分割器样式 */
        QSplitter::handle {
            background-color: #d0d0d0;
            height: 2px;
        }

        QSplitter::handle:hover {
            background-color: #5b8ba8;
        }

        /* 复选框样式 */
        QCheckBox {
            spacing: 5px;
        }

        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            min-width: 18px;
            max-width: 18px;
            min-height: 18px;
            max-height: 18px;
            border: 2px solid #e1e8ed;
            border-radius: 4px;
            background-color: white;
        }

        QCheckBox::indicator:hover {
            border-color: #5b8ba8;
            background-color: #f8fafb;
        }

        QCheckBox::indicator:checked {
            background-color: #5b8ba8;
            border: none;
            image: url(CHECKMARK_URL_PLACEHOLDER);
        }

        QCheckBox::indicator:checked:hover {
            background-color: #4a7a97;
            border: none;
        }
        """

        # 替换对勾图标路径
        checkmark_url = self.checkmark_icon_path.replace('\\', '/')
        style = style.replace('CHECKMARK_URL_PLACEHOLDER', checkmark_url)

        self.setStyleSheet(style)
