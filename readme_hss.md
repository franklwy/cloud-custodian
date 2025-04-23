# 华为云主机安全服务(HSS)适配说明

## 1. 概述

本文档描述了Cloud Custodian适配华为云主机安全服务(HSS)的实现方案。HSS提供主机安全防护、漏洞管理、基线检查等功能，有助于企业保障云上主机资源的安全性。

## 2. 功能清单

### 2.1 Filters

#### 2.1.1 通用 Filters (可复用)

以下filters可以直接复用现有实现：

| 过滤器 | 说明 | 是否需要修改 |
|------|------|------------|
| ValueFilter | 用于过滤资源属性值 | 否 |
| TagFilter | 用于根据标签过滤 | 否 |
| CrossAccountFilter | 跨账号资源过滤 | 否 |
| TimeFilter | 基于时间的过滤 | 否 |
| AgeFilter | 基于资源创建时间的过滤 | 否 |
| MarkedForOpFilter | 标记为特定操作的资源过滤 | 否 |

#### 2.1.2 HSS 特有 Filters (需要开发)

| 过滤器 | 说明 | 依赖SDK | 其他服务依赖 |
|------|------|---------|------------|
| HostStatusFilter | 根据主机防护状态进行过滤 | huaweicloudsdkhss.v5.ListHostStatusRequest | 无 |
| VulnerabilityFilter | 根据主机漏洞状态进行过滤 | huaweicloudsdkhss.v5.ListHostVulsRequest | 无 |
| ProtectionPolicyFilter | 根据防护策略进行过滤 | huaweicloudsdkhss.v5.ListProtectionPolicyRequest | 无 |
| WtpProtectionFilter | 根据网页防篡改防护状态进行过滤 | huaweicloudsdkhss.v5.ListWtpProtectHostRequest | 无 |
| RiskConfigFilter | 根据基线风险配置进行过滤 | huaweicloudsdkhss.v5.ListRiskConfigsRequest | 无 |
| AgentStatusFilter | 根据Agent状态进行过滤 | huaweicloudsdkhss.v5.ListHostStatusRequest | 无 |

### 2.2 Actions

#### 2.2.1 通用 Actions (可复用)

| 操作 | 说明 | 是否需要修改 |
|------|------|------------|
| BaseAction | 基础动作类 | 否 |
| TagAction | 标签相关操作 | 否 |
| AutoTagBase | 自动打标签基类 | 否 |
| MarkForOpAction | 标记资源执行操作 | 否 |

#### 2.2.2 HSS 特有 Actions (需要开发)

| 操作 | 说明 | 依赖SDK | 其他服务依赖 |
|------|------|---------|------------|
| StartProtectionAction | 开启主机防护 | huaweicloudsdkhss.v5.StartProtectionRequest | 无 |
| StopProtectionAction | 关闭主机防护 | huaweicloudsdkhss.v5.StopProtectionRequest | 无 |
| SwitchHostsProtectStatusAction | 切换主机防护状态 | huaweicloudsdkhss.v5.SwitchHostsProtectStatusRequest | 无 |
| SetWtpProtectionStatusAction | 开启/关闭网页防篡改防护 | huaweicloudsdkhss.v5.SetWtpProtectionStatusInfoRequest | 无 |
| SetRaspSwitchAction | 开启/关闭应用防护 | huaweicloudsdkhss.v5.SetRaspSwitchRequest | 无 |
| CreateVulScanTaskAction | 创建漏洞扫描任务 | huaweicloudsdkhss.v5.CreateVulnerabilityScanTaskRequest | 无 |
| ChangeVulStatusAction | 更改漏洞状态 | huaweicloudsdkhss.v5.ChangeVulStatusRequest | 无 |
| AddHostsGroupAction | 添加主机到主机组 | huaweicloudsdkhss.v5.AddHostsGroupRequest | 无 |
| CreateAntiVirusTaskAction | 创建病毒扫描任务 | huaweicloudsdkhss.v5.CreateAntiVirusTaskRequest | 无 |

### 2.3 资源管理器和查询实现

| 组件 | 说明 | 依赖SDK | 其他服务依赖 |
|------|------|---------|------------|
| HssResourceManager | HSS资源管理器 | huaweicloudsdkhss.v5.HssClient | 无 |
| HssDescribe | HSS资源查询 | huaweicloudsdkhss.v5.ListHostStatusRequest | 无 |

## 3. 开发建议

### 3.1 代码结构

```
c7n_huaweicloud/
├── resources/
│   └── hss.py         # HSS资源定义
├── actions/
│   └── hss.py         # HSS相关actions实现
└── filters/
    └── hss.py         # HSS相关filters实现
```

### 3.2 实现步骤

1. 实现HSS资源类型
   - 定义资源元数据(service、类型名、默认报告字段)
   - 实现资源查询功能

2. 实现HSS特有filters
   - 实现HostStatusFilter
   - 实现VulnerabilityFilter
   - 实现其他特有过滤器

3. 实现HSS特有actions
   - 实现StartProtectionAction/StopProtectionAction
   - 实现SetWtpProtectionStatusAction
   - 实现其他特有操作

4. 编写单元测试
   - 资源查询单元测试
   - 过滤器单元测试
   - 操作单元测试

5. 补充功能文档
   - 资源类型和字段说明
   - 过滤器使用方法
   - 操作使用方法

### 3.3 注意事项

1. 日期时间处理
   - 注意日期时间字段类型：HSS API可能使用时间戳整数而非字符串，需要正确处理

2. 异常处理
   - 需要处理API调用错误和重试
   - 主机不存在或不可访问的场景处理

3. 认证和授权
   - 确保正确配置IAM权限
   - 处理跨项目资源访问

4. 资源标识处理
   - 确保正确处理资源标识符
   - 处理企业项目ID

## 4. 示例策略

### 4.1 基本查询和过滤

```yaml
policies:
  - name: hss-all-hosts
    resource: huaweicloud.hss
    filters:
      - type: value
        key: host_name
        value: test-*
        op: glob
```

### 4.2 防护状态管理

```yaml
policies:
  - name: hss-enable-protection
    resource: huaweicloud.hss
    filters:
      - type: host-status
        status: unprotected
    actions:
      - type: start-protection
```

### 4.3 漏洞管理

```yaml
policies:
  - name: hss-critical-vulnerabilities
    resource: huaweicloud.hss
    filters:
      - type: vulnerability
        severity: critical
        status: unfixed
    actions:
      - type: notify
        template: critical-vulnerability.j2
        priority_to: [email]
        subject: 发现严重安全漏洞
```

### 4.4 标签管理

```yaml
policies:
  - name: hss-tag-unprotected
    resource: huaweicloud.hss
    filters:
      - type: host-status
        status: unprotected
    actions:
      - type: tag
        key: security-status
        value: unprotected
```

### 4.5 网页防篡改管理

```yaml
policies:
  - name: hss-enable-wtp-protection
    resource: huaweicloud.hss
    filters:
      - type: wtp-protection
        status: disabled
    actions:
      - type: set-wtp-protection-status
        status: enabled
```
