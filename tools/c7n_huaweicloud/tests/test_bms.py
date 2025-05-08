from huaweicloud_common import BaseTest


class BmsTest(BaseTest):
    """裸金属服务器资源单元测试类"""

    def test_instance_query(self):
        """测试裸金属服务器列表查询"""
        factory = self.replay_flight_data("bms_instance_query")
        p = self.load_policy(
            {"name": "list_bms_details", "resource": "huaweicloud.bms"},
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 3)

    def test_instance_stop_active(self):
        """测试停止运行中的裸金属服务器"""
        factory = self.replay_flight_data("bms_instance_stop_active")
        p = self.load_policy(
            {
                "name": "bms_instance_stop_active",
                "resource": "huaweicloud.bms",
                "filters": [
                    {
                        "type": "value",
                        "key": "id",
                        "value": "bac642b0-a9ca-4a13-b6b9-9e41b35905b6",
                    }
                ],
                "actions": [{"type": "instance-stop", "mode": "SOFT"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["id"], "bac642b0-a9ca-4a13-b6b9-9e41b35905b6")

    def test_instance_stop_shutoff(self):
        """测试停止已关机的裸金属服务器"""
        factory = self.replay_flight_data("bms_instance_stop_shutoff")
        p = self.load_policy(
            {
                "name": "bms_instance_stop_shutoff",
                "resource": "huaweicloud.bms",
                "filters": [
                    {
                        "type": "value",
                        "key": "id",
                        "value": "bac642b0-a9ca-4a13-b6b9-9e41b35905b6",
                    }
                ],
                "actions": [{"type": "instance-stop", "mode": "SOFT"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["id"], "bac642b0-a9ca-4a13-b6b9-9e41b35905b6")

    def test_instance_start_shutoff(self):
        """测试启动已关机的裸金属服务器"""
        factory = self.replay_flight_data("bms_instance_start_shutoff")
        p = self.load_policy(
            {
                "name": "bms_instance_start_shutoff",
                "resource": "huaweicloud.bms",
                "filters": [
                    {
                        "type": "value",
                        "key": "id",
                        "value": "bac642b0-a9ca-4a13-b6b9-9e41b35905b6",
                    }
                ],
                "actions": ["instance-start"],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["id"], "bac642b0-a9ca-4a13-b6b9-9e41b35905b6")

    def test_instance_start_active(self):
        """测试启动运行中的裸金属服务器"""
        factory = self.replay_flight_data("bms_instance_start_active")
        p = self.load_policy(
            {
                "name": "bms_instance_start_active",
                "resource": "huaweicloud.bms",
                "filters": [
                    {
                        "type": "value",
                        "key": "id",
                        "value": "bac642b0-a9ca-4a13-b6b9-9e41b35905b6",
                    }
                ],
                "actions": ["instance-start"],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["id"], "bac642b0-a9ca-4a13-b6b9-9e41b35905b6")

    def test_instance_reboot_active(self):
        """测试重启运行中的裸金属服务器"""
        factory = self.replay_flight_data("bms_instance_reboot_active")
        p = self.load_policy(
            {
                "name": "bms_instance_reboot_active",
                "resource": "huaweicloud.bms",
                "filters": [
                    {
                        "type": "value",
                        "key": "id",
                        "value": "bac642b0-a9ca-4a13-b6b9-9e41b35905b6",
                    }
                ],
                "actions": [{"type": "instance-reboot", "mode": "SOFT"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["id"], "bac642b0-a9ca-4a13-b6b9-9e41b35905b6")

    def test_instance_reboot_shutoff(self):
        """测试重启已关机的裸金属服务器"""
        factory = self.replay_flight_data("bms_instance_reboot_shutoff")
        p = self.load_policy(
            {
                "name": "bms_instance_reboot_shutoff",
                "resource": "huaweicloud.bms",
                "filters": [
                    {
                        "type": "value",
                        "key": "id",
                        "value": "bac642b0-a9ca-4a13-b6b9-9e41b35905b6",
                    }
                ],
                "actions": [{"type": "instance-reboot", "mode": "SOFT"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["id"], "bac642b0-a9ca-4a13-b6b9-9e41b35905b6")

    def test_fetch_job_status(self):
        """测试获取异步任务状态"""
        factory = self.replay_flight_data("bms_fetch_job_status")
        p = self.load_policy(
            {
                "name": "bms_fetch_job_status",
                "resource": "huaweicloud.bms",
                "actions": [
                    {
                        "type": "fetch-job-status",
                        "job_id": "ff8080829585af7f0195c1e776d9475c",
                    }
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)

    def test_set_instance_profile(self):
        """测试设置裸金属服务器元数据"""
        factory = self.replay_flight_data("bms_set_instance_profile")
        p = self.load_policy(
            {
                "name": "bms_set_instance_profile",
                "resource": "huaweicloud.bms",
                "filters": [
                    {
                        "type": "value",
                        "key": "id",
                        "value": "bac642b0-a9ca-4a13-b6b9-9e41b35905b6",
                    }
                ],
                "actions": [
                    {"type": "set-instance-profile", "metadata": {"key": "value"}}
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["id"], "bac642b0-a9ca-4a13-b6b9-9e41b35905b6")

    # ------------------------------ 过滤器测试 ------------------------------#

    def test_instance_age(self):
        """测试裸金属服务器创建时间过滤器"""
        factory = self.replay_flight_data("bms_instance_age")
        p = self.load_policy(
            {
                "name": "bms_instance_age",
                "resource": "huaweicloud.bms",
                "filters": [{"type": "instance-age", "op": "ge", "days": 30}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["id"], "bac642b0-a9ca-4a13-b6b9-9e41b35905b6")

    def test_instance_uptime(self):
        """测试裸金属服务器运行时间过滤器"""
        factory = self.replay_flight_data("bms_instance_uptime")
        p = self.load_policy(
            {
                "name": "bms_instance_uptime",
                "resource": "huaweicloud.bms",
                "filters": [{"type": "instance-uptime", "op": "ge", "days": 90}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["id"], "bms-test-id1")

    def test_instance_attribute(self):
        """测试裸金属服务器属性过滤器"""
        factory = self.replay_flight_data("bms_instance_attribute")
        p = self.load_policy(
            {
                "name": "bms_instance_attribute",
                "resource": "huaweicloud.bms",
                "filters": [
                    {
                        "type": "instance-attribute",
                        "attribute": "OS-EXT-SRV-ATTR:user_data",
                        "key": "Value",
                        "op": "regex",
                        "value": "(?smi).*user=",
                    }
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)

    def test_instance_image_age(self):
        """测试裸金属服务器镜像创建时间过滤器"""
        factory = self.replay_flight_data("bms_instance_image_age")
        p = self.load_policy(
            {
                "name": "bms_instance_image_age",
                "resource": "huaweicloud.bms",
                "filters": [{"type": "instance-image-age", "op": "ge", "days": 180}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["id"], "53206ed0-56de-4d6b-b7ee-ffc62ca26f43")

    def test_instance_image(self):
        """测试裸金属服务器镜像过滤器"""
        factory = self.replay_flight_data("bms_instance_image")
        p = self.load_policy(
            {
                "name": "bms_instance_image",
                "resource": "huaweicloud.bms",
                "filters": [{"type": "instance-image"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["id"], "53206ed0-56de-4d6b-b7ee-ffc62ca26f43")

    def test_instance_user_data(self):
        """测试裸金属服务器用户数据过滤器"""
        factory = self.replay_flight_data("bms_instance_user_data")
        p = self.load_policy(
            {
                "name": "bms_instance_user_data",
                "resource": "huaweicloud.bms",
                "filters": [
                    {
                        "type": "instance-user-data",
                        "op": "regex",
                        "value": "(?smi).*user=",
                    }
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)

    def test_ephemeral(self):
        """测试裸金属服务器临时存储过滤器"""
        factory = self.replay_flight_data("bms_ephemeral")
        p = self.load_policy(
            {
                "name": "bms_ephemeral",
                "resource": "huaweicloud.bms",
                "filters": [{"type": "ephemeral"}],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 0)

    def test_instance_vpc(self):
        """测试裸金属服务器VPC过滤器"""
        factory = self.replay_flight_data("bms_instance_vpc")
        p = self.load_policy(
            {
                "name": "bms_instance_vpc",
                "resource": "huaweicloud.bms",
                "filters": [
                    {
                        "type": "instance-vpc",
                    }
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["id"], "5849fdf1-9d79-4589-80c2-fe557990c417")

    def test_instance_evs(self):
        """测试裸金属服务器EVS卷过滤器"""
        factory = self.replay_flight_data("bms_instance_evs")
        p = self.load_policy(
            {
                "name": "bms_instance_evs",
                "resource": "huaweicloud.bms",
                "filters": [
                    {
                        "type": "instance-evs",
                        "key": "id",
                        "op": "eq",
                        "value": "b1ab47b2-32e2-4848-88c0-c5176b309c5c"
                    }
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["id"], "53206ed0-56de-4d6b-b7ee-ffc62ca26f43")

    def test_instance_evs_with_skip_devices(self):
        """测试裸金属服务器EVS卷过滤器(跳过特定设备)"""
        factory = self.replay_flight_data("bms_instance_evs_skip_devices")
        p = self.load_policy(
            {
                "name": "bms_instance_evs_skip_devices",
                "resource": "huaweicloud.bms",
                "filters": [
                    {
                        "type": "instance-evs",
                        "skip-devices": ["/dev/sda"],
                        "key": "size",
                        "op": "gt",
                        "value": 100
                    }
                ],
            },
            session_factory=factory,
        )
        resources = p.run()
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0]["id"], "53206ed0-56de-4d6b-b7ee-ffc62ca26f43")
