# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import logging
from c7n.filters import Filter
from c7n.utils import type_schema, local_session, chunks
from c7n_huaweicloud.provider import resources
from c7n_huaweicloud.query import QueryResourceManager, TypeInfo
from c7n_huaweicloud.actions.base import HuaweiCloudBaseAction
# from c7n_huaweicloud.utils import PageResource
from huaweicloudsdkhss.v5 import *
from huaweicloudsdkcore import exceptions

log = logging.getLogger('custodian.huaweicloud.hss')

@resources.register('hss')
class HSS(QueryResourceManager):
    """华为云主机安全服务(HSS)资源管理器
    
    :example:

    .. code-block:: yaml

        policies:
          - name: hss-protection-status
            resource: huaweicloud.hss
            filters:
              - type: host-status
                status: unprotected
    """
    
    class resource_type(TypeInfo):
        service = 'hss'
        enum_spec = ('list_host_status', 'data_list', None)  # 使用ListHostStatus API
        id = 'host_id'
        name = 'host_name'
        filter_name = 'host_id'
        filter_type = 'scalar'
        taggable = True
        tag_resource_type = 'hss'

    def augment(self, resources):
        """补充资源信息"""
        client = self.get_client()
        
        for r in resources:
            try:
                # 补充主机详细信息
                host_id = r['host_id']
                request = ListHostStatusRequest(host_id=host_id)
                response = client.list_host_status(request)
                r.update(response.to_dict())
            except exceptions.ClientRequestException as e:
                log.warning(
                    f"获取主机详情失败 ({r.get('host_name', r.get('host_id', 'unknown'))}): {e}"
                )
        return resources

@HSS.filter_registry.register('host-status')
class HostStatusFilter(Filter):
    """主机防护状态过滤器

    :example:

    .. code-block:: yaml

        policies:
          - name: hss-unprotected-hosts
            resource: huaweicloud.hss
            filters:
              - type: host-status
                status: unprotected
    """

    schema = type_schema(
        'host-status',
        status={'type': 'string', 'enum': ['protected', 'unprotected']}
    )

    def process(self, resources, event=None):
        status = self.data.get('status', 'unprotected')
        return [r for r in resources if self._check_protection_status(r) == status]

    def _check_protection_status(self, resource):
        """检查主机防护状态"""
        # 根据HSS API文档,检查主机防护状态
        protection_status = resource.get('agent_status')
        if protection_status == 'RUNNING':
            return 'protected'
        return 'unprotected'

@HSS.filter_registry.register('vulnerability')
class VulnerabilityFilter(Filter):
    """过滤具有指定严重程度和状态的漏洞的主机。

    :example:

    .. code-block:: yaml

        policies:
          - name: hss-hosts-with-critical-vulnerabilities
            resource: huaweicloud.hss
            filters:
              - type: vulnerability
                severity: critical
                status: unfixed
    """

    schema = type_schema(
        'vulnerability',
        required=['severity'],
        severity={'type': 'string', 'enum': ['critical', 'high', 'medium', 'low']},
        status={'type': 'string', 'enum': ['unfixed', 'fixed']}
    )

    def _get_severity_level(self, severity):
        severity_map = {
            'critical': '4',
            'high': '3',
            'medium': '2',
            'low': '1'
        }
        return severity_map.get(severity.lower())

    def process(self, resources, event=None):
        client = local_session(self.manager.session_factory).client()
        severity_level = self._get_severity_level(self.data['severity'])
        status = self.data.get('status', 'unfixed')
        
        matched = []
        for resource in resources:
            try:
                request = ListVulnerabilitiesRequest()
                request.host_id = resource['host_id']
                request.severity = severity_level
                request.status = 1 if status == 'unfixed' else 2
                
                response = client.list_vulnerabilities(request)
                vulnerabilities = response.vulnerabilities
                
                if vulnerabilities:
                    resource['vulnerabilities'] = vulnerabilities
                    matched.append(resource)
                    
            except exceptions.ClientRequestException as e:
                log.warning(f"获取主机 {resource['host_id']} 的漏洞信息失败: {str(e)}")
                continue
                
        return matched
