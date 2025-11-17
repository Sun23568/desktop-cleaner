"""
通义千问API测试脚本
快速验证API配置是否正确
"""
import requests
import config

def test_api():
    """测试通义千问API是否可用"""

    print("="*60)
    print("🧪 开始测试通义千问API")
    print("="*60)

    # 检查API Key
    if not config.TONGYI_API_KEY or config.TONGYI_API_KEY == "":
        print("❌ 错误：API Key未配置！")
        print("请在 config.py 中设置 TONGYI_API_KEY")
        return False

    print(f"✓ API Key已配置: {config.TONGYI_API_KEY[:15]}...{config.TONGYI_API_KEY[-5:]}")
    print(f"✓ 模型: {config.TONGYI_MODEL}")
    print(f"✓ 超时时间: {config.AI_TIMEOUT}秒")
    print()

    # 构造测试请求
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.TONGYI_API_KEY}",
        "Content-Type": "application/json"
    }

    # 简单的测试消息
    test_message = "你好，请回复'测试成功'三个字。"

    data = {
        "model": config.TONGYI_MODEL,
        "messages": [
            {"role": "user", "content": test_message}
        ]
    }

    try:
        print("📡 发送测试请求...")
        print(f"   URL: {url}")
        print(f"   测试消息: {test_message}")
        print()

        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=config.AI_TIMEOUT
        )

        # 检查HTTP状态码
        print(f"📊 HTTP状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            # 打印完整响应（用于调试）
            print("\n📄 API响应内容:")
            print("-"*60)

            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"AI回复: {content}")
                print("-"*60)

                # 检查是否有usage信息
                if 'usage' in result:
                    print(f"\n📈 Token使用情况:")
                    print(f"   输入tokens: {result['usage'].get('prompt_tokens', 'N/A')}")
                    print(f"   输出tokens: {result['usage'].get('completion_tokens', 'N/A')}")
                    print(f"   总计tokens: {result['usage'].get('total_tokens', 'N/A')}")

                print("\n" + "="*60)
                print("✅ API测试成功！通义千问API工作正常")
                print("="*60)
                return True
            else:
                print("❌ 响应格式异常，未找到choices字段")
                print(f"完整响应: {result}")
                return False

        elif response.status_code == 401:
            print("❌ 认证失败：API Key无效或已过期")
            print("请检查config.py中的TONGYI_API_KEY是否正确")
            return False

        elif response.status_code == 429:
            print("❌ 请求过于频繁或额度不足")
            print("请检查通义千问账号余额或稍后再试")
            return False

        else:
            print(f"❌ API调用失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（超过{config.AI_TIMEOUT}秒）")
        print("可能原因：")
        print("  1. 网络连接不稳定")
        print("  2. 超时时间设置过短")
        print("  3. 通义千问服务响应慢")
        return False

    except requests.exceptions.ConnectionError:
        print("❌ 网络连接错误")
        print("可能原因：")
        print("  1. 无法连接到通义千问服务器")
        print("  2. 代理设置问题")
        print("  3. 防火墙拦截")
        return False

    except Exception as e:
        print(f"❌ 发生未知错误: {type(e).__name__}")
        print(f"错误详情: {str(e)}")
        return False


if __name__ == '__main__':
    print()
    success = test_api()
    print()

    if success:
        print("🎉 恭喜！你可以正常使用桌面清理工具了")
        print("   运行命令: python main.py")
    else:
        print("⚠️  请解决上述问题后重新测试")
        print("   重新测试命令: python test_tongyi_api.py")

    print()
