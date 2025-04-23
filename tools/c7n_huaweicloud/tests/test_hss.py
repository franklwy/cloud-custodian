# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from huaweicloud_common import BaseTest


class HssTest(BaseTest):
    """华为云主机安全服务(HSS)资源测试"""

    def test_hss_query(self):
        """测试HSS资源查询和增强"""
        factory = self.replay_flight_data("hss_query")
        p = self.load_policy(
            {
                "name": "hss-query-test",
                "resource": "huaweicloud.hss",
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证VCR: hss_query应包含1个主机
        self.assertEqual(len(resources), 1)
        # 验证VCR: 值应与hss_query中的'host_name'匹配
        self.assertEqual(resources[0]["host_name"], "test-host")
        # 验证augment方法添加了额外信息
        self.assertIn("agent_status", resources[0])
    
    def test_hss_filter_host_status_protected(self):
        """测试主机防护状态过滤器 - 已防护状态"""
        factory = self.replay_flight_data("hss_filter_host_status_protected")
        p = self.load_policy(
            {
                "name": "hss-protected-hosts",
                "resource": "huaweicloud.hss",
                "filters": [{"type": "host-status", "status": "protected"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证VCR: hss_filter_host_status_protected应包含已防护的主机
        self.assertEqual(len(resources), 1)
        # 验证防护状态
        self.assertEqual(resources[0]["agent_status"], "RUNNING")
    
    def test_hss_filter_host_status_unprotected(self):
        """测试主机防护状态过滤器 - 未防护状态"""
        factory = self.replay_flight_data("hss_filter_host_status_unprotected")
        p = self.load_policy(
            {
                "name": "hss-unprotected-hosts",
                "resource": "huaweicloud.hss",
                "filters": [{"type": "host-status", "status": "unprotected"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证VCR: hss_filter_host_status_unprotected应包含未防护的主机
        self.assertEqual(len(resources), 1)
        # 验证防护状态(不是RUNNING)
        self.assertNotEqual(resources[0]["agent_status"], "RUNNING")
    
    def test_hss_filter_vulnerability_critical(self):
        """测试漏洞过滤器 - 严重漏洞"""
        factory = self.replay_flight_data("hss_filter_vulnerability_critical")
        p = self.load_policy(
            {
                "name": "hss-hosts-with-critical-vulnerabilities",
                "resource": "huaweicloud.hss",
                "filters": [
                    {"type": "vulnerability", "severity": "critical", "status": "unfixed"}
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证VCR: hss_filter_vulnerability_critical应包含有严重漏洞的主机
        self.assertEqual(len(resources), 1)
        # 验证漏洞信息已添加到资源
        self.assertIn("vulnerabilities", resources[0])
        # 验证至少有一个漏洞
        self.assertTrue(len(resources[0]["vulnerabilities"]) > 0)
    
    def test_hss_filter_vulnerability_high(self):
        """测试漏洞过滤器 - 高危漏洞"""
        factory = self.replay_flight_data("hss_filter_vulnerability_high")
        p = self.load_policy(
            {
                "name": "hss-hosts-with-high-vulnerabilities",
                "resource": "huaweicloud.hss",
                "filters": [
                    {"type": "vulnerability", "severity": "high", "status": "unfixed"}
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证VCR: hss_filter_vulnerability_high应包含有高危漏洞的主机
        self.assertEqual(len(resources), 1)
        # 验证漏洞信息已添加到资源
        self.assertIn("vulnerabilities", resources[0])
    
    def test_hss_filter_vulnerability_fixed(self):
        """测试漏洞过滤器 - 已修复的漏洞"""
        factory = self.replay_flight_data("hss_filter_vulnerability_fixed")
        p = self.load_policy(
            {
                "name": "hss-hosts-with-fixed-vulnerabilities",
                "resource": "huaweicloud.hss",
                "filters": [
                    {"type": "vulnerability", "severity": "critical", "status": "fixed"}
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证VCR: hss_filter_vulnerability_fixed应包含有已修复漏洞的主机
        self.assertEqual(len(resources), 1)
        # 验证漏洞信息已添加到资源
        self.assertIn("vulnerabilities", resources[0])
    
    def test_hss_filter_combined(self):
        """测试组合多个过滤器 - 未防护且有严重漏洞的主机"""
        factory = self.replay_flight_data("hss_filter_combined")
        p = self.load_policy(
            {
                "name": "hss-unprotected-with-critical-vulnerabilities",
                "resource": "huaweicloud.hss",
                "filters": [
                    {"type": "host-status", "status": "unprotected"},
                    {"type": "vulnerability", "severity": "critical", "status": "unfixed"}
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证VCR: hss_filter_combined应包含未防护且有严重漏洞的主机
        self.assertEqual(len(resources), 1)
        # 验证防护状态(不是RUNNING)
        self.assertNotEqual(resources[0]["agent_status"], "RUNNING")
        # 验证漏洞信息已添加到资源
        self.assertIn("vulnerabilities", resources[0])
    
    def test_hss_filter_vulnerability_no_match(self):
        """测试漏洞过滤器 - 无匹配结果"""
        factory = self.replay_flight_data("hss_filter_vulnerability_no_match")
        p = self.load_policy(
            {
                "name": "hss-hosts-with-no-vulnerabilities",
                "resource": "huaweicloud.hss",
                # 使用一个不太可能匹配的组合
                "filters": [
                    {"type": "vulnerability", "severity": "critical", "status": "unfixed"}
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证VCR: hss_filter_vulnerability_no_match应该没有匹配的主机
        self.assertEqual(len(resources), 0)
    
    def test_hss_filter_value_match(self):
        """测试通用值过滤器 - 根据主机ID"""
        factory = self.replay_flight_data("hss_filter_value_match")
        # 验证VCR: 确保hss_filter_value_match中的host_id与下面匹配
        host_id_to_match = "test-host-id-123"
        p = self.load_policy(
            {
                "name": "hss-filter-by-id",
                "resource": "huaweicloud.hss",
                "filters": [{"type": "value", "key": "host_id", "value": host_id_to_match}],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证VCR: 应该找到一个匹配的主机
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["host_id"], host_id_to_match)
    
    def test_hss_filter_age(self):
        """测试主机创建时间过滤器"""
        factory = self.replay_flight_data("hss_filter_age")
        p = self.load_policy(
            {
                "name": "hss-old-hosts",
                "resource": "huaweicloud.hss",
                # 验证VCR: hss_filter_age中的主机创建时间应超过30天
                "filters": [{"type": "age", "days": 30, "op": "gt"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证VCR: 应找到一个创建时间超过30天的主机
        self.assertEqual(len(resources), 1)
        
        # 测试没有匹配的情况
        p_no_match = self.load_policy(
            {
                "name": "hss-new-hosts",
                "resource": "huaweicloud.hss",
                # 使用一个很短的时间，测试没有匹配的情况
                "filters": [{"type": "age", "days": 1, "op": "lt"}],
            },
            session_factory=factory,
        )
        resources_no_match = p_no_match.run()
        # 验证VCR: 应该没有创建时间小于1天的主机
        self.assertEqual(len(resources_no_match), 0)
    
    def test_hss_tag_filter(self):
        """测试主机标签过滤器"""
        factory = self.replay_flight_data("hss_filter_tag")
        p = self.load_policy(
            {
                "name": "hss-tagged-hosts",
                "resource": "huaweicloud.hss",
                # 验证VCR: hss_filter_tag中应包含带有environment=prod标签的主机
                "filters": [{"tag:environment": "prod"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证VCR: 应该找到一个带有指定标签的主机
        self.assertEqual(len(resources), 1)
        # 验证标签是否存在(实际格式可能需要根据华为云API返回结果调整)
        self.assertTrue(any(
            tag.get("key") == "environment" and tag.get("value") == "prod"
            for tag in resources[0].get("tags", [])
        ))
    
    def test_hss_tag_count_filter(self):
        """测试主机标签数量过滤器"""
        factory = self.replay_flight_data("hss_filter_tag_count")
        p = self.load_policy(
            {
                "name": "hss-multi-tagged-hosts",
                "resource": "huaweicloud.hss",
                # 验证VCR: hss_filter_tag_count中应包含至少有2个标签的主机
                "filters": [{"type": "tag-count", "count": 2, "op": "ge"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证VCR: 应该找到一个带有至少2个标签的主机
        self.assertEqual(len(resources), 1)
        # 验证标签数量
        self.assertTrue(len(resources[0].get("tags", [])) >= 2)

# 注意：以下测试仅作为示例，如果HSS资源目前不支持标记操作或其他操作，则可能需要在资源管理器中实现这些功能
    
    def test_hss_action_tag(self):
        """测试添加标签操作(如HSS支持)"""
        factory = self.replay_flight_data("hss_action_tag")
        p = self.load_policy(
            {
                "name": "hss-tag-hosts",
                "resource": "huaweicloud.hss",
                "filters": [{"tag:CostCenter": "absent"}],  # 只对没有此标签的主机操作
                "actions": [{"type": "tag", "key": "CostCenter", "value": "Security"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证VCR: 应该找到并标记了一个主机
        self.assertEqual(len(resources), 1)
        # 验证API调用：需要检查VCR录像带，确认调用了相应的标记API
    
    def test_hss_action_remove_tag(self):
        """测试删除标签操作(如HSS支持)"""
        factory = self.replay_flight_data("hss_action_remove_tag")
        p = self.load_policy(
            {
                "name": "hss-untag-hosts",
                "resource": "huaweicloud.hss",
                "filters": [{"tag:temporary": "present"}],  # 只对有此标签的主机操作
                "actions": [{"type": "remove-tag", "keys": ["temporary"]}],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证VCR: 应该找到并移除了一个主机的标签
        self.assertEqual(len(resources), 1)
        # 验证API调用：需要检查VCR录像带，确认调用了相应的删除标签API
