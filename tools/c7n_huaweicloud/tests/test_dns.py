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
        self.assertEqual(len(resources), 1) # 假设录像带中有1个公网Zone
        self.assertEqual(resources[0]["name"], "example.com.") # 假设名称
        self.assertTrue("description" in resources[0]) # 验证 augment 添加了信息

    def test_public_zone_filter_age_match(self):
        """测试公网Zone Age过滤器 - 匹配"""
        factory = self.replay_flight_data("dns_public_zone_filter_age")
        p = self.load_policy(
            {
                "name": "dns-public-zone-filter-age-match",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"type": "age", "days": 90, "op": "ge"}], # 假设 Zone >= 90 天
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
                "filters": [{"type": "age", "days": 1, "op": "lt"}], # 假设 Zone >= 90 天
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 0)

    def test_public_zone_action_delete(self):
        """测试删除公网Zone操作"""
        factory = self.replay_flight_data("dns_public_zone_action_delete")
        zone_id_to_delete = "zone_id_from_cassette" # 从录像带中获取要删除的Zone ID
        zone_name_to_delete = "delete.example.com." # 从录像带中获取要删除的Zone Name
        p = self.load_policy(
            {
                "name": "dns-public-zone-action-delete",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"id": zone_id_to_delete}],
                "actions": ["delete"],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]['id'], zone_id_to_delete)
        self.assertEqual(resources[0]['name'], zone_name_to_delete)
        # 验证：检查 VCR 录像带确认调用了 DeletePublicZoneRequest

    def test_public_zone_action_update(self):
        """测试更新公网Zone操作"""
        factory = self.replay_flight_data("dns_public_zone_action_update")
        zone_id_to_update = "zone_id_from_cassette" # 从录像带中获取要更新的Zone ID
        new_email = "updated-admin@example.com"
        new_ttl = 3600
        p = self.load_policy(
            {
                "name": "dns-public-zone-action-update",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"id": zone_id_to_update}],
                "actions": [{"type": "update", "email": new_email, "ttl": new_ttl}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]['id'], zone_id_to_update)
        # 验证：检查 VCR 录像带确认调用了 UpdatePublicZoneRequest，并包含正确的参数

    def test_public_zone_action_set_status_disable(self):
        """测试设置公网Zone状态为DISABLE"""
        factory = self.replay_flight_data("dns_public_zone_action_set_status_disable")
        zone_id_to_disable = "zone_id_from_cassette" # 从录像带获取
        p = self.load_policy(
            {
                "name": "dns-public-zone-action-disable",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"id": zone_id_to_disable}],
                "actions": [{"type": "set-status", "status": "DISABLE"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]['id'], zone_id_to_disable)
        # 验证：检查 VCR 录像带确认调用了 UpdatePublicZoneStatusRequest，status=DISABLE

    def test_public_zone_action_set_status_enable(self):
        """测试设置公网Zone状态为ENABLE"""
        factory = self.replay_flight_data("dns_public_zone_action_set_status_enable")
        zone_id_to_enable = "zone_id_from_cassette" # 从录像带获取
        p = self.load_policy(
            {
                "name": "dns-public-zone-action-enable",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"id": zone_id_to_enable, "status": "DISABLE"}], # 假设先过滤出已禁用的
                "actions": [{"type": "set-status", "status": "ENABLE"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]['id'], zone_id_to_enable)
        # 验证：检查 VCR 录像带确认调用了 UpdatePublicZoneStatusRequest，status=ENABLE


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
        self.assertEqual(len(resources), 1) # 假设录像带中有1个内网Zone
        self.assertEqual(resources[0]["name"], "internal.example.com.") # 假设名称
        self.assertTrue("routers" in resources[0]) # 验证 augment 添加了信息

    def test_private_zone_filter_vpc_associated_match(self):
        """测试内网Zone关联VPC过滤器 - 匹配"""
        factory = self.replay_flight_data("dns_private_zone_filter_vpc")
        vpc_id_associated = "vpc_id_from_cassette" # 从录像带获取关联的VPC ID
        p = self.load_policy(
            {
                "name": "dns-private-zone-filter-vpc-match",
                "resource": "huaweicloud.dns-privatezone",
                "filters": [{"type": "vpc-associated", "vpc_id": vpc_id_associated}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)

    def test_private_zone_filter_vpc_associated_no_match(self):
        """测试内网Zone关联VPC过滤器 - 不匹配"""
        factory = self.replay_flight_data("dns_private_zone_filter_vpc") # 复用录像带
        vpc_id_not_associated = "vpc_id_not_in_cassette" # 一个未关联的VPC ID
        p = self.load_policy(
            {
                "name": "dns-private-zone-filter-vpc-no-match",
                "resource": "huaweicloud.dns-privatezone",
                "filters": [{"type": "vpc-associated", "vpc_id": vpc_id_not_associated}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 0)

    def test_private_zone_filter_age(self):
        """测试内网Zone Age过滤器"""
        factory = self.replay_flight_data("dns_private_zone_filter_age")
        p = self.load_policy(
            {
                "name": "dns-private-zone-filter-age",
                "resource": "huaweicloud.dns-privatezone",
                "filters": [{"type": "age", "days": 30, "op": "gt"}], # 假设 Zone > 30 天
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1) # 假设匹配

    def test_private_zone_action_delete(self):
        """测试删除内网Zone操作"""
        factory = self.replay_flight_data("dns_private_zone_action_delete")
        zone_id_to_delete = "private_zone_id_from_cassette" # 从录像带获取
        p = self.load_policy(
            {
                "name": "dns-private-zone-action-delete",
                "resource": "huaweicloud.dns-privatezone",
                "filters": [{"id": zone_id_to_delete}],
                "actions": ["delete"],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]['id'], zone_id_to_delete)
        # 验证：检查 VCR 录像带确认调用了 DeletePrivateZoneRequest

    def test_private_zone_action_update(self):
        """测试更新内网Zone操作"""
        factory = self.replay_flight_data("dns_private_zone_action_update")
        zone_id_to_update = "private_zone_id_from_cassette" # 从录像带获取
        new_ttl = 1800
        p = self.load_policy(
            {
                "name": "dns-private-zone-action-update",
                "resource": "huaweicloud.dns-privatezone",
                "filters": [{"id": zone_id_to_update}],
                "actions": [{"type": "update", "ttl": new_ttl, "description": "Updated"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]['id'], zone_id_to_update)
        # 验证：检查 VCR 录像带确认调用了 UpdatePrivateZoneRequest

    def test_private_zone_action_associate_vpc(self):
        """测试关联VPC到内网Zone操作"""
        factory = self.replay_flight_data("dns_private_zone_action_associate_vpc")
        zone_id_to_associate = "private_zone_id_from_cassette" # 从录像带获取
        vpc_id_to_associate = "vpc_id_to_associate_from_cassette"
        vpc_region = "cn-north-4" # 假设区域
        p = self.load_policy(
            {
                "name": "dns-private-zone-associate-vpc",
                "resource": "huaweicloud.dns-privatezone",
                "filters": [{"id": zone_id_to_associate}],
                "actions": [{"type": "associate-vpc", "vpc_id": vpc_id_to_associate, "region": vpc_region}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]['id'], zone_id_to_associate)
        # 验证：检查 VCR 录像带确认调用了 AssociateRouterRequest

    def test_private_zone_action_disassociate_vpc(self):
        """测试解关联VPC与内网Zone操作"""
        factory = self.replay_flight_data("dns_private_zone_action_disassociate_vpc")
        zone_id_to_disassociate = "private_zone_id_from_cassette" # 从录像带获取
        vpc_id_to_disassociate = "vpc_id_to_disassociate_from_cassette"
        vpc_region = "cn-north-4" # 假设区域
        p = self.load_policy(
            {
                "name": "dns-private-zone-disassociate-vpc",
                "resource": "huaweicloud.dns-privatezone",
                "filters": [
                    {"id": zone_id_to_disassociate},
                    {"type": "vpc-associated", "vpc_id": vpc_id_to_disassociate} # 确保已关联
                ],
                "actions": [{"type": "disassociate-vpc", "vpc_id": vpc_id_to_disassociate, "region": vpc_region}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]['id'], zone_id_to_disassociate)
        # 验证：检查 VCR 录像带确认调用了 DisassociateRouterRequest


class RecordSetTest(BaseTest):
    """测试DNS记录集资源、过滤器和操作"""

    def test_record_set_query(self):
        """测试记录集查询和augment"""
        # 注意：ListRecordSetsRequest 可能不直接返回 zone_id
        # augment 依赖 zone_id 查询详情。
        # 这里的测试假设录像带中的 ListRecordSets 响应包含了 zone_id，
        # 或者 augment 能够优雅处理缺失 zone_id 的情况（如跳过或只返回基本信息）。
        # 或者测试策略应该先过滤特定 zone_id。
        # 为简单起见，我们假设录像带数据包含 zone_id。
        factory = self.replay_flight_data("dns_record_set_query")
        p = self.load_policy(
            {
                "name": "dns-record-set-query",
                "resource": "huaweicloud.dns-recordset",
                # 可以添加 filter 过滤特定 zone, 确保 augment 有 zone_id
                # "filters": [{"zone_id": "zone_id_from_cassette"}]
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertGreater(len(resources), 0) # 假设至少有一个记录集
        # 假设录像带中第一个记录集有 augment 添加的 description
        self.assertTrue("description" in resources[0])

    def test_record_set_filter_record_type(self):
        """测试记录集类型过滤器"""
        factory = self.replay_flight_data("dns_record_set_filter_type")
        p = self.load_policy(
            {
                "name": "dns-record-set-filter-type-a",
                "resource": "huaweicloud.dns-recordset",
                "filters": [{"type": "record-type", "value": "A"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertGreater(len(resources), 0) # 假设有A记录
        for r in resources:
            self.assertEqual(r['type'], 'A')

    def test_record_set_filter_zone_id(self):
        """测试记录集Zone ID过滤器"""
        factory = self.replay_flight_data("dns_record_set_filter_zone_id")
        target_zone_id = "zone_id_from_cassette"
        p = self.load_policy(
            {
                "name": "dns-record-set-filter-zone-id",
                "resource": "huaweicloud.dns-recordset",
                "filters": [{"type": "zone-id", "value": target_zone_id}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertGreater(len(resources), 0)
        for r in resources:
            self.assertEqual(r['zone_id'], target_zone_id)

    def test_record_set_filter_line_id(self):
        """测试记录集线路ID过滤器"""
        factory = self.replay_flight_data("dns_record_set_filter_line_id")
        target_line_id = "default_line_id_from_cassette" # 或其他线路ID
        p = self.load_policy(
            {
                "name": "dns-record-set-filter-line-id",
                "resource": "huaweicloud.dns-recordset",
                "filters": [{"type": "line-id", "value": target_line_id}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertGreater(len(resources), 0)
        for r in resources:
            # API 可能返回 'line' 或 'line_id'，过滤器处理了这种情况
            self.assertTrue(r.get('line') == target_line_id or r.get('line_id') == target_line_id)

    def test_record_set_filter_age(self):
        """测试记录集Age过滤器"""
        factory = self.replay_flight_data("dns_record_set_filter_age")
        p = self.load_policy(
            {
                "name": "dns-record-set-filter-age",
                "resource": "huaweicloud.dns-recordset",
                "filters": [{"type": "age", "days": 7, "op": "le"}], # 假设记录 <= 7 天
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertGreater(len(resources), 0) # 假设匹配

    def test_record_set_action_delete(self):
        """测试删除记录集操作"""
        factory = self.replay_flight_data("dns_record_set_action_delete")
        recordset_id_to_delete = "recordset_id_from_cassette"
        zone_id_for_delete = "zone_id_for_recordset_from_cassette"
        p = self.load_policy(
            {
                "name": "dns-record-set-action-delete",
                "resource": "huaweicloud.dns-recordset",
                "filters": [
                    {"id": recordset_id_to_delete},
                    {"zone_id": zone_id_for_delete} # 确保资源有zone_id
                 ],
                "actions": ["delete"],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]['id'], recordset_id_to_delete)
        # 验证：检查 VCR 确认调用了 DeleteRecordSetRequest

    def test_record_set_action_update(self):
        """测试更新记录集操作"""
        factory = self.replay_flight_data("dns_record_set_action_update")
        recordset_id_to_update = "recordset_id_from_cassette"
        zone_id_for_update = "zone_id_for_recordset_from_cassette"
        new_ttl = 600
        new_records = ["192.0.2.100", "192.0.2.101"] # 假设更新A记录
        p = self.load_policy(
            {
                "name": "dns-record-set-action-update",
                "resource": "huaweicloud.dns-recordset",
                "filters": [
                    {"id": recordset_id_to_update},
                    {"zone_id": zone_id_for_update}
                ],
                "actions": [{"type": "update", "ttl": new_ttl, "records": new_records}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]['id'], recordset_id_to_update)
        # 验证：检查 VCR 确认调用了 UpdateRecordSetRequest

    def test_record_set_action_set_status(self):
        """测试设置单个记录集状态"""
        factory = self.replay_flight_data("dns_record_set_action_set_status")
        recordset_id_to_set = "recordset_id_from_cassette"
        zone_id_for_set = "zone_id_for_recordset_from_cassette"
        target_status = "DISABLE"
        p = self.load_policy(
            {
                "name": "dns-record-set-action-set-status",
                "resource": "huaweicloud.dns-recordset",
                "filters": [
                    {"id": recordset_id_to_set},
                    {"zone_id": zone_id_for_set}
                ],
                "actions": [{"type": "set-status", "status": target_status}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]['id'], recordset_id_to_set)
        # 验证：检查 VCR 确认调用了 SetRecordSetsStatusRequest (注意是复数形式的API)

    def test_record_set_action_batch_set_status(self):
        """测试批量设置记录集状态"""
        factory = self.replay_flight_data("dns_record_set_action_batch_set_status")
        zone_id_for_batch = "zone_id_for_batch_from_cassette"
        target_status = "ENABLE"
        # 假设录像带中该 zone_id 下有多个记录集需要被设置为 ENABLE
        p = self.load_policy(
            {
                "name": "dns-record-set-action-batch-set-status",
                "resource": "huaweicloud.dns-recordset",
                "filters": [
                    {"zone_id": zone_id_for_batch},
                    {"status": "DISABLE"} # 假设筛选出需要启用的记录
                ],
                "actions": [{"type": "batch-set-status", "status": target_status}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertGreater(len(resources), 1) # 假设批量操作了多个资源
        # 验证：检查 VCR 确认调用了 BatchSetRecordSetsStatusRequest，并检查 recordset_ids 列表


# =========================
# 可复用功能测试 (以 PublicZone 为例)
# =========================

class ReusableFeaturesTest(BaseTest):
    """测试可复用的Filters和Actions在DNS资源上的应用"""

    def test_filter_value_match(self):
        """测试 value 过滤器 - 匹配"""
        factory = self.replay_flight_data("dns_public_zone_filter_value_email")
        target_email = "admin@example.com" # 假设录像带中Zone的email是这个
        p = self.load_policy(
            {
                "name": "dns-filter-value-email-match",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"type": "value", "key": "email", "value": target_email}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
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
        self.assertEqual(len(resources), 0)

    def test_filter_list_item_match(self):
        """测试 list-item 过滤器 - 匹配 (假设tags列表)"""
        # 需要录像带中Zone有 "Tags": [{"Key": "project", "Value": "apollo"}]
        factory = self.replay_flight_data("dns_public_zone_filter_list_item_tag")
        p = self.load_policy(
            {
                "name": "dns-filter-list-item-tag-match",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [
                    {
                        "type": "list-item",
                        "key": "Tags", # 注意这里用的是 augment 后的 Tags
                        "attrs": [
                            {"type": "value", "key": "Key", "value": "project"},
                            {"type": "value", "key": "Value", "value": "apollo"}
                        ]
                    }
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)

    # 注：event, reduce 过滤器的测试比较复杂，通常需要特定的事件或聚合场景，此处省略

    def test_filter_marked_for_op_match(self):
        """测试 marked-for-op 过滤器 - 匹配"""
        # 需要录像带中Zone有标记: 'custodian_cleanup': 'delete@YYYY-MM-DDTHH:MM:SSZ' 且已过期
        factory = self.replay_flight_data("dns_public_zone_filter_marked_for_op")
        p = self.load_policy(
            {
                "name": "dns-filter-marked-for-op-delete-match",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"type": "marked-for-op", "op": "delete", "tag": "custodian_cleanup"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)

    def test_filter_tag_count_match(self):
        """测试 tag-count 过滤器 - 匹配"""
        # 需要录像带中Zone有2个标签
        factory = self.replay_flight_data("dns_public_zone_filter_tag_count")
        p = self.load_policy(
            {
                "name": "dns-filter-tag-count-match",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"type": "tag-count", "count": 2}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)

    def test_filter_tms_match(self):
        """测试 tms 过滤器 - 匹配"""
        # 需要录像带中Zone有标签: {"environment": "production"}
        factory = self.replay_flight_data("dns_public_zone_filter_tms")
        p = self.load_policy(
            {
                "name": "dns-filter-tms-match",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"tag:environment": "production"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)

    def test_filter_tms_absent(self):
        """测试 tms 过滤器 - 标签不存在"""
        factory = self.replay_flight_data("dns_public_zone_filter_tms") # 复用
        p = self.load_policy(
            {
                "name": "dns-filter-tms-absent",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"tag:nonexistent_tag": "absent"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1) # 应该匹配，因为标签确实不存在


    def test_action_tag(self):
        """测试 tag 操作 - 添加新标签"""
        factory = self.replay_flight_data("dns_public_zone_action_tag")
        zone_id_to_tag = "zone_id_from_cassette"
        tag_key = "CostCenter"
        tag_value = "Finance"
        p = self.load_policy(
            {
                "name": "dns-action-tag",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"id": zone_id_to_tag}],
                "actions": [{"type": "tag", "key": tag_key, "value": tag_value}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 验证: 检查 VCR 确认调用了 CreateTag 或 BatchCreateTag API

    def test_action_remove_tag(self):
        """测试 remove-tag 操作 - 删除标签"""
        # 需要录像带中Zone有标签: {"Department": "IT"}
        factory = self.replay_flight_data("dns_public_zone_action_remove_tag")
        zone_id_to_untag = "zone_id_from_cassette"
        tag_to_remove = "Department"
        p = self.load_policy(
            {
                "name": "dns-action-remove-tag",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [
                    {"id": zone_id_to_untag},
                    {f"tag:{tag_to_remove}": "present"}
                 ],
                "actions": [{"type": "remove-tag", "keys": [tag_to_remove]}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 验证: 检查 VCR 确认调用了 DeleteTag 或 BatchCreateTag (带删除动作) API

    # def test_action_rename_tag(self):
    #     """测试 rename-tag 操作 (需要开发)"""
    #     # 需要录像带中Zone有标签: {"old_key": "some_value"}
    #     factory = self.replay_flight_data("dns_public_zone_action_rename_tag")
    #     zone_id_to_rename = "zone_id_from_cassette"
    #     old_key = "old_key"
    #     new_key = "new_key"
    #     p = self.load_policy(
    #         {
    #             "name": "dns-action-rename-tag",
    #             "resource": "huaweicloud.dns-publiczone",
    #             "filters": [
    #                 {"id": zone_id_to_rename},
    #                 {f"tag:{old_key}": "present"}
    #             ],
    #             "actions": [{"type": "rename-tag", "old_key": old_key, "new_key": new_key}],
    #         },
    #         session_factory=factory,
    #     )
    #     resources = p.run()
    #     self.assertEqual(len(resources), 1)
    #     # 验证: 检查 VCR 确认调用了删除旧标签和添加新标签的 API

    def test_action_mark_for_op(self):
        """测试 mark-for-op 操作"""
        factory = self.replay_flight_data("dns_public_zone_action_mark_for_op")
        zone_id_to_mark = "zone_id_from_cassette"
        tag_key = "custodian_mark_delete"
        days = 3
        p = self.load_policy(
            {
                "name": "dns-action-mark-for-op",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [{"id": zone_id_to_mark}],
                "actions": [{"type": "mark-for-op", "op": "delete", "tag": tag_key, "days": days}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 验证: 检查 VCR 确认调用了打标签的 API，标签值包含正确的时间戳

    def test_action_auto_tag_user(self):
        """测试 auto-tag-user 操作"""
        # 需要 augment 后的资源字典包含 "creator" 或 "user_name" 等字段，或者有相关事件信息
        # 此处假设 augment 未提供创建者信息，将打上 "unknown"
        factory = self.replay_flight_data("dns_public_zone_action_auto_tag_user")
        zone_id_to_auto_tag = "zone_id_from_cassette"
        tag_key = "Creator"
        p = self.load_policy(
            {
                "name": "dns-action-auto-tag-user",
                "resource": "huaweicloud.dns-publiczone",
                "filters": [
                    {"id": zone_id_to_auto_tag},
                    {f"tag:{tag_key}": "absent"} # 只对未标记的资源操作
                 ],
                "actions": [{"type": "auto-tag-user", "tag": tag_key, "update": False}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        # 验证: 检查 VCR 确认调用了打标签 API，标签值为 "unknown" (或实际用户名)
