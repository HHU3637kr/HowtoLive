# HowToLive 前端使用指南

## 🎉 前端开发已完成

### 技术栈
- **框架**: React 18 + TypeScript
- **状态管理**: Zustand
- **HTTP 客户端**: Axios
- **样式**: Tailwind CSS
- **流式通信**: Server-Sent Events (SSE)

---

## 📁 项目结构

```
frontend/howtolive-chat/
├── src/
│   ├── components/          # React 组件
│   │   ├── Auth/           # 认证组件
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── Chat/           # 聊天组件
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageItem.tsx
│   │   │   └── InputArea.tsx
│   │   └── Sidebar/        # 侧边栏组件
│   │       ├── SessionList.tsx
│   │       └── SessionItem.tsx
│   ├── services/            # API 服务层
│   │   ├── api.ts          # Axios 配置
│   │   ├── auth.ts         # 认证 API
│   │   ├── sessions.ts     # 会话 API
│   │   └── chat.ts         # SSE 流式聊天
│   ├── store/               # Zustand 状态管理
│   │   ├── authStore.ts    # 认证状态
│   │   ├── sessionStore.ts # 会话状态
│   │   └── chatStore.ts    # 聊天消息状态
│   ├── types/               # TypeScript 类型
│   │   └── index.ts
│   ├── config.ts            # 配置文件
│   └── App.tsx              # 主应用
└── package.json
```

---

## 🚀 启动步骤

### 1. 启动后端 API
在项目根目录：
```bash
cd backend
conda activate howtolive
python api/main.py
```
后端将运行在 `http://localhost:8000`

### 2. 启动前端
在另一个终端：
```bash
cd frontend/howtolive-chat
npm start
```
前端将运行在 `http://localhost:3001` 并自动打开浏览器

---

## ✨ 功能特性

### 1. 用户认证
- ✅ 用户注册（用户名、密码、可选邮箱）
- ✅ 用户登录
- ✅ JWT Token 认证
- ✅ Token 自动刷新和验证

### 2. 会话管理
- ✅ 创建新会话
- ✅ 会话列表显示
- ✅ 切换会话
- ✅ 删除会话
- ✅ 加载历史消息

### 3. 实时聊天
- ✅ SSE 流式响应
- ✅ 逐字显示 AI 回复
- ✅ 消息历史保存
- ✅ 多 Agent 支持（howtoeat, howtocook, howtosleep, howtoexercise）

### 4. UI/UX
- ✅ ChatGPT 风格界面
- ✅ 响应式设计
- ✅ 加载状态指示
- ✅ 错误提示
- ✅ 自动滚动到底部

---

## 🔧 配置说明

### API 基础地址
在 `src/config.ts` 中配置：
```typescript
export const API_BASE_URL = 'http://localhost:8000';
```

### 修改端口
前端默认运行在 3001 端口。如果需要修改，可以在 `package.json` 中更改：
```json
"scripts": {
  "start": "PORT=3002 react-scripts start"
}
```

---

## 📝 API 端点

前端对接以下后端 API：

### 认证
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `GET /api/auth/me` - 获取用户信息

### 会话
- `POST /api/sessions` - 创建会话
- `GET /api/sessions` - 获取会话列表
- `GET /api/sessions/{session_id}` - 获取会话详情
- `DELETE /api/sessions/{session_id}` - 删除会话

### 聊天
- `POST /api/chat/stream` - SSE 流式聊天

---

## 🐛 常见问题

### Q: 前端无法连接后端？
**A**: 检查：
1. 后端是否已启动（`http://localhost:8000`）
2. `src/config.ts` 中的 `API_BASE_URL` 是否正确
3. 浏览器控制台是否有 CORS 错误
4. 后端 CORS 配置是否允许 `http://localhost:3001`

### Q: 登录后刷新页面需要重新登录？
**A**: Token 存储在 `localStorage`，正常情况下不会丢失。如果出现此问题，检查浏览器控制台是否有 401 错误。

### Q: SSE 流式响应不工作？
**A**: 检查：
1. 后端 `/api/chat/stream` 端点是否正常
2. 浏览器是否支持 SSE（现代浏览器都支持）
3. 网络控制台中查看 SSE 连接状态

### Q: Tailwind CSS 样式不生效？
**A**: 确保：
1. `tailwind.config.js` 中 `content` 路径正确
2. `src/index.css` 中已引入 Tailwind directives
3. 重启开发服务器

---

## 🎯 使用流程

1. **注册/登录**
   - 首次使用点击"立即注册"创建账号
   - 已有账号直接登录

2. **创建会话**
   - 点击左侧"新建对话"按钮
   - 或自动加载已有会话

3. **开始聊天**
   - 在输入框输入消息
   - 按 Enter 发送（Shift+Enter 换行）
   - AI 将实时流式返回回复

4. **管理会话**
   - 点击会话切换对话
   - 鼠标悬停会话显示删除按钮

5. **退出登录**
   - 点击左下角"退出登录"按钮

---

## 📊 性能优化建议

1. **代码分割**: 使用 React.lazy 进行组件懒加载
2. **Memo 优化**: 对频繁渲染的组件使用 React.memo
3. **虚拟滚动**: 消息数量过多时使用虚拟滚动库
4. **图片优化**: 使用 WebP 格式和懒加载
5. **Bundle 分析**: 使用 webpack-bundle-analyzer 分析打包体积

---

## 🔒 安全注意事项

1. **Token 存储**: 生产环境考虑使用 httpOnly Cookie
2. **XSS 防护**: React 默认转义 HTML，注意 dangerouslySetInnerHTML 使用
3. **CSRF 防护**: 后端实现 CSRF Token 验证
4. **HTTPS**: 生产环境必须使用 HTTPS
5. **敏感信息**: 不要在前端存储敏感数据

---

## 📦 生产部署

### 构建生产版本
```bash
npm run build
```

### 部署选项
1. **静态托管**: Vercel, Netlify, GitHub Pages
2. **Docker**: 使用 Nginx 镜像
3. **CDN**: 结合 CDN 加速静态资源

### 环境变量
创建 `.env.production`：
```
REACT_APP_API_URL=https://your-api-domain.com
```

---

## 🎨 自定义样式

所有组件使用 Tailwind CSS，可以通过以下方式自定义：

1. **修改主题**: 在 `tailwind.config.js` 中扩展主题
2. **自定义类**: 在组件中直接使用 Tailwind 类
3. **全局样式**: 在 `src/index.css` 中添加

---

## 📞 技术支持

如有问题，请查看：
- 浏览器控制台错误信息
- 网络请求状态
- 后端日志输出

祝使用愉快！ 🎉

