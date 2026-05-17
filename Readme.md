# 东南大学二手交易平台 - 环境配置与启动指南

本文档将指导您如何从零开始配置并运行该前后端分离项目。

## 环境要求

* **Python**: 3.10 或更高版本
* **Node.js**: v18 或更高版本
* **数据库**: MySQL 8.0
* **包管理器**: `npm`

---

## 第一步：数据库准备

1. 本地安装并启动 MySQL 8.0 服务。
2. 登录 MySQL 客户端，执行项目根目录下的 SQL 脚本：

```bash
mysql -u root -p < mysql_init.sql
```

   *(注：该脚本会自动创建名为 `campus_market` 的数据库，并建立相关的表及外键关系。)*

---

## 第二步：后端环境配置 (Flask)

1. 进入后端目录：

   ```bash
   cd backend
   ```

2. 创建并激活 Python 虚拟环境：

   * **Windows**:
  
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

   * **macOS/Linux**:

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

4. **配置文件与上传目录检查**
   * 确保 `backend/static/uploads` 目录存在。如果不存在，请手动创建（用于保存本地图片）。
   * 修改 `backend/` 目录下的 `config.py` 文件，填入本地数据库信息：

    ```python
    # 数据库配置 (请将 root 和 password 替换为你本地的 MySQL 账号密码)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@127.0.0.1:3306/campus_market?charset=utf8mb4'   
    ```

5. **启动后端服务**

   ```bash
   python run.py
   ```

   *后端服务默认将运行在 `http://localhost:5000`*

---

## 第三步：前端环境配置 (Vue 3)

1. 新开一个终端，进入前端目录：

   ```bash
   cd frontend
   ```

2. 安装项目依赖：

   ```bash
   npm install
   ```

3. 启动前端开发服务器：

   ```bash
   npm run dev
   ```

   *前端服务通常将运行在 `http://localhost:5173` (Vite 默认端口)*

---

## 第四步：系统联调测试

1. 打开浏览器访问 `http://localhost:5173`。
2. **注册账号**：进入登录/注册页面，注册两个测试账号（例如 UserA 和 UserB）。
3. **测试发布**：使用 UserA 登录，进入发布页面，尝试上传图片并发布一件闲置商品。
4. **测试交易**：使用 UserB 登录，在首页找到该商品，点击“购买”。
5. **测试聊天**：UserB 在商品详情页点击“联系卖家”，测试基于 SocketIO 的实时通讯是否正常，检查双方是否能收到即时消息。
