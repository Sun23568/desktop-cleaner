"""
批次处理和日志测试脚本
用于验证分批处理和详细日志功能
"""
import sys
sys.path.append('.')

from core.ai_analyzer import AIAnalyzer
import config

def test_batch_processing():
    """测试批次处理和日志输出"""

    print("="*80)
    print("🧪 批次处理和日志测试")
    print("="*80)
    print(f"\n当前配置:")
    print(f"  每批大小: {config.MAX_FILES_PER_REQUEST}")
    print(f"  超时时间: {config.AI_TIMEOUT}秒")
    print(f"  最大重试: {config.AI_MAX_RETRIES}次")
    print(f"  重试间隔: {config.AI_RETRY_DELAY}秒")
    print(f"  详细日志: {config.ENABLE_DETAIL_LOG}")
    print(f"  请求日志: {config.LOG_REQUEST_PARAMS}")
    print(f"  响应日志: {config.LOG_RESPONSE_CONTENT}")
    print()

    # 创建测试数据（模拟多个文件）
    test_files = []
    for i in range(25):  # 创建25个测试文件
        test_files.append({
            'name': f'test_file_{i+1}.txt',
            'path': f'/home/user/Desktop/test_file_{i+1}.txt',
            'extension': '.txt',
            'size_mb': round(0.5 + i * 0.1, 2),
            'modified_time': '2025-11-17 10:00:00',
            'created_time': '2025-11-17 09:00:00',
        })

    print(f"📂 准备测试 {len(test_files)} 个文件")
    print(f"   预计分批数: {(len(test_files) + config.MAX_FILES_PER_REQUEST - 1) // config.MAX_FILES_PER_REQUEST}")
    print()

    input("按回车键开始测试（Ctrl+C 取消）...")

    # 创建分析器并测试
    analyzer = AIAnalyzer()

    try:
        result = analyzer.analyze_files(test_files)

        print("\n" + "="*80)
        print("✅ 测试完成！")
        print("="*80)
        print(f"总建议数: {len(result.get('suggestions', []))}")
        print(f"分类数: {len(result.get('categories', {}))}")

        # 显示部分建议
        if result.get('suggestions'):
            print(f"\n前3条建议:")
            for i, suggestion in enumerate(result['suggestions'][:3], 1):
                print(f"{i}. {suggestion.get('file_path', 'N/A')}")
                print(f"   操作: {suggestion.get('action', 'N/A')}")
                print(f"   理由: {suggestion.get('reason', 'N/A')}")
                print()

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    print()
    test_batch_processing()
    print()
