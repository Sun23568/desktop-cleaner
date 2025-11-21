"""
AI提供商工厂
根据配置创建对应的AI提供商
"""
from typing import Dict
from .base_provider import AIProvider
from .tongyi_provider import TongyiProvider
from .rule_based_provider import RuleBasedProvider


class AIProviderFactory:
    """AI提供商工厂类"""

    # 注册的提供商
    PROVIDERS = {
        'tongyi': TongyiProvider,
        'rule_based': RuleBasedProvider,
        # 可以继续添加其他提供商
        # 'openai': OpenAIProvider,
        # 'ollama': OllamaProvider,
    }

    @staticmethod
    def create_provider(provider_type: str, config: Dict = None) -> AIProvider:
        """
        创建AI提供商实例

        :param provider_type: 提供商类型 ('tongyi', 'rule_based', 'openai'等)
        :param config: 配置字典
        :return: AI提供商实例
        """
        provider_type = provider_type.lower()

        if provider_type not in AIProviderFactory.PROVIDERS:
            raise ValueError(
                f"不支持的AI提供商: {provider_type}。"
                f"支持的提供商: {', '.join(AIProviderFactory.PROVIDERS.keys())}"
            )

        provider_class = AIProviderFactory.PROVIDERS[provider_type]
        provider = provider_class(config)

        print(f"\n{'='*80}")
        print(f"🤖 AI提供商: {provider.get_provider_name()}")
        print(f"   类型: {provider_type}")
        print(f"   可用性: {'✅ 可用' if provider.is_available() else '❌ 不可用'}")
        print(f"{'='*80}\n")

        return provider

    @staticmethod
    def get_available_providers() -> list:
        """获取所有可用的提供商类型"""
        return list(AIProviderFactory.PROVIDERS.keys())

    @staticmethod
    def register_provider(name: str, provider_class):
        """
        注册新的AI提供商

        :param name: 提供商名称
        :param provider_class: 提供商类
        """
        if not issubclass(provider_class, AIProvider):
            raise TypeError("提供商类必须继承自AIProvider")

        AIProviderFactory.PROVIDERS[name.lower()] = provider_class
        print(f"✅ 已注册AI提供商: {name}")
