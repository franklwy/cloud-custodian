# 华为云BMS服务适配Cloud Custodian文档

## 1. 华为云BMS资源类型

华为云BMS（裸金属服务器）服务提供以下资源类型，对应华为云的ECS服务：

-   `huaweicloud.bms`: 裸金属服务器。对应已适配完成的`huaweicloud.ecs`服务器。

## 2. 通用Filters (适用于BMS资源)

| Filter             | 说明                       | 是否可复用            | 开发状态 | 华为云API链接                                                                                | 涉及其他服务                                 |
| :----------------- | :------------------------- | :-------------------- |:-----| :------------------------------------------------------------------------------------------- | :------------------------------------------- |
| value              | 基于资源属性值的通用过滤器 | 可复用                | 已复用   | 不适用                                                                                       | 无                                           |
| list-item          | 列表元素过滤器             | 可复用                | 已复用   | 不适用                                                                                       | 无                                           |
| event              | 事件过滤器                 | 可复用                | 已复用   | 不适用                                                                                       | LTS (日志流服务) / CTS (云审计服务)          |
| reduce             | 聚合过滤器                 | 可复用                | 已复用   | 不适用                                                                                       | 无                                           |
| marked-for-op      | 标记操作过滤器             | 可复用                | 已复用   | 不适用                                                                                       | 无                                           |
| tag-count          | 标签数量过滤器             | 可复用                | 已复用   | 不适用                                                                                       | 无                                           |
| tms                | 标签过滤器                 | 可复用 `tms.py`       | 已复用   | [查询指定实例的标签信息](https://support.huaweicloud.com/api-bms/ShowBaremetalServerTags.html) | TMS (标签管理服务)                           |
| finding            | 安全发现过滤器             | 需要适配              | 不开发  | 不适用                                                                                       | AWR (应用风险感知) / Config (配置审计服务) |
| ops-item           | 运维项过滤器               | 需要适配              | 不开发  | 不适用                                                                                       | O&M (运维管理)                               |
| config-compliance  | 配置合规性过滤器           | 需要适配              | 不开发  | 不适用                                                                                       | Config (配置审计服务)                        |

## 3. BMS特定Filters (`huaweicloud.bms`)

| Filter                      | 说明                         | 是否可复用 | 开发状态   | 华为云API链接                                                                                                                    | 涉及其他服务 |
| :-------------------------- | :--------------------------- | :--------- | :--------- | :-------------------------------------------------------------------------------------------------------------------------------- | :----------- |
| instance-age                | 服务器创建时间筛选                | 可复用 `ecs.py`  | 待开发 | [查询裸金属服务器详情列表](https://support.huaweicloud.com/api-bms/bms_api_0609.html)                                          | 无           |
| instance-uptime             | 服务器运行时间筛选                | 可复用 `ecs.py`  | 待开发 | [查询裸金属服务器详情列表](https://support.huaweicloud.com/api-bms/bms_api_0609.html)                                          | 无           |
| instance-attribute          | 服务器属性筛选                  | 可复用 `ecs.py`  | 待开发 | [查询裸金属服务器详情](https://support.huaweicloud.com/api-bms/bms_api_0608.html)                                              | 无           |
| instance-image-age          | 镜像创建时间筛选                | 需要开发   | 待开发   | [查询裸金属服务器详情列表](https://support.huaweicloud.com/api-bms/bms_api_0609.html)                                          | IMS (镜像服务) |
| instance-image              | 镜像筛选                      | 需要开发   | 待开发   | [查询裸金属服务器详情列表](https://support.huaweicloud.com/api-bms/bms_api_0609.html)                                          | IMS (镜像服务) |
| ephemeral                   | 是否使用临时存储                | 需要开发   | 待开发   | [查询裸金属服务器详情](https://support.huaweicloud.com/api-bms/bms_api_0608.html)                                              | 无           |
| instance-user-data          | 用户数据筛选                    | 需要开发   | 待开发   | [查询裸金属服务器详情](https://support.huaweicloud.com/api-bms/bms_api_0608.html)                                              | 无           |
| instance-evs                | EVS卷筛选                    | 需要开发   | 待开发   | [查询裸金属服务器详情](https://support.huaweicloud.com/api-bms/bms_api_0608.html)                                              | EVS (云硬盘) |
| instance-vpc                | VPC筛选                       | 需要开发   | 待开发   | [查询裸金属服务器详情列表](https://support.huaweicloud.com/api-bms/bms_api_0609.html)                                          | VPC (虚拟私有云) |
| instance-volumes-not-compliance | 云硬盘不合规筛选              | 需要开发   | 待开发   | [查询裸金属服务器详情](https://support.huaweicloud.com/api-bms/bms_api_0608.html)                                              | EVS (云硬盘) |
| instance-image-not-compliance | 镜像不合规筛选                | 需要开发   | 待开发   | [查询裸金属服务器详情列表](https://support.huaweicloud.com/api-bms/bms_api_0609.html)                                          | IMS (镜像服务) |
| instance-tag                | 标签筛选                      | 需要开发   | 待开发   | [查询裸金属服务器详情列表](https://support.huaweicloud.com/api-bms/bms_api_0609.html)                                          | TMS (标签管理服务) |

## 4. 通用Actions (适用于BMS资源)

| Action           | 说明                | 是否可复用            | 开发状态 | 华为云API链接                                                                                                             | 涉及其他服务                                                  |
| :--------------- | :------------------ | :-------------------- |:-----| :------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------ |
| tag              | 添加标签            | 可复用 `tms.py`       | 已复用   | [为指定实例添加标签](https://support.huaweicloud.com/api-bms/CreateBaremetalServerTag.html)                             | TMS                                                           |
| remove-tag       | 删除标签            | 可复用 `tms.py`       | 已复用   | [删除指定实例的标签](https://support.huaweicloud.com/api-bms/DeleteBaremetalServerTag.html)                             | TMS                                                           |
| rename-tag       | 重命名标签键        | 需要适配 (基于删+添)  | 需要开发 | [批量添加/删除指定实例的标签](https://support.huaweicloud.com/api-bms/BatchCreateBaremetalServerTags.html)              | TMS                                                           |
| mark-for-op      | 标记待操作          | 可复用                | 已复用   | 不适用                                                                                                                    | 无                                                            |
| auto-tag-user    | 自动标记创建者      | 可复用 `autotag.py`   | 已复用   | [为指定实例添加标签](https://support.huaweicloud.com/api-bms/CreateBaremetalServerTag.html)                             | TMS, IAM                                                      |
| notify           | 发送通知            | 可复用                | 不开发 | 不适用                                                                                                                    | SMN (消息通知服务) / 第三方通知渠道                           |
| webhook          | 调用Webhook         | 可复用                | 不开发 | 不适用                                                                                                                    | 无                                                            |
| put-metric       | 发布监控指标        | 需要适配              | 不开发 | 不适用                                                                                                                    | CES (云监控服务)                                              |
| invoke-lambda    | 调用函数            | 需要适配              | 不开发 | 不适用                                                                                                                    | FunctionGraph (函数工作流)                                    |
| invoke-sfn       | 调用状态机          | 需要适配              | 不开发 | 不适用                                                                                                                    | FunctionGraph (函数工作流) / DMS (分布式消息服务)             |
| post-finding     | 推送安全发现        | 需要适配              | 不开发 | 不适用                                                                                                                    | AWR / Config                                                  |
| post-item        | 推送运维项          | 需要适配              | 不开发 | 不适用                                                                                                                    | O&M                                                           |

## 5. BMS特定Actions (`huaweicloud.bms`)

| Action                     | 说明                                        | 是否可复用       | 开发状态 | 华为云API链接                                                                                                | 涉及其他服务                                          |
| :------------------------- | :------------------------------------------ | :--------------- | :------- | :----------------------------------------------------------------------------------------------------------- | :---------------------------------------------------- |
| fetch-job-status           | 获取异步任务状态                            | 可复用 `ecs.py`   | 待开发   | [查询Job的执行状态](https://support.huaweicloud.com/api-bms/bms_api_0640.html)                              | 无                                                    |
| instance-start             | 启动裸金属服务器                            | 需要开发         | 待开发   | [启动裸金属服务器](https://support.huaweicloud.com/api-bms/bms_api_0613.html)                               | 无                                                    |
| instance-stop              | 关闭裸金属服务器                            | 需要开发         | 待开发   | [关闭裸金属服务器](https://support.huaweicloud.com/api-bms/bms_api_0615.html)                               | 无                                                    |
| instance-reboot            | 重启裸金属服务器                            | 需要开发         | 待开发   | [重启裸金属服务器](https://support.huaweicloud.com/api-bms/bms_api_0614.html)                               | 无                                                    |
| instance-terminate         | 删除裸金属服务器                            | 需要开发         | 待开发   | [删除裸金属服务器](https://support.huaweicloud.com/api-bms/bms_api_0631.html)                               | 无                                                    |
| instance-add-security-groups | 添加安全组                                | 需要开发         | 待开发   | [添加安全组](https://support.huaweicloud.com/api-bms/AttachBaremetalServerSecurityGroup.html)              | VPC (虚拟私有云)                                      |
| instance-delete-security-groups | 移除安全组                             | 需要开发         | 待开发   | [移除安全组](https://support.huaweicloud.com/api-bms/DetachBaremetalServerSecurityGroup.html)              | VPC (虚拟私有云)                                      |
| set-instance-profile       | 设置服务器元数据                            | 需要开发         | 待开发   | [更新裸金属服务器元数据](https://support.huaweicloud.com/api-bms/UpdateBaremetalServerMetadata.html)         | 无                                                    |
| instance-whole-image       | 创建整机镜像                                | 需要开发         | 待开发   | [创建裸金属服务器整机镜像](https://support.huaweicloud.com/api-ims/ims_03_0203.html)                         | IMS (镜像服务), CBR (云备份)                           |
| instance-snapshot          | 创建快照                                    | 需要开发         | 待开发   | [创建备份](https://support.huaweicloud.com/api-cbr/CreateCheckpoint.html)                                    | CBR (云备份)                                          |
| instance-volumes-corrections | 修正云硬盘删除属性                        | 需要开发         | 待开发   | [修改云硬盘](https://support.huaweicloud.com/api-evs/evs_04_2095.html)                                       | EVS (云硬盘)                                          |
| instance-delete-metadata-key | 删除元数据键                              | 需要开发         | 待开发   | [删除裸金属服务器指定元数据](https://support.huaweicloud.com/api-bms/DeleteBaremetalServerMetadata.html)     | 无                                                    |
| instance-reinstall-os      | 重装操作系统                                | 需要开发         | 待开发   | [重装裸金属服务器操作系统](https://support.huaweicloud.com/api-bms/ReinstallBaremetalServerOs.html)          | IMS (镜像服务)                                        |

## 6. 开发建议

1. **资源定义**: 创建`huaweicloud.bms`资源类，实现对裸金属服务器的管理。
2. **复用与适配**:
   - 优先复用通用filters和actions（如`value`, `list-item`, `tms`等）
   - 对于标签相关功能，复用`tms.py`中的实现
   - 对于自动标记功能，复用`autotag.py`中的实现
   - 对于服务器状态和属性相关的过滤器，可参考`ecs.py`中的实现
3. **开发新功能**:
   - 针对BMS特定操作和过滤条件，开发对应的filters和actions
   - 调用华为云BMS SDK（huaweicloudsdkbms）
4. **特别考虑**:
   - **批量操作**: 华为云BMS提供批量启动、停止、重启等API，可提高操作效率
   - **异步操作**: BMS的多数操作是异步的，需要通过job_id查询任务状态
   - **镜像与硬盘**: BMS支持EVS云硬盘作为系统盘和数据盘，需特别关注相关操作
5. **其他服务集成**: 明确各filters和actions依赖的华为云服务（VPC, EVS, IMS, CBR, TMS, CES, SMN, FunctionGraph, IAM等），确保开发和使用时有正确的配置和权限。

## 7. 注意事项

1. 相比ECS，BMS具有物理服务器特性，启动、停止、重启等操作需更长时间
2. BMS支持EVS云硬盘挂载，但部分规格BMS也具有本地存储
3. BMS支持使用与ECS相同的镜像，但需注意镜像兼容性
4. BMS服务与ECS服务的API路径和参数存在差异，尽管功能相似
5. BMS操作多为异步操作，需配合使用Job管理API查询任务状态
