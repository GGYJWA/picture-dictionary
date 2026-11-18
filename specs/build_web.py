# -*- coding: utf-8 -*-
"""生成 GitHub Pages 网页：从7章 Markdown 提取112条词条 → 数据JSON + 静态网页
功能：关键词模糊搜索（中/英/俗称）→ 带出中英文提示词 + 配图缩略图 + 一键复制
"""
import re, os, html, json, shutil, subprocess, tempfile

BASE = "/Users/mac/WorkBuddy/2026-11-18-10-09-49"
SITE = os.path.join(BASE, "site")
SITE_IMG = os.path.join(SITE, "images")

# 章节配置：文件、章号、别名关键词、配色
CH = [
    ("第1章_光影与布光_16条.md", 1, "光影"),
    ("第2章_镜头与景别_15条.md", 2, "镜头"),
    ("第3章_构图与机位_11条.md", 3, "构图"),
    ("第4章_风格流派_25条.md", 4, "风格"),
    ("第5章_色彩_18条.md", 5, "色彩"),
    ("第6章_纹理与材质_12条.md", 6, "纹理"),
    ("第7章_氛围与画质_10条.md", 7, "氛围"),
]
CH_COLOR = {1:"#E8462F",2:"#2E5CE8",3:"#C8890B",4:"#12A05C",5:"#7B4FA8",6:"#E07B39",7:"#1B9AAA"}
SAMPLE = "白皮书样板_人读版_v2.md"

# 别名关键词（俗称/白描/英文）——从ima检索版沿用
ALIAS = {
    "伦勃朗光":"三角光 三角鼻影 45度侧光 脸一半亮一半暗 肖像明暗分割 Rembrandt triangular nose shadow chiaroscuro",
    "三点布光":"三角布光 主光补光轮廓光 人像立体 影棚光 three-point lighting key fill rim",
    "明暗对照法":"暗调 低调 烛光油画 暗部有细节 chiaroscuro low key candlelit painterly",
    "体积光（丁达尔效应）":"丁达尔效应 光柱 光束 耶稣光 浮尘 volumetric light god rays light shafts sunbeam",
    "主光":"主光源 主要光 打光主力 key light main light",
    "补光":"辅助光 填光 提亮阴影 fill light soft fill",
    "轮廓光":"逆光勾边 背光 边缘光 勾亮边 rim light backlight edge",
    "硬光":"直射光 锐利阴影 强反差 hard light direct light sharp shadows",
    "柔光":"散射光 柔和光 磨皮光 soft light diffused light",
    "逆光":"背光 轮廓发光 发丝光 backlight rim glow hair light",
    "侧光":"四十五度光 侧前方光 明暗分界 side light 45-degree lighting",
    "顶光":"正上方光 头顶光 显老光 top light overhead lighting",
    "底光（脚光）":"脚光 从下往上 恐怖片打光 uplight footlight horror lighting",
    "窗光":"自然侧光 靠窗光 柔光箱 window light natural side light",
    "光比":"明暗比 亮度比 反差 lighting ratio contrast ratio",
    "色温":"冷暖光 开尔文 色温值 color temperature warm cool kelvin",
    "黄金时刻":"日落前一小时 日出后 暖金光 golden hour warm sunlight",
    "蓝调时刻":"日落后深蓝 暮色 城市蓝 blue hour twilight",
    "剪影":"黑色轮廓 逆光剪影 只留外形 silhouette backlit outline",
    "眼神光":"眼睛高光 瞳孔亮点 点睛 catchlight eye highlight",
    "特写与大特写":"大特写 眼部特写 局部放大 close-up extreme close-up",
    "近景":"半身像 胸部以上 medium close-up",
    "中景":"半身 膝盖以上 带环境 medium shot",
    "全景":"全身像 人物全身 full shot full body",
    "远景":"大远景 旷野小人 苍茫 long shot wide shot",
    "推镜头":"推近 向前推进 纵深 push in dolly in",
    "拉镜头":"拉远 后退 从近到远 pull out dolly out",
    "摇镜头":"水平摇 摇摄 转头 pan",
    "移镜头":"平移 横移 轨道 视差 tracking shot dolly",
    "跟镜头":"跟随 跟拍 follow shot",
    "升降镜头":"升镜头 降镜头 俯仰变化 crane jib",
    "甩镜头":"快速摇 运动模糊 拖影 whip pan motion blur",
    "广角镜头":"广角 透视夸张 前景放大 wide angle lens",
    "长焦镜头":"长焦 压缩空间 背景虚化 telephoto lens",
    "浅景深与背景虚化":"虚化 散景 大光圈 shallow depth of field bokeh",
    "引导线":"视线引导 汇聚线 透视纵深 leading lines converging lines",
    "三分法":"九宫格 三分线 rule of thirds",
    "中心构图":"居中 正面对称 centered composition",
    "对称构图":"镜像 倒影 上下对称 symmetry mirror reflection",
    "留白":"负空间 极简 大面积空白 negative space minimal",
    "前景遮挡":"前景虚化 遮挡 层次 foreground framing",
    "框架构图":"画框 门窗取景 天然框 framing arch",
    "对角线构图":"斜线 对角线张力 diagonal composition",
    "低角度与高角度":"仰拍 俯拍 机位角度 low angle high angle",
    "鸟瞰视角":"俯瞰 无人机 垂直俯拍 bird's eye aerial top-down",
    "荷兰角（倾斜构图）":"倾斜构图 歪斜画面 dutch angle tilted",
    "纵深感与层次":"三层 前中远 空间层次 depth layering",
    "装饰艺术":"Art Deco 爵士年代 金黑几何 放射纹 art deco geometric sunburst",
    "新艺术":"Art Nouveau 穆卡 鞭索曲线 花卉藤蔓 art nouveau mucha whiplash",
    "格拉斯哥学派":"Glasgow 麦金托什 高背椅 玫瑰纹 glasgow mackintosh",
    "维也纳分离派":"Secession 克里姆特 金箔 马赛克 vienna secession klimt gold",
    "高蒂与加泰罗尼亚现代主义":"Gaudi 圣家堂 螺旋曲线 马赛克 gaudi sagrada familia",
    "包豪斯":"Bauhaus 三原色 几何构成 功能主义 bauhaus geometric primary",
    "流线型风格":"Streamline 子弹头 空气动力 1930s streamline Moderne",
    "孟菲斯风格":"Memphis 彩色积木 水磨石 1980s memphis terrazzo",
    "极简主义":"Minimalism 留白 极简 性冷淡 minimalism minimal",
    "波普艺术":"Pop art 沃霍尔 丝网印刷 大色块 pop art warhol silkscreen",
    "黑色电影":"Film noir 侦探片 雨夜 明暗对照 film noir detective",
    "诗意现实主义":"Poetic realism 雾码头 法国电影 潮湿 忧郁 poetic realism",
    "巴洛克戏剧光":"Baroque 卡拉瓦乔 追光 烛光 baroque chiaroscuro caravaggio",
    "绘画性油画质感":"Impasto 厚涂 笔触 刮刀 oil painting impasto brushstroke",
    "浮世绘":"Ukiyo-e 神奈川冲浪 葛饰北斋 版画 ukiyo-e hokusai great wave",
    "印象派":"Impressionism 莫奈 斑驳光 户外 impressionism monet dappled",
    "超现实主义":"Surrealism 达利 融化的钟 梦境 surrealism dali melting clock",
    "立体主义":"Cubism 毕加索 几何分解 多视角 cubism picasso geometric",
    "赛博朋克":"Cyberpunk 霓虹 高科技低生活 银翼杀手 cyberpunk neon blade runner",
    "蒸汽朋克":"Steampunk 黄铜 齿轮 飞艇 维多利亚 steampunk brass gears airship",
    "废土风":"Wasteland 末日 沙漠废墟 后启示录 post apocalyptic wasteland",
    "梦幻核梦核":"Dreamcore liminal 阈限空间 诡异熟悉 dreamcore liminal space",
    "日系清新":"Japanese fresh 日系 夏天 逆光 学生 japanese cinematic summer",
    "国风水墨":"Ink wash 水墨 留白 山水 宣纸 chinese ink wash shanshui",
    "二次元动漫风":"Anime 二次元 新海诚 赛璐璐 anime cel shading",
    "绿色":"春绿 嫩芽 砷绿 希望 毒药 green hope poison emerald arsenic",
    "红色":"玫瑰红 爱情 警示 仇恨 red love anger warning",
    "蓝色":"忠诚蓝 深海 忧郁 遥远 blue loyalty melancholy ocean",
    "紫色":"权力紫 皇冠 高贵 花哨 purple royalty kitsch",
    "黑色":"优雅黑 礼服 丧服 哀悼 black elegance mourning",
    "白色":"纯洁白 婚纱 空白 雪原 white purity emptiness",
    "黄色":"阳光黄 向日葵 背叛 黄袍 yellow sunshine betrayal",
    "橙色":"暖橙 秋日 廉价 促销 orange warm cheap",
    "粉色":"温柔粉 婴儿房 稚嫩 荧光粉 pink tender juvenile",
    "青橙调色":"Teal orange 好莱坞调色 互补色 teal and orange color grade blockbuster",
    "莫兰迪色":"Morandi 高级灰 低饱和 灰调 morandi muted grey",
    "冷暖双时空":"Warm cool split 冷暖分区 两个季节 warm cool contrast split",
    "蓝灰影调":"Blue grey 冷调 凉白开 低饱和 blue grey cinematic mood",
    "红绿互补高饱和":"Red green complementary 撞色 节庆 red green saturated complementary",
    "低饱和高级灰":"Low saturation advanced grey 褪色 气质 low sat sophisticated",
    "单色系搭配":"Monochrome 同色系 深浅单色 monochromatic tones",
    "撞色对比":"Color clash 撞色 对比色 complementary clash vibrant",
    "褪色质感":"Faded 旧照片 复古 褪色 faded vintage photo",
    "磨砂金属":"Brushed metal 哑光金属 拉丝 颗粒 brushed matte metal",
    "粗花呢":"Tweed 毛呢 粗纱 混色 tweed wool woven",
    "丝绸":"Silk 绸缎 流动光泽 酒红 silk satin flowing sheen",
    "风化混凝土":"Weathered concrete 斑驳 水渍 裂纹 concrete weathered rough",
    "水彩晕染":"Watercolor bleed 水痕 颜料化开 watercolor bleeding wash",
    "厚涂笔触":"Impasto 厚涂 颜料堆叠 刮刀 impasto thick paint palette knife",
    "胶片颗粒":"Film grain 噪点 复古 grain noise vintage",
    "磨砂玻璃":"Frosted glass 雾面 毛玻璃 透光 frosted glass translucent matte",
    "液态金属":"Liquid metal 流动银色 future 科幻 liquid chrome metal",
    "纸张纤维":"Paper fiber 纸纹 绒毛 毛边 paper texture fiber deckle",
    "绒面皮革":"Suede 麂皮 短绒 哑光 suede leather nap matte",
    "釉面陶瓷":"Glazed ceramic 青瓷 釉光 温润 celadon glazed ceramic",
    "电影感":"Cinematic 宽银幕 电影截帧 低饱和 cinematic film still anamorphic",
    "柔焦朦胧":"Soft focus 薄纱 柔化 朦胧 soft focus dreamy haze",
    "过曝高光":"Overexposed 过曝 高光溢出 发白 overexposed blown highlight high key",
    "暗角":"Vignette 渐晕 四角压暗 vignette corners darkened",
    "空气透视":"Atmospheric perspective 雾感纵深 远近 air perspective fog depth",
    "镜头光晕":"Lens flare 眩光 光斑 逆光 lens flare ghosts glare",
    "散景光斑":"Bokeh 圆形光斑 虚化 bokeh circular light orbs",
    "超细节":"Ultra detail 8K 超清 纤毫毕现 ultra detail hyperreal sharp",
    "黑白影调":"Black white 黑白 单色 明暗 monochrome black and white",
    "暗调氛围":"Low key 暗调 低调 阴影 low key dark moody shadow",
}

# 图片映射（名字 -> 文件路径）
NAME_IMG = {
    "伦勃朗光":"去水印/伦勃朗光.png","三点布光":"去水印/三点布光.png","明暗对照法":"去水印/明暗对照法.png",
    "体积光（丁达尔效应）":"去水印/体积光.png","主光":"去水印/主光.png","补光":"去水印/补光.png","轮廓光":"去水印/轮廓光.png",
    "硬光":"去水印/硬光.png","柔光":"去水印/柔光.png","逆光":"去水印/逆光.png","侧光":"去水印/侧光.png",
    "顶光":"去水印/顶光.png","底光（脚光）":"去水印/底光.png","窗光":"去水印/窗光.png","光比":"去水印/光比.png",
    "色温":"去水印/色温.png","黄金时刻":"去水印/黄金时刻.png","蓝调时刻":"去水印/蓝调时刻.png",
    "剪影":"去水印/剪影.png","眼神光":"去水印/眼神光.png",
    "特写与大特写":"去水印/大特写.png","近景":"去水印/近景.png","中景":"去水印/中景.png","全景":"去水印/全景.png",
    "远景":"去水印/远景.png","推镜头":"去水印/推镜头.png","拉镜头":"去水印/远景.png","摇镜头":"去水印/移镜头.png",
    "移镜头":"去水印/移镜头.png","跟镜头":"去水印/中景.png","升降镜头":"去水印/升降镜头.png","甩镜头":"去水印/甩镜头.png",
    "广角镜头":"去水印/广角镜头.png","长焦镜头":"去水印/长焦镜头.png","浅景深与背景虚化":"去水印/浅景深.png",
    "引导线":"去水印/推镜头.png","三分法":"去水印/三分法.png","中心构图":"去水印/中心构图.png","对称构图":"去水印/对称构图.png",
    "留白":"去水印/留白.png","前景遮挡":"去水印/前景遮挡.png","框架构图":"去水印/框架构图.png",
    "对角线构图":"去水印/对角线构图.png","低角度与高角度":"去水印/低角度仰拍.png","鸟瞰视角":"去水印/鸟瞰视角.png",
    "荷兰角（倾斜构图）":"去水印/荷兰角.png","纵深感与层次":"去水印/纵深层次.png",
}
for i,n in enumerate(["装饰艺术","新艺术","格拉斯哥学派","维也纳分离派","高蒂与加泰罗尼亚现代主义","包豪斯","流线型风格","孟菲斯风格","极简主义","波普艺术","黑色电影","诗意现实主义","巴洛克戏剧光","绘画性油画质感","浮世绘","印象派","超现实主义","立体主义","赛博朋克","蒸汽朋克","废土风","梦幻核梦核","日系清新","国风水墨","二次元动漫风"],1):
    NAME_IMG[n]=f"第4章配图/去水印/{i:02d}{n if len(n)<=4 else n[:2]}.png"
# 第4/5/6/7章文件名不规整，用实际清单映射
CH4_FILES=["01装饰艺术","02新艺术","03格拉斯哥","04维也纳分离派","05高蒂","06包豪斯","07流线型","08孟菲斯","09极简主义","10波普艺术","11黑色电影","12诗意现实主义","13巴洛克戏剧光","14油画质感","15浮世绘","16印象派","17超现实","18立体主义","19赛博朋克","20蒸汽朋克","21废土风","22梦核","23日系清新","24国风水墨","25二次元"]
CH4_NAMES=["装饰艺术","新艺术","格拉斯哥学派","维也纳分离派","高蒂与加泰罗尼亚现代主义","包豪斯","流线型风格","孟菲斯风格","极简主义","波普艺术","黑色电影","诗意现实主义","巴洛克戏剧光","绘画性油画质感","浮世绘","印象派","超现实主义","立体主义","赛博朋克","蒸汽朋克","废土风","梦幻核梦核","日系清新","国风水墨","二次元动漫风"]
for n,f in zip(CH4_NAMES,CH4_FILES): NAME_IMG[n]=f"第4章配图/去水印/{f}.png"
CH5_NAMES=["绿色","红色","蓝色","紫色","黑色","白色","黄色","橙色","粉色","青橙调色","莫兰迪色","冷暖双时空","蓝灰影调","红绿互补高饱和","低饱和高级灰","单色系搭配","撞色对比","褪色质感"]
CH5_FILES=["01绿色","02红色","03蓝色","04紫色","05黑色","06白色","07黄色","08橙色","09粉色","10青橙调色","11莫兰迪色","12冷暖双时空","13蓝灰影调","14红绿互补高饱和","15低饱和高级灰","16单色系","17撞色对比","18褪色质感"]
for n,f in zip(CH5_NAMES,CH5_FILES): NAME_IMG[n]=f"第5章配图/去水印/{f}.png"
CH6_NAMES=["磨砂金属","粗花呢","丝绸","风化混凝土","水彩晕染","厚涂笔触","胶片颗粒","磨砂玻璃","液态金属","纸张纤维","绒面皮革","釉面陶瓷"]
for i,n in enumerate(CH6_NAMES,1): NAME_IMG[n]=f"第6章配图/去水印/{i:02d}{n}.png"
CH7_NAMES=["电影感","柔焦朦胧","过曝高光","暗角","空气透视","镜头光晕","散景光斑","超细节","黑白影调","暗调氛围"]
for i,n in enumerate(CH7_NAMES,1): NAME_IMG[n]=f"第7章配图/去水印/{i:02d}{n}.png"
# 褪色质感在第5章第18张
NAME_IMG["褪色质感"]="第5章配图/去水印/18褪色质感.png"

def parse(text):
    entries,cur=[],None
    for line in text.split('\n'):
        m=re.match(r'^## (\d{2})\s+(.+)$',line)
        if m:
            if cur: entries.append(cur)
            cur={'num':m.group(1),'title':m.group(2),'lines':[]}
        elif cur is not None: cur['lines'].append(line)
    if cur: entries.append(cur)
    return entries

def extract(e):
    name=e['title'].split('：',1)[0]
    cn=en=''
    mode='intro'
    for ln in e['lines']:
        s=ln.strip()
        if s.startswith('**中文版**'): mode='cn'; continue
        if s.startswith('**英文版**'): mode='en'; continue
        if s.startswith('> '):
            c=s[2:].strip().strip('`')
            if mode=='cn' and not cn: cn=c
            elif mode=='en' and not en: en=c
    return name,cn,en

def main():
    os.makedirs(SITE_IMG,exist_ok=True)
    data=[]
    # 样板补4条光影 + 引导线
    sample=parse(open(os.path.join(BASE,SAMPLE),encoding='utf-8').read())
    extras=[e for e in sample if e['num'] in ('01','02','03','04')]
    guide=[e for e in sample if e['num']=='09']
    for e in extras:
        n,cn,en=extract(e); data.append((1,n,cn,en))
    for e in guide:
        n,cn,en=extract(e); data.append((3,n,cn,en))
    for f,ch,_ in CH:
        for e in parse(open(os.path.join(BASE,f),encoding='utf-8').read()):
            n,cn,en=extract(e); data.append((ch,n,cn,en))

    out=[]
    seen=set()
    for ch,name,cn,en in data:
        if name in seen: continue
        seen.add(name)
        src=NAME_IMG.get(name)
        img=''
        if src and os.path.exists(os.path.join(BASE,"白皮书实测/测试样张",src)):
            fn=os.path.basename(src)
            dst=os.path.join(SITE_IMG,fn)
            if not os.path.exists(dst):
                shutil.copy2(os.path.join(BASE,"白皮书实测/测试样张",src),dst)
            img="images/"+fn
        out.append({
            "name":name, "alias":ALIAS.get(name,""), "cn":cn, "en":en,
            "ch":ch, "chapter":{1:"光影与布光",2:"镜头与景别",3:"构图与机位",4:"风格流派",5:"色彩",6:"纹理与材质",7:"氛围与画质"}[ch],
            "color":CH_COLOR[ch], "img":img,
        })

    with open(os.path.join(SITE,"data.json"),'w',encoding='utf-8') as f:
        json.dump(out,f,ensure_ascii=False,indent=1)
    print("词条数:",len(out)," 配图:",sum(1 for o in out if o['img']))
    print("数据文件:",os.path.join(SITE,"data.json"))

if __name__=='__main__': main()
