# 华为云DNS服务适配Cloud Custodian文档

## 1. 华为云DNS资源类型

华为云DNS服务主要涉及以下资源类型，对应AWS Route53的相关资源：

-   `huaweicloud.dns-publiczone`: 公网DNS托管区域。对应AWS的`aws.hostedzone`公共区域。
-   `huaweicloud.dns-privatezone`: 内网DNS托管区域。对应AWS的`aws.hostedzone`私有区域。
-   `huaweicloud.dns-recordset`: DNS记录集。对应AWS的`aws.rrset`。

## 2. 通用Filters (适用于所有DNS资源)

| Filter             | 说明                       | 是否可复用            | 开发状态 | 华为云SDK链接                                                                                | 涉及其他服务                                 |
| :----------------- | :------------------------- | :-------------------- |:-----| :------------------------------------------------------------------------------------------- | :------------------------------------------- |
| value              | 基于资源属性值的通用过滤器 | 可复用                | 无需开发 | 不适用                                                                                       | 无                                           |
| list-item          | 列表元素过滤器             | 可复用                | 无需开发 | 不适用                                                                                       | 无                                           |
| event              | 事件过滤器                 | 可复用                | 无需开发 | 不适用                                                                                       | LTS (日志流服务) / CTS (云审计服务)          |
| reduce             | 聚合过滤器                 | 可复用                | 无需开发 | 不适用                                                                                       | 无                                           |
| marked-for-op      | 标记操作过滤器             | 可复用                | 无需开发 | 不适用                                                                                       | 无                                           |
| tag-count          | 标签数量过滤器             | 可复用                | 无需开发 | 不适用                                                                                       | 无                                           |
| tms                | 标签过滤器                 | 可复用 `tms.py`       | 无需开发 | [查询指定实例的标签信息](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=ShowResourceTag) | TMS (标签管理服务)                           |
| finding            | 安全发现过滤器             | 需要适配              | 不开发  | 不适用                                                                                       | AWR (应用风险感知) / Config (配置审计服务) |
| ops-item           | 运维项过滤器               | 需要适配              | 不开发  | 不适用                                                                                       | O&M (运维管理)                               |
| config-compliance  | 配置合规性过滤器           | 需要适配              | 不开发  | 不适用                                                                                       | Config (配置审计服务)                        |

## 3. DNS PublicZone特定Filters (`huaweicloud.dns-publiczone`)

| Filter | 说明                             | 是否可复用 | 开发状态   | 华为云SDK链接                                                                           | 涉及其他服务 |
| :----- |:-------------------------------| :--------- | :--------- | :-------------------------------------------------------------------------------------- | :----------- |
| status | 状态过滤器 (ACTIVE/PENDING_CREATE等) | 需要开发   | 需要开发   | [查询公网Zone列表](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=ListPublicZones) | 无           |
| email  | 邮箱地址过滤器                        | 需要开发   | 需要开发   | [查询公网Zone列表](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=ListPublicZones) | 无           |
## 4. DNS PrivateZone特定Filters (`huaweicloud.dns-privatezone`)

| Filter         | 说明                             | 是否可复用 | 开发状态   | 华为云SDK链接                                                                                                | 涉及其他服务 |
|:---------------|:-------------------------------| :--------- | :--------- |:--------------------------------------------------------------------------------------------------------|:------|
| status         | 状态过滤器 (ACTIVE/PENDING_CREATE等) | 需要开发   | 需要开发   | [查询内网Zone列表](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=ListPrivateZones)        | 无     |
| vpc-associated | 关联VPC过滤器                       | 需要开发   | 需要开发   | [查询内网Zone列表](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=ListPrivateZones)        | VPC (虚拟私有云) |

## 5. DNS RecordSet特定Filters (`huaweicloud.dns-recordset`)

| Filter      | 说明                                    | 是否可复用 | 开发状态   | 华为云SDK链接                                                                                     | 涉及其他服务 |
| :---------- | :-------------------------------------- | :--------- | :--------- | :------------------------------------------------------------------------------------------------ | :----------- |
| record-type | 记录类型过滤器 (A, CNAME, MX等)         | 需要开发   | 需要开发   | [查询租户Record Set资源列表](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=ListRecordSets) | 无           |
| zone-id     | 所属Zone ID过滤器                         | 需要开发   | 需要开发   | [查询租户Record Set资源列表](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=ListRecordSets) | 无           |
| status      | 状态过滤器 (ACTIVE/PENDING_CREATE等)    | 需要开发   | 需要开发   | [查询租户Record Set资源列表](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=ListRecordSets) | 无           |
| line-id     | 线路ID过滤器 (用于区分智能解析线路)     | 需要开发   | 需要开发  | [查询租户Record Set资源列表](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=ListRecordSets) | 无           |

## 6. 通用Actions (适用于所有DNS资源)

| Action           | 说明                | 是否可复用            | 开发状态 | 华为云SDK链接                                                                                     | 涉及其他服务                                                  |
| :--------------- | :------------------ | :-------------------- |:-----| :------------------------------------------------------------------------------------------------ | :------------------------------------------------------------ |
| tag              | 添加标签            | 可复用 `tms.py`       | 无需开发 | [为指定实例添加标签](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=CreateTag)        | TMS                                                           |
| remove-tag       | 删除标签            | 可复用 `tms.py`       | 无需开发 | [删除资源标签](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=DeleteTag)            | TMS                                                           |
| rename-tag       | 重命名标签键        | 需要适配 (基于删+添)  | 需要开发 | [为指定实例批量添加或删除标签](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=BatchCreateTag) | TMS                                                           |
| mark-for-op      | 标记待操作          | 可复用                | 不开发  | 不适用                                                                                            | 无                                                            |
| auto-tag-user    | 自动标记创建者      | 可复用 `autotag.py`   | 不开发  | [为指定实例添加标签](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=CreateTag)        | TMS, IAM                                                      |
| copy-related-tag | 复制相关标签        | 需要适配              | 不开发 | [为指定实例批量添加或删除标签](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=BatchCreateTag) | TMS                                                           |
| notify           | 发送通知            | 可复用                | 不开发 | 不适用                                                                                            | SMN (消息通知服务) / 第三方通知渠道                           |
| webhook          | 调用Webhook         | 可复用                | 不开发 | 不适用                                                                                            | 无                                                            |
| put-metric       | 发布监控指标        | 需要适配              | 不开发 | 不适用                                                                                            | CES (云监控服务)                                              |
| invoke-lambda    | 调用函数            | 需要适配              | 不开发 | 不适用                                                                                            | FunctionGraph (函数工作流)                                    |
| invoke-sfn       | 调用状态机          | 需要适配              | 不开发 | 不适用                                                                                            | FunctionGraph (函数工作流) / DMS (分布式消息服务)             |
| post-finding     | 推送安全发现        | 需要适配              | 不开发 | 不适用                                                                                            | AWR / Config                                                  |
| post-item        | 推送运维项          | 需要适配              | 不开发 | 不适用                                                                                            | O&M                                                           |

## 7. DNS PublicZone特定Actions (`huaweicloud.dns-publiczone`)

| Action     | 说明       | 是否可复用 | 开发状态   | 华为云SDK链接                                                                                | 涉及其他服务 |
| :--------- |:---------| :--------- | :--------- | :------------------------------------------------------------------------------------------- | :----------- |
| delete     | 删除公网域名   | 需要开发   | 需要开发   | [删除单个公网Zone](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=DeletePublicZone) | 无           |
| update     | 更新公网域名属性 | 需要开发   | 需要开发   | [修改单个公网Zone](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=UpdatePublicZone) | 无           |
| set-status | 设置公网域名状态 | 需要开发   | 需要开发   | [设置单个公网Zone状态](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=UpdatePublicZoneStatus), [批量设置Zone状态](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=BatchSetZonesStatus) | 无           |

## 8. DNS PrivateZone特定Actions (`huaweicloud.dns-privatezone`)

| Action           | 说明                    | 是否可复用 | 开发状态   | 华为云SDK链接                                                                                 | 涉及其他服务 |
| :--------------- | :---------------------- | :--------- | :--------- | :-------------------------------------------------------------------------------------------- | :----------- |
| delete           | 删除内网区域            | 需要开发   | 需要开发   | [删除单个内网Zone](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=DeletePrivateZone) | 无           |
| update           | 更新内网区域属性        | 需要开发   | 需要开发   | [修改单个内网Zone](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=UpdatePrivateZone) | 无           |
| associate-vpc    | 关联VPC                 | 需要开发   | 需要开发   | [在内网Zone上关联VPC](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=AssociateRouter)    | VPC          |
| disassociate-vpc | 解关联VPC               | 需要开发   | 需要开发   | [在内网Zone上解关联VPC](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=DisassociateRouter)  | VPC          |

## 9. DNS RecordSet特定Actions (`huaweicloud.dns-recordset`)

| Action     | 说明                             | 是否可复用 | 开发状态   | 华为云SDK链接                                                                                                  | 涉及其他服务 |
| :--------- | :------------------------------- | :--------- | :--------- | :------------------------------------------------------------------------------------------------------------- | :----------- |
| delete     | 删除记录集                       | 需要开发   | 需要开发   | [删除单个Record Set](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=DeleteRecordSet), [批量删除Record Set](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=BatchDeleteRecordSets) | 无           |
| update     | 更新记录集 (如TTL、记录值)       | 需要开发   | 需要开发   | [修改单个Record Set](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=UpdateRecordSet), [批量修改RecordSet](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=BatchUpdateRecordSetWithLine) | 无           |
| set-status | 设置状态 (启用/禁用)             | 需要开发   | 需要开发   | [设置Record Set状态](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=SetRecordSetsStatus), [批量设置Record Set状态](https://console.huaweicloud.com/apiexplorer/#/openapi/DNS/sdk?api=BatchSetRecordSetsStatus) | 无           |

## 11. 开发建议

1.  **资源定义**: 分别创建三个主要资源类: `huaweicloud.dns-publiczone`, `huaweicloud.dns-privatezone`, `huaweicloud.dns-recordset`。由于公网Zone和内网Zone使用完全不同的API，应**分别实现**而非合并。
2.  **复用与适配**: 优先复用通用filters和actions（如`value`, `list-item`, `tms`等）。对于标签相关功能，可复用`tms.py`中的实现。对于自动标记功能，可复用`autotag.py`中的实现。需要适配的功能需根据华为云对应服务进行实现。
3.  **开发新功能**: 针对不同资源类型的特定操作和过滤条件，开发对应的filters和actions，调用相应的公网/内网Zone、RecordSet或PTR的华为云DNS SDK。
4.  **特别考虑**:
    *   **批量操作**: 华为云DNS提供多种批量API，可提高操作效率，在实现相关Actions时应考虑使用。
    *   **线路管理**: 华为云支持复杂的线路管理功能，RecordSet相关的filters和actions需要能处理线路ID (`line-id`)。
    *   **公私网分离**: 严格区分公网Zone和内网Zone的API调用。
5.  **其他服务集成**: 明确各filters和actions依赖的华为云服务（VPC, EIP, TMS, CES, SMN, FunctionGraph, IAM, LTS, CTS, Config, AWR, O&M等），确保开发和使用时有正确的配置和权限。
