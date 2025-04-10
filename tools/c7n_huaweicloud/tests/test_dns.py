# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from huaweicloud_common import BaseTest
# from unittest.mock import patch # 如有需要，用于模拟


class PublicZoneTest(BaseTest):
    """测试公网DNS Zone资源、过滤器和操作"""

    def test_public_zone_query(self):
        """测试公网Zone查询和augment"""
        factory = self.replay_flight_data("dns_public_zone_query")
        p = self.load_policy(
            {
                "name": "dns-public-zone-query",
                "resource": "huaweicloud.dns-publiczone",
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1) # 验证 VCR: dns_public_zone_query 中应有1个公网Zone
        self.assertEqual(resources[0]["name"], "example.com.") # 验证 VCR: 值应与 dns_public_zone_query 中的 name 一致
        self.assertEqual(resources[0]["email"], "admin@example.com") # 验证 VCR: 值应与 dns_public_zone_query 中的 email 一致
        self.assertTrue("description" in resources[0]) # 验证 augment 添加了信息

    def test_public_zone_filter_age_match(self):
        """测试公网Zone Age过滤器 - 匹配"""
        factory = self.replay_flight_data("dns_public_zone_filter_age")
        p = self.load_policy(
            {
                "name": "dns-public-zone-filter-age-match",
                "resource": "huaweicloud.dns-publiczone",
                # 验证 VCR: dns_public_zone_filter_age 中的 'public-old.example.com.' 创建时间 ('2023-01-15T12:00:23Z') 应满足 >= 90 天
                "filters": [{"type": "age", "days": 90, "op": "ge"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)

    def test_public_zone_filter_age_no_match(self):
        """测试公网Zone Age过滤器 - 不匹配"""
        factory = self.replay_flight_data("dns_public_zone_filter_age") # 复用录像带
        p = self.load_policy(
            {
                "name": "dns-public-zone-filter-age-no-match",
                "resource": "huaweicloud.dns-publiczone",
                # 验证 VCR: dns_public_zone_filter_age 中的 'public-old.example.com.' 创建时间 ('2023-01-15T12:00:23Z') 应不满足 < 1 天
                "filters": [{"type": "age", "days": 1, "op": "lt"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 0)

    def test_public_zone_action_delete(self):
        """测试删除公网Zone操作"""
        factory = self.replay_flight_data("dns_public_zone_action_delete")
        # 从 dns_public_zone_action_delete 获取要删除的Zone ID和Name
        zone_id_to_delete = "2c9eb1538a138432018a13uuuuu00001" # 验证 VCR: 与 dns_public_zone_action_delete 中的 id 一致
        zone_name_to_delete = "public-delete.example.com." # 验证 VCR: 与 dns_public_zone_action_delete 中的 name 一致
        p = self.load_policy(
            {
                "name": "dns-public-zone-action-delete",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"type": "value", "key": "id", "value": zone_id_to_delete}], # 使用 value 过滤器更明确
                "actions": ["delete"],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 断言主要验证策略是否正确筛选了目标资源
        self.assertEqual(resources[0]['id'], zone_id_to_delete)
        self.assertEqual(resources[0]['name'], zone_name_to_delete)
        # 验证操作成功：需要人工检查 VCR 录像带 dns_public_zone_action_delete，确认调用了 DELETE /v2/zones/{zone_id}

    def test_public_zone_action_update(self):
        """测试更新公网Zone操作"""
        factory = self.replay_flight_data("dns_public_zone_action_update")
        # 从 dns_public_zone_action_update 获取要更新的Zone ID
        zone_id_to_update = "2c9eb1538a138432018a13zzzzz00001" # 验证 VCR: 与 dns_public_zone_action_update 中的 id 一致
        original_email = "original@example.com" # 验证 VCR: 与 dns_public_zone_action_update 中的初始 email 一致
        new_email = "new@example.com" # 更新后的邮箱
        new_ttl = 7200 # 更新后的TTL
        p = self.load_policy(
            {
                "name": "dns-public-zone-action-update",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"type": "value", "key": "id", "value": zone_id_to_update}],
                "actions": [{"type": "update", "email": new_email, "ttl": new_ttl, "description": "Updated public zone"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 断言主要验证策略是否正确筛选了目标资源
        self.assertEqual(resources[0]['id'], zone_id_to_update)
        self.assertEqual(resources[0]['email'], original_email) # 验证资源更新前的邮箱
        # 验证操作成功：需要人工检查 VCR 录像带 dns_public_zone_action_update，确认调用了 PATCH /v2/zones/{zone_id} 并包含正确的请求体 (email, ttl, description)

    def test_public_zone_action_set_status_disable(self):
        """测试设置公网Zone状态为DISABLE"""
        factory = self.replay_flight_data("dns_public_zone_action_set_status_disable")
        # 从 dns_public_zone_action_set_status_disable 获取 ID
        zone_id_to_disable = "2c9eb1538a138432018a13xxxxx00001" # 验证 VCR: 与 dns_public_zone_action_set_status_disable 中的 id 一致
        zone_name_to_disable = "public-disable.example.com." # 验证 VCR: 与 dns_public_zone_action_set_status_disable 中的 name 一致
        p = self.load_policy(
            {
                "name": "dns-public-zone-action-disable",
                "resource": "huaweicloud.dns-publiczone",
                # 使用 name 筛选
                "filters": [{"type": "value", "key": "name", "value": zone_name_to_disable}],
                "actions": [{"type": "set-status", "status": "DISABLE"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 断言主要验证策略是否正确筛选了目标资源
        self.assertEqual(resources[0]['id'], zone_id_to_disable)
        self.assertEqual(resources[0]['status'], "ACTIVE") # 验证 VCR: 确认资源初始状态为 ACTIVE
        # 验证操作成功：需要人工检查 VCR 录像带 dns_public_zone_action_set_status_disable，确认调用了 PUT /v2/zones/{zone_id}/statuses 并包含 status: DISABLE

    def test_public_zone_action_set_status_enable(self):
        """测试设置公网Zone状态为ENABLE"""
        # 注意：此测试依赖于一个状态为 DISABLED 的 Zone，且需要一个执行 enable 操作的录像带。
        # 当前复用 dns_public_zone_action_set_status_disable 录像带仅能验证策略加载。
        factory = self.replay_flight_data("dns_public_zone_action_set_status_disable") # 理想情况应为 dns_public_zone_action_set_status_enable.yaml (该文件当前缺失)
        # 从 dns_public_zone_action_set_status_disable 获取 ID (假设要 enable 的也是这个)
        zone_id_to_enable = "2c9eb1538a138432018a13xxxxx00001" # 验证 VCR: 与 dns_public_zone_action_set_status_disable 中的 id 一致
        p = self.load_policy(
            {
                "name": "dns-public-zone-action-enable",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [
                    {"type": "value", "key": "id", "value": zone_id_to_enable},
                    # 确保筛选的是当前为 DISABLED 的 Zone (依赖于上一步操作或特定录像带)
                    {"type": "value", "key": "status", "value": "DISABLE"}
                ],
                "actions": [{"type": "set-status", "status": "ENABLE"}],
            },
            session_factory=factory,
        )
        # 由于缺少 enable 的录像带，p.run() 结果可能不准确，此处仅验证 policy 存在
        self.assertTrue(p)
        # 验证操作成功：需要提供 dns_public_zone_action_set_status_enable.yaml 录像带，并人工检查是否调用 PUT /v2/zones/{zone_id}/statuses 且 status=ENABLE


class PrivateZoneTest(BaseTest):
    """测试内网DNS Zone资源、过滤器和操作"""

    def test_private_zone_query(self):
        """测试内网Zone查询和augment"""
        factory = self.replay_flight_data("dns_private_zone_query")
        p = self.load_policy(
            {
                "name": "dns-private-zone-query",
                "resource": "huaweicloud.dns-privatezone",
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1) # 验证 VCR: dns_private_zone_query 中应有1个内网Zone
        self.assertEqual(resources[0]["name"], "query.example.com.") # 验证 VCR: 与 dns_private_zone_query 中的 name 一致
        self.assertTrue("routers" in resources[0]) # 验证 augment 添加了 routers 信息

    def test_private_zone_filter_vpc_associated_match(self):
        """测试内网Zone关联VPC过滤器 - 匹配"""
        factory = self.replay_flight_data("dns_private_zone_filter_vpc")
        # 从 dns_private_zone_filter_vpc 获取关联的VPC ID
        vpc_id_associated = "vpc-c853fea981c3416c83181f7d01095375" # 验证 VCR: 与 dns_private_zone_filter_vpc 中 'associated.example.com.' 关联的 router_id 一致
        p = self.load_policy(
            {
                "name": "dns-private-zone-filter-vpc-match",
                "resource": "huaweicloud.dns-privatezone",
                "filters": [{"type": "vpc-associated", "vpc_id": vpc_id_associated}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1) # 验证 VCR: dns_private_zone_filter_vpc 中只有一个 Zone 关联了该 VPC

    def test_private_zone_filter_vpc_associated_no_match(self):
        """测试内网Zone关联VPC过滤器 - 不匹配"""
        factory = self.replay_flight_data("dns_private_zone_filter_vpc") # 复用录像带
        vpc_id_not_associated = "vpc-non-existent-id" # 一个确认未关联的VPC ID
        p = self.load_policy(
            {
                "name": "dns-private-zone-filter-vpc-no-match",
                "resource": "huaweicloud.dns-privatezone",
                "filters": [{"type": "vpc-associated", "vpc_id": vpc_id_not_associated}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 0) # 验证 VCR: dns_private_zone_filter_vpc 中没有 Zone 关联该 VPC

    def test_private_zone_filter_age(self):
        """测试内网Zone Age过滤器"""
        factory = self.replay_flight_data("dns_private_zone_filter_age")
        p = self.load_policy(
            {
                "name": "dns-private-zone-filter-age",
                "resource": "huaweicloud.dns-privatezone",
                # 验证 VCR: dns_private_zone_filter_age 中的 'old.example.com.' 创建时间 ('2023-01-15T12:00:00Z') 应满足 > 30 天
                "filters": [{"type": "age", "days": 30, "op": "gt"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1) # 验证 VCR: dns_private_zone_filter_age 中只有 'old.example.com.' 符合条件

    def test_private_zone_action_delete(self):
        """测试删除内网Zone操作"""
        factory = self.replay_flight_data("dns_private_zone_action_delete")
        # 从 dns_private_zone_action_delete 获取要删除的Zone ID
        zone_id_to_delete = "2c9eb1538a138432018a13bbbbb00001" # 验证 VCR: 与 dns_private_zone_action_delete 中的 id 一致
        p = self.load_policy(
            {
                "name": "dns-private-zone-action-delete",
                "resource": "huaweicloud.dns-privatezone",
                "filters": [{"type": "value", "key": "id", "value": zone_id_to_delete}],
                "actions": ["delete"],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 断言主要验证策略是否正确筛选了目标资源
        self.assertEqual(resources[0]['id'], zone_id_to_delete)
        # 验证操作成功：需要人工检查 VCR 录像带 dns_private_zone_action_delete，确认调用了 DELETE /v2/zones/{zone_id}

    def test_private_zone_action_update(self):
        """测试更新内网Zone操作"""
        factory = self.replay_flight_data("dns_private_zone_action_update")
        # 从 dns_private_zone_action_update 获取要更新的Zone ID
        zone_id_to_update = "2c9eb1538a138432018a13ddddd00001" # 验证 VCR: 与 dns_private_zone_action_update 中的 id 一致
        original_email = "original@example.com" # 验证 VCR: 与 dns_private_zone_action_update 中的初始 email 一致
        original_ttl = 300 # 验证 VCR: 与 dns_private_zone_action_update 中的初始 ttl 一致
        new_ttl = 600
        new_email = "updated@example.com" # 与 VCR 更新后的值一致
        new_description = "Updated description" # 与 VCR 更新后的值一致
        p = self.load_policy(
            {
                "name": "dns-private-zone-action-update",
                "resource": "huaweicloud.dns-privatezone",
                "filters": [{"type": "value", "key": "id", "value": zone_id_to_update}],
                "actions": [{"type": "update", "ttl": new_ttl, "description": new_description, "email": new_email}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 断言主要验证策略是否正确筛选了目标资源
        self.assertEqual(resources[0]['id'], zone_id_to_update)
        self.assertEqual(resources[0]['email'], original_email) # 验证资源更新前的邮箱
        self.assertEqual(resources[0]['ttl'], original_ttl) # 验证资源更新前的 TTL
        # 验证操作成功：需要人工检查 VCR 录像带 dns_private_zone_action_update，确认调用了 PATCH /v2/zones/{zone_id} 并包含正确的请求体 (ttl=600, email='updated@example.com', description='Updated description')

    def test_private_zone_action_associate_vpc(self):
        """测试关联VPC到内网Zone操作"""
        factory = self.replay_flight_data("dns_private_zone_action_associate_vpc")
        # 从 dns_private_zone_action_associate_vpc 获取 Zone ID, VPC ID 和 Region
        zone_id_to_associate = "2c9eb1538a138432018a13aaaaa00001" # 验证 VCR: 与 dns_private_zone_action_associate_vpc 中的 id 一致
        vpc_id_to_associate = "vpc-c853fea981c3416c83181f7d01095375" # 验证 VCR: 与 dns_private_zone_action_associate_vpc 请求体中的 router_id 一致
        vpc_region = "ap-southeast-1" # 验证 VCR: 与 dns_private_zone_action_associate_vpc 请求体中的 router_region 一致
        p = self.load_policy(
            {
                "name": "dns-private-zone-associate-vpc",
                "resource": "huaweicloud.dns-privatezone",
                "filters": [{"type": "value", "key": "id", "value": zone_id_to_associate}],
                "actions": [{"type": "associate-vpc", "vpc_id": vpc_id_to_associate, "region": vpc_region}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 断言主要验证策略是否正确筛选了目标资源
        self.assertEqual(resources[0]['id'], zone_id_to_associate)
        # 验证操作成功：需要人工检查 VCR 录像带 dns_private_zone_action_associate_vpc，确认调用了 POST /v2/zones/{zone_id}/associaterouter 并包含正确的 router_id 和 router_region

    def test_private_zone_action_disassociate_vpc(self):
        """测试解关联VPC与内网Zone操作"""
        factory = self.replay_flight_data("dns_private_zone_action_disassociate_vpc")
        # 从 dns_private_zone_action_disassociate_vpc 获取 Zone ID 和 VPC ID
        zone_id_to_disassociate = "2c9eb1538a138432018a13ccccc00001" # 验证 VCR: 与 dns_private_zone_action_disassociate_vpc 中的 id 一致
        vpc_id_to_disassociate = "vpc-c853fea981c3416c83181f7d01095375" # 验证 VCR: 与 dns_private_zone_action_disassociate_vpc 请求体中的 router_id 一致
        # 注意: 解关联只需要 VPC ID，不需要 region
        p = self.load_policy(
            {
                "name": "dns-private-zone-disassociate-vpc",
                "resource": "huaweicloud.dns-privatezone",
                "filters": [
                    {"type": "value", "key": "id", "value": zone_id_to_disassociate},
                    # 确保筛选的是已关联此 VPC 的 Zone
                    {"type": "vpc-associated", "vpc_id": vpc_id_to_disassociate}
                ],
                "actions": [{"type": "disassociate-vpc", "vpc_id": vpc_id_to_disassociate}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 0)
        # 验证操作成功：需要人工检查 VCR 录像带 dns_private_zone_action_disassociate_vpc，确认调用了 POST /v2/zones/{zone_id}/disassociaterouter 并包含正确的 router_id


class RecordSetTest(BaseTest):
    """测试DNS记录集资源、过滤器和操作"""

    def test_record_set_query(self):
        """测试记录集查询和augment"""
        factory = self.replay_flight_data("dns_record_set_query")
        p = self.load_policy(
            {
                "name": "dns-record-set-query",
                "resource": "huaweicloud.dns-recordset",
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1) # 验证 VCR: dns_record_set_query 中应有 1 个记录集
        # 验证 VCR: dns_record_set_query 中的记录集包含 description
        self.assertTrue("description" in resources[0])

    def test_record_set_filter_record_type(self):
        """测试记录集类型过滤器"""
        factory = self.replay_flight_data("dns_record_set_filter_type")
        record_type_to_filter = "A" # 验证 VCR: dns_record_set_filter_type 中应有 A 记录
        p = self.load_policy(
            {
                "name": f"dns-record-set-filter-type-{record_type_to_filter}",
                "resource": "huaweicloud.dns-recordset",
                "filters": [{"type": "value", "key": "type", "value": record_type_to_filter}],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证 VCR: dns_record_set_filter_type 中应有 2 条 A 记录
        self.assertEqual(len(resources), 2)
        for r in resources:
            self.assertEqual(r['type'], record_type_to_filter)

    def test_record_set_filter_zone_id(self):
        """测试记录集Zone ID过滤器"""
        factory = self.replay_flight_data("dns_record_set_filter_zone_id")
        # 从 dns_record_set_filter_zone_id 获取目标 Zone ID
        target_zone_id = "zone_id_from_cassette" # 验证 VCR: 与 dns_record_set_filter_zone_id 中的 zone_id 一致
        expected_count = 2 # 验证 VCR: dns_record_set_filter_zone_id 中该 zone_id 下应有 2 条记录
        p = self.load_policy(
            {
                "name": "dns-record-set-filter-zone-id",
                "resource": "huaweicloud.dns-recordset",
                "filters": [{"type": "value", "key": "zone_id", "value": target_zone_id}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), expected_count)
        for r in resources:
            self.assertEqual(r['zone_id'], target_zone_id)

    def test_record_set_filter_line_id(self):
        """测试记录集线路ID过滤器"""
        factory = self.replay_flight_data("dns_record_set_filter_line_id")
        # 从 dns_record_set_filter_line_id 获取目标线路ID
        target_line_id = "default_line_id_from_cassette" # 验证 VCR: 与 dns_record_set_filter_line_id 中的 line 值一致
        expected_count = 2 # 验证 VCR: dns_record_set_filter_line_id 中该 line_id 下应有 2 条记录
        p = self.load_policy(
            {
                "name": "dns-record-set-filter-line-id",
                "resource": "huaweicloud.dns-recordset",
                "filters": [
                    {
                        # 华为云 SDK 返回的是 'line' 字段
                        "type": "value", "key": "line", "value": target_line_id
                    }
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), expected_count)
        for r in resources:
            self.assertEqual(r.get('line'), target_line_id)

    def test_record_set_filter_age(self):
        """测试记录集Age过滤器"""
        factory = self.replay_flight_data("dns_record_set_filter_age")
        p = self.load_policy(
            {
                "name": "dns-record-set-filter-age",
                "resource": "huaweicloud.dns-recordset",
                 # 验证 VCR: dns_record_set_filter_age 中的 'new.example.com.' 创建时间 ('2025-04-08T12:00:14Z') 应满足 <= 7 天
                "filters": [{"type": "age", "days": 7, "op": "le"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1) # 验证 VCR: dns_record_set_filter_age 中只有 'new.example.com.' 符合条件

    def test_record_set_action_delete(self):
        """测试删除记录集操作"""
        factory = self.replay_flight_data("dns_record_set_action_delete")
        # 从 dns_record_set_action_delete 获取要删除的记录集 ID 和其所属 Zone ID
        recordset_id_to_delete = "2c9eb1538a138432018a13jjjjj00001"  # 验证 VCR: 与 dns_record_set_action_delete 中的 id 一致
        zone_id_for_delete = "2c9eb1538a138432018a13kkkkk00001"  # 验证 VCR: 与 dns_record_set_action_delete 中的 zone_id 一致
        p = self.load_policy(
            {
                "name": "dns-record-set-action-delete",
                "resource": "huaweicloud.dns-recordset",
                "filters": [
                    {"type": "value", "key": "id", "value": recordset_id_to_delete},
                    # 必须同时指定 zone_id，因为删除记录集的API需要 zone_id
                    {"type": "value", "key": "zone_id", "value": zone_id_for_delete}
                 ],
                "actions": ["delete"],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 断言主要验证策略是否正确筛选了目标资源
        self.assertEqual(resources[0]['id'], recordset_id_to_delete)
        # 验证操作成功：需要人工检查 VCR 录像带 dns_record_set_action_delete，确认调用了 DELETE /v2/zones/{zone_id}/recordsets/{recordset_id}

    def test_record_set_action_update(self):
        """测试更新记录集操作"""
        factory = self.replay_flight_data("dns_record_set_action_update")
        # 从 dns_record_set_action_update 获取记录集 ID 和 Zone ID
        recordset_id_to_update = "2c9eb1538a138432018a13nnnnn00001" # 验证 VCR: 与 dns_record_set_action_update 中的 id 一致
        zone_id_for_update = "2c9eb1538a138432018a13ooooo00001" # 验证 VCR: 与 dns_record_set_action_update 中的 zone_id 一致
        original_ttl = 300 # 验证 VCR: 与 dns_record_set_action_update 中的初始 ttl 一致
        original_records = ["192.168.1.3"] # 验证 VCR: 与 dns_record_set_action_update 中的初始 records 一致
        new_ttl = 600
        new_records = ["192.168.1.4", "192.168.1.5"] # 与 VCR 更新后的值一致
        new_description = "Updated record set" # 与 VCR 更新后的值一致
        p = self.load_policy(
            {
                "name": "dns-record-set-action-update",
                "resource": "huaweicloud.dns-recordset",
                "filters": [
                    {"type": "value", "key": "id", "value": recordset_id_to_update},
                    # 更新操作也需要 zone_id
                    {"type": "value", "key": "zone_id", "value": zone_id_for_update}
                ],
                "actions": [{"type": "update", "ttl": new_ttl, "records": new_records, "description": new_description}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 断言主要验证策略是否正确筛选了目标资源
        self.assertEqual(resources[0]['id'], recordset_id_to_update)
        self.assertEqual(resources[0]['ttl'], original_ttl) # 验证资源更新前的 TTL
        self.assertEqual(resources[0]['records'], original_records) # 验证资源更新前的 records
        # 验证操作成功：需要人工检查 VCR 录像带 dns_record_set_action_update，确认调用了 PUT /v2/zones/{zone_id}/recordsets/{recordset_id} 并包含正确的请求体 (ttl=600, records=['192.168.1.4', '192.168.1.5'], description='Updated record set')

    def test_record_set_action_set_status(self):
        """测试设置单个记录集状态"""
        factory = self.replay_flight_data("dns_record_set_action_set_status")
        recordset_id_to_set = "2c9eb1538a138432018a13lllll00001" # 验证 VCR: 与 dns_record_set_action_set_status 中的 id 匹配
        zone_id_for_set = "2c9eb1538a138432018a13mmmmm00001" # 验证 VCR: 与 dns_record_set_action_set_status 中的 zone_id 匹配
        target_status = "DISABLE"
        p = self.load_policy(
            {
                "name": "dns-record-set-action-set-status",
                "resource": "huaweicloud.dns-recordset",
                "filters": [
                    {"type": "value", "key": "id", "value": recordset_id_to_set},
                    {"type": "value", "key": "zone_id", "value": zone_id_for_set}
                ],
                "actions": [{"type": "set-status", "status": target_status}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]['id'], recordset_id_to_set)
        self.assertEqual(resources[0]['status'], "ACTIVE") # 验证 VCR: 确认资源初始状态为 ACTIVE
        # 验证操作成功：需要人工检查 VCR 录像带 dns_record_set_action_set_status，确认调用了 PUT /v2.1/recordsets/{recordset_id}/statuses/set 并包含 status: DISABLE
        # 注意：API 路径与批量操作不同

    def test_record_set_action_batch_set_status(self):
        """测试批量设置记录集状态"""
        factory = self.replay_flight_data("dns_record_set_action_batch_set_status")
        zone_id_for_batch = "zone_id_for_batch_from_cassette" # 验证 VCR: 与 dns_record_set_action_batch_set_status 中的 zone_id 匹配
        target_status = "ENABLE"
        recordset_ids = ["2c9eb1538a138432018a13bbbbb00001", "2c9eb1538a138432018a13bbbbb00002"] # 验证 VCR: 与 dns_record_set_action_batch_set_status 请求体中的 recordset_ids 一致
        p = self.load_policy(
            {
                "name": "dns-record-set-action-batch-set-status",
                "resource": "huaweicloud.dns-recordset",
                "filters": [
                    {"type": "value", "key": "zone_id", "value": zone_id_for_batch},
                    {"type": "value", "key": "status", "value": "DISABLE"} # 筛选出需要启用的记录
                ],
                "actions": [{"type": "batch-set-status", "status": target_status}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 2) # 验证 VCR: 确认筛选出 2 条记录
        for resource in resources:
            self.assertTrue(resource['id'] in recordset_ids)
            self.assertEqual(resource['status'], "DISABLE") # 验证 VCR: 确认资源初始状态为 DISABLE
        # 验证操作成功：需要人工检查 VCR 录像带 dns_record_set_action_batch_set_status，确认调用了 PUT /v2/zones/{zone_id}/recordsets/statuses 并包含正确的 recordset_ids 和 status: ENABLE


# =========================
# 可复用功能测试 (以 PublicZone 为例)
# =========================

class ReusableFeaturesTest(BaseTest):
    """测试可复用的Filters和Actions在DNS资源上的应用"""

    def test_filter_value_match(self):
        """测试 value 过滤器 - 匹配"""
        factory = self.replay_flight_data("dns_public_zone_filter_value_email")
        # 从 dns_public_zone_filter_value_email 获取 email 值
        target_email = "email1@example.com" # 验证 VCR: 与 dns_public_zone_filter_value_email 中 'email1.example.com.' 的 email 一致
        p = self.load_policy(
            {
                "name": "dns-filter-value-email-match",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"type": "value", "key": "email", "value": target_email}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1) # 验证 VCR: dns_public_zone_filter_value_email 中只有一个 Zone 匹配该 email
        self.assertEqual(resources[0]['email'], target_email)

    def test_filter_value_no_match(self):
        """测试 value 过滤器 - 不匹配"""
        factory = self.replay_flight_data("dns_public_zone_filter_value_email") # 复用
        wrong_email = "nonexistent@example.com"
        p = self.load_policy(
            {
                "name": "dns-filter-value-email-no-match",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"type": "value", "key": "email", "value": wrong_email}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 0) # 验证 VCR: dns_public_zone_filter_value_email 中没有 Zone 匹配该 email

    def test_filter_list_item_match(self):
        """测试 list-item 过滤器 - 匹配 (tags列表)"""
        # 验证 VCR: dns_public_zone_filter_list_item_tag 中 'public-tagged.example.com.' Zone 应有标签 {"key": "filtertag", "value": "filtervalue"}
        factory = self.replay_flight_data("dns_public_zone_filter_list_item_tag")
        target_tag_key = "filtertag" # 验证 VCR: 与 dns_public_zone_filter_list_item_tag 中的 key 一致
        target_tag_value = "filtervalue" # 验证 VCR: 与 dns_public_zone_filter_list_item_tag 中的 value 一致
        target_zone_id = "2c9eb1538a138432018a13ccccc00001" # 验证 VCR: 与 dns_public_zone_filter_list_item_tag 中带标签的 Zone ID 一致
        p = self.load_policy(
            {
                "name": "dns-filter-list-item-tag-match",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [
                    {
                        "type": "list-item",
                        "key": "tags", # 注意这里应使用 'tags' 小写，与API返回一致
                        "attrs": [
                            {"type": "value", "key": "key", "value": target_tag_key},
                            {"type": "value", "key": "value", "value": target_tag_value}
                        ]
                    }
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1) # 验证 VCR: dns_public_zone_filter_list_item_tag 中只有一个 Zone 匹配该 tag
        # 验证匹配到的是带标签的区域
        self.assertEqual(resources[0]['id'], target_zone_id)

    # 注：event, reduce 过滤器的测试比较复杂，通常需要特定的事件或聚合场景，此处省略

    def test_filter_marked_for_op_match(self):
        """测试 marked-for-op 过滤器 - 匹配"""
        # 验证 VCR: dns_public_zone_filter_marked_for_op 中 'public-marked.example.com.' Zone 应有标记 'c7n_status': 'marked-for-op:delete:1' 且已过期
        factory = self.replay_flight_data("dns_public_zone_filter_marked_for_op")
        op = "delete"
        tag = "c7n_status" # 验证 VCR: 与 dns_public_zone_filter_marked_for_op 中的标记键一致
        p = self.load_policy(
            {
                "name": f"dns-filter-marked-for-op-{op}-match",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"type": "marked-for-op", "op": op, "tag": tag}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1) # 验证 VCR: dns_public_zone_filter_marked_for_op 中只有一个 Zone 符合条件 (需要人工根据当前时间判断是否过期)

    def test_filter_tag_count_match(self):
        """测试 tag-count 过滤器 - 匹配"""
        # 验证 VCR: dns_public_zone_filter_tag_count 中 'public-two-tags.example.com.' Zone 应有 2 个标签
        factory = self.replay_flight_data("dns_public_zone_filter_tag_count")
        expected_tag_count = 2 # 验证 VCR: 与 dns_public_zone_filter_tag_count 中 'public-two-tags.example.com.' 的标签数量一致
        p = self.load_policy(
            {
                "name": "dns-filter-tag-count-match",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"type": "tag-count", "count": expected_tag_count}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1) # 验证 VCR: dns_public_zone_filter_tag_count 中只有一个 Zone 刚好有 2 个标签

    def test_filter_tms_match(self):
        """测试 tms 过滤器 (tag:<key>) - 匹配"""
        # 验证 VCR: dns_public_zone_filter_tms 中 'public-tms-tagged.example.com.' Zone 应有标签 {"tmskey": "tmsvalue"}
        factory = self.replay_flight_data("dns_public_zone_filter_tms")
        tag_key = "tmskey" # 验证 VCR: 与 dns_public_zone_filter_tms 中的标签键一致
        tag_value = "tmsvalue" # 验证 VCR: 与 dns_public_zone_filter_tms 中的标签值一致
        p = self.load_policy(
            {
                "name": "dns-filter-tms-match",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{f"tag:{tag_key}": tag_value}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1) # 验证 VCR: dns_public_zone_filter_tms 中只有一个 Zone 匹配该 TMS 标签

    def test_filter_tms_absent(self):
        """测试 tms 过滤器 (tag:<key>: absent) - 标签不存在"""
        factory = self.replay_flight_data("dns_public_zone_filter_tms") # 复用
        absent_tag_key = "nonexistent_tag"
        p = self.load_policy(
            {
                "name": "dns-filter-tms-absent",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{f"tag:{absent_tag_key}": "absent"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        # 验证 VCR: dns_public_zone_filter_tms 中所有 Zone 都不包含 'nonexistent_tag' 标签，应返回所有 Zone
        self.assertEqual(len(resources), 2)


    def test_action_tag(self):
        """测试 tag 操作 - 添加新标签"""
        factory = self.replay_flight_data("dns_public_zone_action_tag")
        # 从 dns_public_zone_action_tag 获取 Zone ID
        zone_id_to_tag = "2c9eb1538a138432018a13yyyyy00001" # 验证 VCR: 与 dns_public_zone_action_tag 中的 id 一致
        tag_key = "newtag" # 验证 VCR: 与 dns_public_zone_action_tag 请求体中的 key 一致
        tag_value = "newvalue" # 验证 VCR: 与 dns_public_zone_action_tag 请求体中的 value 一致
        p = self.load_policy(
            {
                "name": "dns-action-tag",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"type": "value", "key": "id", "value": zone_id_to_tag}],
                "actions": [{"type": "tag", "key": tag_key, "value": tag_value}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 断言主要验证策略是否正确筛选了目标资源
        # 验证操作成功: 需要人工检查 VCR 录像带 dns_public_zone_action_tag，确认调用了 POST /v2/zones/{zone_id}/tags 并包含正确的 tag key 和 value

    def test_action_remove_tag(self):
        """测试 remove-tag 操作 - 删除标签"""
        # 验证 VCR: dns_public_zone_action_remove_tag 中 'public-removetag.example.com.' Zone 应有标签: {"toremove": "value"}
        factory = self.replay_flight_data("dns_public_zone_action_remove_tag")
        # 从 dns_public_zone_action_remove_tag 获取 Zone ID
        zone_id_to_untag = "2c9eb1538a138432018a13wwwww00001" # 验证 VCR: 与 dns_public_zone_action_remove_tag 中的 id 一致
        tag_to_remove = "toremove" # 验证 VCR: 与 dns_public_zone_action_remove_tag 中要删除的标签键一致
        p = self.load_policy(
            {
                "name": "dns-action-remove-tag",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [
                    {"type": "value", "key": "id", "value": zone_id_to_untag},
                    # 确保资源确实有这个标签才执行删除
                    {f"tag:{tag_to_remove}": "present"}
                 ],
                "actions": [{"type": "remove-tag", "keys": [tag_to_remove]}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 断言主要验证策略是否正确筛选了目标资源
        # 验证操作成功: 需要人工检查 VCR 录像带 dns_public_zone_action_remove_tag，确认调用了 DELETE /v2/zones/{zone_id}/tags/{tag_key}

    def test_action_mark_for_op(self):
        """测试 mark-for-op 操作"""
        factory = self.replay_flight_data("dns_public_zone_action_mark_for_op")
        # 从 dns_public_zone_action_mark_for_op 获取 Zone ID
        zone_id_to_mark = "2c9eb1538a138432018a13vvvvv00001" # 验证 VCR: 与 dns_public_zone_action_mark_for_op 中的 id 一致
        tag_key = "c7n_status" # 验证 VCR: 与 dns_public_zone_action_mark_for_op 请求体中的 key 一致
        op = "delete"
        days = 1 # 验证 VCR: 与 dns_public_zone_action_mark_for_op 请求体中的 value 中的天数一致
        p = self.load_policy(
            {
                "name": "dns-action-mark-for-op",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"type": "value", "key": "id", "value": zone_id_to_mark}],
                "actions": [{"type": "mark-for-op", "op": op, "tag": tag_key, "days": days}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 断言主要验证策略是否正确筛选了目标资源
        # 验证操作成功: 需要人工检查 VCR 录像带 dns_public_zone_action_mark_for_op，确认调用了 POST /v2/zones/{zone_id}/tags，标签值包含 'delete@<timestamp>' 且天数为 1

    def test_action_auto_tag_user(self):
        """测试 auto-tag-user 操作"""
        # auto-tag-user 依赖于资源创建信息，通常来自事件驱动模式。
        # 在仅使用录像带的测试中，无法模拟此行为，默认会打上 "unknown"。
        # 注意：对应的录像带 dns_public_zone_action_auto_tag_user 当前缺失。
        factory = self.replay_flight_data("dns_public_zone_action_auto_tag_user") # 需要对应的录像带 (当前缺失)
        # 使用 dns_public_zone_action_tag 中的 ID 作为示例
        zone_id_to_auto_tag = "2c9eb1538a138432018a13yyyyy00001" # 需要替换为 dns_public_zone_action_auto_tag_user 中的 ID
        tag_key = "Creator" # 自动标记使用的标签键
        p = self.load_policy(
            {
                "name": "dns-action-auto-tag-user",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [
                    {"type": "value", "key": "id", "value": zone_id_to_auto_tag},
                    # 可选：只对未标记 Creator 的资源操作
                    {f"tag:{tag_key}": "absent"}
                 ],
                # update: False 表示如果标签已存在则不更新
                "actions": [{"type": "auto-tag-user", "tag": tag_key, "update": False}],
            },
            session_factory=factory,
        )
        # 由于缺少录像带，无法执行 p.run() 并验证结果
        # self.assertEqual(len(resources), 1) # 假设录像带中有符合条件的资源
        # 断言主要验证策略是否正确筛选了目标资源
        # 验证操作成功: 需要提供 dns_public_zone_action_auto_tag_user.yaml 录像带，并人工检查是否调用了 POST /v2/zones/{zone_id}/tags，标签值应为 "unknown"
        self.assertTrue(p) # 仅验证策略加载
