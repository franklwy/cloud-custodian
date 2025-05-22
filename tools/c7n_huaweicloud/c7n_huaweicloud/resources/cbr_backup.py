import logging
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkcbr.v1 import DeleteBackupRequest
from huaweicloudsdkcbr.v1 import ListBackupsRequest, ListVaultRequest, CreateVaultRequest, \
    CreateCheckpointRequest
from huaweicloudsdkecs.v2 import ListServersDetailsRequest
from huaweicloudsdkecs.v2.region.ecs_region import EcsRegion
from huaweicloudsdkcbr.v1.region.cbr_region import CbrRegion

from c7n.utils import type_schema, local_session
from c7n_huaweicloud.actions.base import HuaweiCloudBaseAction
from c7n_huaweicloud.provider import resources
from c7n_huaweicloud.query import QueryResourceManager, TypeInfo

log = logging.getLogger("custodian.huaweicloud.resources.cbr-backup")


@resources.register('cbr-backup')
class CbrBackup(QueryResourceManager):
    class resource_type(TypeInfo):
        service = 'cbr-backup'
        enum_spec = ('list_backups', 'backups', 'offset')
        id = 'id'
        tag_resource_type = ''


@CbrBackup.action_registry.register('delete')
class CbrDeleteBackup(HuaweiCloudBaseAction):
    """Checks if a recovery point is encrypted.Delete the recovery point not encrypted.

    WARNING: Deleted backups are unrecoverable forever.

    : Example:

    .. code-block:: yaml

        policies:
            - name: delete-unencrypted-backup
              resource: huaweicloud.cbr-backup
              filters:
                - and:
                  - type: value
                    key: extend_info.encrypted
                    value: false
                  - type: value
                    key: resource_type
                    value: "OS::Cinder::Volume"
              actions:
                  - delete
    """
    schema = type_schema('delete')

    def perform_action(self, resource):
        client = self.manager.get_client()
        try:
            request = DeleteBackupRequest()
            request.backup_id = resource['id']
            response = client.delete_backup(request)
        except exceptions.ClientRequestException as e:
            log.error(e.status_code, e.request_id, e.error_code, e.error_msg)
            raise
        return response


@CbrBackup.action_registry.register('backup-ecs')
class CbrBackupEcs(HuaweiCloudBaseAction):
    """备份ECS资源根据标签策略。

    此操作会检查所有ECS资源的backup_policy标签，并根据标签值决定是否创建备份。
    - 如果标签值为"need_backup"，则会检查是否已有备份和存储库，并根据需要创建备份。
    - 如果标签值为"no_backup"，则不会创建备份。

    : Example:

    .. code-block:: yaml

        policies:
            - name: backup-ecs-resources
              resource: huaweicloud.cbr-backup
              actions:
                  - type:backup-ecs
                    no_backup: [45Dd]
                    need_backup: [false]
    """
    schema = type_schema(
        'backup-ecs',
        required=['no_backup', 'need_backup'],
        no_backup={'type': 'array'},
        need_backup={'type': 'array'}
    )

    def _get_ecs_client(self):
        """获取ECS客户端"""
        client = local_session(self.manager.session_factory).client("ecs")
        return client

    def _get_cbr_client(self):
        """获取CBR客户端"""
        client = local_session(self.manager.session_factory).client("cbr")
        return client

    def perform_action(self, resource):
        ecs_client = self._get_ecs_client()
        cbr_client = self._get_cbr_client()
        results = []

        no_backup: list[str] = self.data['no_backup']
        need_backup: list[str] = self.data['need_backup']

        try:
            # 1. 查询所有ECS资源
            ecs_request = ListServersDetailsRequest()
            ecs_response = ecs_client.list_servers_details(ecs_request)
            servers = ecs_response.servers

            for server in servers:
                server_id = server.id
                tags: list[str] = server.tags if hasattr(server, 'tags') else []

                backup_policy = None
                for tag in tags:
                    if tag.startswith('backup_policy='):
                        backup_policy = tag.replace('backup_policy=', '')
                        break

                # 2. 判断是否包含backup_policy标签
                if backup_policy is None:
                    log.info(f"ECS {server_id} 应当包含backup_policy标签")
                    results.append({
                        'server_id': server_id,
                        'status': 'missing_tag',
                        'message': '应当包含backup_policy标签'
                    })
                    continue

                # 判断标签值是否合法
                if backup_policy not in no_backup and backup_policy not in need_backup:
                    log.info(f"ECS {server_id} 的backup_policy标签值 {backup_policy} 不合法")
                    results.append({
                        'server_id': server_id,
                        'status': 'invalid_tag',
                        'message': f'标签值 {backup_policy} 不合法'
                    })
                    continue

                if backup_policy in no_backup:
                    log.info(f"ECS {server_id} 不需要创建备份")
                    results.append({
                        'server_id': server_id,
                        'status': 'skipped',
                        'message': '不需要创建备份'
                    })
                    continue

                # 处理需要备份的情况
                if backup_policy in need_backup:
                    # 查询该ECS是否已备份
                    backup_request = ListBackupsRequest()
                    backup_request.resource_id = server_id
                    backup_response = cbr_client.list_backups(backup_request)

                    if backup_response.count > 0:
                        log.info(f"ECS {server_id} 已备份")
                        results.append({
                            'server_id': server_id,
                            'status': 'already_backed_up',
                            'message': '该ECS已备份'
                        })
                        continue

                    # 查询ECS是否绑定存储库
                    vault_request = ListVaultRequest()
                    vault_request.resource_id = server_id
                    vault_response = cbr_client.list_vault(vault_request)

                    vault_id = None
                    if vault_response.count > 0:
                        # 获取存在的存储库ID
                        vault_id = vault_response.vaults[0].id
                        log.info(f"ECS {server_id} 已绑定存储库 {vault_id}")
                    else:
                        # 创建存储库
                        create_vault_request = CreateVaultRequest()
                        create_vault_request.body = {
                            "vault": {
                                "resources": [
                                    {
                                        "id": server_id,
                                        "type": "OS::Nova::Server"
                                    }
                                ],
                                "name": f"auto-vault-{server_id}",
                                "billing": {
                                    "protect_type": "backup",
                                    "size": 100,
                                    "charging_mode": "post_paid",
                                    "object_type": "server"
                                }
                            }
                        }

                        create_vault_response = cbr_client.create_vault(create_vault_request)
                        vault_id = create_vault_response.vault.id
                        log.info(f"为ECS {server_id} 创建存储库 {vault_id}")

                    # 执行备份
                    if vault_id:
                        checkpoint_request = CreateCheckpointRequest()
                        checkpoint_request.body = {
                            "checkpoint": {
                                "vault_id": vault_id,
                                "name": f"auto-backup-{server_id}"
                            }
                        }

                        checkpoint_response = cbr_client.create_checkpoint(checkpoint_request)
                        log.info(
                            f"为ECS {server_id} 创建备份成功，备份ID: {checkpoint_response.checkpoint.id}")
                        results.append({
                            'server_id': server_id,
                            'status': 'backup_created',
                            'message': f'创建备份成功，备份ID: {checkpoint_response.checkpoint.id}',
                            'checkpoint_id': checkpoint_response.checkpoint.id
                        })

        except exceptions.ClientRequestException as e:
            log.error(f"备份失败: {e.status_code}, {e.request_id}, {e.error_code}, {e.error_msg}")
            raise

        return results
