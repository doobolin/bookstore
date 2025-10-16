#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册功能测试脚本
用于测试注册API是否正常工作
"""

import requests
import json

# API基础URL
BASE_URL = 'http://localhost:5000/api'

def test_register():
    """测试注册功能"""
    print("=" * 60)
    print("测试用户注册API")
    print("=" * 60)

    # 测试数据
    test_user = {
        'username': 'testuser123',
        'email': 'testuser123@example.com',
        'password': 'password123'
    }

    print(f"\n📤 发送注册请求...")
    print(f"用户名: {test_user['username']}")
    print(f"邮箱: {test_user['email']}")
    print(f"密码: {test_user['password']}")

    try:
        response = requests.post(
            f'{BASE_URL}/register',
            json=test_user,
            headers={'Content-Type': 'application/json'}
        )

        print(f"\n📥 收到响应:")
        print(f"状态码: {response.status_code}")
        print(f"响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 200:
            print("\n✅ 注册成功！")
            return True
        else:
            print(f"\n❌ 注册失败: {response.json().get('message', '未知错误')}")
            return False

    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败：无法连接到后端服务")
        print("请确保后端服务已启动: python app.py")
        return False
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        return False

def test_login():
    """测试登录功能"""
    print("\n" + "=" * 60)
    print("测试用户登录API")
    print("=" * 60)

    # 使用刚才注册的用户登录
    login_data = {
        'username': 'testuser123',
        'password': 'password123'
    }

    print(f"\n📤 发送登录请求...")
    print(f"用户名: {login_data['username']}")
    print(f"密码: {login_data['password']}")

    try:
        response = requests.post(
            f'{BASE_URL}/login',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )

        print(f"\n📥 收到响应:")
        print(f"状态码: {response.status_code}")
        print(f"响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 200:
            print("\n✅ 登录成功！")
            return True
        else:
            print(f"\n❌ 登录失败: {response.json().get('message', '未知错误')}")
            return False

    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败：无法连接到后端服务")
        return False
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        return False

def test_duplicate_register():
    """测试重复注册（预期应该失败）"""
    print("\n" + "=" * 60)
    print("测试重复注册（预期失败）")
    print("=" * 60)

    # 使用相同的用户名和邮箱
    test_user = {
        'username': 'testuser123',
        'email': 'testuser123@example.com',
        'password': 'newpassword456'
    }

    print(f"\n📤 尝试使用相同用户名注册...")

    try:
        response = requests.post(
            f'{BASE_URL}/register',
            json=test_user,
            headers={'Content-Type': 'application/json'}
        )

        print(f"\n📥 收到响应:")
        print(f"状态码: {response.status_code}")
        print(f"响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 400:
            print("\n✅ 正确拒绝了重复注册！")
            return True
        else:
            print("\n⚠️ 警告：系统允许了重复注册，这不应该发生")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        return False

def check_backend_status():
    """检查后端服务状态"""
    print("=" * 60)
    print("检查后端服务状态")
    print("=" * 60)

    try:
        response = requests.get(f'{BASE_URL}/health', timeout=3)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            return True
        else:
            print("⚠️ 后端服务响应异常")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("请确保后端已启动: cd backend && python app.py")
        return False
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return False

def main():
    """主测试流程"""
    print("\n" + "🚀" * 30)
    print("注册功能完整测试")
    print("🚀" * 30 + "\n")

    # 1. 检查后端状态
    if not check_backend_status():
        print("\n⛔ 测试终止：后端服务未运行")
        return

    # 2. 测试注册
    print("\n" + "-" * 60)
    register_success = test_register()

    # 3. 如果注册成功，测试登录
    if register_success:
        print("\n" + "-" * 60)
        test_login()

    # 4. 测试重复注册
    print("\n" + "-" * 60)
    test_duplicate_register()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

    print("\n💡 提示：")
    print("- 如果注册失败提示'用户已存在'，可以修改脚本中的用户名")
    print("- 可以在MySQL中查看注册的用户: SELECT * FROM users;")
    print("- 测试完成后可以删除测试用户")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {str(e)}")
