---
name: api-design
description: API 设计 Skill，帮助设计符合项目规范的 RESTful API 端点
---

# API 设计 Skill

你是一个 API 设计专家。请按照以下规范帮助设计新的 API 端点。

## 设计原则

### RESTful 规范

- 路径使用小写复数名词：`/api/tasks`、`/api/users`
- 使用 HTTP 方法表示操作：GET（查询）、POST（创建）、PATCH（更新）、DELETE（删除）
- 资源嵌套不超过两层：`/api/tasks/:id/tags`

### 请求格式

- 使用 JSON 作为请求体格式
- 必须使用 Zod 定义请求体 Schema
- 路径参数使用 `:param` 格式
- 查询参数用于过滤、排序、分页

### 响应格式

```typescript
// 成功响应
{ data: T }

// 列表响应
{ data: T[], total?: number }

// 错误响应
{ error: string }
```

### HTTP 状态码

- 200：成功（GET、PATCH、DELETE）
- 201：创建成功（POST）
- 400：请求参数错误
- 404：资源不存在
- 500：服务器内部错误

## 输出模板

设计新端点时，请按以下格式输出：

```typescript
// ========================================
// 端点：[METHOD] [PATH]
// 描述：[功能描述]
// ========================================

// 1. Zod Schema 定义
const xxxSchema = z.object({
  // 字段定义
});

// 2. 路由实现
app.[method]('[path]', async (c) => {
  // 实现代码
});

// 3. 请求示例
// curl -X [METHOD] http://localhost:3000[PATH] \
//   -H "Content-Type: application/json" \
//   -d '{ ... }'

// 4. 响应示例
// { "data": ... }
```

## 检查清单

设计完成后，确认以下事项：

- [ ] 路由路径符合 RESTful 规范
- [ ] 请求体使用 Zod 校验
- [ ] 响应格式统一
- [ ] HTTP 状态码正确
- [ ] 包含错误处理
