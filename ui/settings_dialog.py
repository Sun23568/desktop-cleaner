"""
设置对话框
允许用户配置AI提供商和相关参数
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QGroupBox,
    QSpinBox, QCheckBox, QMessageBox, QFormLayout,
    QWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor
from core.user_config import get_config_manager


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = get_config_manager()
        self.init_ui()
        self.load_current_config()

    @staticmethod
    def create_checkmark_icon():
        """创建对勾图标"""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制对勾
        pen = QPen(QColor(255, 255, 255), 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        # 绘制对勾路径
        from PyQt6.QtGui import QPainterPath
        path = QPainterPath()
        path.moveTo(4, 10)
        path.lineTo(8, 14)
        path.lineTo(16, 6)
        painter.drawPath(path)

        painter.end()
        return QIcon(pixmap)

    @staticmethod
    def get_arrow_svg_base64(direction='down'):
        """获取箭头SVG的base64编码"""
        import base64
        if direction == 'down':
            svg = '''<svg width="12" height="12" viewBox="0 0 12 12" xmlns="http://www.w3.org/2000/svg">
                <path d="M2 4 L6 8 L10 4" stroke="#666" stroke-width="1.5"
                      stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            </svg>'''
        else:  # up
            svg = '''<svg width="12" height="12" viewBox="0 0 12 12" xmlns="http://www.w3.org/2000/svg">
                <path d="M2 8 L6 4 L10 8" stroke="#666" stroke-width="1.5"
                      stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            </svg>'''
        return base64.b64encode(svg.encode('utf-8')).decode('utf-8')

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

        self.provider_combo = QComboBox()
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
        tongyi_layout.addRow("API Key:", self.api_key_input)

        # 显示/隐藏密码按钮
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(self.api_key_input)

        self.show_key_btn = QPushButton("👁")
        self.show_key_btn.setMaximumWidth(40)
        self.show_key_btn.setCheckable(True)
        self.show_key_btn.toggled.connect(self.toggle_api_key_visibility)
        api_key_layout.addWidget(self.show_key_btn)

        api_key_widget = QWidget()
        api_key_widget.setLayout(api_key_layout)
        tongyi_layout.addRow("API Key:", api_key_widget)

        self.model_combo = QComboBox()
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

        # 为复选框设置对勾图标
        self.fallback_checkbox.setStyleSheet(self.get_checkbox_style())

    def get_checkbox_style(self):
        """获取复选框样式（包含对勾图标）"""
        # 使用data URI内嵌SVG对勾图标
        checkmark_svg = '''
        <svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 10 L8 14 L16 6" stroke="white" stroke-width="2.5"
                  stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </svg>
        '''
        import base64
        svg_bytes = checkmark_svg.encode('utf-8')
        svg_base64 = base64.b64encode(svg_bytes).decode('utf-8')

        return f"""
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #dcdcdc;
                background-color: white;
            }}
            QCheckBox::indicator:hover {{
                border-color: #5b8ba8;
            }}
            QCheckBox::indicator:checked {{
                background-color: #5b8ba8;
                border-color: #5b8ba8;
                image: url(data:image/svg+xml;base64,{svg_base64});
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: #4a7a97;
                border-color: #4a7a97;
            }}
        """

    def apply_style(self):
        """应用样式"""
        # 获取箭头图标
        down_arrow = self.get_arrow_svg_base64('down')
        up_arrow = self.get_arrow_svg_base64('up')

        self.setStyleSheet(f"""
            QDialog {{
                background-color: #fafafa;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #dcdcdc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QPushButton {{
                background-color: #5b8ba8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: 500;
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
                background-color: #999;
            }}
            QLineEdit {{
                padding: 6px;
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                background-color: white;
            }}

            /* ========== 下拉框样式优化 ========== */
            QComboBox {{
                padding: 6px 30px 6px 10px;
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                background-color: white;
                min-height: 25px;
            }}
            QComboBox:hover {{
                border: 1px solid #5b8ba8;
            }}
            QComboBox:focus {{
                border: 2px solid #5b8ba8;
            }}
            /* 下拉箭头区域 */
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid #e0e0e0;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }}
            QComboBox::drop-down:hover {{
                background-color: #f0f8fc;
            }}
            /* 下拉箭头 */
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
                image: url(data:image/svg+xml;base64,{down_arrow});
            }}
            /* 下拉列表 */
            QComboBox QAbstractItemView {{
                border: 1px solid #dcdcdc;
                background-color: white;
                selection-background-color: #e8f4f8;
                selection-color: #333;
                outline: none;
                padding: 2px;
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 30px;
                padding: 5px 10px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: #f0f8fc;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: #e8f4f8;
                color: #333;
            }}

            /* ========== 数字选择框样式优化 ========== */
            QSpinBox {{
                padding: 6px 25px 6px 10px;
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                background-color: white;
                min-height: 25px;
            }}
            QSpinBox:hover {{
                border: 1px solid #5b8ba8;
            }}
            QSpinBox:focus {{
                border: 2px solid #5b8ba8;
            }}
            /* 上下按钮容器 */
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 20px;
                background-color: transparent;
                border: none;
                border-left: 1px solid #e0e0e0;
            }}
            QSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                border-top-right-radius: 4px;
            }}
            QSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                border-bottom-right-radius: 4px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: #f0f8fc;
            }}
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {{
                background-color: #e8f4f8;
            }}
            /* 上下箭头 */
            QSpinBox::up-arrow {{
                width: 10px;
                height: 10px;
                image: url(data:image/svg+xml;base64,{up_arrow});
            }}
            QSpinBox::down-arrow {{
                width: 10px;
                height: 10px;
                image: url(data:image/svg+xml;base64,{down_arrow});
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
            self.show_key_btn.setText("🙈")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("👁")

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
