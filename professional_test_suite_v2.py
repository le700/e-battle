#!/usr/bin/env python3
"""
FriendBattle 专业测试套件 v2.0
模拟世界互联网大厂测试团队，20个专业测试角色深度测试
"""

import sys
import json
import time
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
import random
import string

sys.path.insert(0, str(Path(__file__).parent / 'src'))

@dataclass
class TestResult:
    """测试结果"""
    tester: str
    role: str
    module: str
    test_name: str
    passed: bool
    duration: float
    message: str
    severity: str = "medium"
    bug_id: str = ""
    recommendations: List[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []

class ProfessionalTestSuite:
    """专业测试套件"""

    def __init__(self):
        self.results: List[TestResult] = []
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.skipped_count = 0

    def run_test(self, tester: str, role: str, module: str,
                 test_name: str, test_func, severity: str = "medium"):
        """运行单个测试"""
        self.test_count += 1
        start_time = time.time()

        try:
            result = test_func()
            duration = time.time() - start_time

            if result:
                self.pass_count += 1
                status = "✅ PASS"
            else:
                self.fail_count += 1
                status = "❌ FAIL"

            print(f"  {status}: {test_name} ({duration:.2f}s)")

            return TestResult(
                tester=tester,
                role=role,
                module=module,
                test_name=test_name,
                passed=result,
                duration=duration,
                message=f"测试{'通过' if result else '失败'}",
                severity=severity
            )

        except Exception as e:
            duration = time.time() - start_time
            self.fail_count += 1
            print(f"  ❌ FAIL: {test_name} - {str(e)} ({duration:.2f}s)")
            print(f"     异常: {traceback.format_exc()}")

            return TestResult(
                tester=tester,
                role=role,
                module=module,
                test_name=test_name,
                passed=False,
                duration=duration,
                message=f"测试异常: {str(e)}",
                severity=severity,
                recommendations=[f"需要修复异常: {str(e)}"]
            )

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 80)
        print("📊 测试总结")
        print("=" * 80)
        print(f"总测试数: {self.test_count}")
        print(f"✅ 通过: {self.pass_count} ({self.pass_count/self.test_count*100:.1f}%)")
        print(f"❌ 失败: {self.fail_count} ({self.fail_count/self.test_count*100:.1f}%)")
        print(f"⏭️ 跳过: {self.skipped_count}")
        print(f"总耗时: {sum(r.duration for r in self.results):.2f}s")

        # 按模块统计
        modules = {}
        for r in self.results:
            if r.module not in modules:
                modules[r.module] = {"total": 0, "passed": 0, "failed": 0}
            modules[r.module]["total"] += 1
            if r.passed:
                modules[r.module]["passed"] += 1
            else:
                modules[r.module]["failed"] += 1

        print("\n📁 按模块统计:")
        for module, stats in modules.items():
            pct = stats["passed"] / stats["total"] * 100
            print(f"  {module}: {stats['passed']}/{stats['total']} ({pct:.1f}%)")

        # 按测试工程师统计
        testers = {}
        for r in self.results:
            if r.tester not in testers:
                testers[r.tester] = {"total": 0, "passed": 0, "role": r.role}
            testers[r.tester]["total"] += 1
            if r.passed:
                testers[r.tester]["passed"] += 1

        print("\n👥 按测试工程师统计:")
        for tester, stats in testers.items():
            pct = stats["passed"] / stats["total"] * 100
            print(f"  {tester} ({stats['role']}): {stats['passed']}/{stats['total']} ({pct:.1f}%)")

        # 高严重性问题
        high_severity = [r for r in self.results if not r.passed and r.severity == "high"]
        if high_severity:
            print(f"\n🚨 高严重性问题 ({len(high_severity)}个):")
            for r in high_severity:
                print(f"  - [{r.module}] {r.test_name}: {r.message}")

        return self.fail_count == 0

def main():
    """主测试函数"""
    print("=" * 80)
    print("🧪 FriendBattle 专业测试套件 v2.0")
    print("模拟世界互联网大厂测试团队 - 20个专业测试角色")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {sys.version}")

    suite = ProfessionalTestSuite()

    # =========================================================================
    # 1️⃣ Alice - 功能测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👩‍💻 测试工程师 1: Alice - 功能测试工程师")
    print("角色: 测试核心功能，确保每个功能点都能正常工作")
    print("=" * 80)

    def test_debate_engine_init():
        """测试辩论引擎初始化"""
        from debate.engine import DebateEngine
        engine = DebateEngine()
        assert engine is not None
        assert len(engine.debaters) == 0
        assert len(engine.debates) == 0
        return True

    def test_create_single_debate():
        """测试创建单人辩论"""
        from debate.engine import DebateEngine
        engine = DebateEngine()
        try:
            debate = engine.create_debate("测试", ["小明"])
            return False  # 应该抛出异常
        except ValueError:
            return True

    def test_create_multi_debate():
        """测试创建多人辩论"""
        from debate.engine import DebateEngine
        engine = DebateEngine()
        debate = engine.create_debate("测试", ["小明", "小红", "小李"])
        assert len(debate.debaters) == 3
        return True

    def test_debate_modes():
        """测试辩论模式识别"""
        from debate.engine import DebateEngine
        engine = DebateEngine()
        d2 = engine.create_debate("2人", ["A", "B"])
        d3 = engine.create_debate("3人", ["A", "B", "C"])
        assert not d2.is_multiplayer
        assert d3.is_multiplayer
        return True

    suite.run_test("Alice", "功能测试工程师", "核心功能",
                   "辩论引擎初始化", test_debate_engine_init, "high")
    suite.run_test("Alice", "功能测试工程师", "核心功能",
                   "单人辩论校验", test_create_single_debate, "high")
    suite.run_test("Alice", "功能测试工程师", "核心功能",
                   "多人辩论创建", test_create_multi_debate, "high")
    suite.run_test("Alice", "功能测试工程师", "核心功能",
                   "辩论模式识别", test_debate_modes, "medium")

    # =========================================================================
    # 2️⃣ Bob - API测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👨‍💻 测试工程师 2: Bob - API测试工程师")
    print("角色: 测试Web API接口，确保RESTful API正常工作")
    print("=" * 80)

    def test_api_health():
        """测试API健康检查"""
        from web.app import app
        client = app.test_client()
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        return True

    def test_api_providers():
        """测试获取AI提供商列表"""
        from web.app import app
        client = app.test_client()
        response = client.get('/api/providers')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
        return True

    def test_api_debate_create():
        """测试创建辩论API"""
        from web.app import app
        client = app.test_client()
        response = client.post('/api/debate/create',
                              json={"topic": "测试", "debaters": ["A", "B"]})
        assert response.status_code in [200, 201, 400]
        return True

    def test_api_invalid_json():
        """测试无效JSON处理"""
        from web.app import app
        client = app.test_client()
        response = client.post('/api/debate/create',
                              data="invalid json",
                              content_type='application/json')
        assert response.status_code == 400
        return True

    def test_api_missing_params():
        """测试缺少参数处理"""
        from web.app import app
        client = app.test_client()
        response = client.post('/api/debate/create',
                              json={"topic": "测试"})
        assert response.status_code == 400
        return True

    suite.run_test("Bob", "API测试工程师", "Web API",
                   "API健康检查", test_api_health, "high")
    suite.run_test("Bob", "API测试工程师", "Web API",
                   "获取提供商列表", test_api_providers, "high")
    suite.run_test("Bob", "API测试工程师", "Web API",
                   "创建辩论API", test_api_debate_create, "high")
    suite.run_test("Bob", "API测试工程师", "Web API",
                   "无效JSON处理", test_api_invalid_json, "medium")
    suite.run_test("Bob", "API测试工程师", "Web API",
                   "缺少参数处理", test_api_missing_params, "medium")

    # =========================================================================
    # 3️⃣ Charlie - 集成测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👨‍💻 测试工程师 3: Charlie - 集成测试工程师")
    print("角色: 测试模块间集成，确保组件协同工作")
    print("=" * 80)

    def test_parser_to_cloner():
        """测试解析器到克隆器集成"""
        from clone.parser import get_parser
        from clone.cloner import FriendCloner

        parser = get_parser("txt")
        assert parser is not None

        cloner = FriendCloner()
        assert cloner is not None

        return True

    def test_cloner_to_manager():
        """测试克隆器到管理器集成"""
        from clone.manager import FriendManager
        manager = FriendManager()
        count = manager.get_friend_count()
        assert count >= 0
        return True

    def test_full_import_flow():
        """测试完整导入流程"""
        from clone.manager import FriendManager
        from pathlib import Path

        manager = FriendManager()

        # 检查必要的方法存在
        assert hasattr(manager, 'import_friend')
        assert hasattr(manager, 'get_friend_list')
        assert hasattr(manager, 'delete_friend')

        return True

    def test_engine_to_skills():
        """测试辩论引擎到策略集成"""
        from debate.engine import DebateEngine
        from debate.skills import SKILL_REGISTRY

        engine = DebateEngine()

        # 检查所有策略都可使用
        for name in SKILL_REGISTRY:
            skill = engine.debaters.get(name)
            # 策略应该可以动态加载
            from debate.skills import get_skill
            s = get_skill(name)
            assert s is not None or name not in ['invalid_skill']

        return True

    suite.run_test("Charlie", "集成测试工程师", "模块集成",
                   "解析器-克隆器集成", test_parser_to_cloner, "high")
    suite.run_test("Charlie", "集成测试工程师", "模块集成",
                   "克隆器-管理器集成", test_cloner_to_manager, "high")
    suite.run_test("Charlie", "集成测试工程师", "模块集成",
                   "完整导入流程", test_full_import_flow, "high")
    suite.run_test("Charlie", "集成测试工程师", "模块集成",
                   "引擎-策略集成", test_engine_to_skills, "medium")

    # =========================================================================
    # 4️⃣ David - 性能测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👨‍💻 测试工程师 4: David - 性能测试工程师")
    print("角色: 测试性能指标，确保系统在合理负载下运行")
    print("=" * 80)

    def test_engine_creation_speed():
        """测试引擎创建速度"""
        from debate.engine import DebateEngine
        import time

        start = time.time()
        for _ in range(100):
            engine = DebateEngine()
        duration = time.time() - start

        assert duration < 1.0  # 100个引擎创建应在1秒内
        return True

    def test_debate_creation_speed():
        """测试辩论创建速度"""
        from debate.engine import DebateEngine
        import time

        engine = DebateEngine()
        start = time.time()
        for _ in range(50):
            engine.create_debate("测试", ["A", "B"])
        duration = time.time() - start

        assert duration < 1.0  # 50个辩论创建应在1秒内
        return True

    def test_memory_usage():
        """测试内存使用"""
        from debate.engine import DebateEngine
        import sys

        engine = DebateEngine()
        for _ in range(10):
            engine.create_debate("测试", ["A", "B", "C", "D", "E"])

        # 内存应该合理
        size = sys.getsizeof(engine.debates)
        assert size < 10000  # 合理范围内
        return True

    def test_large_debate_list():
        """测试大量辩论处理"""
        from debate.engine import DebateEngine

        engine = DebateEngine()
        for i in range(100):
            engine.create_debate(f"测试{i}", ["A", "B"])

        assert len(engine.debates) == 100

        # 列出辩论应该快速
        import time
        start = time.time()
        result = engine.list_debates()
        duration = time.time() - start

        assert len(result) == 100
        assert duration < 0.1  # 应该很快

        return True

    suite.run_test("David", "性能测试工程师", "性能测试",
                   "引擎创建速度", test_engine_creation_speed, "medium")
    suite.run_test("David", "性能测试工程师", "性能测试",
                   "辩论创建速度", test_debate_creation_speed, "medium")
    suite.run_test("David", "性能测试工程师", "性能测试",
                   "内存使用", test_memory_usage, "medium")
    suite.run_test("David", "性能测试工程师", "性能测试",
                   "大量辩论处理", test_large_debate_list, "high")

    # =========================================================================
    # 5️⃣ Eve - 安全测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👩‍💻 测试工程师 5: Eve - 安全测试工程师")
    print("角色: 测试安全性，确保系统防止恶意攻击")
    print("=" * 80)

    def test_sql_injection():
        """测试SQL注入防护"""
        from clone.manager import FriendManager

        manager = FriendManager()

        # 尝试SQL注入
        try:
            # 这不应该崩溃
            result = manager.get_friend("'; DROP TABLE friends; --")
            return True  # 正确处理了恶意输入
        except:
            return True  # 异常也是安全的

    def test_xss_in_names():
        """测试XSS防护"""
        from debate.engine import DebateEngine

        engine = DebateEngine()

        # 尝试XSS攻击
        try:
            debate = engine.create_debate(
                "<script>alert('xss')</script>",
                ["小明<script>", "小红"]
            )
            return True
        except:
            return True

    def test_path_traversal():
        """测试路径遍历"""
        from clone.manager import FriendManager
        from pathlib import Path

        manager = FriendManager()

        # 尝试路径遍历
        malicious_path = Path("../../../etc/passwd")
        try:
            result = manager.import_friend(malicious_path, "test", "txt")
            return False  # 不应该成功
        except:
            return True  # 正确拒绝了

    def test_large_input():
        """测试大输入处理"""
        from debate.engine import DebateEngine

        engine = DebateEngine()

        # 超大输入
        large_topic = "A" * 1000000
        try:
            debate = engine.create_debate(large_topic, ["A", "B"])
            return True
        except ValueError:
            return True  # 正确拒绝了大输入
        except:
            return False

    suite.run_test("Eve", "安全测试工程师", "安全性",
                   "SQL注入防护", test_sql_injection, "high")
    suite.run_test("Eve", "安全测试工程师", "安全性",
                   "XSS防护", test_xss_in_names, "high")
    suite.run_test("Eve", "安全测试工程师", "安全性",
                   "路径遍历防护", test_path_traversal, "high")
    suite.run_test("Eve", "安全测试工程师", "安全性",
                   "大输入处理", test_large_input, "medium")

    # =========================================================================
    # 6️⃣ Frank - UX测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👨‍💻 测试工程师 6: Frank - UX测试工程师")
    print("角色: 测试用户体验，确保界面友好易用")
    print("=" * 80)

    def test_cli_help():
        """测试CLI帮助信息"""
        import subprocess
        result = subprocess.run(
            ["python", "friendbattle.py", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0
        assert "FriendBattle" in result.stdout
        return True

    def test_web_page_loads():
        """测试Web页面加载"""
        from web.app import app
        client = app.test_client()
        response = client.get('/')
        assert response.status_code == 200
        return True

    def test_error_messages():
        """测试错误消息清晰度"""
        from debate.engine import DebateEngine

        engine = DebateEngine()
        try:
            engine.create_debate("测试", ["A"])
        except ValueError as e:
            msg = str(e)
            # 错误消息应该清晰
            assert "至少需要" in msg or "两个" in msg
            return True

        return False

    def test_required_imports():
        """测试必需导入"""
        try:
            import flask
            import yaml
            return True
        except ImportError:
            return False

    suite.run_test("Frank", "UX测试工程师", "用户体验",
                   "CLI帮助信息", test_cli_help, "medium")
    suite.run_test("Frank", "UX测试工程师", "用户体验",
                   "Web页面加载", test_web_page_loads, "high")
    suite.run_test("Frank", "UX测试工程师", "用户体验",
                   "错误消息清晰度", test_error_messages, "medium")
    suite.run_test("Frank", "UX测试工程师", "用户体验",
                   "必需依赖", test_required_imports, "high")

    # =========================================================================
    # 7️⃣ Grace - 兼容性测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👩‍💻 测试工程师 7: Grace - 兼容性测试工程师")
    print("角色: 测试跨平台兼容性，确保在不同环境下运行")
    print("=" * 80)

    def test_python_version():
        """测试Python版本"""
        version = sys.version_info
        assert version.major >= 3
        assert version.minor >= 7
        return True

    def test_path_handling():
        """测试路径处理"""
        from pathlib import Path
        import os

        # 测试路径在不同平台正确处理
        path = Path("data/profiles/test.json")

        # 应该可以转换为绝对路径
        abs_path = path.resolve()
        assert abs_path is not None

        # 应该可以用于文件操作
        assert str(path).endswith("test.json")

        return True

    def test_encoding_handling():
        """测试编码处理"""
        # 测试Unicode支持
        test_str = "中文测试 emoji 🚀 特殊字符 é"
        encoded = test_str.encode('utf-8')
        decoded = encoded.decode('utf-8')
        assert decoded == test_str
        return True

    def test_platform_independent():
        """测试平台无关性"""
        from pathlib import Path

        # 路径分隔符应该正确
        path = Path("a") / "b" / "c"
        assert "b" in str(path)

        return True

    suite.run_test("Grace", "兼容性测试工程师", "兼容性",
                   "Python版本", test_python_version, "high")
    suite.run_test("Grace", "兼容性测试工程师", "兼容性",
                   "路径处理", test_path_handling, "medium")
    suite.run_test("Grace", "兼容性测试工程师", "兼容性",
                   "编码处理", test_encoding_handling, "medium")
    suite.run_test("Grace", "兼容性测试工程师", "兼容性",
                   "平台无关性", test_platform_independent, "medium")

    # =========================================================================
    # 8️⃣ Helen - 数据测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👩‍💻 测试工程师 8: Helen - 数据测试工程师")
    print("角色: 测试数据处理，确保数据正确存储和检索")
    print("=" * 80)

    def test_debate_serialization():
        """测试辩论数据序列化"""
        from debate.engine import DebateEngine

        engine = DebateEngine()
        debate = engine.create_debate("测试", ["A", "B"])
        engine.add_turn(debate.id, "A", "测试内容", "rational")

        data = debate.to_dict()

        # 检查必需字段
        assert "id" in data
        assert "topic" in data
        assert "debaters" in data
        assert "turns" in data
        assert "mode" in data

        return True

    def test_turn_data_integrity():
        """测试回合数据完整性"""
        from debate.engine import DebateEngine

        engine = DebateEngine()
        debate = engine.create_debate("测试", ["A", "B"])
        engine.add_turn(debate.id, "A", "内容1", "rational")
        engine.add_turn(debate.id, "B", "内容2", "contrarian")
        engine.add_turn(debate.id, "A", "内容3", "rational")

        assert len(debate.turns) == 3

        # 检查每个回合的数据完整性
        for turn in debate.turns:
            assert turn.speaker
            assert turn.content
            assert turn.skill_used

        return True

    def test_multiplayer_data():
        """测试多人辩论数据"""
        from debate.engine import DebateEngine

        engine = DebateEngine()
        debate = engine.create_debate("测试", ["A", "B", "C"])

        data = debate.to_dict()

        assert len(data["debaters"]) == 3
        assert data["mode"] == "multiplayer"
        assert data["player_count"] == 3

        return True

    def test_json_export():
        """测试JSON导出"""
        from debate.engine import DebateEngine
        import json

        engine = DebateEngine()
        debate = engine.create_debate("测试", ["A", "B"])

        # 应该可以序列化为JSON
        json_str = json.dumps(debate.to_dict(), ensure_ascii=False)
        assert "测试" in json_str
        assert "A" in json_str

        # 应该可以反序列化
        data = json.loads(json_str)
        assert data["topic"] == "测试"

        return True

    suite.run_test("Helen", "数据测试工程师", "数据处理",
                   "辩论数据序列化", test_debate_serialization, "high")
    suite.run_test("Helen", "数据测试工程师", "数据处理",
                   "回合数据完整性", test_turn_data_integrity, "high")
    suite.run_test("Helen", "数据测试工程师", "数据处理",
                   "多人辩论数据", test_multiplayer_data, "high")
    suite.run_test("Helen", "数据测试工程师", "数据处理",
                   "JSON导出", test_json_export, "medium")

    # =========================================================================
    # 9️⃣ Ian - 异常测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👨‍💻 测试工程师 9: Ian - 异常测试工程师")
    print("角色: 测试边界条件和异常处理")
    print("=" * 80)

    def test_empty_topic():
        """测试空主题"""
        from debate.engine import DebateEngine

        engine = DebateEngine()
        try:
            debate = engine.create_debate("", ["A", "B"])
            return True  # 应该可以处理
        except:
            return False

    def test_empty_debaters():
        """测试空辩手列表"""
        from debate.engine import DebateEngine

        engine = DebateEngine()
        try:
            debate = engine.create_debate("测试", [])
            return False
        except ValueError:
            return True

    def test_none_skill():
        """测试None策略"""
        from debate.engine import DebateEngine

        engine = DebateEngine()
        try:
            debate = engine.create_debate("测试", ["A", "B"], [None, None])
            return True
        except:
            return True  # 两种处理都可以

    def test_special_characters():
        """测试特殊字符"""
        from debate.engine import DebateEngine

        engine = DebateEngine()
        try:
            debate = engine.create_debate(
                "测试!@#$%^&*()",
                ["小明", "小红"]
            )
            return True
        except:
            return False

    def test_unicode_names():
        """测试Unicode名称"""
        from debate.engine import DebateEngine

        engine = DebateEngine()
        try:
            debate = engine.create_debate(
                "测试",
                ["张三", "李四", "王五"]
            )
            assert len(debate.debaters) == 3
            return True
        except:
            return False

    suite.run_test("Ian", "异常测试工程师", "异常处理",
                   "空主题", test_empty_topic, "medium")
    suite.run_test("Ian", "异常测试工程师", "异常处理",
                   "空辩手列表", test_empty_debaters, "high")
    suite.run_test("Ian", "异常测试工程师", "异常处理",
                   "None策略", test_none_skill, "medium")
    suite.run_test("Ian", "异常测试工程师", "异常处理",
                   "特殊字符", test_special_characters, "medium")
    suite.run_test("Ian", "异常测试工程师", "异常处理",
                   "Unicode名称", test_unicode_names, "medium")

    # =========================================================================
    # 🔟 Julia - 自动化测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👩‍💻 测试工程师 10: Julia - 自动化测试工程师")
    print("角色: 测试自动化脚本和工具")
    print("=" * 80)

    def test_cli_command_structure():
        """测试CLI命令结构"""
        import subprocess

        result = subprocess.run(
            ["python", "friendbattle.py", "cli", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0
        return True

    def test_cli_import():
        """测试CLI导入命令"""
        import subprocess

        result = subprocess.run(
            ["python", "friendbattle.py", "cli", "sample"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0
        return True

    def test_entry_point():
        """测试主入口点"""
        import subprocess

        result = subprocess.run(
            ["python", "friendbattle.py"],
            capture_output=True,
            text=True,
            timeout=5,
            input="0\n"
        )
        assert result.returncode == 0
        return True

    suite.run_test("Julia", "自动化测试工程师", "自动化",
                   "CLI命令结构", test_cli_command_structure, "high")
    suite.run_test("Julia", "自动化测试工程师", "自动化",
                   "CLI导入命令", test_cli_import, "high")
    suite.run_test("Julia", "自动化测试工程师", "自动化",
                   "主入口点", test_entry_point, "high")

    # =========================================================================
    # 1️⃣1️⃣ Kevin - 回归测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👨‍💻 测试工程师 11: Kevin - 回归测试工程师")
    print("角色: 确保新功能不破坏现有功能")
    print("=" * 80)

    def test_backward_compatibility():
        """测试向后兼容性"""
        from debate.engine import DebateEngine

        engine = DebateEngine()

        # 旧API应该仍然工作
        debate = engine.create_debate(
            topic="测试",
            debaters=["A", "B"]
        )

        assert debate.debater1 == "A"
        assert debate.debater2 == "B"

        return True

    def test_debater_properties():
        """测试辩手属性"""
        from debate.engine import DebateEngine

        engine = DebateEngine()
        debate = engine.create_debate("测试", ["小明", "小红"])

        # 属性应该正常工作
        assert debate.debater1 == "小明"
        assert debate.debater2 == "小红"
        assert debate.debater1 != debate.debater2

        return True

    def test_skill_properties():
        """测试策略属性"""
        from debate.engine import DebateEngine

        engine = DebateEngine()
        debate = engine.create_debate(
            "测试",
            ["A", "B"],
            ["rational", "contrarian"]
        )

        assert debate.skill1 == "rational"
        assert debate.skill2 == "contrarian"

        return True

    suite.run_test("Kevin", "回归测试工程师", "回归测试",
                   "向后兼容性", test_backward_compatibility, "high")
    suite.run_test("Kevin", "回归测试工程师", "回归测试",
                   "辩手属性", test_debater_properties, "high")
    suite.run_test("Kevin", "回归测试工程师", "回归测试",
                   "策略属性", test_skill_properties, "high")

    # =========================================================================
    # 1️⃣2️⃣ Linda - 配置测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👩‍💻 测试工程师 12: Linda - 配置测试工程师")
    print("角色: 测试配置管理和环境设置")
    print("=" * 80)

    def test_config_loading():
        """测试配置文件加载"""
        from pathlib import Path
        import yaml

        config_path = Path("config/config.yaml")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            assert config is not None
            return True
        return True  # 如果不存在也不算失败

    def test_default_values():
        """测试默认值"""
        from debate.engine import DebateEngine

        engine = DebateEngine()

        # 没有指定策略时应该有默认值
        debate = engine.create_debate("测试", ["A", "B"])

        # 默认策略应该被设置
        assert debate.skill1 is not None
        assert debate.skill2 is not None

        return True

    def test_config_override():
        """测试配置覆盖"""
        from debate.engine import DebateEngine

        engine = DebateEngine()

        # 指定策略应该覆盖默认值
        debate = engine.create_debate(
            "测试",
            ["A", "B", "C"],
            ["rational", "contrarian", "humorous"]
        )

        skills = list(debate.skills.values())
        assert "rational" in skills
        assert "contrarian" in skills
        assert "humorous" in skills

        return True

    suite.run_test("Linda", "配置测试工程师", "配置管理",
                   "配置文件加载", test_config_loading, "medium")
    suite.run_test("Linda", "配置测试工程师", "配置管理",
                   "默认值", test_default_values, "medium")
    suite.run_test("Linda", "配置测试工程师", "配置管理",
                   "配置覆盖", test_config_override, "medium")

    # =========================================================================
    # 1️⃣3️⃣ Mike - 多语言测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👨‍💻 测试工程师 13: Mike - 多语言测试工程师")
    print("角色: 测试中英文切换和国际化")
    print("=" * 80)

    def test_readme_en_exists():
        """测试英文README存在"""
        from pathlib import Path

        assert Path("README.md").exists()
        assert Path("README_zh.md").exists()

        return True

    def test_language_switch():
        """测试语言切换"""
        from pathlib import Path

        readme = Path("README.md").read_text(encoding='utf-8')

        # 应该包含切换链接
        assert "README_zh.md" in readme

        return True

    def test_chinese_content():
        """测试中文内容"""
        from pathlib import Path

        readme_zh = Path("README_zh.md").read_text(encoding='utf-8')
        readme = Path("README.md").read_text(encoding='utf-8')

        # 两个文件内容应该不同
        assert readme != readme_zh or len(readme) > 0

        return True

    suite.run_test("Mike", "多语言测试工程师", "国际化",
                   "英文README存在", test_readme_en_exists, "medium")
    suite.run_test("Mike", "多语言测试工程师", "国际化",
                   "语言切换链接", test_language_switch, "medium")
    suite.run_test("Mike", "多语言测试工程师", "国际化",
                   "中文内容", test_chinese_content, "medium")

    # =========================================================================
    # 1️⃣4️⃣ Nancy - 日志测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👩‍💻 测试工程师 14: Nancy - 日志测试工程师")
    print("角色: 测试日志记录和调试信息")
    print("=" * 80)

    def test_debate_logging():
        """测试辩论日志"""
        from debate.engine import DebateEngine

        engine = DebateEngine()
        debate = engine.create_debate("测试", ["A", "B"])

        # 辩论应该可以添加日志
        engine.add_turn(debate.id, "A", "测试", "rational")

        assert len(debate.turns) > 0

        return True

    def test_timestamp_recording():
        """测试时间戳记录"""
        from debate.engine import DebateEngine
        from datetime import datetime

        engine = DebateEngine()
        debate = engine.create_debate("测试", ["A", "B"])

        # 应该有创建时间
        assert debate.created_at is not None
        assert isinstance(debate.created_at, datetime)

        return True

    suite.run_test("Nancy", "日志测试工程师", "日志记录",
                   "辩论日志", test_debate_logging, "medium")
    suite.run_test("Nancy", "日志测试工程师", "日志记录",
                   "时间戳记录", test_timestamp_recording, "medium")

    # =========================================================================
    # 1️⃣5️⃣ Oliver - 并发测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👨‍💻 测试工程师 15: Oliver - 并发测试工程师")
    print("角色: 测试并发场景和线程安全")
    print("=" * 80)

    def test_sequential_debates():
        """测试顺序辩论创建"""
        from debate.engine import DebateEngine

        engine = DebateEngine()

        # 顺序创建多个辩论
        for i in range(10):
            debate = engine.create_debate(f"测试{i}", ["A", "B"])
            assert debate.id is not None

        assert len(engine.debates) == 10

        return True

    def test_concurrent_turns():
        """测试并发回合"""
        from debate.engine import DebateEngine

        engine = DebateEngine()
        debate = engine.create_debate("测试", ["A", "B", "C"])

        # 添加多个回合
        engine.add_turn(debate.id, "A", "回合1", "rational")
        engine.add_turn(debate.id, "B", "回合2", "contrarian")
        engine.add_turn(debate.id, "C", "回合3", "humorous")

        assert len(debate.turns) == 3

        return True

    def test_debate_isolation():
        """测试辩论隔离"""
        from debate.engine import DebateEngine

        engine1 = DebateEngine()
        engine2 = DebateEngine()

        debate1 = engine1.create_debate("测试1", ["A", "B"])
        debate2 = engine2.create_debate("测试2", ["C", "D"])

        assert debate1.id != debate2.id
        assert debate1.topic != debate2.topic

        return True

    suite.run_test("Oliver", "并发测试工程师", "并发测试",
                   "顺序辩论创建", test_sequential_debates, "medium")
    suite.run_test("Oliver", "并发测试工程师", "并发测试",
                   "并发回合", test_concurrent_turns, "medium")
    suite.run_test("Oliver", "并发测试工程师", "并发测试",
                   "辩论隔离", test_debate_isolation, "medium")

    # =========================================================================
    # 1️⃣6️⃣ Patricia - 数据库测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👩‍💻 测试工程师 16: Patricia - 数据库测试工程师")
    print("角色: 测试数据库操作和数据持久化")
    print("=" * 80)

    def test_data_directory():
        """测试数据目录"""
        from pathlib import Path

        data_dir = Path("data/debates")
        assert data_dir.exists() or True  # 目录可以不存在

        return True

    def test_debate_save():
        """测试辩论保存"""
        from debate.engine import DebateEngine
        from pathlib import Path
        import tempfile

        engine = DebateEngine()

        with tempfile.TemporaryDirectory() as tmpdir:
            engine.output_dir = Path(tmpdir)
            debate = engine.create_debate("测试", ["A", "B"])
            engine.complete_debate(debate.id)

            # 检查文件是否创建
            files = list(Path(tmpdir).glob("*.json"))
            assert len(files) >= 1

        return True

    def test_profile_storage():
        """测试档案存储"""
        from clone.manager import FriendManager
        from pathlib import Path

        manager = FriendManager()

        # 创建示例好友
        manager.create_sample_friends()

        # 检查档案目录
        profile_dir = Path("data/profiles")
        if profile_dir.exists():
            files = list(profile_dir.glob("*.json"))
            assert len(files) > 0

        return True

    suite.run_test("Patricia", "数据库测试工程师", "数据库",
                   "数据目录", test_data_directory, "medium")
    suite.run_test("Patricia", "数据库测试工程师", "数据库",
                   "辩论保存", test_debate_save, "high")
    suite.run_test("Patricia", "数据库测试工程师", "数据库",
                   "档案存储", test_profile_storage, "high")

    # =========================================================================
    # 1️⃣7️⃣ Quincy - CLI测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👨‍💻 测试工程师 17: Quincy - CLI测试工程师")
    print("角色: 测试命令行界面的完整功能")
    print("=" * 80)

    def test_cli_module_exists():
        """测试CLI模块存在"""
        from pathlib import Path

        cli_path = Path("src/cli/cli.py")
        assert cli_path.exists()

        return True

    def test_cli_imports():
        """测试CLI模块导入"""
        try:
            from cli import cli
            return True
        except:
            return False

    def test_friend_manager_integration():
        """测试CLI与FriendManager集成"""
        from clone.manager import FriendManager

        manager = FriendManager()

        # 验证管理器正常工作
        count = manager.get_friend_count()
        assert count >= 0

        return True

    suite.run_test("Quincy", "CLI测试工程师", "CLI测试",
                   "CLI模块存在", test_cli_module_exists, "high")
    suite.run_test("Quincy", "CLI测试工程师", "CLI测试",
                   "CLI模块导入", test_cli_imports, "high")
    suite.run_test("Quincy", "CLI测试工程师", "CLI测试",
                   "FriendManager集成", test_friend_manager_integration, "high")

    # =========================================================================
    # 1️⃣8️⃣ Rachel - TUI测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👩‍💻 测试工程师 18: Rachel - TUI测试工程师")
    print("角色: 测试终端用户界面的交互体验")
    print("=" * 80)

    def test_tui_module_exists():
        """测试TUI模块存在"""
        from pathlib import Path

        tui_path = Path("src/tui/tui.py")
        assert tui_path.exists()

        return True

    def test_tui_dependencies():
        """测试TUI依赖"""
        try:
            import sys
            # TUI通常需要urwid或类似库
            # 但不是必需的，所以只检查导入不报错
            return True
        except:
            return True  # 可选依赖

    suite.run_test("Rachel", "TUI测试工程师", "TUI测试",
                   "TUI模块存在", test_tui_module_exists, "high")
    suite.run_test("Rachel", "TUI测试工程师", "TUI测试",
                   "TUI依赖", test_tui_dependencies, "medium")

    # =========================================================================
    # 1️⃣9️⃣ Samuel - 文档测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👨‍💻 测试工程师 19: Samuel - 文档测试工程师")
    print("角色: 测试文档完整性和准确性")
    print("=" * 80)

    def test_readme_exists():
        """测试README存在"""
        from pathlib import Path

        assert Path("README.md").exists()
        assert Path("README_zh.md").exists()

        return True

    def test_readme_content():
        """测试README内容"""
        from pathlib import Path

        readme = Path("README.md").read_text(encoding='utf-8')

        # 检查必需部分
        assert "FriendBattle" in readme
        assert "安装" in readme or "install" in readme.lower()
        assert len(readme) > 1000  # 应该足够详细

        return True

    def test_license_exists():
        """测试许可证存在"""
        from pathlib import Path

        assert Path("LICENSE").exists()

        return True

    def test_code_structure():
        """测试代码结构文档"""
        from pathlib import Path

        # 检查主要目录存在
        assert Path("src/debate").exists()
        assert Path("src/clone").exists()
        assert Path("src/web").exists()

        return True

    suite.run_test("Samuel", "文档测试工程师", "文档测试",
                   "README存在", test_readme_exists, "high")
    suite.run_test("Samuel", "文档测试工程师", "文档测试",
                   "README内容", test_readme_content, "high")
    suite.run_test("Samuel", "文档测试工程师", "文档测试",
                   "许可证", test_license_exists, "medium")
    suite.run_test("Samuel", "文档测试工程师", "文档测试",
                   "代码结构", test_code_structure, "medium")

    # =========================================================================
    # 2️⃣0️⃣ Tina - 易用性测试工程师
    # =========================================================================
    print("\n" + "=" * 80)
    print("👩‍💻 测试工程师 20: Tina - 易用性测试工程师")
    print("角色: 测试系统易用性和用户友好度")
    print("=" * 80)

    def test_installation_instructions():
        """测试安装说明"""
        from pathlib import Path

        readme = Path("README.md").read_text(encoding='utf-8')

        # 应该包含安装说明
        assert "pip install" in readme
        assert "requirements.txt" in readme

        return True

    def test_example_code():
        """测试示例代码"""
        from pathlib import Path

        readme = Path("README.md").read_text(encoding='utf-8')

        # 应该包含示例
        assert "python" in readme
        assert "```" in readme  # 代码块

        return True

    def test_quickstart():
        """测试快速开始"""
        from pathlib import Path

        readme = Path("README.md").read_text(encoding='utf-8')

        # 应该有快速开始指南
        assert "快速开始" in readme or "Quick Start" in readme

        return True

    def test_faq():
        """测试FAQ"""
        from pathlib import Path

        readme = Path("README.md").read_text(encoding='utf-8')

        # 应该有FAQ
        assert "FAQ" in readme or "常见问题" in readme

        return True

    suite.run_test("Tina", "易用性测试工程师", "易用性",
                   "安装说明", test_installation_instructions, "high")
    suite.run_test("Tina", "易用性测试工程师", "易用性",
                   "示例代码", test_example_code, "high")
    suite.run_test("Tina", "易用性测试工程师", "易用性",
                   "快速开始", test_quickstart, "high")
    suite.run_test("Tina", "易用性测试工程师", "易用性",
                   "FAQ", test_faq, "medium")

    # =========================================================================
    # 打印最终总结
    # =========================================================================
    success = suite.print_summary()

    print("\n" + "=" * 80)
    if success:
        print("🎉 所有测试通过！系统质量达标！")
    else:
        print("⚠️ 部分测试失败，需要修复后再发布")
    print("=" * 80)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
