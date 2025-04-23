# 华为云主机安全服务(HSS)适配说明

## 1. 概述

本文档描述了Cloud Custodian适配华为云主机安全服务(HSS)的实现方案。HSS提供主机安全防护、漏洞管理、基线检查等功能。

## 2. 功能清单

### 2.1 Filters

#### 2.1.1 通用 Filters (可复用)

以下filters可以直接复用现有实现：

- ValueFilter: 用于过滤资源属性值
- TagFilter: 用于根据标签过滤
- CrossAccountFilter: 跨账号资源过滤
- TimeFilter: 基于时间的过滤

#### 2.1.2 HSS 特有 Filters (需要开发)

1. 主机防护状态过滤器
   - SDK: huaweicloudsdkhss.v2.ListHostStatusRequest
   - 依赖服务: 无
   - 功能: 根据主机防护状态进行过滤

2. 网页防篡改状态过滤器
   - SDK: huaweicloudsdkhss.v2.ListWtpProtectHostRequest
   - 依赖服务: 无
   - 功能: 根据网页防篡改防护状态进行过滤

### 2.2 Actions

#### 2.2.1 通用 Actions (可复用)

以下actions可以直接复用现有实现：

- BaseAction: 基础动作类
- TagAction: 标签相关操作
- AutoTagBase: 自动打标签基类

#### 2.2.2 HSS 特有 Actions (需要开发)

1. 勒索病毒防护控制
   - 开启防护
     - SDK: huaweicloudsdkhss.v2.StartProtectionRequest
     - 依赖服务: 无
   - 关闭防护
     - SDK: huaweicloudsdkhss.v2.StopProtectionRequest
     - 依赖服务: 无

2. 网页防篡改防护控制
   - 开启/关闭静态防护
     - SDK: huaweicloudsdkhss.v2.SetWtpProtectionStatusInfoRequest
     - 依赖服务: 无
   - 开启/关闭动态防护
     - SDK: huaweicloudsdkhss.v2.SetRaspSwitchRequest
     - 依赖服务: 无

## 3. 开发建议

### 3.1 代码结构

```
c7n_huaweicloud/
├── actions/
│   └── hss.py    # HSS相关actions实现
└── filters/
    └── hss.py    # HSS相关filters实现
```

### 3.2 实现步骤

1. 实现HSS资源类型
2. 实现HSS特有filters
3. 实现HSS特有actions
4. 编写单元测试
5. 补充功能文档

### 3.3 注意事项

1. 需要处理API调用错误和重试
2. 确保正确处理资源标识符
3. 遵循Cloud Custodian的最佳实践
4. 完善日志记录和错误提示

## 4. 示例策略

```yaml
policies:
  - name: hss-ransomware-protection
    resource: huaweicloud.hss
    filters:
      - type: host-status
        status: unprotected
    actions:
      - type: start-protection
```
