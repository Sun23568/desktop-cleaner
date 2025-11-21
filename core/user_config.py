"""
用户配置管理模块
负责保存和加载用户的个性化配置
"""
import json
import os
from pathlib import Path
from typing import Dict, Any


class UserConfigManager:
    """用户配置管理器"""

    def __init__(self, config_file: str = None):
        """
        初始化配置管理器
        :param config_file: 配置文件路径，默认保存在用户目录
        """
        if config_file is None:
            # 默认保存在用户目录下的 .desktop-cleaner 文件夹
            config_dir = Path.home() / ".desktop-cleaner"
            config_dir.mkdir(exist_ok=True)
            self.config_file = config_dir / "user_config.json"
        else:
            self.config_file = Path(config_file)

        # 默认配置（从config.py读取）
        try:
            import config as default_config
            self.default_config = {
                'ai_provider': getattr(default_config, 'AI_PROVIDER', 'tongyi'),
                'tongyi_api_key': getattr(default_config, 'TONGYI_API_KEY', ''),
                'tongyi_model': getattr(default_config, 'TONGYI_MODEL', 'qwen-plus'),
                'ai_fallback': getattr(default_config, 'AI_FALLBACK_TO_RULES', True),
                'rule_old_file_days': getattr(default_config, 'RULE_OLD_FILE_DAYS', 90),
                'rule_temp_file_days': getattr(default_config, 'RULE_TEMP_FILE_DAYS', 7),
                'max_files_per_request': getattr(default_config, 'MAX_FILES_PER_REQUEST', 10),
                'ai_timeout': getattr(default_config, 'AI_TIMEOUT', 120),
            }
        except:
            # 如果无法导入config.py，使用硬编码默认值
            self.default_config = {
                'ai_provider': 'tongyi',
                'tongyi_api_key': '',
                'tongyi_model': 'qwen-plus',
                'ai_fallback': True,
                'rule_old_file_days': 90,
                'rule_temp_file_days': 7,
                'max_files_per_request': 10,
                'ai_timeout': 120,
            }

        # 加载配置
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        从文件加载配置
        :return: 配置字典
        """
        if not self.config_file.exists():
            return self.default_config.copy()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)

            # 合并默认配置和加载的配置
            config = self.default_config.copy()
            config.update(loaded_config)
            return config

        except Exception as e:
            print(f"⚠️  加载配置失败: {e}，使用默认配置")
            return self.default_config.copy()

    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """
        保存配置到文件
        :param config: 要保存的配置，如果为None则保存当前配置
        :return: 是否保存成功
        """
        if config is not None:
            self.config = config

        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            print(f"✅ 配置已保存到: {self.config_file}")
            return True

        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False

    def get(self, key: str, default=None):
        """获取配置项"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置项"""
        self.config[key] = value

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config.copy()

    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self.default_config.copy()
        self.save_config()

    def get_provider_config(self) -> Dict[str, Any]:
        """
        获取AI提供商所需的配置
        :return: 提供商配置字典
        """
        return {
            'api_key': self.config.get('tongyi_api_key', ''),
            'model': self.config.get('tongyi_model', 'qwen-plus'),
            'timeout': self.config.get('ai_timeout', 120),
            'max_retries': 3,
            'retry_delay': 5,
            'enable_detail_log': True,
            'old_file_days': self.config.get('rule_old_file_days', 90),
            'temp_file_days': self.config.get('rule_temp_file_days', 7),
        }


# 全局单例
_config_manager = None


def get_config_manager() -> UserConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = UserConfigManager()
    return _config_manager


if __name__ == '__main__':
    # 测试代码
    manager = UserConfigManager()

    print("当前配置:")
    print(json.dumps(manager.get_all(), indent=2, ensure_ascii=False))

    # 修改配置
    manager.set('ai_provider', 'rule_based')
    manager.set('tongyi_api_key', 'sk-test-key')
    manager.save_config()

    print("\n配置已保存")

    # 重新加载
    manager2 = UserConfigManager()
    print("\n重新加载的配置:")
    print(json.dumps(manager2.get_all(), indent=2, ensure_ascii=False))
