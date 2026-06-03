"""
演示数据填充脚本
- 清除所有旧数据
- 创建 3 个测试用户（test1/test2/test3，密码均为 123）
- 使用项目根目录的 商品.png 作为所有商品图片
- 图片按后端规则（UUID重命名）复制到 static/uploads/
"""
import sys
import os
import uuid
import shutil

# 切换到 backend 目录，确保所有导入路径正确
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
os.chdir(BACKEND_DIR)
sys.path.insert(0, BACKEND_DIR)

from app import create_app
from app.extensions import db
from app.models import User, Product, Order, Message
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()

# 路径常量
ROOT_DIR = os.path.dirname(BACKEND_DIR)  # 项目根目录
SOURCE_IMAGE = os.path.join(ROOT_DIR, '商品.png')
UPLOAD_FOLDER = os.path.join(BACKEND_DIR, 'static', 'uploads')

# ── 分类中文映射 ──
CAT_LABELS = {
    'textbook': '教材教辅', 'electronics': '电子数码', 'daily': '生活日用',
    'clothing': '服饰鞋包', 'sports': '运动户外', 'other': '其他'
}

# ── 商品数据 ──
# 每个分类 4-5 件商品，模拟真实校园二手交易场景
PRODUCTS_RAW = [
    # === 教材教辅 ===
    ("高等数学（同济第七版）上册", "九成新，只有前两章有少量笔记，适合考研复习使用。附赠课后习题答案。", "textbook", 12.00),
    ("数据结构（C语言版）- 严蔚敏", "经典教材，计算机考研必备。书角轻微磨损，内页干净无标记。", "textbook", 15.50),
    ("考研数学复习全书（张宇）", "去年考研用书，全套三本不拆卖。数学一二三通用版，重点章节已标注。", "textbook", 28.00),
    ("大学英语四级词汇闪过", "全新未拆封，买多了出一本。2025版，适合大一大二备考四级。", "textbook", 8.00),
    ("电路分析基础（第五版）", "电子学院必修课教材，书况良好。期末考试重点已用荧光笔标注。", "textbook", 10.00),

    # === 电子数码 ===
    ("罗技 G304 无线鼠标", "入手半年，换 GPW 了故出。无拆修无暗病，电池仓弹簧完好，送一节电池。", "electronics", 69.00),
    ("小米手环 8 Pro", "充新成色，表带有轻微使用痕迹。功能正常，续航约一周。配件齐全带包装盒。", "electronics", 129.00),
    ("iPad mini 6 64G 星光色", "2024年购入，主要用于看网课和记笔记。屏幕无划痕，边框轻微掉漆。带原装充电器和盒子，送一个保护壳。", "electronics", 1899.00),
    ("ANKER 65W 氮化镓充电头", "刚买一个月，发现用不上这么大功率的。单口 65W 最大，支持笔记本充电。", "electronics", 45.00),
    ("索尼 WH-CH720N 降噪头戴耳机", "用了不到三个月，换 XM5 了所以出。降噪效果不错，佩戴舒适不夹头。箱说全。", "electronics", 299.00),

    # === 生活日用 ===
    ("小米 LED 护眼台灯", "宿舍必备，三档色温可调，亮度无级调节。灯臂灵活可折叠，不占桌面空间。", "daily", 35.00),
    ("保温杯 316不锈钢 500ml", "全新未使用，公司年会礼品。内胆 316 不锈钢，保温 12 小时。白色磨砂质感。", "daily", 18.00),
    ("可折叠收纳箱 大号 66L", "宿舍搬家买的，现在用不上了。承重好，可叠放。展开尺寸 50×35×38cm。", "daily", 15.00),
    ("桌面小风扇 USB充电款", "夏天图书馆必备，三档风力，超静音。内置 2000mAh 电池，续航 6 小时。", "daily", 22.00),

    # === 服饰鞋包 ===
    ("SEU 限定纪念卫衣 均码", "校庆纪念款，仅穿过一次拍照。深绿色，胸前有东南大学校徽刺绣。均码偏宽松。", "clothing", 49.00),
    ("匡威 Chuck 70 高帮 黑色 42码", "去年双十一购入，穿了一个季度。鞋底正常磨损，鞋面无破损。经典百搭款。", "clothing", 129.00),
    ("Jansport 双肩包 黑色", "大二用到大三了，除了底部有点脏之外完好。超轻款，背电脑很舒服。", "clothing", 45.00),
    ("优衣库轻羽绒马甲 男款 M码", "几乎没怎么穿过，南京的秋天穿正合适。轻薄保暖可收纳，深蓝色。", "clothing", 59.00),

    # === 运动户外 ===
    ("尤尼克斯羽毛球拍 NR-200", "入门级好拍，适合新手练习。弦是上个月刚换的 BG65 24磅。送一个拍套。", "sports", 89.00),
    ("Keep 瑜伽垫 加厚 10mm", "买来用了两次就闲置了… 几乎全新。加厚款膝盖不疼，送绑带。", "sports", 35.00),
    ("迪卡侬 20kg 可调节哑铃", "可调节重量很方便，宿舍健身够用了。外观轻微磨损不影响使用。", "sports", 79.00),
    ("自行车头盔 + 手套套装", "骑行了半个学期，头盔完好无摔过。一并购入的骑行手套 L码也在。", "sports", 40.00),

    # === 其他 ===
    ("卡西欧 fx-991CN 计算器", "考试专用，大学生必备。功能完好，屏幕无坏点。送两颗备用电池。", "other", 25.00),
    ("SEU 校园卡套 + 挂绳", "全新手工皮质卡套，印有东南大学校名。可放两张卡片，挂绳可拆卸。", "other", 9.90),
    ("剧本杀《来电》全套", "玩过一次，卡牌齐全无损坏。包含主持人手册和道具，非常适合宿舍团建。", "other", 19.00),
    ("桌面多肉植物组合 3盆", "养了半年，状态很好。包括熊童子、玉露和生石花三个品种，带陶盆。", "other", 12.00),
]

# ── 订单关系（买家索引, 卖家索引, 商品在 PRODUCTS_RAW 中的索引）──
ORDERS_RAW = [
    (1, 0, 6),   # test2 买 test1 的小米手环
    (2, 0, 8),   # test3 买 test1 的 ANKER 充电头
    (0, 1, 12),  # test1 买 test2 的保温杯
    (2, 1, 15),  # test3 买 test2 的 SEU 卫衣
    (0, 2, 20),  # test1 买 test3 的尤尼克斯球拍
    (1, 0, 2),   # test2 买 test1 的考研数学 → 取消
]

# ── 消息数据 ──
MESSAGES_RAW = [
    # test1 ↔ test2
    (0, 1, "你好，请问高等数学还在吗？"),
    (1, 0, "在的，需要的话可以直接拍下~"),
    (0, 1, "好的，书里面笔记多吗？"),
    (1, 0, "不多，只有前两章有一些，后面都是全新的"),
    (0, 1, "OK，那我现在拍！"),
    # test3 ↔ test1
    (2, 0, "您好，iPad mini 可以小刀吗？"),
    (0, 2, "可以稍微降一点，你出多少？"),
    (2, 0, "1750 可以吗？面交"),
    (0, 2, "1770 吧，我送你一个保护壳"),
    (2, 0, "行，我拍了"),
    # test2 ↔ test3
    (1, 2, "羽毛球拍还在吗？"),
    (2, 1, "在的在的，拍子成色很好"),
    (1, 2, "弦是新换的吗？"),
    (2, 1, "对，上个月刚换的 BG65，24磅"),
]


def copy_image():
    """将商品.png复制到uploads目录，返回UUID文件名"""
    if not os.path.exists(SOURCE_IMAGE):
        print(f"ERROR: 源图片不存在: {SOURCE_IMAGE}")
        sys.exit(1)
    filename = f"{uuid.uuid4().hex}.png"
    dest = os.path.join(UPLOAD_FOLDER, filename)
    shutil.copy2(SOURCE_IMAGE, dest)
    return filename


with app.app_context():
    # ==========================================
    # 1. 清除所有旧数据（按外键依赖顺序）
    # ==========================================
    print("Clearing old data...")
    Message.query.delete()
    Order.query.delete()
    Product.query.delete()
    User.query.delete()
    db.session.commit()
    print("  Done - old data cleared")

    # ==========================================
    # 2. 清理上传目录中的旧图片
    # ==========================================
    print("Clearing upload directory...")
    for f in os.listdir(UPLOAD_FOLDER):
        if f == '.gitkeep':
            continue
        fpath = os.path.join(UPLOAD_FOLDER, f)
        if os.path.isfile(fpath):
            os.remove(fpath)
    print("  Done - upload directory cleared")

    # ==========================================
    # 3. 创建测试用户
    # ==========================================
    print("Creating test users...")
    users = []
    for i in range(1, 4):
        u = User(
            username=f"test{i}",
            email=f"test{i}@seu.edu.cn",
            password_hash=generate_password_hash("123")
        )
        db.session.add(u)
        users.append(u)
    db.session.commit()
    for u in users:
        db.session.refresh(u)
    for u in users:
        print(f"  Created: {u.username} (id={u.id}, email={u.email}) password: 123")

    # ==========================================
    # 4. 创建商品
    # ==========================================
    print("Creating products...")
    products = []
    for idx, (title, desc, cat, price) in enumerate(PRODUCTS_RAW):
        seller = users[idx % 3]
        img_filename = copy_image()
        image_url = f"http://localhost:5000/static/uploads/{img_filename}"

        p = Product(
            seller_id=seller.id,
            title=title,
            description=desc,
            category=cat,
            price=price,
            image_url=image_url,
            status='active'
        )
        db.session.add(p)
        products.append(p)
        print(f"  [{CAT_LABELS[cat]}] {title}  {price:.2f} (seller: {seller.username})")
    db.session.commit()
    for p in products:
        db.session.refresh(p)

    # ==========================================
    # 5. 创建订单
    # ==========================================
    print("Creating orders...")
    for oi, (buyer_idx, seller_idx, prod_idx) in enumerate(ORDERS_RAW):
        buyer = users[buyer_idx]
        product = products[prod_idx]

        now_str = datetime.now().strftime('%Y%m%d%H%M%S')
        order_no = f"{now_str}{uuid.uuid4().hex[:8].upper()}"

        is_cancelled = (oi == len(ORDERS_RAW) - 1)
        status = 'cancelled' if is_cancelled else 'completed'

        order = Order(
            order_no=order_no,
            buyer_id=buyer.id,
            seller_id=product.seller_id,
            product_id=product.id,
            deal_price=product.price,
            status=status
        )
        db.session.add(order)

        if is_cancelled:
            product.status = 'active'
        else:
            product.status = 'sold'

        tag = "CANCELLED" if is_cancelled else "COMPLETED"
        print(f"  Order [{tag}] {buyer.username} bought '{product.title}' for {product.price:.2f}")

    db.session.commit()

    # ==========================================
    # 6. 创建聊天消息
    # ==========================================
    print("Creating chat messages...")
    for sender_idx, receiver_idx, content in MESSAGES_RAW:
        sender = users[sender_idx]
        receiver = users[receiver_idx]
        msg = Message(
            sender_id=sender.id,
            receiver_id=receiver.id,
            content=content,
            is_read=True
        )
        db.session.add(msg)
    db.session.commit()
    print(f"  Created {len(MESSAGES_RAW)} messages")

    # ==========================================
    # 7. 汇总
    # ==========================================
    print()
    print("=" * 55)
    print("  DEMO DATA CREATED SUCCESSFULLY")
    print("=" * 55)
    print(f"  Users:    {User.query.count()}")
    print(f"  Products: {Product.query.count()} (active={Product.query.filter_by(status='active').count()}, sold={Product.query.filter_by(status='sold').count()}, deleted=0)")
    print(f"  Orders:   {Order.query.count()} (completed={Order.query.filter_by(status='completed').count()}, cancelled={Order.query.filter_by(status='cancelled').count()})")
    print(f"  Messages: {Message.query.count()}")
    print()
    print("  Demo accounts:")
    for u in users:
        db.session.refresh(u)
        print(f"    {u.email} / 123")
    print()
    upload_count = len([f for f in os.listdir(UPLOAD_FOLDER) if f != '.gitkeep'])
    print(f"  Uploaded images: {upload_count}")
