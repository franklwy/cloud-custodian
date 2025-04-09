# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import logging
import datetime
from dateutil.parser import parse

from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkdns.v2 import (
    # 公网Zone管理
    ListPublicZonesRequest,
    ShowPublicZoneRequest,
    DeletePublicZoneRequest,
    UpdatePublicZoneStatusRequest,
    UpdatePublicZoneStatusRequestBody,
    UpdatePublicZoneRequest,
    UpdatePublicZoneInfo,
    ShowPublicZoneNameServerRequest,
    
    # 内网Zone管理
    ListPrivateZonesRequest,
    ShowPrivateZoneRequest,
    DeletePrivateZoneRequest,
    UpdatePrivateZoneRequest,
    UpdatePrivateZoneInfoReq,
    AssociateRouterRequest,
    AssociateRouterRequestBody,
    DisassociateRouterRequest,
    DisassociaterouterRequestBody,
    ShowPrivateZoneNameServerRequest,
    Router,
    
    # Record Set管理
    ListRecordSetsRequest,
    ListRecordSetsByZoneRequest,
    ShowRecordSetRequest,
    DeleteRecordSetRequest,
    UpdateRecordSetRequest,
    UpdateRecordSetReq,
    SetRecordSetsStatusRequest,
    SetRecordSetsStatusRequestBody,
    
    # 批量接口管理
    BatchDeleteRecordSetsRequest,
    BatchDeleteRecordSetsRequestBody,
    BatchSetRecordSetsStatusRequest,
    BatchSetRecordSetsStatusRequestBody,
    BatchDeleteZonesRequest,
    BatchDeleteZonesRequestBody,
    BatchSetZonesStatusRequest,
    BatchSetZonesStatusRequestBody,
)

from c7n_huaweicloud.provider import resources
from c7n_huaweicloud.query import QueryResourceManager, TypeInfo
from c7n_huaweicloud.actions.base import HuaweiCloudBaseAction
from c7n.utils import type_schema, local_session
from c7n.filters import Filter, ValueFilter
from c7n.filters.core import AgeFilter

log = logging.getLogger('custodian.huaweicloud.dns')

# 公网DNS域名区域资源管理
@resources.register('dns-publiczone')
class PublicZone(QueryResourceManager):
    """华为云公网DNS托管区域资源管理器。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-publiczone-active
            resource: huaweicloud.dns-publiczone
            filters:
              - type: status
                key: status
                value: ACTIVE
    """
    
    class resource_type(TypeInfo):
        service = 'dns-publiczone'
        enum_spec = ('list_public_zones', 'zones', 'marker')
        id = 'id'
        name = 'name'
        filter_name = 'name'
        filter_type = 'scalar'
        taggable = True
        tag_resource_type = 'DNS-publiczone'
        
    def augment(self, resources):
        """增强资源信息，添加标签等。"""
        client = self.get_client()
        
        for r in resources:
            try:
                request = ShowPublicZoneRequest(zone_id=r['id'])
                response = client.show_public_zone(request)
                zone_info = response.to_dict()
                r.update(zone_info)
            except exceptions.ClientRequestException as e:
                log.warning(f"获取公网域名区域详情失败 ({r.get('name', r.get('id', 'unknown'))}): {e}")
        
        return resources


@PublicZone.filter_registry.register('status')
class PublicZoneStatusFilter(ValueFilter):
    """公网DNS域名区域状态过滤器。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-publiczone-status
            resource: huaweicloud.dns-publiczone
            filters:
              - type: status
                key: status
                value: ACTIVE
    """
    
    schema = type_schema('status', rinherit=ValueFilter.schema)
    schema_alias = True
    
    def process(self, resources, event=None):
        return [r for r in resources if self.match(r.get('status'))]


@PublicZone.filter_registry.register('age')
class PublicZoneAgeFilter(AgeFilter):
    """公网DNS域名区域创建时间过滤器。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-publiczone-old
            resource: huaweicloud.dns-publiczone
            filters:
              - type: age
                days: 90
                op: gt
    """

    schema = type_schema('age', rinherit=AgeFilter.schema)
    date_attribute = "created_at"

@PublicZone.action_registry.register('delete')
class DeletePublicZoneAction(HuaweiCloudBaseAction):
    """删除公网DNS域名区域操作。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-publiczone-delete
            resource: huaweicloud.dns-publiczone
            filters:
              - type: value
                key: name
                value: example.com.
            actions:
              - delete
    """
    
    schema = type_schema('delete')
    
    def perform_action(self, resource):
        client = self.manager.get_client()
        zone_id = resource['id']
        try:
            request = DeletePublicZoneRequest(zone_id=zone_id)
            client.delete_public_zone(request)
            self.log.info(f"成功删除公网域名区域: {resource.get('name')} (ID: {zone_id})")
        except exceptions.ClientRequestException as e:
            self.log.error(f"删除公网域名区域失败 {resource.get('name')} (ID: {zone_id}): {e}")
            raise


@PublicZone.action_registry.register('update')
class UpdatePublicZoneAction(HuaweiCloudBaseAction):
    """更新公网DNS域名区域属性操作。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-publiczone-update
            resource: huaweicloud.dns-publiczone
            filters:
              - type: value
                key: name
                value: example.com.
            actions:
              - type: update
                email: new-admin@example.com
                ttl: 7200
                description: "Updated by Cloud Custodian"
    """
    
    schema = type_schema(
        'update',
        email={'type': 'string'},
        ttl={'type': 'integer'},
        description={'type': 'string'}
    )
    
    def perform_action(self, resource):
        client = self.manager.get_client()
        zone_id = resource['id']
        
        # 构建更新参数
        email = self.data.get('email')
        ttl = self.data.get('ttl')
        description = self.data.get('description')
        
        if not any([email, ttl, description]):
            self.log.info(f"无需更新公网域名区域，未提供更新参数: {resource.get('name')} (ID: {zone_id})")
            return
        
        try:
            update_info = UpdatePublicZoneInfo()
            if email is not None:
                update_info.email = email
            if ttl is not None:
                update_info.ttl = ttl
            if description is not None:
                update_info.description = description
                
            request = UpdatePublicZoneRequest(zone_id=zone_id, body=update_info)
            client.update_public_zone(request)
            self.log.info(f"成功更新公网域名区域: {resource.get('name')} (ID: {zone_id})")
        except exceptions.ClientRequestException as e:
            self.log.error(f"更新公网域名区域失败 {resource.get('name')} (ID: {zone_id}): {e}")
            raise


@PublicZone.action_registry.register('set-status')
class SetPublicZoneStatusAction(HuaweiCloudBaseAction):
    """设置公网DNS域名区域状态操作。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-publiczone-disable
            resource: huaweicloud.dns-publiczone
            filters:
              - type: value
                key: name
                value: example.com.
            actions:
              - type: set-status
                status: DISABLE
    """
    
    schema = type_schema(
        'set-status',
        required=['status'],
        status={'type': 'string', 'enum': ['ENABLE', 'DISABLE']}
    )
    
    def perform_action(self, resource):
        client = self.manager.get_client()
        zone_id = resource['id']
        status = self.data.get('status')
        
        try:
            request_body = UpdatePublicZoneStatusRequestBody(status=status)
            request = UpdatePublicZoneStatusRequest(zone_id=zone_id, body=request_body)
            client.update_public_zone_status(request)
            self.log.info(f"成功设置公网域名区域状态为 {status}: {resource.get('name')} (ID: {zone_id})")
        except exceptions.ClientRequestException as e:
            self.log.error(f"设置公网域名区域状态失败 {resource.get('name')} (ID: {zone_id}): {e}")
            raise


# 内网DNS域名区域资源管理
@resources.register('dns-privatezone')
class PrivateZone(QueryResourceManager):
    """华为云内网DNS托管区域资源管理器。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-privatezone-active
            resource: huaweicloud.dns-privatezone
            filters:
              - type: status
                key: status
                value: ACTIVE
    """
    
    class resource_type(TypeInfo):
        service = 'dns-privatezone'
        enum_spec = ('list_private_zones', 'zones', 'marker')
        id = 'id'
        name = 'name'
        filter_name = 'name'
        filter_type = 'scalar'
        taggable = True
        tag_resource_type = 'DNS-privatezone'
        
    def augment(self, resources):
        """增强资源信息，添加标签等。"""
        client = self.get_client()
        for r in resources:
            try:
                request = ShowPrivateZoneRequest(zone_id=r['id'])
                response = client.show_private_zone(request)
                zone_info = response.to_dict()
                r.update(zone_info)
            except exceptions.ClientRequestException as e:
                log.warning(f"获取内网域名区域详情失败 ({r.get('name', r.get('id', 'unknown'))}): {e}")
        
        return resources


@PrivateZone.filter_registry.register('status')
class PrivateZoneStatusFilter(ValueFilter):
    """内网DNS域名区域状态过滤器。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-privatezone-status
            resource: huaweicloud.dns-privatezone
            filters:
              - type: status
                key: status
                value: ACTIVE
    """
    
    schema = type_schema('status', rinherit=ValueFilter.schema)
    schema_alias = True
    
    def process(self, resources, event=None):
        print(resources)
        return [r for r in resources if self.match(r.get('status'))]


@PrivateZone.filter_registry.register('vpc-associated')
class PrivateZoneVpcAssociatedFilter(Filter):
    """内网DNS域名区域关联VPC过滤器。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-privatezone-vpc
            resource: huaweicloud.dns-privatezone
            filters:
              - type: vpc-associated
                vpc_id: vpc-12345678
    """
    
    schema = type_schema(
        'vpc-associated',
        vpc_id={'type': 'string'}
    )
    
    def process(self, resources, event=None):
        vpc_id = self.data.get('vpc_id')
        if not vpc_id:
            return resources
        
        result = []
        for r in resources:
            routers = r.get('routers', [])
            for router in routers:
                if router.get('router_id') == vpc_id:
                    result.append(r)
                    break
        
        return result


@PrivateZone.filter_registry.register('age')
class PrivateZoneAgeFilter(AgeFilter):
    """内网DNS域名区域创建时间过滤器。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-privatezone-old
            resource: huaweicloud.dns-privatezone
            filters:
              - type: age
                days: 90
                op: gt
    """
    
    schema = type_schema('age', rinherit=AgeFilter.schema)
    date_attribute = "created_at"


@PrivateZone.action_registry.register('delete')
class DeletePrivateZoneAction(HuaweiCloudBaseAction):
    """删除内网DNS域名区域操作。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-privatezone-delete
            resource: huaweicloud.dns-privatezone
            filters:
              - type: value
                key: name
                value: example.com.
            actions:
              - delete
    """
    
    schema = type_schema('delete')
    
    def perform_action(self, resource):
        client = self.manager.get_client()
        zone_id = resource['id']
        try:
            request = DeletePrivateZoneRequest(zone_id=zone_id)
            client.delete_private_zone(request)
            self.log.info(f"成功删除内网域名区域: {resource.get('name')} (ID: {zone_id})")
        except exceptions.ClientRequestException as e:
            self.log.error(f"删除内网域名区域失败 {resource.get('name')} (ID: {zone_id}): {e}")
            raise


@PrivateZone.action_registry.register('update')
class UpdatePrivateZoneAction(HuaweiCloudBaseAction):
    """更新内网DNS域名区域属性操作。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-privatezone-update
            resource: huaweicloud.dns-privatezone
            filters:
              - type: value
                key: name
                value: example.com.
            actions:
              - type: update
                email: new-admin@example.com
                ttl: 7200
                description: "Updated by Cloud Custodian"
    """
    
    schema = type_schema(
        'update',
        email={'type': 'string'},
        ttl={'type': 'integer'},
        description={'type': 'string'}
    )
    
    def perform_action(self, resource):
        client = self.manager.get_client()
        zone_id = resource['id']
        
        # 构建更新参数
        email = self.data.get('email')
        ttl = self.data.get('ttl')
        description = self.data.get('description')
        
        if not any([email, ttl, description]):
            self.log.info(f"无需更新内网域名区域，未提供更新参数: {resource.get('name')} (ID: {zone_id})")
            return
        
        try:
            update_info = UpdatePrivateZoneInfoReq()
            if email is not None:
                update_info.email = email
            if ttl is not None:
                update_info.ttl = ttl
            if description is not None:
                update_info.description = description
                
            request = UpdatePrivateZoneRequest(zone_id=zone_id, body=update_info)
            client.update_private_zone(request)
            self.log.info(f"成功更新内网域名区域: {resource.get('name')} (ID: {zone_id})")
        except exceptions.ClientRequestException as e:
            self.log.error(f"更新内网域名区域失败 {resource.get('name')} (ID: {zone_id}): {e}")
            raise


@PrivateZone.action_registry.register('associate-vpc')
class AssociateVpcAction(HuaweiCloudBaseAction):
    """关联VPC到内网DNS域名区域操作。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-privatezone-associate-vpc
            resource: huaweicloud.dns-privatezone
            filters:
              - type: value
                key: name
                value: example.com.
            actions:
              - type: associate-vpc
                vpc_id: vpc-12345678
                region: cn-north-4
    """
    
    schema = type_schema(
        'associate-vpc',
        required=['vpc_id'],
        vpc_id={'type': 'string'},
        region={'type': 'string'}
    )
    
    def perform_action(self, resource):
        client = self.manager.get_client()
        zone_id = resource['id']
        vpc_id = self.data.get('vpc_id')
        region = self.data.get('region', None)
        
        try:
            router = Router(router_id=vpc_id, router_region=region)
            request_body = AssociateRouterRequestBody(router=router)
            request = AssociateRouterRequest(zone_id=zone_id, body=request_body)
            client.associate_router(request)
            self.log.info(f"成功关联VPC {vpc_id} 到内网域名区域: {resource.get('name')} (ID: {zone_id})")
        except exceptions.ClientRequestException as e:
            self.log.error(f"关联VPC到内网域名区域失败 {resource.get('name')} (ID: {zone_id}): {e}")
            raise


@PrivateZone.action_registry.register('disassociate-vpc')
class DisassociateVpcAction(HuaweiCloudBaseAction):
    """解关联VPC与内网DNS域名区域操作。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-privatezone-disassociate-vpc
            resource: huaweicloud.dns-privatezone
            filters:
              - type: value
                key: name
                value: example.com.
              - type: vpc-associated
                vpc_id: vpc-12345678
            actions:
              - type: disassociate-vpc
                vpc_id: vpc-12345678
                region: cn-north-4
    """
    
    schema = type_schema(
        'disassociate-vpc',
        required=['vpc_id'],
        vpc_id={'type': 'string'},
        region={'type': 'string'}
    )
    
    def perform_action(self, resource):
        client = self.manager.get_client()
        zone_id = resource['id']
        vpc_id = self.data.get('vpc_id')
        region = self.data.get('region', None)
        
        try:
            router = Router(router_id=vpc_id, router_region=region)
            request_body = DisassociaterouterRequestBody(router=router)
            request = DisassociateRouterRequest(zone_id=zone_id, body=request_body)
            client.disassociate_router(request)
            self.log.info(f"成功解关联VPC {vpc_id} 与内网域名区域: {resource.get('name')} (ID: {zone_id})")
        except exceptions.ClientRequestException as e:
            self.log.error(f"解关联VPC与内网域名区域失败 {resource.get('name')} (ID: {zone_id}): {e}")
            raise


# 记录集资源管理
@resources.register('dns-recordset')
class RecordSet(QueryResourceManager):
    """华为云DNS记录集资源管理器。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-recordset-a-records
            resource: huaweicloud.dns-recordset
            filters:
              - type: record-type
                value: A
    """
    
    class resource_type(TypeInfo):
        service = 'dns-recordset'
        enum_spec = ('list_record_sets', 'recordsets', 'marker')
        id = 'id'
        name = 'name'
        filter_name = 'name'
        filter_type = 'scalar'
        taggable = True
        tag_resource_type = 'DNS-recordset'
        
    def augment(self, resources):
        """增强资源信息，添加标签等。"""
        client = self.get_client()
        
        for r in resources:
            try:
                # 记录集需要zone_id来查询详情
                if 'zone_id' in r:
                    request = ShowRecordSetRequest(zone_id=r['zone_id'], recordset_id=r['id'])
                    response = client.show_record_set(request)
                    record_info = response.to_dict()
                    r.update(record_info)
            except exceptions.ClientRequestException as e:
                log.warning(f"获取记录集详情失败 ({r.get('name', r.get('id', 'unknown'))}): {e}")
        
        return resources


@RecordSet.filter_registry.register('record-type')
class RecordTypeFilter(ValueFilter):
    """DNS记录集类型过滤器。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-recordset-a-records
            resource: huaweicloud.dns-recordset
            filters:
              - type: record-type
                value: A
    """
    
    schema = type_schema('record-type', rinherit=ValueFilter.schema)
    schema_alias = True
    
    def process(self, resources, event=None):
        return [r for r in resources if self.match(r.get('type'))]


@RecordSet.filter_registry.register('zone-id')
class ZoneIdFilter(ValueFilter):
    """DNS记录集所属区域ID过滤器。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-recordset-by-zone
            resource: huaweicloud.dns-recordset
            filters:
              - type: zone-id
                value: ff8080825b8fc86c015b94bc6f8712c3
    """
    
    schema = type_schema('zone-id', rinherit=ValueFilter.schema)
    schema_alias = True
    
    def process(self, resources, event=None):
        return [r for r in resources if self.match(r.get('zone_id'))]


@RecordSet.filter_registry.register('status')
class RecordSetStatusFilter(ValueFilter):
    """DNS记录集状态过滤器。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-recordset-status-active
            resource: huaweicloud.dns-recordset
            filters:
              - type: status
                key: status
                value: ACTIVE
    """
    
    schema = type_schema('status', rinherit=ValueFilter.schema)
    schema_alias = True
    
    def process(self, resources, event=None):
        return [r for r in resources if self.match(r.get('status'))]


@RecordSet.filter_registry.register('line-id')
class LineIdFilter(ValueFilter):
    """DNS记录集线路ID过滤器。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-recordset-by-line
            resource: huaweicloud.dns-recordset
            filters:
              - type: line-id
                value: default_view
    """
    
    schema = type_schema('line-id', rinherit=ValueFilter.schema)
    schema_alias = True
    
    def process(self, resources, event=None):
        return [r for r in resources if self.match(r.get('line') or r.get('line_id'))]


@RecordSet.filter_registry.register('age')
class RecordSetAgeFilter(AgeFilter):
    """DNS记录集创建时间过滤器。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-recordset-old
            resource: huaweicloud.dns-recordset
            filters:
              - type: age
                days: 90
                op: gt
    """
    
    schema = type_schema('age', rinherit=AgeFilter.schema)
    date_attribute = "created_at"


@RecordSet.action_registry.register('delete')
class DeleteRecordSetAction(HuaweiCloudBaseAction):
    """删除DNS记录集操作。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-recordset-delete
            resource: huaweicloud.dns-recordset
            filters:
              - type: record-type
                value: TXT
            actions:
              - delete
    """
    
    schema = type_schema('delete')
    
    def perform_action(self, resource):
        client = self.manager.get_client()
        recordset_id = resource['id']
        zone_id = resource.get('zone_id')
        
        if not zone_id:
            self.log.warning(f"无法删除记录集，缺少zone_id: {resource.get('name')} (ID: {recordset_id})")
            return
        
        try:
            request = DeleteRecordSetRequest(zone_id=zone_id, recordset_id=recordset_id)
            client.delete_record_set(request)
            self.log.info(f"成功删除记录集: {resource.get('name')} (ID: {recordset_id})")
        except exceptions.ClientRequestException as e:
            self.log.error(f"删除记录集失败 {resource.get('name')} (ID: {recordset_id}): {e}")
            raise


@RecordSet.action_registry.register('update')
class UpdateRecordSetAction(HuaweiCloudBaseAction):
    """更新DNS记录集操作。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-recordset-update-ttl
            resource: huaweicloud.dns-recordset
            filters:
              - type: record-type
                value: A
              - type: value
                key: ttl
                op: lt
                value: 300
            actions:
              - type: update
                ttl: 3600
                description: "Updated by Cloud Custodian"
    """
    
    schema = type_schema(
        'update',
        ttl={'type': 'integer'},
        records={'type': 'array', 'items': {'type': 'string'}},
        description={'type': 'string'}
    )
    
    def perform_action(self, resource):
        client = self.manager.get_client()
        recordset_id = resource['id']
        zone_id = resource.get('zone_id')
        
        if not zone_id:
            self.log.warning(f"无法更新记录集，缺少zone_id: {resource.get('name')} (ID: {recordset_id})")
            return
        
        # 构建更新参数
        ttl = self.data.get('ttl')
        records = self.data.get('records')
        description = self.data.get('description')
        
        if not any([ttl, records, description]):
            self.log.info(f"无需更新记录集，未提供更新参数: {resource.get('name')} (ID: {recordset_id})")
            return
        
        try:
            update_info = UpdateRecordSetReq()
            if ttl is not None:
                update_info.ttl = ttl
            if records is not None:
                update_info.records = records
            if description is not None:
                update_info.description = description
                
            request = UpdateRecordSetRequest(zone_id=zone_id, recordset_id=recordset_id, body=update_info)
            client.update_record_set(request)
            self.log.info(f"成功更新记录集: {resource.get('name')} (ID: {recordset_id})")
        except exceptions.ClientRequestException as e:
            self.log.error(f"更新记录集失败 {resource.get('name')} (ID: {recordset_id}): {e}")
            raise


@RecordSet.action_registry.register('set-status')
class SetRecordSetStatusAction(HuaweiCloudBaseAction):
    """设置DNS记录集状态操作。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-recordset-disable
            resource: huaweicloud.dns-recordset
            filters:
              - type: record-type
                value: A
            actions:
              - type: set-status
                status: DISABLE
    """
    
    schema = type_schema(
        'set-status',
        required=['status'],
        status={'type': 'string', 'enum': ['ENABLE', 'DISABLE']}
    )
    
    def perform_action(self, resource):
        client = self.manager.get_client()
        recordset_id = resource['id']
        zone_id = resource.get('zone_id')
        status = self.data.get('status')
        
        if not zone_id:
            self.log.warning(f"无法设置记录集状态，缺少zone_id: {resource.get('name')} (ID: {recordset_id})")
            return
        
        try:
            request_body = SetRecordSetsStatusRequestBody(status=status, recordset_ids=[recordset_id])
            request = SetRecordSetsStatusRequest(zone_id=zone_id, body=request_body)
            client.set_record_sets_status(request)
            self.log.info(f"成功设置记录集状态为 {status}: {resource.get('name')} (ID: {recordset_id})")
        except exceptions.ClientRequestException as e:
            self.log.error(f"设置记录集状态失败 {resource.get('name')} (ID: {recordset_id}): {e}")
            raise


@RecordSet.action_registry.register('batch-set-status')
class BatchSetRecordSetStatusAction(HuaweiCloudBaseAction):
    """批量设置DNS记录集状态操作。
    
    :example:
    
    .. code-block:: yaml
    
        policies:
          - name: dns-recordset-batch-disable
            resource: huaweicloud.dns-recordset
            filters:
              - type: record-type
                value: A
              - type: zone-id
                value: ff8080825b8fc86c015b94bc6f8712c3
            actions:
              - type: batch-set-status
                status: DISABLE
    """
    
    schema = type_schema(
        'batch-set-status',
        required=['status'],
        status={'type': 'string', 'enum': ['ENABLE', 'DISABLE']}
    )
    
    def process(self, resources):
        client = self.manager.get_client()
        status = self.data.get('status')
        
        # 按zone_id分组处理
        zone_records = {}
        for r in resources:
            zone_id = r.get('zone_id')
            if not zone_id:
                self.log.warning(f"无法处理记录集，缺少zone_id: {r.get('name')} (ID: {r.get('id')})")
                continue
                
            if zone_id not in zone_records:
                zone_records[zone_id] = []
            zone_records[zone_id].append(r)
        
        for zone_id, records in zone_records.items():
            recordset_ids = [r['id'] for r in records]
            try:
                request_body = BatchSetRecordSetsStatusRequestBody(status=status, recordset_ids=recordset_ids)
                request = BatchSetRecordSetsStatusRequest(zone_id=zone_id, body=request_body)
                client.batch_set_record_sets_status(request)
                self.log.info(f"成功批量设置区域 {zone_id} 中 {len(recordset_ids)} 个记录集状态为 {status}")
            except exceptions.ClientRequestException as e:
                self.log.error(f"批量设置记录集状态失败，区域 {zone_id}: {e}")
                raise
                
        return resources
