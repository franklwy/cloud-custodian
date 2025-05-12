# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import logging
import base64
import json
import zlib
from concurrent.futures import as_completed

from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkbms.v1 import (
    ListBareMetalServerDetailsRequest,
    BatchStartBaremetalServersRequest,
    BatchStopBaremetalServersRequest,
    BatchRebootBaremetalServersRequest,
    OsStartBody,
    OsStopBody,
    OsStopBodyType,
    RebootBody,
    UpdateBaremetalServerMetadataRequest,
    UpdateBaremetalServerMetadataReq,
    StartServersInfo, ServersList, ServersInfoType,
    ShowBaremetalServerVolumeInfoRequest,
)

from huaweicloudsdkims.v2 import (
    ListImagesRequest,
)

from c7n import utils
from c7n.utils import type_schema, local_session
from c7n_huaweicloud.actions.base import HuaweiCloudBaseAction
from c7n_huaweicloud.provider import resources
from c7n_huaweicloud.query import QueryResourceManager, TypeInfo
from c7n.filters import AgeFilter, ValueFilter, Filter, OPERATORS
from dateutil.parser import parse

log = logging.getLogger("custodian.huaweicloud.resources.bms")


@resources.register("bms")
class Bms(QueryResourceManager):
    """华为云裸金属服务器资源

    :example:

    .. code-block:: yaml

        policies:
          - name: bms-tag-compliance
            resource: huaweicloud.bms
            filters:
              - "tag:costcenter": absent
            actions:
              - type: tag
                key: costcenter
                value: unknown
    """

    class resource_type(TypeInfo):
        service = "bms"
        enum_spec = ("list_bare_metal_servers", "servers", "offset")
        id = "id"
        tag_resource_type = "bms"


# ----------------------- BMS Filters -----------------------

@Bms.filter_registry.register("instance-age")
class BmsInstanceAgeFilter(AgeFilter):
    """BMS裸金属服务器创建时间过滤器: 大于或小于指定的阈值日期

    :Example:

    .. code-block:: yaml

        policies:
          - name: bms-instances-age
            resource: huaweicloud.bms
            filters:
              - type: instance-age
                op: ge
                days: 30
    """

    date_attribute = "created"

    schema = type_schema(
        "instance-age",
        op={"$ref": "#/definitions/filters_common/comparison_operators"},
        days={"type": "number"},
        hours={"type": "number"},
        minutes={"type": "number"},
    )


@Bms.filter_registry.register("instance-uptime")
class BmsInstanceUptimeFilter(AgeFilter):
    """过滤大于或小于给定运行时间的裸金属服务器。

    :Example:

    .. code-block:: yaml

        policies:
          - name: bms-instances-long-running
            resource: huaweicloud.bms
            filters:
              - type: instance-uptime
                op: ge
                days: 90
    """

    date_attribute = "created"

    schema = type_schema(
        "instance-uptime",
        op={"$ref": "#/definitions/filters_common/comparison_operators"},
        days={"type": "number"},
    )


@Bms.filter_registry.register("instance-attribute")
class BmsInstanceAttributeFilter(ValueFilter):
    """BMS裸金属服务器属性值过滤器。

    :Example:

    .. code-block:: yaml

        policies:
          - name: bms-instances-attribute
            resource: huaweicloud.bms
            filters:
              - type: instance-attribute
                attribute: OS-EXT-SRV-ATTR:user_data
                key: "Value"
                op: regex
                value: (?smi).*user=
    """

    valid_attrs = (
        "flavorId",
        "OS-EXT-SRV-ATTR:user_data",
        "OS-EXT-SRV-ATTR:root_device_name",
    )

    schema = type_schema(
        "instance-attribute",
        rinherit=ValueFilter.schema,
        attribute={"enum": valid_attrs},
        required=("attribute",),
    )
    schema_alias = False

    def process(self, resources, event=None):
        attribute = self.data["attribute"]
        self.get_instance_attribute(resources, attribute)
        return [
            resource
            for resource in resources
            if self.match(resource["c7n:attribute-%s" % attribute])
        ]

    def get_instance_attribute(self, resources, attribute):
        for resource in resources:
            userData = resource.get("OS-EXT-SRV-ATTR:user_data", "")
            flavorId = resource["flavor"]["id"]
            rootDeviceName = ["OS-EXT-SRV-ATTR:root_device_name"]
            attributes = {
                "OS-EXT-SRV-ATTR:user_data": {"Value": deserialize_user_data(userData)},
                "flavorId": {"Value": flavorId},
                "OS-EXT-SRV-ATTR:root_device_name": {"Value": rootDeviceName},
            }
            resource["c7n:attribute-%s" % attribute] = attributes[attribute]


class BmsInstanceImageBase:
    """裸金属服务器镜像基础类"""

    def prefetch_instance_images(self, instances):
        self.image_map = self.get_local_image_mapping(instances)

    def get_base_image_mapping(self, image_ids):
        ims_client = local_session(self.manager.session_factory).client("ims")
        request = ListImagesRequest(id=image_ids, limit=1000)
        return {i.id: i for i in ims_client.list_images(request).images}

    def get_instance_image_created_at(self, instance):
        return instance["image:created_at"]

    def get_local_image_mapping(self, instances):
        image_ids = ",".join(
            list(set(item["metadata"]["metering.image_id"] for item in instances))
        )
        base_image_map = self.get_base_image_mapping(image_ids)
        for r in instances:
            if r["metadata"]["metering.image_id"] in base_image_map.keys():
                r["image:created_at"] = base_image_map[
                    r["metadata"]["metering.image_id"]
                ].created_at
            else:
                r["image:created_at"] = "2000-01-01T01:01:01.000Z"
        return instances


@Bms.filter_registry.register("instance-image-age")
class BmsImageAgeFilter(AgeFilter, BmsInstanceImageBase):
    """BMS裸金属服务器镜像年龄过滤器

    根据镜像的创建时间过滤裸金属服务器

    :Example:

    .. code-block:: yaml

        policies:
          - name: bms-old-image
            resource: huaweicloud.bms
            filters:
              - type: instance-image-age
                op: ge
                days: 180
    """

    date_attribute = "created_at"

    schema = type_schema(
        "instance-image-age",
        op={"$ref": "#/definitions/filters_common/comparison_operators"},
        days={"type": "number"},
    )

    def process(self, resources, event=None):
        self.prefetch_instance_images(resources)
        return super(BmsImageAgeFilter, self).process(resources, event)

    def get_resource_date(self, i):
        image = self.get_instance_image_created_at(i)
        return parse(image)


@Bms.filter_registry.register("instance-image")
class BmsInstanceImageFilter(ValueFilter, BmsInstanceImageBase):
    """BMS裸金属服务器镜像过滤器

    :Example:

    .. code-block:: yaml

        policies:
          - name: bms-image-filter
            resource: huaweicloud.bms
            filters:
              - type: instance-image
    """

    schema = type_schema("instance-image", rinherit=ValueFilter.schema)
    schema_alias = False

    def process(self, resources, event=None):
        results = []
        image_ids = ",".join(
            list(item["metadata"]["metering.image_id"] for item in resources)
        )
        base_image_map = self.get_base_image_mapping(image_ids)
        for r in resources:
            if r["metadata"]["metering.image_id"] in base_image_map.keys():
                results.append(r)
        return results


def deserialize_user_data(user_data):
    """解析用户数据内容"""
    if not user_data:
        return ""
    data = base64.b64decode(user_data)
    # 尝试普通和压缩格式解码
    try:
        return data.decode("utf8")
    except UnicodeDecodeError:
        return zlib.decompress(data, 16).decode("utf8")


@Bms.filter_registry.register("instance-user-data")
class BmsInstanceUserData(ValueFilter):
    """过滤具有匹配用户数据的裸金属服务器
    
    注意: 建议使用带?sm标志的正则表达式，因为Custodian使用re.match()且用户数据可能跨多行。

    :example:

    .. code-block:: yaml

        policies:
          - name: bms-instance-user-data
            resource: huaweicloud.bms
            filters:
              - type: instance-user-data
                op: regex
                value: (?smi).*user=
            actions:
              - instance-stop
    """

    schema = type_schema("instance-user-data", rinherit=ValueFilter.schema)
    schema_alias = False
    batch_size = 50
    annotation = "OS-EXT-SRV-ATTR:user_data"

    def __init__(self, data, manager):
        super(BmsInstanceUserData, self).__init__(data, manager)
        self.data["key"] = "OS-EXT-SRV-ATTR:user_data"

    def process(self, resources, event=None):
        results = []
        with self.executor_factory(max_workers=3) as w:
            futures = {}
            for instance_set in utils.chunks(resources, self.batch_size):
                futures[w.submit(self.process_instance_user_data, instance_set)] = (
                    instance_set
                )

            for f in as_completed(futures):
                if f.exception():
                    self.log.error(
                        "处理裸金属服务器用户数据时出错 %s", f.exception()
                    )
                results.extend(f.result())
        return results

    def process_instance_user_data(self, resources):
        results = []
        client = self.manager.get_client()
        for r in resources:
            try:
                # 获取服务器详情
                request = ListBareMetalServerDetailsRequest(server_id=r["id"])
                response = client.list_bare_metal_server_details(request)
                user_data = response.server.os_ext_srv_att_ruser_data
                r[self.annotation] = deserialize_user_data(user_data) if user_data else None
            except exceptions.ClientRequestException as e:
                log.error(e.status_code, e.request_id, e.error_code, e.error_msg)
                continue

            if self.match(r):
                results.append(r)
        return results


@Bms.filter_registry.register("ephemeral")
class BmsInstanceEphemeralFilter(Filter):
    """具有临时存储的裸金属服务器

    过滤具有临时存储的裸金属服务器

    :Example:

    .. code-block:: yaml

        policies:
          - name: bms-ephemeral
            resource: huaweicloud.bms
            filters:
              - type: ephemeral

    """

    schema = type_schema("ephemeral")

    def __call__(self, i):
        return self.is_ephemeral(i)

    def is_ephemeral(self, i):
        # 检查flavor性能类型判断是否为临时存储
        from huaweicloudsdkecs.v2 import NovaShowFlavorExtraSpecsRequest

        flavorId = i["flavor"]["id"]
        request = NovaShowFlavorExtraSpecsRequest(flavor_id=flavorId)
        client = local_session(self.manager.session_factory).client("ecs")
        try:
            response = client.nova_show_flavor_extra_specs(request)
        except exceptions.ClientRequestException as e:
            log.error(e.status_code, e.request_id, e.error_code, e.error_msg)
            raise
        performancetype = response.extra_specs.get("ecs:performancetype", "")
        if performancetype in ("highio", "diskintensive"):
            return True
        return False


@Bms.filter_registry.register("instance-vpc")
class BmsInstanceVpc(Filter):
    """裸金属服务器VPC过滤器

    过滤指定VPC ID的裸金属服务器

    :Example:

    .. code-block:: yaml

       policies:
         - name: bms-vpc-filter
           resource: huaweicloud.bms
           filters:
             - type: instance-vpc
    """

    schema = type_schema("instance-vpc")
    schema_alias = False

    def process(self, resources, event=None):
        return self.get_vpcs(resources)

    def get_vpcs(self, resources):
        vpcs = self.manager.get_resource_manager("huaweicloud.vpc").resources()
        vpc_ids = {vpc["id"] for vpc in vpcs}
        return [
            resource for resource in resources
            if resource["metadata"]["vpc_id"] in vpc_ids
        ]


@Bms.filter_registry.register("instance-evs")
class BmsInstanceEvs(ValueFilter):
    """裸金属服务器挂载的EVS卷过滤器。

    过滤裸金属服务器挂载的EVS存储设备

    :Example:

    .. code-block:: yaml

       policies:
         - name: bms-instance-evs
           resource: huaweicloud.bms
           filters:
             - type: instance-evs
               key: id
               op: eq
               value: "卷ID"
    """

    schema = type_schema(
        "instance-evs",
        rinherit=ValueFilter.schema,
        **{"skip-devices": {"type": "array", "items": {"type": "string"}}}
    )
    schema_alias = False
    batch_size = 10

    def process(self, resources, event=None):
        self.skip = self.data.get("skip-devices", [])
        self.operator = self.data.get("operator", "or") == "or" and any or all
        results = []
        with self.executor_factory(max_workers=3) as w:
            futures = {}
            for instance_set in utils.chunks(resources, self.batch_size):
                futures[w.submit(self.process_instance_volumes, instance_set)] = instance_set

            for f in as_completed(futures):
                if f.exception():
                    self.log.error(
                        "处理裸金属服务器卷信息时出错 %s", f.exception()
                    )
                results.extend(f.result())
        return results

    def process_instance_volumes(self, resources):
        client = self.manager.get_client()
        results = []
        for r in resources:
            try:
                # 获取裸金属服务器卷信息
                request = ShowBaremetalServerVolumeInfoRequest(server_id=r["id"])
                response = client.show_baremetal_server_volume_info(request)
                volumes = response.volume_attachments

                if not volumes:
                    continue

                # 过滤需要跳过的设备
                if self.skip:
                    volumes = [v for v in volumes if v.device not in self.skip]

                if not volumes:
                    continue

                # 将volumes添加到资源中供匹配
                r['c7n:volumes'] = [v.to_dict() for v in volumes]
                if r['c7n:volumes']:
                    for volume in r['c7n:volumes']:
                        if self.match(volume):
                            results.append(r)
            except exceptions.ClientRequestException as e:
                log.error(f"{e.status_code}, {e.request_id}, {e.error_code}, {e.error_msg}")
                continue
        return results

    def __call__(self, r):
        volumes = r.get('c7n:volumes', [])
        if not volumes:
            return False
        return self.match(volumes)


# ----------------------- BMS Actions -----------------------

@Bms.action_registry.register("fetch-job-status")
class BmsFetchJobStatus(HuaweiCloudBaseAction):
    """获取裸金属服务器异步任务状态。

    :Example:

    .. code-block:: yaml

        policies:
          - name: bms-fetch-job-status
            resource: huaweicloud.bms
            actions:
              - type: fetch-job-status
                job_id: "异步任务ID"
    """

    schema = type_schema(
        "fetch-job-status", job_id={"type": "string"}, required=("job_id",)
    )

    def process(self, resources):
        job_id = self.data.get("job_id")
        client = self.manager.get_client()
        from huaweicloudsdkbms.v1 import ShowJobInfosRequest
        request = ShowJobInfosRequest(job_id=job_id)
        try:
            response = client.show_job_infos(request)
        except exceptions.ClientRequestException as e:
            log.error(f"{e.status_code}, {e.request_id}, {e.error_code}, {e.error_msg}")
            raise
        return json.dumps(response.to_dict())

    def perform_action(self, resource):
        return super().perform_action(resource)


@Bms.action_registry.register("instance-start")
class BmsStart(HuaweiCloudBaseAction):
    """启动裸金属服务器。

    :Example:

    .. code-block:: yaml

        policies:
          - name: start-bms-server
            resource: huaweicloud.bms
            filters:
              - type: value
                key: id
                value: "服务器ID"
            actions:
              - instance-start
    """

    valid_origin_states = ("SHUTOFF",)
    schema = type_schema("instance-start")

    def process(self, resources):
        if len(resources) > 1000:
            log.error("一次最多能启动1000个裸金属服务器")
            return

        client = self.manager.get_client()
        instances = self.filter_resources(resources, "status", self.valid_origin_states)

        if not instances:
            log.warning("没有需要启动的裸金属服务器")
            return None

        request = self.init_request(instances)
        try:
            response = client.batch_start_baremetal_servers(request)
        except exceptions.ClientRequestException as e:
            log.error(f"{e.status_code}, {e.request_id}, {e.error_code}, {e.error_msg}")
            raise
        return json.dumps(response.to_dict())

    def init_request(self, instances):
        server_ids = []
        for r in instances:
            server_ids.append(r["id"])

        server_info = StartServersInfo(servers=server_ids)
        os_start = OsStartBody(os_start=server_info)
        request = BatchStartBaremetalServersRequest(body=os_start)
        return request

    def perform_action(self, resource):
        return super().perform_action(resource)


@Bms.action_registry.register("instance-stop")
class BmsStop(HuaweiCloudBaseAction):
    """停止裸金属服务器。

    :Example:

    .. code-block:: yaml

        policies:
          - name: stop-bms-server
            resource: huaweicloud.bms
            filters:
              - type: value
                key: id
                value: "服务器ID"
            actions:
              - type: instance-stop
                mode: "SOFT"
    """

    valid_origin_states = ("ACTIVE",)
    schema = type_schema("instance-stop", mode={"type": "string"})

    def process(self, resources):
        if len(resources) > 1000:
            log.error("一次最多能停止1000个裸金属服务器")
            return

        client = self.manager.get_client()
        instances = self.filter_resources(resources, "status", self.valid_origin_states)

        if not instances:
            log.warning("没有需要停止的裸金属服务器")
            return None

        request = self.init_request(instances)
        try:
            response = client.batch_stop_baremetal_servers(request)
        except exceptions.ClientRequestException as e:
            log.error(f"{e.status_code}, {e.request_id}, {e.error_code}, {e.error_msg}")
            raise
        return json.dumps(response.to_dict())

    def init_request(self, instances):
        server_ids = []
        for r in instances:
            server_ids.append(ServersList(r["id"]))

        mode = self.data.get("mode", "SOFT")
        os_stop = OsStopBodyType(type=mode, servers=server_ids)
        body = OsStopBody(os_stop=os_stop)
        request = BatchStopBaremetalServersRequest(body=body)
        return request

    def perform_action(self, resource):
        return super().perform_action(resource)


@Bms.action_registry.register("instance-reboot")
class BmsReboot(HuaweiCloudBaseAction):
    """重启裸金属服务器。

    :Example:

    .. code-block:: yaml

        policies:
          - name: reboot-bms-server
            resource: huaweicloud.bms
            filters:
              - type: value
                key: id
                value: "服务器ID"
            actions:
              - type: instance-reboot
                mode: "SOFT"
    """

    valid_origin_states = ("ACTIVE",)
    schema = type_schema("instance-reboot", mode={"type": "string"})

    def process(self, resources):
        if len(resources) > 1000:
            log.error("一次最多能重启1000个裸金属服务器")
            return

        client = self.manager.get_client()
        instances = self.filter_resources(resources, "status", self.valid_origin_states)

        if not instances:
            log.warning("没有需要重启的裸金属服务器")
            return None

        request = self.init_request(instances)
        try:
            response = client.batch_reboot_baremetal_servers(request)
        except exceptions.ClientRequestException as e:
            log.error(f"{e.status_code}, {e.request_id}, {e.error_code}, {e.error_msg}")
            raise
        return json.dumps(response.to_dict())

    def init_request(self, instances):
        server_ids = []
        for r in instances:
            server_ids.append(ServersList(r["id"]))

        mode = self.data.get("mode", "SOFT")
        os_reboot = ServersInfoType(type=mode, servers=server_ids)
        reboot = RebootBody(reboot=os_reboot)
        request = BatchRebootBaremetalServersRequest(body=reboot)
        return request

    def perform_action(self, resource):
        return super().perform_action(resource)


@Bms.action_registry.register("set-instance-profile")
class BmsSetInstanceProfile(HuaweiCloudBaseAction):
    """设置裸金属服务器的元数据。

    :Example:

    .. code-block:: yaml

        policies:
          - name: set-bms-profile
            resource: huaweicloud.bms
            filters:
              - type: value
                key: id
                value: "服务器ID"
            actions:
              - type: set-instance-profile
                metadata:
                  key1: value1
                  key2: value2
    """

    schema = type_schema("set-instance-profile", metadata={"type": "object"})

    def perform_action(self, resource):
        client = self.manager.get_client()
        metadata = self.data.get("metadata", None)
        if not metadata:
            log.warning("未提供元数据")
            return None

        metadata_req = UpdateBaremetalServerMetadataReq(metadata=metadata)
        request = UpdateBaremetalServerMetadataRequest(
            server_id=resource["id"], body=metadata_req
        )
        try:
            response = client.update_baremetal_server_metadata(request)
            return response
        except exceptions.ClientRequestException as e:
            log.error(f"{e.status_code}, {e.request_id}, {e.error_code}, {e.error_msg}")
            raise
