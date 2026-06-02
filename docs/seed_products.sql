-- ???????MySQL?
-- ???gugou_backend/seed_products.json + ????? product/product_image
-- ???????????? product_id ?????? product_id + image_url ??????
SET NAMES utf8mb4;
START TRANSACTION;

INSERT INTO product
  (created_at, updated_at, product_id, name, ip_name, character_name, category, reference_price, main_image, description, status, created_by_id)
VALUES
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290001', '沙奈朵手办', '精灵宝可梦', '沙奈朵', 'figure', 688.00, '/images/products/沙奈朵手办.png', '精灵宝可梦沙奈朵手办，限量发售', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290002', '春日限定徽章', '初音未来', '初音', 'badge', 58.00, '/images/products/春日限定徽章.png', '春日祭限定徽章，樱花主题', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290003', '阿尼亚表情包立牌', '间谍过家家', '阿尼亚', 'acrylic', 75.00, '/images/products/阿尼亚表情包立牌.png', '阿尼亚经典表情亚克力立牌', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290004', '蕾姆泳装手办', 'Re:从零开始的异世界生活', '蕾姆', 'figure', 298.00, '/images/products/蕾姆泳装手办.png', '蕾姆泳装Ver. 1/7比例手办', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290005', '炭治郎日轮刀模型', '鬼灭之刃', '炭治郎', 'figure', 450.00, '/images/products/炭治郎日轮刀模型.png', '炭治郎日轮刀 1:1复刻模型', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290006', '皮卡丘毛绒玩偶', '精灵宝可梦', '皮卡丘', 'doll', 129.00, '/images/products/皮卡丘毛绒玩偶.png', '皮卡丘大号毛绒玩偶 30cm', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290007', '明日香限定卡片', '新世纪福音战士', '明日香', 'card', 45.00, '/images/products/明日香限定卡片.png', 'EVA明日香限定收藏卡片', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290008', '路飞五档海报', '海贼王', '路飞', 'poster', 35.00, '/images/products/路飞五档海报.png', '路飞五档尼卡形态 A2海报', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290009', '亚丝娜亚克力挂件', '刀剑神域', '亚丝娜', 'acrylic', 42.00, '/images/products/亚丝娜亚克力挂件.png', '亚丝娜战斗服Ver.亚克力挂件', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290010', '祢豆子竹筒玩偶', '鬼灭之刃', '祢豆子', 'doll', 89.00, '/images/products/祢豆子竹筒玩偶.png', '祢豆子竹筒装迷你玩偶 20cm', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290011', '雷电影主题徽章套装', '原神', '雷电影', 'badge', 118.00, '/images/products/雷电影主题徽章套装.png', '雷电影主题金属徽章', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290012', '枫原万叶流沙亚克力', '原神', '枫原万叶', 'acrylic', 86.00, '/images/products/枫原万叶流沙亚克力.png', '枫叶主题双层流沙亚克力摆件，适合桌面展示', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290013', '纳西妲立牌', '原神', '纳西妲', 'acrylic', 92.00, '/images/products/纳西妲立牌.png', '纳西妲亚克力立牌，透明底座款', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290014', '钟离烫金色纸', '原神', '钟离', 'poster', 138.00, '/images/products/钟离烫金色纸.png', '钟离主题限定烫金色纸，岩纹压印工艺', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290015', '芙宁娜纪念卡册', '原神', '芙宁娜', 'card', 76.00, '/images/products/芙宁娜纪念卡册.png', '芙宁娜角色纪念卡册，内含角色卡与场景卡', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290016', '星野爱徽章', '我推的孩子', '星野爱', 'badge', 68.00, '/images/products/星野爱徽章.png', '星野爱徽章', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290017', '有马加奈角色立牌', '我推的孩子', '有马加奈', 'acrylic', 72.00, '/images/products/有马加奈角色立牌.png', '角色亚克力立牌，有马加奈造型，适合桌面展示', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290018', '黑川茜收藏卡', '我推的孩子', '黑川茜', 'card', 39.00, '/images/products/黑川茜收藏卡.png', '黑川茜写真风收藏卡，单包装随机闪卡', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290019', '五条悟无量空处手办', '咒术回战', '五条悟', 'figure', 398.00, '/images/products/五条悟无量空处手办.png', '五条悟无量空处姿态手办，特效件可拆卸', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290020', '虎杖悠仁战斗徽章', '咒术回战', '虎杖悠仁', 'badge', 52.00, '/images/products/虎杖悠仁战斗徽章.png', '虎杖悠仁战斗姿态徽章，哑光金属底', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290021', '伏黑惠海报', '咒术回战', '伏黑惠', 'poster', 46.00, '/images/products/伏黑惠海报.png', '伏黑惠式神主题 A2 海报，厚磅纸印刷', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290022', '钉崎野蔷薇亚克力挂件', '咒术回战', '钉崎野蔷薇', 'acrylic', 48.00, '/images/products/钉崎野蔷薇亚克力挂件.png', '钉崎野蔷薇武器主题亚克力挂件，双面印刷', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290023', '灶门炭治郎水之呼吸手办', '鬼灭之刃', '灶门炭治郎', 'figure', 328.00, '/images/products/灶门炭治郎水之呼吸手办.png', '水之呼吸特效底座手办，动态斩击姿态', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290024', '我妻善逸雷之呼吸徽章', '鬼灭之刃', '我妻善逸', 'badge', 49.00, '/images/products/我妻善逸雷之呼吸徽章.png', '雷之呼吸主题闪电边框徽章', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290025', '嘴平伊之助毛绒挂件', '鬼灭之刃', '嘴平伊之助', 'doll', 79.00, '/images/products/嘴平伊之助毛绒挂件.png', '伊之助头套造型毛绒挂件，附金属扣', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290026', '蝴蝶忍色纸', '鬼灭之刃', '蝴蝶忍', 'poster', 88.00, '/images/products/蝴蝶忍色纸.png', '蝴蝶忍主题色纸，紫色珠光纸材', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290027', '路飞尼卡手办', '海贼王', '路飞', 'figure', 520.00, '/images/products/路飞尼卡手办.png', '路飞五档尼卡形态手办，云雾特效底座', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290028', '索隆三刀流亚克力', '海贼王', '索隆', 'acrylic', 84.00, '/images/products/索隆三刀流亚克力.png', '索隆三刀流动作亚克力立牌，绿色刀光底座', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290029', '娜美航海图卡套', '海贼王', '娜美', 'card', 55.00, '/images/products/娜美航海图卡套.png', '娜美航海图主题卡套，含透明保护袋', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290030', '乔巴冬岛毛绒玩偶', '海贼王', '乔巴', 'doll', 119.00, '/images/products/乔巴冬岛毛绒玩偶.png', '乔巴冬岛造型毛绒玩偶，坐姿款 25cm', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290031', '鸣人九尾查克拉手办', '火影忍者', '漩涡鸣人', 'figure', 368.00, '/images/products/鸣人九尾查克拉手办.png', '鸣人九尾查克拉模式手办，透明火焰特效', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290032', '佐助须佐能乎徽章', '火影忍者', '宇智波佐助', 'badge', 64.00, '/images/products/佐助须佐能乎徽章.png', '须佐能乎主题镭射徽章，紫色闪膜', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290033', '卡卡西写轮眼海报', '火影忍者', '旗木卡卡西', 'poster', 42.00, '/images/products/卡卡西写轮眼海报.png', '卡卡西写轮眼主题 A2 海报，暗纹背景', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290034', '宇智波鼬亚克力', '火影忍者', '宇智波鼬', 'acrylic', 98.00, '/images/products/宇智波鼬亚克力.png', '鼬与乌鸦剪影双层亚克力摆件', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290035', '初音未来雪未来手办', '初音未来', '初音未来', 'figure', 428.00, '/images/products/初音未来雪未来手办.png', '雪未来主题手办，雪花底座与围巾配件', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290036', '绫波丽白色驾驶服手办', '新世纪福音战士', '绫波丽', 'figure', 360.00, '/images/products/绫波丽白色驾驶服手办.png', '绫波丽白色驾驶服手办，透明底座款', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290037', '明日香红色驾驶服手办', '新世纪福音战士', '明日香', 'figure', 372.00, '/images/products/明日香红色驾驶服手办.png', '明日香红色驾驶服手办，战斗姿态款', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290038', '初号机金属徽章', '新世纪福音战士', '初号机', 'badge', 72.00, '/images/products/初号机金属徽章.png', '初号机头部金属徽章，紫绿色珐琅', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290039', 'EVA 机体设定海报', '新世纪福音战士', '初号机', 'poster', 95.00, '/images/products/EVA 机体设定海报.png', 'EVA 机体设定图 A1 海报，工程图风格', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290040', '阿尼亚校服毛绒玩偶', '间谍过家家', '阿尼亚', 'doll', 108.00, '/images/products/阿尼亚校服毛绒玩偶.png', '阿尼亚校服造型毛绒玩偶，坐姿 22cm', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290041', '约尔亚克力', '间谍过家家', '约尔', 'acrylic', 82.00, '/images/products/约尔亚克力.png', '约尔主题亚克力立牌，黑红配色', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290042', '劳埃德任务卡片', '间谍过家家', '劳埃德', 'card', 36.00, '/images/products/劳埃德任务卡片.png', '劳埃德任务档案风收藏卡片', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290043', '波奇塔毛绒挂件', '电锯人', '波奇塔', 'doll', 69.00, '/images/products/波奇塔毛绒挂件.png', '波奇塔迷你毛绒挂件，链条可拆卸', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290044', '电次电锯形态手办', '电锯人', '电次', 'figure', 410.00, '/images/products/电次电锯形态手办.png', '电次电锯形态动态手办，血迹特效涂装', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290045', '帕瓦恶魔角徽章', '电锯人', '帕瓦', 'badge', 54.00, '/images/products/帕瓦恶魔角徽章.png', '帕瓦恶魔角造型徽章，红色闪膜', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290046', '早川秋海报', '电锯人', '早川秋', 'poster', 58.00, '/images/products/早川秋海报.png', '主题海报，暗色电影海报风', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290047', '喜多川海梦水族馆立牌', '更衣人偶坠入爱河', '喜多川海梦', 'acrylic', 88.00, '/images/products/喜多川海梦水族馆立牌.png', '水族馆约会主题亚克力立牌，蓝色透明底座', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290048', '时崎狂三哥特手办', '约会大作战', '时崎狂三', 'figure', 488.00, '/images/products/时崎狂三哥特手办.png', '狂三哥特礼服手办，钟表底座与枪械配件', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290049', '夜刀神十香灵装徽章', '约会大作战', '夜刀神十香', 'badge', 59.00, '/images/products/夜刀神十香灵装徽章.png', '十香灵装主题徽章，紫色渐变底', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290050', '雪之下雪乃校园色纸', '我的青春恋爱物语果然有问题', '雪之下雪乃', 'poster', 82.00, '/images/products/雪之下雪乃校园色纸.png', '雪乃校园主题收藏色纸，社团教室背景', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290051', '由比滨结衣亚克力挂件', '我的青春恋爱物语果然有问题', '由比滨结衣', 'acrylic', 52.00, '/images/products/由比滨结衣亚克力挂件.png', '结衣校服造型亚克力挂件，糖果色底板', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290052', '牧濑红莉栖实验室手办', '命运石之门', '牧濑红莉栖', 'figure', 399.00, '/images/products/牧濑红莉栖实验室手办.png', '红莉栖实验室白大褂手办，附书本配件', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290053', '冈部伦太郎凤凰院徽章', '命运石之门', '冈部伦太郎', 'badge', 44.00, '/images/products/冈部伦太郎凤凰院徽章.png', '凤凰院凶真主题徽章，实验室标识设计', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290054', 'Saber誓约胜利之剑手办', 'Fate/stay night', 'Saber', 'figure', 568.00, '/images/products/Saber誓约胜利之剑手办.png', 'Saber 持剑战斗姿态手办，透明剑光特效', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290055', '远坂凛宝石魔术徽章', 'Fate/stay night', '远坂凛', 'badge', 62.00, '/images/products/远坂凛宝石魔术徽章.png', '远坂凛宝石魔术主题徽章，红宝石烫印', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290056', '间桐樱樱花亚克力', 'Fate/stay night', '间桐樱', 'acrylic', 74.00, '/images/products/间桐樱樱花亚克力.png', '樱花主题亚克力立牌，淡紫透明底座', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290057', '爱蜜莉雅雪花手办', 'Re:从零开始的异世界生活', '爱蜜莉雅', 'figure', 336.00, '/images/products/爱蜜莉雅雪花手办.png', '爱蜜莉雅雪花主题手办，银白色礼服款', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290058', '拉姆女仆徽章', 'Re:从零开始的异世界生活', '拉姆', 'badge', 48.00, '/images/products/拉姆女仆徽章.png', '拉姆女仆装主题徽章，粉色边框', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290059', '蕾姆拉姆双人色纸', 'Re:从零开始的异世界生活', '蕾姆/拉姆', 'poster', 108.00, '/images/products/蕾姆拉姆双人色纸.png', '蕾姆与拉姆双人收藏色纸，限定双签风设计', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290060', '空条承太郎白金之星手办', 'JOJO的奇妙冒险', '空条承太郎', 'figure', 498.00, '/images/products/空条承太郎白金之星手办.png', '承太郎与白金之星组合手办，双角色底座', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290061', '乔鲁诺黄金体验徽章', 'JOJO的奇妙冒险', '乔鲁诺', 'badge', 66.00, '/images/products/乔鲁诺黄金体验徽章.png', '乔鲁诺黄金体验主题徽章，金色镜面工艺', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290063', '阿米娅罗德岛徽章', '明日方舟', '阿米娅', 'badge', 38.00, '/images/products/阿米娅罗德岛徽章.png', '阿米娅罗德岛主题徽章，采用角色立绘与罗德岛标识设计', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290064', '凯尔希女仆亚克力立牌', '明日方舟', '凯尔希', 'acrylic', 88.00, '/images/products/凯尔希女仆亚克力立牌.png', '凯尔希女仆主题亚克力立牌，适合桌面展示与收藏', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290065', '火陈通行证挂件', '明日方舟', '陈', 'other', 45.00, '/images/products/火陈通行证挂件.png', '火陈主题挂件，配有角色武器与龙门元素装饰', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290066', '能天使拉特兰亚克力立牌', '明日方舟', '能天使', 'acrylic', 86.00, '/images/products/能天使拉特兰亚克力立牌.png', '能天使拉特兰主题亚克力立牌，采用活泼明亮的角色形象设计', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290067', '银灰谢拉格收藏立牌', '明日方舟', '银灰', 'acrylic', 98.00, '/images/products/银灰谢拉格收藏立牌.png', '银灰谢拉格主题收藏立牌，突出领主形象与雪境风格', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290068', '艾雅法拉手办', '明日方舟', '艾雅法拉', 'figure', 50.00, '/images/products/艾雅法拉手办.png', '艾雅法拉火山主题手办，结合术师元素与温暖色调设计', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290069', '史尔特尔主题立牌', '明日方舟', '史尔特尔', 'acrylic', 108.00, '/images/products/史尔特尔主题立牌.png', '史尔特尔主题亚克力立牌，突出火焰与剑刃视觉元素', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290070', '浊心斯卡蒂深海主题徽章', '明日方舟', '浊心斯卡蒂', 'badge', 58.00, '/images/products/浊心斯卡蒂深海主题徽章.png', '浊心斯卡蒂深海主题徽章，采用蓝色系与海嗣风格元素设计', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290071', '森蚺手办', '明日方舟', '森蚺', 'figure', 52.00, '/images/products/森蚺手办.png', '森蚺手办，优美又华丽', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290072', '《黑白的阿维斯塔》小说第一卷 凶战士篇', '神座万象', '黑白的阿维斯塔', 'other', 52.00, '/images/products/《黑白的阿维斯塔》小说第一卷 凶战士篇.jpg', '《黑白的阿维斯塔》小说第一卷 凶战士篇', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290073', '《黑白的阿维斯塔》小说第二卷 惭愧之空篇', '神座万象', '黑白的阿维斯塔', 'other', 52.00, '/images/products/《黑白的阿维斯塔》小说第二卷 惭愧之空篇.jpg', '《黑白的阿维斯塔》小说第二卷 惭愧之空篇', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290074', '《黑白的阿维斯塔》小说第三卷 不变之物篇', '神座万象', '黑白的阿维斯塔', 'other', 52.00, '/images/products/《黑白的阿维斯塔》小说第三卷 不变之物篇.jpg', '《黑白的阿维斯塔》小说第三卷 不变之物篇', 'active', NULL),
  (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'G202605290075', '《黑白的阿维斯塔》小说第四卷 堕天无惭乐土篇', '神座万象', '黑白的阿维斯塔', 'other', 52.00, '/images/products/《黑白的阿维斯塔》小说第四卷 堕天无惭乐土篇.jpg', '《黑白的阿维斯塔》小说第四卷 堕天无惭乐土篇', 'active', NULL)
ON DUPLICATE KEY UPDATE
  updated_at = CURRENT_TIMESTAMP,
  name = VALUES(name),
  ip_name = VALUES(ip_name),
  character_name = VALUES(character_name),
  category = VALUES(category),
  reference_price = VALUES(reference_price),
  main_image = VALUES(main_image),
  description = VALUES(description),
  status = VALUES(status);

INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/沙奈朵手办.png', 0, 'G202605290001'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290001' AND image_url = '/images/products/沙奈朵手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/春日限定徽章.png', 0, 'G202605290002'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290002' AND image_url = '/images/products/春日限定徽章.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/阿尼亚表情包立牌.png', 0, 'G202605290003'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290003' AND image_url = '/images/products/阿尼亚表情包立牌.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/蕾姆泳装手办.png', 0, 'G202605290004'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290004' AND image_url = '/images/products/蕾姆泳装手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/炭治郎日轮刀模型.png', 0, 'G202605290005'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290005' AND image_url = '/images/products/炭治郎日轮刀模型.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/皮卡丘毛绒玩偶.png', 0, 'G202605290006'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290006' AND image_url = '/images/products/皮卡丘毛绒玩偶.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/明日香限定卡片.png', 0, 'G202605290007'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290007' AND image_url = '/images/products/明日香限定卡片.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/路飞五档海报.png', 0, 'G202605290008'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290008' AND image_url = '/images/products/路飞五档海报.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/亚丝娜亚克力挂件.png', 0, 'G202605290009'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290009' AND image_url = '/images/products/亚丝娜亚克力挂件.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/祢豆子竹筒玩偶.png', 0, 'G202605290010'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290010' AND image_url = '/images/products/祢豆子竹筒玩偶.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/雷电影主题徽章套装.png', 0, 'G202605290011'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290011' AND image_url = '/images/products/雷电影主题徽章套装.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/枫原万叶流沙亚克力.png', 0, 'G202605290012'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290012' AND image_url = '/images/products/枫原万叶流沙亚克力.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/纳西妲立牌.png', 0, 'G202605290013'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290013' AND image_url = '/images/products/纳西妲立牌.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/钟离烫金色纸.png', 0, 'G202605290014'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290014' AND image_url = '/images/products/钟离烫金色纸.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/芙宁娜纪念卡册.png', 0, 'G202605290015'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290015' AND image_url = '/images/products/芙宁娜纪念卡册.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/星野爱徽章.png', 0, 'G202605290016'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290016' AND image_url = '/images/products/星野爱徽章.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/有马加奈角色立牌.png', 0, 'G202605290017'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290017' AND image_url = '/images/products/有马加奈角色立牌.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/黑川茜收藏卡.png', 0, 'G202605290018'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290018' AND image_url = '/images/products/黑川茜收藏卡.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/五条悟无量空处手办.png', 0, 'G202605290019'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290019' AND image_url = '/images/products/五条悟无量空处手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/虎杖悠仁战斗徽章.png', 0, 'G202605290020'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290020' AND image_url = '/images/products/虎杖悠仁战斗徽章.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/伏黑惠海报.png', 0, 'G202605290021'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290021' AND image_url = '/images/products/伏黑惠海报.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/钉崎野蔷薇亚克力挂件.png', 0, 'G202605290022'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290022' AND image_url = '/images/products/钉崎野蔷薇亚克力挂件.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/灶门炭治郎水之呼吸手办.png', 0, 'G202605290023'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290023' AND image_url = '/images/products/灶门炭治郎水之呼吸手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/我妻善逸雷之呼吸徽章.png', 0, 'G202605290024'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290024' AND image_url = '/images/products/我妻善逸雷之呼吸徽章.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/嘴平伊之助毛绒挂件.png', 0, 'G202605290025'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290025' AND image_url = '/images/products/嘴平伊之助毛绒挂件.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/蝴蝶忍色纸.png', 0, 'G202605290026'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290026' AND image_url = '/images/products/蝴蝶忍色纸.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/路飞尼卡手办.png', 0, 'G202605290027'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290027' AND image_url = '/images/products/路飞尼卡手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/索隆三刀流亚克力.png', 0, 'G202605290028'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290028' AND image_url = '/images/products/索隆三刀流亚克力.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/娜美航海图卡套.png', 0, 'G202605290029'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290029' AND image_url = '/images/products/娜美航海图卡套.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/乔巴冬岛毛绒玩偶.png', 0, 'G202605290030'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290030' AND image_url = '/images/products/乔巴冬岛毛绒玩偶.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/鸣人九尾查克拉手办.png', 0, 'G202605290031'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290031' AND image_url = '/images/products/鸣人九尾查克拉手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/佐助须佐能乎徽章.png', 0, 'G202605290032'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290032' AND image_url = '/images/products/佐助须佐能乎徽章.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/卡卡西写轮眼海报.png', 0, 'G202605290033'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290033' AND image_url = '/images/products/卡卡西写轮眼海报.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/宇智波鼬亚克力.png', 0, 'G202605290034'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290034' AND image_url = '/images/products/宇智波鼬亚克力.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/初音未来雪未来手办.png', 0, 'G202605290035'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290035' AND image_url = '/images/products/初音未来雪未来手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/绫波丽白色驾驶服手办.png', 0, 'G202605290036'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290036' AND image_url = '/images/products/绫波丽白色驾驶服手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/明日香红色驾驶服手办.png', 0, 'G202605290037'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290037' AND image_url = '/images/products/明日香红色驾驶服手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/初号机金属徽章.png', 0, 'G202605290038'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290038' AND image_url = '/images/products/初号机金属徽章.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/EVA 机体设定海报.png', 0, 'G202605290039'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290039' AND image_url = '/images/products/EVA 机体设定海报.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/阿尼亚校服毛绒玩偶.png', 0, 'G202605290040'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290040' AND image_url = '/images/products/阿尼亚校服毛绒玩偶.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/约尔亚克力.png', 0, 'G202605290041'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290041' AND image_url = '/images/products/约尔亚克力.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/劳埃德任务卡片.png', 0, 'G202605290042'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290042' AND image_url = '/images/products/劳埃德任务卡片.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/波奇塔毛绒挂件.png', 0, 'G202605290043'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290043' AND image_url = '/images/products/波奇塔毛绒挂件.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/电次电锯形态手办.png', 0, 'G202605290044'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290044' AND image_url = '/images/products/电次电锯形态手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/帕瓦恶魔角徽章.png', 0, 'G202605290045'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290045' AND image_url = '/images/products/帕瓦恶魔角徽章.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/早川秋海报.png', 0, 'G202605290046'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290046' AND image_url = '/images/products/早川秋海报.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/喜多川海梦水族馆立牌.png', 0, 'G202605290047'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290047' AND image_url = '/images/products/喜多川海梦水族馆立牌.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/时崎狂三哥特手办.png', 0, 'G202605290048'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290048' AND image_url = '/images/products/时崎狂三哥特手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/夜刀神十香灵装徽章.png', 0, 'G202605290049'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290049' AND image_url = '/images/products/夜刀神十香灵装徽章.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/雪之下雪乃校园色纸.png', 0, 'G202605290050'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290050' AND image_url = '/images/products/雪之下雪乃校园色纸.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/由比滨结衣亚克力挂件.png', 0, 'G202605290051'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290051' AND image_url = '/images/products/由比滨结衣亚克力挂件.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/牧濑红莉栖实验室手办.png', 0, 'G202605290052'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290052' AND image_url = '/images/products/牧濑红莉栖实验室手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/冈部伦太郎凤凰院徽章.png', 0, 'G202605290053'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290053' AND image_url = '/images/products/冈部伦太郎凤凰院徽章.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/Saber誓约胜利之剑手办.png', 0, 'G202605290054'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290054' AND image_url = '/images/products/Saber誓约胜利之剑手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/远坂凛宝石魔术徽章.png', 0, 'G202605290055'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290055' AND image_url = '/images/products/远坂凛宝石魔术徽章.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/间桐樱樱花亚克力.png', 0, 'G202605290056'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290056' AND image_url = '/images/products/间桐樱樱花亚克力.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/爱蜜莉雅雪花手办.png', 0, 'G202605290057'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290057' AND image_url = '/images/products/爱蜜莉雅雪花手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/拉姆女仆徽章.png', 0, 'G202605290058'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290058' AND image_url = '/images/products/拉姆女仆徽章.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/蕾姆拉姆双人色纸.png', 0, 'G202605290059'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290059' AND image_url = '/images/products/蕾姆拉姆双人色纸.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/空条承太郎白金之星手办.png', 0, 'G202605290060'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290060' AND image_url = '/images/products/空条承太郎白金之星手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/乔鲁诺黄金体验徽章.png', 0, 'G202605290061'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290061' AND image_url = '/images/products/乔鲁诺黄金体验徽章.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/阿米娅罗德岛徽章.png', 0, 'G202605290063'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290063' AND image_url = '/images/products/阿米娅罗德岛徽章.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/凯尔希女仆亚克力立牌.png', 0, 'G202605290064'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290064' AND image_url = '/images/products/凯尔希女仆亚克力立牌.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/火陈通行证挂件.png', 0, 'G202605290065'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290065' AND image_url = '/images/products/火陈通行证挂件.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/能天使拉特兰亚克力立牌.png', 0, 'G202605290066'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290066' AND image_url = '/images/products/能天使拉特兰亚克力立牌.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/银灰谢拉格收藏立牌.png', 0, 'G202605290067'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290067' AND image_url = '/images/products/银灰谢拉格收藏立牌.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/艾雅法拉手办.png', 0, 'G202605290068'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290068' AND image_url = '/images/products/艾雅法拉手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/史尔特尔黄昏主题立牌.png', 0, 'G202605290069'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290069' AND image_url = '/images/products/史尔特尔黄昏主题立牌.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/浊心斯卡蒂深海主题徽章.png', 0, 'G202605290070'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290070' AND image_url = '/images/products/浊心斯卡蒂深海主题徽章.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/森蚺手办.png', 0, 'G202605290071'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290071' AND image_url = '/images/products/森蚺手办.png'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/《黑白的阿维斯塔》小说第一卷 凶战士篇.jpg', 0, 'G202605290072'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290072' AND image_url = '/images/products/《黑白的阿维斯塔》小说第一卷 凶战士篇.jpg'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/《黑白的阿维斯塔》小说第二卷 惭愧之空篇.jpg', 0, 'G202605290073'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290073' AND image_url = '/images/products/《黑白的阿维斯塔》小说第二卷 惭愧之空篇.jpg'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/《黑白的阿维斯塔》小说第三卷 不变之物篇.jpg', 0, 'G202605290074'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290074' AND image_url = '/images/products/《黑白的阿维斯塔》小说第三卷 不变之物篇.jpg'
);
INSERT INTO product_image
  (created_at, updated_at, image_url, sort_order, product_id)
SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '/images/products/《黑白的阿维斯塔》小说第四卷 堕天无惭乐土篇.jpg', 0, 'G202605290075'
WHERE NOT EXISTS (
  SELECT 1 FROM product_image
  WHERE product_id = 'G202605290075' AND image_url = '/images/products/《黑白的阿维斯塔》小说第四卷 堕天无惭乐土篇.jpg'
);

COMMIT;
