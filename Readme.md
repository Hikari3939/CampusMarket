# 东南大学二手交易平台 (CampusMarket)

基于 **Vue 3 + Flask + MySQL + WebSocket** 的校园二手交易平台，支持商品发布、搜索浏览、在线购买、实时私信聊天等功能。

---

## 项目概览

| 层级 | 技术栈 | 说明 |
| :--- | :--- | :--- |
| **前端** | Vue 3 (Composition API) + Vite + Pinia + Vue Router + Element Plus + Axios | SPA 单页应用，东南大学 VIS 色彩体系 |
| **后端** | Python 3.14 + Flask 3.x + Flask-SQLAlchemy + Flask-JWT-Extended + Flask-SocketIO | RESTful API + WebSocket 实时推送 |
| **数据库** | MySQL 8.0 | utf8mb4 字符集，InnoDB 引擎 |
| **实时通讯** | Flask-SocketIO (gevent) + socket.io-client | 全局 WebSocket 长连接，支持多标签页同步 |

### 核心功能

- **用户认证**：邮箱注册 + JWT Token 鉴权，路由守卫拦截未登录访问
- **商品管理**：发布（含图片上传）、列表搜索（模糊匹配）、详情查看、下架删除（软删除 + 越权校验）
- **交易流程**：立即购买，数据库行级锁防超卖，订单快照记录成交价
- **实时通讯**：WebSocket 私信，联系人列表、未读红点、已读回执、消息持久化
- **个人中心**："我发布的" / "我买到的" 双 Tab 历史记录

---

## 环境要求

| 工具 | 最低版本 |
| :--- | :--- |
| Python | 3.10+ |
| Node.js | 18+ |
| MySQL | 8.0 |
| npm | 9+ |

---

## 快速启动

### 第一步：数据库初始化

1. 启动本地 MySQL 8.0 服务
2. 执行初始化脚本：

```bash
mysql -u root -p < mysql_init.sql
```

脚本会自动创建 `campus_market` 数据库及 `users`、`products`、`orders`、`messages` 四张表。

### 第二步：后端启动

```bash
cd backend

# 使用已有 conda 环境 (推荐)
conda activate campus_market

# 或创建新虚拟环境
# python -m venv venv && source venv/bin/activate (Linux/macOS)
# python -m venv venv && venv\Scripts\activate (Windows)

# 安装依赖
pip install -r requirements.txt

# 修改 config.py 中的数据库连接信息（如密码不是 3939）
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:你的密码@127.0.0.1:3306/campus_market?charset=utf8mb4'

# 启动服务 (默认 http://localhost:5000)
python run.py
```

### 第三步：前端启动

```bash
cd frontend

# 安装依赖 (仅首次)
npm install

# 启动开发服务器 (默认 http://localhost:5173)
npm run dev
```

### 第四步：功能验证

1. 浏览器访问 `http://localhost:5173`
2. **注册**：注册两个测试账号（如 UserA 和 UserB）
3. **发布商品**：用 UserA 登录 → 点击"发布闲置" → 上传图片并填写信息
4. **浏览搜索**：在首页搜索框输入关键词，验证模糊搜索
5. **购买**：用 UserB 登录 → 进入商品详情 → 点击"立即购买"
6. **聊天**：在商品详情页点击"联系卖家" → 进入聊天中心测试实时通讯

---

## 项目结构

```text
CampusMarket/
├── backend/                    # Flask 后端
│   ├── app/
│   │   ├── __init__.py         # 应用工厂 (create_app)
│   │   ├── extensions.py       # 扩展实例 (db, jwt, cors, socketio)
│   │   ├── models.py           # ORM 模型 (User, Product, Order, Message)
│   │   ├── socket_events.py    # WebSocket 事件处理 (鉴权/收发/已读)
│   │   └── api/
│   │       ├── auth.py         # 注册 / 登录
│   │       ├── product.py      # 商品 CRUD + 图片上传
│   │       ├── order.py        # 创建订单 (含行级锁防超卖)
│   │       ├── user.py         # 个人历史 (我发布的/我买到的)
│   │       └── message.py      # 联系人列表 + 聊天历史
│   ├── static/uploads/         # 商品图片存储目录
│   ├── config.py               # 配置文件 (数据库/JWT/上传限制)
│   ├── run.py                  # 启动入口
│   └── requirements.txt        # Python 依赖
├── frontend/                   # Vue 3 前端
│   └── src/
│       ├── api/                # API 请求封装 (集中管理，禁止在 .vue 中直接调 axios)
│       │   ├── request.js      # Axios 拦截器 (Token 注入 + 401 处理)
│       │   ├── auth.js         # 登录/注册
│       │   ├── product.js      # 商品相关
│       │   ├── order.js        # 订单相关
│       │   ├── user.js         # 用户历史
│       │   └── message.js      # 私信相关
│       ├── stores/             # Pinia 全局状态
│       │   ├── user.js         # 用户登录态 + Token 管理
│       │   └── chat.js         # WebSocket 连接 + 消息管理
│       ├── router/index.js     # 路由配置 + 导航守卫
│       ├── views/              # 页面级组件
│       │   ├── Home.vue        # 首页 (搜索 + 商品瀑布流)
│       │   ├── Login.vue       # 登录/注册双 Tab
│       │   ├── ProductDetail.vue  # 商品详情 + 购买/联系
│       │   ├── Publish.vue     # 发布商品 (FormData 上传)
│       │   ├── Profile.vue     # 个人中心 (发布/购买历史)
│       │   └── Chat.vue        # 聊天中心 (联系人 + 对话框)
│       ├── components/
│       │   └── ProductCard.vue # 商品卡片 (复用组件)
│       ├── App.vue             # 根组件 (WebSocket 生命周期管理)
│       ├── main.js             # 入口 (注册 Pinia/Router/ElementPlus)
│       └── style.css           # 全局主题 (CSS 变量 + 东南大学 VIS 色彩)
├── documents/                  # 项目文档
│   ├── 项目文档.md             # 完整 API 文档 + 开发规范
│   ├── 项目结构.md             # 目录结构说明
│   ├── 开发流程.md             # 分阶段开发指南
│   ├── 标准主色.pdf            # 东南大学 VIS 主色参考
│   └── 标准辅助色.pdf          # 东南大学 VIS 辅助色参考
└── mysql_init.sql              # 数据库初始化脚本
```

---

## API 接口速查

| 方法 | 路径 | 权限 | 说明 |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | 公开 | 用户注册 |
| `POST` | `/api/auth/login` | 公开 | 用户登录，返回 JWT Token |
| `GET`  | `/api/products` | 公开 | 商品列表，支持 `?keyword=` 模糊搜索 |
| `POST` | `/api/products` | 需登录 | 发布商品（FormData，含图片） |
| `GET`  | `/api/products/<id>` | 公开 | 商品详情 |
| `DELETE` | `/api/products/<id>` | 需登录 | 下架商品（仅卖家） |
| `POST` | `/api/orders` | 需登录 | 立即购买（JSON: `product_id`） |
| `GET`  | `/api/users/me/published` | 需登录 | 我发布的商品历史 |
| `GET`  | `/api/users/me/bought` | 需登录 | 我购买的订单历史 |
| `GET`  | `/api/messages/contacts` | 需登录 | 联系人列表（含未读数） |
| `GET`  | `/api/messages/history/<id>` | 需登录 | 与某联系人的聊天记录 |

> 完整 API 文档（含请求/响应示例）见 [documents/项目文档.md](documents/项目文档.md)

---

## 设计规范要点

### 色彩体系

基于东南大学 VIS 规范，所有颜色通过 CSS 变量定义在 [style.css](frontend/src/style.css)：

| 变量名 | 色值 | 用途 |
| :--- | :--- | :--- |
| `--seu-green` | `#587558` | 主色调、主要按钮、激活态 |
| `--seu-yellow` | `#fdd000` | 点缀、强调 |
| `--seu-black` | `#231815` | 深色背景、阴影 |
| `--seu-orange` | `#F6AB00` | 价格文字、辅助操作 |
| `--seu-dark-blue` | `#151E49` | Banner / 大面积背景 |

### 安全规范

- **密码加密**：werkzeug `generate_password_hash` 哈希存储
- **JWT 鉴权**：所有敏感接口需 `Authorization: Bearer <token>` 请求头
- **越权防护**：删除商品校验 `seller_id`，购买禁止自买
- **软删除**：商品删除仅改 `status='deleted'`，保留订单关联历史
- **防超卖**：创建订单使用 `with_for_update()` 行级悲观锁
- **文件名安全**：上传图片使用 `uuid.uuid4().hex` 重命名防路径穿越

---

## 常见问题

**Q: 前端请求报 CORS 错误？**
确保后端 `config.py` 中 `Flask-CORS` 已启用，且前端 `request.js` 的 `baseURL` 指向正确的后端地址。

**Q: 图片上传失败？**
确保 `backend/static/uploads/` 目录存在，且单张图片不超过 5MB。

**Q: WebSocket 连接失败？**
检查后端是否使用 `socketio.run()` 启动（非 `app.run()`），前端 Token 是否有效。

**Q: 如何在多台设备上测试？**
前端 `vite.config.js` 已设置 `host: '0.0.0.0'`，后端 `run.py` 同样配置。同局域网设备可通过 IP 访问，注意修改 `request.js` 中的 `baseURL`。
