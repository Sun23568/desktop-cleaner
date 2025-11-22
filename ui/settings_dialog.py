"""
设置对话框
允许用户配置AI提供商和相关参数
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QGroupBox,
    QSpinBox, QCheckBox, QMessageBox, QFormLayout,
    QWidget, QStyledItemDelegate, QStyleOptionViewItem, QStyle
)
from PyQt6.QtCore import Qt, QModelIndex, QRect, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QPainterPath, QPalette
from core.user_config import get_config_manager
import os
import tempfile


class CustomComboBox(QComboBox):
    """自定义ComboBox，修复弹出位置问题"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def showPopup(self):
        """重写showPopup，确保列表显示在ComboBox下方"""
        # 先调用父类方法显示弹出窗口
        super().showPopup()

        # 获取弹出窗口
        popup = self.view().parentWidget()
        if popup:
            # 计算ComboBox在屏幕上的位置
            combo_pos = self.mapToGlobal(self.rect().bottomLeft())

            # 设置弹出窗口的位置到ComboBox正下方
            popup.move(combo_pos.x(), combo_pos.y())

            # 确保弹出窗口的宽度与ComboBox一致
            popup.setMinimumWidth(self.width())

        # 延迟滚动到顶部
        QTimer.singleShot(0, self._scroll_to_top)

    def _scroll_to_top(self):
        """滚动到列表顶部"""
        view = self.view()
        if view and view.model() and view.model().rowCount() > 0:
            # 滚动到第一项
            first_index = view.model().index(0, 0)
            view.scrollTo(first_index, view.ScrollHint.PositionAtTop)


class ComboBoxItemDelegate(QStyledItemDelegate):
    """自定义下拉框项目委托，用于绘制 hover 效果"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        """自定义绘制下拉项"""
        painter.save()

        # 获取项目矩形
        rect = option.rect

        # 根据状态设置颜色
        if option.state & QStyle.StateFlag.State_Selected:
            # 选中状态
            if option.state & QStyle.StateFlag.State_MouseOver:
                # 选中且鼠标悬浮 - 深蓝色
                bg_color = QColor("#4a7a97")
            else:
                # 仅选中 - 蓝色
                bg_color = QColor("#5b8ba8")
            text_color = QColor("#ffffff")
        elif option.state & QStyle.StateFlag.State_MouseOver:
            # 仅鼠标悬浮 - 浅蓝色
            bg_color = QColor("#d5e8f0")
            text_color = QColor("#000000")
        else:
            # 默认状态 - 白色
            bg_color = QColor("#ffffff")
            text_color = QColor("#2c3e50")

        # 绘制背景 - 左右留边距，上下填满
        bg_rect = rect.adjusted(4, 0, -4, 0)  # 仅左右各4px边距，上下填满
        painter.fillRect(bg_rect, bg_color)

        # 绘制文字
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if text:
            painter.setPen(text_color)
            text_rect = rect.adjusted(12, 0, -12, 0)  # 左右各留12px边距
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)

        painter.restore()

    def sizeHint(self, option, index):
        """设置项目大小"""
        size = super().sizeHint(option, index)
        size.setHeight(34)  # 设置高度为34px
        return size


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = get_config_manager()
        self.arrow_icons = {}
        self.create_modern_arrow_icons()
        self.init_ui()
        self.load_current_config()

    def create_modern_arrow_icons(self):
        """创建现代化的箭头图标和对勾图标"""
        # 创建临时目录存放图标
        temp_dir = tempfile.gettempdir()

        # 向下箭头（现代化设计）
        down_pixmap = QPixmap(16, 16)
        down_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(down_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制圆润的向下箭头
        path = QPainterPath()
        path.moveTo(3, 5)
        path.lineTo(8, 10)
        path.lineTo(13, 5)

        pen = QPen(QColor(102, 102, 102), 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)
        painter.end()

        down_path = os.path.join(temp_dir, 'arrow_down.png')
        down_pixmap.save(down_path)
        self.arrow_icons['down'] = down_path

        # 向上箭头
        up_pixmap = QPixmap(16, 16)
        up_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(up_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.moveTo(3, 11)
        path.lineTo(8, 6)
        path.lineTo(13, 11)

        painter.setPen(pen)
        painter.drawPath(path)
        painter.end()

        up_path = os.path.join(temp_dir, 'arrow_up.png')
        up_pixmap.save(up_path)
        self.arrow_icons['up'] = up_path

        # 对勾图标（用于复选框）
        check_pixmap = QPixmap(20, 20)
        check_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(check_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制对勾
        path = QPainterPath()
        path.moveTo(4, 10)
        path.lineTo(8, 14)
        path.lineTo(16, 6)

        pen = QPen(QColor(255, 255, 255), 2.5)  # 白色对勾
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)
        painter.end()

        check_path = os.path.join(temp_dir, 'checkmark.png')
        check_pixmap.save(check_path)
        self.arrow_icons['checkmark'] = check_path

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("设置")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # ========== AI提供商选择 ==========
        provider_group = QGroupBox("AI提供商")
        provider_layout = QFormLayout()

        self.provider_combo = CustomComboBox()
        self.provider_combo.addItem("通义千问 (需要API Key)", "tongyi")
        self.provider_combo.addItem("规则引擎 (完全离线)", "rule_based")
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        provider_layout.addRow("选择引擎:", self.provider_combo)

        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)

        # ========== 通义千问配置 ==========
        self.tongyi_group = QGroupBox("通义千问配置")
        tongyi_layout = QFormLayout()

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("请输入你的通义千问API Key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)

        # 显示/隐藏密码按钮
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(self.api_key_input)

        self.show_key_btn = QPushButton("显示")
        self.show_key_btn.setMaximumWidth(60)
        self.show_key_btn.setCheckable(True)
        self.show_key_btn.toggled.connect(self.toggle_api_key_visibility)
        api_key_layout.addWidget(self.show_key_btn)

        api_key_widget = QWidget()
        api_key_widget.setLayout(api_key_layout)
        tongyi_layout.addRow("API Key:", api_key_widget)

        self.model_combo = CustomComboBox()
        self.model_combo.addItems([
            "qwen-plus (推荐)",
            "qwen-max (最强)",
            "qwen-turbo (快速)",
            "qwen3-coder-plus (代码专用)"
        ])
        tongyi_layout.addRow("模型:", self.model_combo)

        # API Key获取提示
        tip_label = QLabel('<a href="https://dashscope.aliyun.com/">点击这里获取API Key</a>')
        tip_label.setOpenExternalLinks(True)
        tip_label.setStyleSheet("color: #6b9ac4; font-size: 12px;")
        tongyi_layout.addRow("", tip_label)

        self.tongyi_group.setLayout(tongyi_layout)
        layout.addWidget(self.tongyi_group)

        # ========== 规则引擎配置 ==========
        self.rule_group = QGroupBox("规则引擎配置")
        rule_layout = QFormLayout()

        self.old_file_days_spin = QSpinBox()
        self.old_file_days_spin.setRange(1, 365)
        self.old_file_days_spin.setSuffix(" 天")
        self.old_file_days_spin.setValue(90)
        rule_layout.addRow("旧文件阈值:", self.old_file_days_spin)

        self.temp_file_days_spin = QSpinBox()
        self.temp_file_days_spin.setRange(1, 90)
        self.temp_file_days_spin.setSuffix(" 天")
        self.temp_file_days_spin.setValue(7)
        rule_layout.addRow("临时文件阈值:", self.temp_file_days_spin)

        self.rule_group.setLayout(rule_layout)
        layout.addWidget(self.rule_group)

        # ========== 文件过滤配置 ==========
        filter_group = QGroupBox("文件过滤配置")
        filter_layout = QFormLayout()

        self.ignore_extensions_input = QLineEdit()
        self.ignore_extensions_input.setPlaceholderText("例如: .ini, .sys, .dll, .exe")
        self.ignore_extensions_input.setToolTip("输入要忽略的文件扩展名，用逗号分隔。例如: .ini, .sys, .dll, .exe")
        filter_layout.addRow("忽略扩展名:", self.ignore_extensions_input)

        tip_label2 = QLabel("提示: 扫描时会自动跳过这些类型的文件")
        tip_label2.setStyleSheet("color: #666; font-size: 11px;")
        filter_layout.addRow("", tip_label2)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # ========== 高级设置 ==========
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QFormLayout()

        self.fallback_checkbox = QCheckBox("启用自动降级")
        self.fallback_checkbox.setChecked(True)
        self.fallback_checkbox.setToolTip("当AI分析失败时，自动切换到规则引擎")
        advanced_layout.addRow("", self.fallback_checkbox)

        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(5, 50)
        self.batch_size_spin.setValue(10)
        self.batch_size_spin.setToolTip("每批次分析的文件数量")
        advanced_layout.addRow("批次大小:", self.batch_size_spin)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(30, 300)
        self.timeout_spin.setSuffix(" 秒")
        self.timeout_spin.setValue(120)
        advanced_layout.addRow("超时时间:", self.timeout_spin)

        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)

        # ========== 按钮 ==========
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.test_btn = QPushButton("测试连接")
        self.test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_btn)

        self.reset_btn = QPushButton("恢复默认")
        self.reset_btn.clicked.connect(self.reset_to_default)
        button_layout.addWidget(self.reset_btn)

        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        # 应用样式
        self.apply_style()

        # 为所有ComboBox设置下拉列表样式
        self.setup_combobox_styles()

        # 为复选框设置对勾图标
        self.fallback_checkbox.setStyleSheet(self.get_checkbox_style())

    def setup_combobox_styles(self):
        """为所有ComboBox设置下拉列表的样式 - 使用自定义委托"""
        from PyQt6.QtCore import QMargins

        # 创建自定义委托
        delegate = ComboBoxItemDelegate(self)

        # 为所有ComboBox应用委托和样式
        for combo in self.findChildren(QComboBox):
            # 获取下拉列表视图
            list_view = combo.view()

            # 设置自定义委托（关键！这会完全控制项目的绘制）
            list_view.setItemDelegate(delegate)

            # 启用鼠标跟踪（必须！否则hover状态不会触发）
            list_view.setMouseTracking(True)

            # 设置内容边距为0（关键！确保列表从顶部开始）
            list_view.setContentsMargins(0, 0, 0, 0)
            list_view.setViewportMargins(0, 0, 0, 0)

            # 设置间距为0
            list_view.setSpacing(0)

            # 设置框架宽度为0
            list_view.setFrameShape(list_view.Shape.NoFrame)

            # 设置列表容器的样式 - 移除padding避免位置偏移
            list_view_style = """
                QListView {
                    border: 2px solid #e1e8ed;
                    border-radius: 8px;
                    background-color: white;
                    outline: none;
                    padding: 0px;
                    margin: 0px;
                }
                QListView::item:first {
                    margin-top: 0px;
                    padding-top: 0px;
                }
            """
            list_view.setStyleSheet(list_view_style)

            # 设置视图位置模式，确保从顶部开始
            list_view.setVerticalScrollMode(list_view.ScrollMode.ScrollPerPixel)

            # 确保第一个项目可见
            if list_view.model() and list_view.model().rowCount() > 0:
                list_view.scrollToTop()

    def get_checkbox_style(self):
        """获取复选框样式（包含对勾图标）"""
        # 转换Windows路径为URL格式
        checkmark_url = self.arrow_icons['checkmark'].replace('\\', '/')

        return f"""
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 5px;
                border: 2px solid #e1e8ed;
                background-color: white;
            }}
            QCheckBox::indicator:hover {{
                border-color: #5b8ba8;
                background-color: #f8fafb;
            }}
            QCheckBox::indicator:checked {{
                background-color: #5b8ba8;
                border-color: #5b8ba8;
                image: url({checkmark_url});
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: #4a7a97;
                border-color: #4a7a97;
            }}
            QCheckBox {{
                spacing: 8px;
                color: #2c3e50;
            }}
        """

    def apply_style(self):
        """应用样式 - 现代化设计"""
        # 转换Windows路径为URL格式
        down_arrow_url = self.arrow_icons['down'].replace('\\', '/')
        up_arrow_url = self.arrow_icons['up'].replace('\\', '/')

        self.setStyleSheet(f"""
            QDialog {{
                background-color: #f5f7fa;
            }}
            QGroupBox {{
                font-weight: 600;
                font-size: 14px;
                border: 2px solid #e1e8ed;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #2c3e50;
            }}
            QPushButton {{
                background-color: #5b8ba8;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #4a7a97;
            }}
            QPushButton:pressed {{
                background-color: #3a6a85;
            }}
            QPushButton#test_btn {{
                background-color: #6b9ac4;
            }}
            QPushButton#reset_btn {{
                background-color: #95a5a6;
            }}
            QPushButton#reset_btn:hover {{
                background-color: #7f8c8d;
            }}
            QLineEdit {{
                padding: 8px 12px;
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
            }}
            QLineEdit:hover {{
                border: 2px solid #bdc3c7;
            }}
            QLineEdit:focus {{
                border: 2px solid #5b8ba8;
                background-color: #f8fafb;
            }}

            /* ========== 现代化下拉框样式 ========== */
            QComboBox {{
                padding: 8px 12px;
                padding-right: 35px;
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: white;
                min-height: 28px;
                font-size: 13px;
            }}
            QComboBox:hover {{
                border: 2px solid #bdc3c7;
                background-color: #f8fafb;
            }}
            QComboBox:focus {{
                border: 2px solid #5b8ba8;
                background-color: white;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 30px;
                border-left: none;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
            QComboBox::drop-down:hover {{
                background-color: #ecf0f1;
            }}
            QComboBox::down-arrow {{
                image: url({down_arrow_url});
                width: 16px;
                height: 16px;
            }}
            QComboBox QAbstractItemView {{
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                background-color: white;
                outline: none;
                padding: 4px;
            }}
            QComboBox QAbstractItemView::item {{
                height: 32px;
                padding-left: 12px;
                padding-right: 12px;
                border: none;
            }}
            /* 注意：这里不设置item的background和color，让Qt自己处理 */

            /* ========== 现代化数字选择框样式 ========== */
            QSpinBox {{
                padding: 8px 12px;
                padding-right: 25px;
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                background-color: white;
                min-height: 28px;
                font-size: 13px;
            }}
            QSpinBox:hover {{
                border: 2px solid #bdc3c7;
                background-color: #f8fafb;
            }}
            QSpinBox:focus {{
                border: 2px solid #5b8ba8;
                background-color: white;
            }}
            QSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 22px;
                border: none;
                border-top-right-radius: 4px;
                background-color: transparent;
            }}
            QSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 22px;
                border: none;
                border-bottom-right-radius: 4px;
                background-color: transparent;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: #ecf0f1;
            }}
            QSpinBox::up-arrow {{
                image: url({up_arrow_url});
                width: 12px;
                height: 12px;
            }}
            QSpinBox::down-arrow {{
                image: url({down_arrow_url});
                width: 12px;
                height: 12px;
            }}

            /* ========== Label 样式 ========== */
            QLabel {{
                color: #2c3e50;
            }}
        """)

    def load_current_config(self):
        """加载当前配置"""
        config = self.config_manager.get_all()

        # 设置提供商
        provider = config.get('ai_provider', 'tongyi')
        index = self.provider_combo.findData(provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)

        # 设置API Key
        api_key = config.get('tongyi_api_key', '')
        self.api_key_input.setText(api_key)

        # 设置模型
        model = config.get('tongyi_model', 'qwen-plus')
        for i in range(self.model_combo.count()):
            if model in self.model_combo.itemText(i).lower():
                self.model_combo.setCurrentIndex(i)
                break

        # 设置规则引擎参数
        self.old_file_days_spin.setValue(config.get('rule_old_file_days', 90))
        self.temp_file_days_spin.setValue(config.get('rule_temp_file_days', 7))

        # 设置高级选项
        self.fallback_checkbox.setChecked(config.get('ai_fallback', True))
        self.batch_size_spin.setValue(config.get('max_files_per_request', 10))
        self.timeout_spin.setValue(config.get('ai_timeout', 120))

        # 设置文件过滤配置
        ignore_extensions = config.get('ignore_extensions', ['.ini', '.sys', '.dll', '.exe'])
        # 将列表转换为逗号分隔的字符串
        self.ignore_extensions_input.setText(', '.join(ignore_extensions))

        # 更新UI显示
        self.on_provider_changed()

    def on_provider_changed(self):
        """当提供商改变时更新UI"""
        provider = self.provider_combo.currentData()

        # 根据选择的提供商显示/隐藏相应的配置组
        if provider == 'tongyi':
            self.tongyi_group.setVisible(True)
            self.rule_group.setVisible(False)
            self.test_btn.setVisible(True)
            self.test_btn.setText("测试API Key")
        elif provider == 'rule_based':
            self.tongyi_group.setVisible(False)
            self.rule_group.setVisible(True)
            self.test_btn.setVisible(False)

    def toggle_api_key_visibility(self, checked):
        """切换API Key显示/隐藏"""
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setText("隐藏")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("显示")

    def test_connection(self):
        """测试API连接"""
        provider = self.provider_combo.currentData()

        if provider == 'tongyi':
            api_key = self.api_key_input.text().strip()

            if not api_key:
                QMessageBox.warning(self, "警告", "请先输入API Key")
                return

            # 简单验证API Key格式
            if not api_key.startswith('sk-'):
                QMessageBox.warning(self, "警告", "API Key格式不正确，应该以 'sk-' 开头")
                return

            QMessageBox.information(
                self,
                "提示",
                "API Key格式正确！\n\n"
                "具体连接测试将在实际分析时进行。\n"
                "如果API Key有效，分析将正常进行。"
            )

    def reset_to_default(self):
        """恢复默认设置"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要恢复默认设置吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.reset_to_default()
            self.load_current_config()
            QMessageBox.information(self, "成功", "已恢复默认设置")

    def save_settings(self):
        """保存设置"""
        provider = self.provider_combo.currentData()

        # 如果选择通义千问但没有API Key，提示用户
        if provider == 'tongyi':
            api_key = self.api_key_input.text().strip()
            if not api_key:
                reply = QMessageBox.question(
                    self,
                    "提示",
                    "你还没有填写API Key，\n"
                    "这样将无法使用通义千问分析。\n\n"
                    "建议：\n"
                    "1. 填写API Key后再保存\n"
                    "2. 或者切换到'规则引擎'（完全离线）\n\n"
                    "是否仍要保存？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return

        # 解析过滤扩展名
        ignore_ext_text = self.ignore_extensions_input.text().strip()
        ignore_extensions = []
        if ignore_ext_text:
            # 分割并清理每个扩展名
            ignore_extensions = [
                ext.strip().lower() if ext.strip().startswith('.') else '.' + ext.strip().lower()
                for ext in ignore_ext_text.split(',')
                if ext.strip()
            ]

        # 收集配置
        config = {
            'ai_provider': provider,
            'tongyi_api_key': self.api_key_input.text().strip(),
            'tongyi_model': self.model_combo.currentText().split()[0],  # 提取模型名
            'ai_fallback': self.fallback_checkbox.isChecked(),
            'rule_old_file_days': self.old_file_days_spin.value(),
            'rule_temp_file_days': self.temp_file_days_spin.value(),
            'max_files_per_request': self.batch_size_spin.value(),
            'ai_timeout': self.timeout_spin.value(),
            'ignore_extensions': ignore_extensions,
        }

        # 保存配置
        if self.config_manager.save_config(config):
            QMessageBox.information(
                self,
                "成功",
                f"设置已保存！\n\n"
                f"当前引擎: {self.provider_combo.currentText()}\n"
                f"配置文件: {self.config_manager.config_file}"
            )
            self.accept()
        else:
            QMessageBox.critical(self, "错误", "保存设置失败")


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.exec()
    sys.exit()
