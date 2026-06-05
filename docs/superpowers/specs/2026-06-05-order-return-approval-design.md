# 订单退货审批流程设计

日期：2026-06-05

## 概述

将当前"买家直接退货"改为"买家申请 → 管理员审批 → 退款"的三步流程。

## 一、状态机变更

### Order.Status 新增

```python
PENDING_RETURN = "pending_return", "待审核退货"
```

### 退货状态流转

```
receiving ──→ pending_return ──→ refunded (审批通过)
                 │
                 └──→ receiving   (审批驳回)
```

### 状态权限约束

- `pending_return` 期间买家不可操作确认收货、改地址
- `pending_return` 期间卖家不可操作
- 仅管理员可审批（通过/驳回）

## 二、后端改动

### 2.1 模型 (orders/models.py)

- `Order.Status` 新增 `PENDING_RETURN`

### 2.2 序列化器 (orders/serializers.py)

**OrderReturnSerializer 重构：**
- 校验条件：`order.status == Order.Status.RECEIVING`（不变）
- `save()` 改为仅设置 `pending_return` + 写状态日志（不执行退款/库存恢复）

**新增 OrderReturnApproveSerializer：**
- 校验：order 必须是 `pending_return`，operator 必须是 admin
- `save()` 执行原退款逻辑：订单→refunded, 支付→refunded, 库存恢复, 资产解锁, 信用扣分

**新增 OrderReturnRejectSerializer：**
- 校验条件：`order.status == Order.Status.PENDING_RETURN`
- `save()` 将状态恢复为 `receiving`，附带驳回原因写入状态日志

### 2.3 视图 (orders/views.py)

**OrderReturnView (修改)：**
- 使用重构后的 OrderReturnSerializer
- 成功后提示"退货申请已提交，等待管理员审核"

**新增 OrderReturnApproveView：**
- `POST /orders/{order_id}/return/approve/`
- `IsAdmin` 权限
- 调用 OrderReturnApproveSerializer

**新增 OrderReturnRejectView：**
- `POST /orders/{order_id}/return/reject/`
- `IsAdmin` 权限
- 调用 OrderReturnRejectSerializer
- 请求体含 `reason` 字段

### 2.4 URL (orders/urls.py)

新增两条路由。

### 2.5 迁移

新增迁移文件：Order 模型 Status choices 变更。

## 三、前端改动

### 3.1 用户端 OrderDetailView.vue

- `receiving` 状态：「退货」按钮行为不变，提示改为"退货申请已提交"
- `pending_return` 状态：按钮替换为灰色文字 **"退货审核中"**，隐藏确认收货/改地址按钮

### 3.2 管理端 AdminOrdersView.vue

- 左侧状态筛选新增「待审核退货」选项（value=`pending_return`）
- 表格中 `pending_return` 订单行显示「通过」「驳回」按钮
- 驳回：`ElMessageBox.prompt` 收集原因
- 通过：`ElMessageBox.confirm` 二次确认

### 3.3 API 层 (api/order.ts)

新增：
- `approveReturn(orderId: string)` → `POST /orders/{id}/return/approve/`
- `rejectReturn(orderId: string, reason: string)` → `POST /orders/{id}/return/reject/`

## 四、AdminOperationLog

审批操作写入 `AdminOperationLog`（复用现有模型），module="订单管理"，action 为"通过退货"/"驳回退货"。

## 五、订单详情响应

`OrderDetailSerializer` 的 `status_logs` 已包含状态变更记录，前端可直接展示审批轨迹。
