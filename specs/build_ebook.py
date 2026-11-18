# -*- coding: utf-8 -*-
"""《把画面说给AI听》全书电子书生成器 · 陶阿狗君风格
白底 + 纯黑粗框 + 中文巨字 + 分章强调色 + 杂志卡片排版
"""
import re, os, html, base64, subprocess, tempfile, random

BASE = "/Users/mac/WorkBuddy/2026-11-18-10-09-49"

def img_datauri(path, quality=68):
    """把图片转JPEG压缩后base64内嵌，返回 data URI"""
    if not path or not os.path.exists(path):
        return None
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tf:
        tmp = tf.name
    subprocess.run(['sips','-s','format','jpeg','-s','formatOptions',str(quality),path,'--out',tmp],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        with open(tmp,'rb') as f:
            data = base64.b64encode(f.read()).decode('ascii')
        return f"data:image/jpeg;base64,{data}"
    finally:
        os.unlink(tmp)
IMG_DIR = os.path.join(BASE, "白皮书实测/测试样张/去水印")
IMG_DIR4 = os.path.join(BASE, "白皮书实测/测试样张/第4章配图/去水印")
IMG_DIR5 = os.path.join(BASE, "白皮书实测/测试样张/第5章配图/去水印")
IMG_DIR6 = os.path.join(BASE, "白皮书实测/测试样张/第6章配图/去水印")
IMG_DIR7 = os.path.join(BASE, "白皮书实测/测试样张/第7章配图/去水印")
OUT = os.path.join(BASE, "白皮书成品")
OUT_HTML = os.path.join(OUT, "把画面说给AI听_全书.html")
WEB_IMG_DIR = os.path.join(OUT, "images")  # 复制到此处，HTML用相对路径引用

# 章节分色（用户定：按章节分）
CH_COLOR = {1: "#E8462F", 2: "#2E5CE8", 3: "#C8890B", 4: "#12A05C", 5: "#7B4FA8", 6: "#E07B39", 7: "#1B9AAA"}  # 朱红/宝蓝/金黄/翠绿/紫/橙/青
CH_LABEL = {1: "光影", 2: "镜头", 3: "构图", 4: "风格", 5: "色彩", 6: "纹理", 7: "氛围"}

# 中文名 -> 图片
NAME_MAP = {
    "伦勃朗光": "伦勃朗光.png", "三点布光": "三点布光.png", "明暗对照法": "明暗对照法.png",
    "体积光（丁达尔效应）": "体积光.png", "主光": "主光.png", "补光": "补光.png", "轮廓光": "轮廓光.png",
    "硬光": "硬光.png", "柔光": "柔光.png", "逆光": "逆光.png", "侧光": "侧光.png",
    "顶光": "顶光.png", "底光（脚光）": "底光.png", "窗光": "窗光.png", "光比": "光比.png",
    "色温": "色温.png", "黄金时刻": "黄金时刻.png", "蓝调时刻": "蓝调时刻.png",
    "剪影": "剪影.png", "眼神光": "眼神光.png",
    "特写与大特写": "大特写.png", "近景": "近景.png", "中景": "中景.png", "全景": "全景.png",
    "远景": "远景.png", "推镜头": "推镜头.png", "拉镜头": "远景.png", "摇镜头": "移镜头.png",
    "移镜头": "移镜头.png", "跟镜头": "中景.png", "升降镜头": "升降镜头.png", "甩镜头": "甩镜头.png",
    "广角镜头": "广角镜头.png", "长焦镜头": "长焦镜头.png", "浅景深与背景虚化": "浅景深.png",
    "引导线": "推镜头.png", "三分法": "三分法.png", "中心构图": "中心构图.png", "对称构图": "对称构图.png",
    "留白": "留白.png", "前景遮挡": "前景遮挡.png", "框架构图": "框架构图.png",
    "对角线构图": "对角线构图.png", "低角度与高角度": "低角度仰拍.png", "鸟瞰视角": "鸟瞰视角.png",
    "荷兰角（倾斜构图）": "荷兰角.png", "纵深感与层次": "纵深层次.png",
    # 第4章 风格流派（在 IMG_DIR4 目录）
    "装饰艺术": "01装饰艺术.png", "新艺术": "02新艺术.png", "格拉斯哥学派": "03格拉斯哥.png",
    "维也纳分离派": "04维也纳分离派.png", "高蒂与加泰罗尼亚现代主义": "05高蒂.png",
    "包豪斯": "06包豪斯.png", "流线型风格": "07流线型.png", "孟菲斯风格": "08孟菲斯.png",
    "极简主义": "09极简主义.png", "波普艺术": "10波普艺术.png", "黑色电影": "11黑色电影.png",
    "诗意现实主义": "12诗意现实主义.png", "巴洛克戏剧光": "13巴洛克戏剧光.png",
    "绘画性油画质感": "14油画质感.png", "浮世绘": "15浮世绘.png", "印象派": "16印象派.png",
    "超现实主义": "17超现实.png", "立体主义": "18立体主义.png", "赛博朋克": "19赛博朋克.png",
    "蒸汽朋克": "20蒸汽朋克.png", "废土风": "21废土风.png", "梦幻核梦核": "22梦核.png",
    "日系清新": "23日系清新.png", "国风水墨": "24国风水墨.png", "二次元动漫风": "25二次元.png",
    # 第5章 色彩（在 IMG_DIR5 目录）
    "绿色": "01绿色.png", "红色": "02红色.png", "蓝色": "03蓝色.png", "紫色": "04紫色.png",
    "黑色": "05黑色.png", "白色": "06白色.png", "黄色": "07黄色.png", "橙色": "08橙色.png",
    "粉色": "09粉色.png", "青橙调色": "10青橙调色.png", "莫兰迪色": "11莫兰迪色.png",
    "冷暖双时空": "12冷暖双时空.png", "蓝灰影调": "13蓝灰影调.png", "红绿互补高饱和": "14红绿互补高饱和.png",
    "低饱和高级灰": "15低饱和高级灰.png", "单色系搭配": "16单色系.png", "撞色对比": "17撞色对比.png",
    "褪色质感": "18褪色质感.png",
    # 第6章 纹理与材质（在 IMG_DIR6 目录）
    "磨砂金属": "01磨砂金属.png", "粗花呢": "02粗花呢.png", "丝绸": "03丝绸.png",
    "风化混凝土": "04风化混凝土.png", "水彩晕染": "05水彩晕染.png", "厚涂笔触": "06厚涂笔触.png",
    "胶片颗粒": "07胶片颗粒.png", "磨砂玻璃": "08磨砂玻璃.png", "液态金属": "09液态金属.png",
    "纸张纤维": "10纸张纤维.png", "绒面皮革": "11绒面皮革.png", "釉面陶瓷": "12釉面陶瓷.png",
    # 第7章 氛围与画质（在 IMG_DIR7 目录）
    "电影感": "01电影感.png", "柔焦朦胧": "02柔焦朦胧.png", "过曝高光": "03过曝高光.png",
    "暗角": "04暗角.png", "空气透视": "05空气透视.png", "镜头光晕": "06镜头光晕.png",
    "散景光斑": "07散景光斑.png", "超细节": "08超细节.png", "黑白影调": "09黑白影调.png",
    "暗调氛围": "10暗调氛围.png",
}

# 中文名 -> 英文大词（海报副标）
EN_MAP = {
    "伦勃朗光":"REMBRANDT", "三点布光":"THREE-POINT", "明暗对照法":"CHIAROSCURO",
    "体积光（丁达尔效应）":"VOLUMETRIC", "主光":"KEY LIGHT", "补光":"FILL LIGHT", "轮廓光":"RIM LIGHT",
    "硬光":"HARD LIGHT", "柔光":"SOFT LIGHT", "逆光":"BACKLIGHT", "侧光":"SIDE LIGHT",
    "顶光":"TOP LIGHT", "底光（脚光）":"UPLIGHT", "窗光":"WINDOW LIGHT", "光比":"LIGHT RATIO",
    "色温":"COLOR TEMP", "黄金时刻":"GOLDEN HOUR", "蓝调时刻":"BLUE HOUR",
    "剪影":"SILHOUETTE", "眼神光":"CATCHLIGHT",
    "特写与大特写":"CLOSE-UP", "近景":"MEDIUM CLOSE", "中景":"MEDIUM SHOT", "全景":"FULL SHOT",
    "远景":"LONG SHOT", "推镜头":"PUSH IN", "拉镜头":"PULL OUT", "摇镜头":"PAN",
    "移镜头":"TRACKING", "跟镜头":"FOLLOW", "升降镜头":"CRANE", "甩镜头":"WHIP PAN",
    "广角镜头":"WIDE ANGLE", "长焦镜头":"TELEPHOTO", "浅景深与背景虚化":"SHALLOW DOF",
    "引导线":"LEADING LINES", "三分法":"RULE OF THIRDS", "中心构图":"CENTERED", "对称构图":"SYMMETRY",
    "留白":"NEGATIVE SPACE", "前景遮挡":"FOREGROUND", "框架构图":"FRAMING",
    "对角线构图":"DIAGONAL", "低角度与高角度":"LOW ANGLE", "鸟瞰视角":"BIRD'S EYE",
    "荷兰角（倾斜构图）":"DUTCH ANGLE", "纵深感与层次":"DEPTH",
    "装饰艺术":"ART DECO", "新艺术":"ART NOUVEAU", "格拉斯哥学派":"GLASGOW",
    "维也纳分离派":"SECESSION", "高蒂与加泰罗尼亚现代主义":"GAUDI",
    "包豪斯":"BAUHAUS", "流线型风格":"STREAMLINE", "孟菲斯风格":"MEMPHIS",
    "极简主义":"MINIMALISM", "波普艺术":"POP ART", "黑色电影":"FILM NOIR",
    "诗意现实主义":"POETIC REALISM", "巴洛克戏剧光":"BAROQUE",
    "绘画性油画质感":"IMPASTO", "浮世绘":"UKIYO-E", "印象派":"IMPRESSIONISM",
    "超现实主义":"SURREALISM", "立体主义":"CUBISM", "赛博朋克":"CYBERPUNK",
    "蒸汽朋克":"STEAMPUNK", "废土风":"WASTELAND", "梦幻核梦核":"DREAMCORE",
    "日系清新":"JAPANESE FRESH", "国风水墨":"INK WASH", "二次元动漫风":"ANIME",
    "绿色":"GREEN", "红色":"RED", "蓝色":"BLUE", "紫色":"PURPLE", "黑色":"BLACK",
    "白色":"WHITE", "黄色":"YELLOW", "橙色":"ORANGE", "粉色":"PINK",
    "青橙调色":"TEAL & ORANGE", "莫兰迪色":"MORANDI", "冷暖双时空":"WARM / COOL",
    "蓝灰影调":"BLUE GREY", "红绿互补高饱和":"RED & GREEN", "低饱和高级灰":"ADVANCED GREY",
    "单色系搭配":"MONOCHROME", "撞色对比":"COLOR CLASH", "褪色质感":"FADED",
    "磨砂金属":"BRUSHED METAL", "粗花呢":"TWEED", "丝绸":"SILK", "风化混凝土":"WEATHERED CONCRETE",
    "水彩晕染":"WATERCOLOR", "厚涂笔触":"IMPASTO", "胶片颗粒":"FILM GRAIN", "磨砂玻璃":"FROSTED GLASS",
    "液态金属":"LIQUID METAL", "纸张纤维":"PAPER FIBER", "绒面皮革":"SUEDE", "釉面陶瓷":"GLAZED CERAMIC",
    "电影感":"CINEMATIC", "柔焦朦胧":"SOFT FOCUS", "过曝高光":"OVEREXPOSED", "暗角":"VIGNETTE",
    "空气透视":"ATMOSPHERIC", "镜头光晕":"LENS FLARE", "散景光斑":"BOKEH", "超细节":"ULTRA DETAIL",
    "黑白影调":"BLACK & WHITE", "暗调氛围":"LOW KEY",
}

def make_micro_collage(n=143, seed=11):
    """封面像素马赛克层：用全书内嵌图，按规则网格紧密平铺成13×11像素墙。
    规则排列有秩序；透明度随机制造深浅呼吸；整页统一白纱，文字浮上层。"""
    rnd = random.Random(seed)
    uris = [u for u in _uri_cache.values() if u]
    if not uris:
        return ''
    rnd.shuffle(uris)
    pieces = []
    for i in range(n):
        uri = uris[i % len(uris)]
        op = round(rnd.uniform(0.55, 1.0), 2)  # 深浅呼吸感
        pieces.append(f'<img src="{uri}" style="opacity:{op}">')
    return '<div class="micro">' + ''.join(pieces) + '</div>'

def esc(s):
    return html.escape(s, quote=False)

def md_inline(s):
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'`(.+?)`', r'\1', s)
    return s

def big_name(name):
    """巨字用短名：去括号、取顿号/与字前的主名"""
    s = re.sub(r'（.*?）', '', name)
    s = s.split('与')[0].split('、')[0]
    return s.strip() or name

def big_size(name):
    n = len(big_name(name))
    return 132 if n <= 4 else (104 if n <= 6 else 82)

_uri_cache = {}
def pick_image(name, used, chapter=1):
    f = NAME_MAP.get(name)
    if not f:
        return None
    d = {4: IMG_DIR4, 5: IMG_DIR5, 6: IMG_DIR6, 7: IMG_DIR7}.get(chapter, IMG_DIR)
    path = os.path.join(d, f)
    if os.path.exists(path):
        used.add(f)
        if path not in _uri_cache:
            _uri_cache[path] = img_datauri(path)
        return _uri_cache[path]
    return None

def parse_entries(text):
    entries, cur = [], None
    for line in text.split('\n'):
        m = re.match(r'^## (\d{2})\s+(.+)$', line)
        if m:
            if cur: entries.append(cur)
            cur = {'num': m.group(1), 'title': m.group(2), 'lines': []}
        elif cur is not None:
            cur['lines'].append(line)
    if cur: entries.append(cur)
    return entries

def render_entry(e, used, chapter):
    num, title = e['num'], e['title']
    name = title.split('：', 1)[0] if '：' in title else title
    sub = title.split('：', 1)[1] if '：' in title else ''
    en = EN_MAP.get(name, '')
    img = pick_image(name, used, chapter)
    color = CH_COLOR[chapter]

    paras = [ln.strip() for ln in e['lines'] if ln.strip()
             and not ln.strip().startswith('[配图') and ln.strip() != '---']
    intro = principle = pairing = fingerprint = source = cn_prompt = en_prompt = ''
    mode = 'intro'
    for p in paras:
        if p.startswith('两版提示词'): mode = 'prompt'; continue
        if p.startswith('**中文版**'): mode = 'cn'; continue
        if p.startswith('**英文版**'): mode = 'en'; continue
        if p.startswith('*知识来源'):
            source = p.strip('*')
            if source.startswith('知识来源：'): source = source[len('知识来源：'):]
            continue
        if p.startswith('> '):
            c = p[2:].strip().strip('`')
            if mode == 'cn': cn_prompt = c
            elif mode == 'en': en_prompt = c
            continue
        if any(k in p for k in ['这里有个坑，作者当年亲自踩过', '先替你把雷排了', '这一条有个隐藏脾气']):
            fingerprint = p; mode = 'after'; continue
        if mode in ('cn', 'en', 'prompt'):
            pairing = p; mode = 'after'; continue
        if mode == 'intro': intro = p; mode = 'principle'; continue
        if mode == 'principle': principle = p; continue
        if mode == 'after': pairing = p

    img_html = (f'<div class="media"><img src="{img}" alt="{esc(name)}"></div>'
                if img else '<div class="media empty">示意图</div>')
    sub_html = f'<div class="sub">{md_inline(sub)}</div>' if sub else ''

    return f'''<article class="entry" style="--c:{color}">
  <div class="hero">
    <div class="bar"><span>{num} / {CH_LABEL[chapter]}</span><span>{en}</span></div>
    <div class="big" style="font-size:{big_size(name)}px">{esc(big_name(name))}</div>
    {sub_html}
  </div>
  <div class="card">
    <div class="text">
      <span class="tag">它是什么</span>
      <p>{md_inline(intro)}</p>
      <p>{md_inline(principle)}</p>
      <p class="pair">{md_inline(pairing)}</p>
      <div class="tip">⚑ {md_inline(fingerprint)}</div>
    </div>
    {img_html}
  </div>
  <div class="prompt">
    <div class="pt">中文提示词 · 国产工具直接粘</div>
    <div class="zh">{md_inline(cn_prompt)}</div>
    <div class="pt">英文提示词 · 给 AI 看的，不用背</div>
    <div class="en-p">{esc(en_prompt)}</div>
    <div class="source">知识来源：{md_inline(source)}</div>
  </div>
</article>'''

# ------- 读内容 -------
ch1 = open(os.path.join(BASE, "第1章_光影与布光_16条.md"), encoding='utf-8').read()
ch2 = open(os.path.join(BASE, "第2章_镜头与景别_15条.md"), encoding='utf-8').read()
ch3 = open(os.path.join(BASE, "第3章_构图与机位_11条.md"), encoding='utf-8').read()
ch4 = open(os.path.join(BASE, "第4章_风格流派_25条.md"), encoding='utf-8').read()
ch5 = open(os.path.join(BASE, "第5章_色彩_18条.md"), encoding='utf-8').read()
ch6 = open(os.path.join(BASE, "第6章_纹理与材质_12条.md"), encoding='utf-8').read()
ch7 = open(os.path.join(BASE, "第7章_氛围与画质_10条.md"), encoding='utf-8').read()
sample = open(os.path.join(BASE, "白皮书样板_人读版_v2.md"), encoding='utf-8').read()
sample_entries = parse_entries(sample)

ch1_sample = [e for e in sample_entries if e['num'] in ('01','02','03','04')]
guide = [e for e in sample_entries if e['num'] == '09']
for e in guide: e['num'] = '01'

used = set()
ch1_html = '\n'.join(render_entry(e, used, 1) for e in ch1_sample + parse_entries(ch1))
ch2_html = '\n'.join(render_entry(e, used, 2) for e in parse_entries(ch2))
ch3_html = '\n'.join(render_entry(e, used, 3) for e in guide + parse_entries(ch3))
ch4_html = '\n'.join(render_entry(e, used, 4) for e in parse_entries(ch4))
ch5_html = '\n'.join(render_entry(e, used, 5) for e in parse_entries(ch5))
ch6_html = '\n'.join(render_entry(e, used, 6) for e in parse_entries(ch6))
ch7_html = '\n'.join(render_entry(e, used, 7) for e in parse_entries(ch7))

CSS = '''
:root{--ink:#111;--faint:#9a9a9a;--line:#e8e8e8;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#fff;color:var(--ink);}
.wrap{max-width:900px;margin:0 auto;padding:28px 32px 100px;}

.top{display:flex;justify-content:space-between;align-items:center;
  border-bottom:4px solid var(--ink);padding-bottom:12px;margin-bottom:48px;}
.top .logo{font-size:15px;font-weight:900;letter-spacing:.06em;}
.top .num{font-size:11px;color:var(--faint);letter-spacing:.2em;font-weight:700;}

.cover{border:6px solid var(--ink);margin-bottom:40px;position:relative;overflow:hidden;background:#fff;
  min-height:88vh;display:flex;flex-direction:column;}
.cover .micro{position:absolute;inset:0;z-index:0;pointer-events:none;
  display:grid;grid-template-columns:repeat(13,1fr);grid-auto-rows:1fr;gap:0;}
.cover .micro img{display:block;width:100%;height:100%;object-fit:cover;}
.cover .veil{position:absolute;inset:0;z-index:1;pointer-events:none;
  background:rgba(255,255,255,.84);}
.cover .cd-top{background:var(--ink);color:#fff;padding:12px 24px;font-size:13px;
  font-weight:900;letter-spacing:.3em;display:flex;justify-content:space-between;position:relative;z-index:2;}
.cover .cd-body{padding:54px 40px 46px;text-align:left;position:relative;z-index:2;
  background:transparent;}
.cover .cd-body p,.cover .cd-body .en-title,.cover .cd-body .meta{text-shadow:0 0 6px #fff,0 0 4px #fff;}
.cover .kicker{display:inline-block;background:#E8462F;color:#fff;font-size:13px;
  font-weight:900;padding:6px 16px;letter-spacing:.14em;margin-bottom:30px;}
.cover h1{font-size:96px;line-height:1.02;font-weight:900;letter-spacing:-.05em;}
.cover h1 .r{color:#E8462F;} .cover h1 .b{color:#2E5CE8;} .cover h1 .y{color:#C8890B;}
.cover .en-title{font-size:22px;font-weight:900;letter-spacing:.24em;color:var(--ink);
  margin-top:22px;padding-top:20px;border-top:4px solid var(--ink);}
.cover .lead{font-size:16px;color:#444;line-height:2;margin:26px 0 0;max-width:620px;}
.cover .cd-bar{margin-top:26px;display:flex;gap:8px;}
.cover .cd-bar i{display:block;height:10px;flex:1;}
.cover .meta{font-size:12px;color:var(--faint);letter-spacing:.16em;margin-top:20px;}
.cover .cd-toc{position:relative;z-index:2;margin:30px 40px 0;padding:22px 26px;
  background:rgba(255,255,255,.93);border:4px solid var(--ink);}
.cover .toc-title{font-size:12px;font-weight:900;letter-spacing:.2em;color:#fff;background:var(--ink);
  display:inline-block;padding:5px 14px;margin-bottom:16px;}
.cover .toc-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px 26px;}
.cover .toc-item{display:flex;align-items:center;gap:9px;font-size:14px;border-bottom:1px solid var(--line);padding:7px 0;}
.cover .toc-item i{width:14px;height:14px;display:block;flex:none;}
.cover .toc-item b{font-weight:800;flex:1;}
.cover .toc-item span{font-size:11px;color:var(--faint);font-weight:700;}
.cover .toc-foot{font-size:13px;color:#666;font-weight:700;text-align:right;margin-top:16px;font-style:italic;}

.chapter-page{min-height:70vh;display:flex;flex-direction:column;justify-content:center;
  align-items:flex-start;padding:60px 0 40px;}
.chapter-page .lab{font-size:14px;font-weight:900;letter-spacing:.4em;}
.chapter-page h2{font-size:96px;font-weight:900;line-height:1.1;margin:18px 0 24px;letter-spacing:-.03em;}
.chapter-page .lead{font-size:18px;line-height:2;color:#555;max-width:640px;}
.chapter-page .rule{width:80px;height:6px;margin-top:30px;}

.entry{margin-bottom:64px;}
.hero{border:5px solid var(--ink);}
.hero .bar{background:var(--ink);color:#fff;padding:9px 20px;font-size:12px;
  letter-spacing:.22em;font-weight:800;display:flex;justify-content:space-between;}
.hero .big{font-weight:900;letter-spacing:-.04em;line-height:1;padding:34px 20px 6px;text-align:center;color:var(--c);}
.hero .sub{text-align:center;font-size:17px;font-weight:700;color:#666;padding:0 20px 30px;}

.card{display:grid;grid-template-columns:1fr 1fr;border:5px solid var(--ink);border-top:none;}
.card .text{padding:28px 30px;border-right:5px solid var(--ink);}
.card .text .tag{display:inline-block;background:var(--ink);color:#fff;font-size:11px;
  font-weight:800;padding:4px 12px;letter-spacing:.1em;margin-bottom:16px;}
.card .text p{font-size:15px;line-height:1.9;margin-bottom:14px;}
.card .text b{background:var(--c);color:#fff;padding:1px 6px;}
.card .text .pair{color:#444;}
.card .text .tip{border-left:6px solid var(--c);background:#FAFAFA;padding:12px 14px;
  font-size:13.5px;line-height:1.8;margin-top:6px;}
.card .media{background:#f2f2f2;display:flex;align-items:center;justify-content:center;overflow:hidden;min-height:340px;}
.card .media img{width:100%;height:100%;object-fit:cover;display:block;}
.card .media.empty{color:#bbb;font-size:14px;font-weight:800;letter-spacing:.3em;}

.prompt{border:5px solid var(--ink);border-top:none;padding:24px 30px;}
.prompt .pt{font-size:11px;font-weight:800;letter-spacing:.14em;color:var(--faint);margin:0 0 8px;}
.prompt .zh{font-size:17px;font-weight:800;line-height:1.7;padding:14px 18px;
  background:#EFF3FF;border-left:8px solid #2E5CE8;margin-bottom:18px;}
.prompt .en-p{font-family:Menlo,Consolas,monospace;font-size:13px;line-height:1.8;color:#777;
  padding:14px 18px;background:#F7F7F7;border-left:8px solid #ccc;word-break:break-word;}
.source{text-align:right;font-size:11px;color:var(--faint);margin-top:12px;letter-spacing:.05em;}

/* 结束词页 */
.ending{border:6px solid var(--ink);margin-top:0;padding:0;page-break-before:always;break-before:page;}
.ending .ed-top{background:var(--ink);color:#fff;padding:12px 24px;font-size:13px;
  font-weight:900;letter-spacing:.3em;display:flex;justify-content:space-between;}
.ending .ed-body{padding:40px 44px;}
.ending .ed-kicker{display:inline-block;background:#E8462F;color:#fff;font-size:12px;
  font-weight:900;padding:5px 14px;letter-spacing:.16em;margin-bottom:24px;}
.ending h2{font-size:52px;font-weight:900;line-height:1.1;letter-spacing:-.03em;margin-bottom:28px;}
.ending h2 span{color:#E8462F;}
.ending h3{font-size:20px;font-weight:900;margin:26px 0 10px;padding-left:14px;border-left:6px solid #111;}
.ending p{font-size:15px;line-height:2;color:#333;margin:0 0 14px;}
.ending p b{color:#E8462F;}
.ending .value-box{border:4px solid var(--ink);padding:20px 24px;margin:20px 0;background:#FFF9F2;}
.ending .notice{border:4px solid var(--ink);padding:20px 24px;margin:24px 0 0;background:#F6F6F6;}
.ending .notice p{font-size:14px;line-height:1.95;}
.ending .patents{font-family:Menlo,Consolas,monospace;font-size:12.5px;line-height:2;color:#555;
  background:#EFEFEF;padding:10px 14px;margin-top:14px;word-break:break-all;}
.ending .ed-foot{border-top:4px solid var(--ink);margin-top:30px;padding-top:18px;
  display:flex;justify-content:space-between;font-size:12px;color:var(--faint);font-weight:800;letter-spacing:.1em;}
.tail{border-top:4px solid var(--ink);padding-top:20px;margin-top:70px;text-align:center;
  font-size:12px;color:var(--faint);letter-spacing:.3em;font-weight:800;}
@media(max-width:640px){
  .card{grid-template-columns:1fr;} .card .text{border-right:none;border-bottom:5px solid var(--ink);}
  .cover h1{font-size:44px;} .chapter-page h2{font-size:60px;}
}

/* ===== 打印：固定满页网格，版式规格全页一致 ===== */
@page{size:A4;margin:13mm;
  @top-right{content:"嘀嗒版权所有 · 严禁抄袭搬运";font-family:"PingFang SC",sans-serif;
    font-size:8px;color:#9a9a9a;font-weight:700;letter-spacing:.1em;}}

@media print{
  html,body{background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
  .wrap{max-width:none;padding:0;margin:0;}
  .top{display:none;}
  .cover{page-break-after:always;break-after:page;margin-bottom:0;min-height:271mm;height:auto;}
  .cover .cd-body{padding:40px 40px 30px;}
  .cover h1{font-size:84px;}
  .cover .cd-toc{margin:22px 40px 0;padding:16px 22px;}
  .cover .toc-grid{gap:6px 22px;}
  .cover .toc-item{font-size:12.5px;padding:5px 0;}
  .cover .toc-title{font-size:11px;margin-bottom:12px;}
  .cover .toc-foot{font-size:11px;margin-top:12px;}
  .ending{height:271mm;overflow:hidden;page-break-inside:avoid;break-inside:avoid;}
  .ending .ed-top{padding:9px 22px;font-size:11px;}
  .ending .ed-body{padding:16px 34px;}
  .ending .ed-kicker{font-size:10px;padding:4px 11px;margin-bottom:14px;}
  .ending h2{font-size:38px;margin-bottom:18px;}
  .ending h3{font-size:15px;margin:13px 0 6px;padding-left:10px;}
  .ending p{font-size:11px;line-height:1.6;margin-bottom:7px;}
  .ending .notice p{font-size:10px;line-height:1.55;margin-bottom:5px;}
  .ending .patents{font-size:9.5px;line-height:1.6;padding:6px 10px;margin-top:8px;}
  .ending .value-box{padding:10px 14px;margin:10px 0;}
  .ending .notice{padding:12px 16px;margin:14px 0 0;}
  .ending .ed-foot{margin-top:16px;padding-top:10px;font-size:10px;}
  .chapter-page{page-break-before:always;break-before:page;page-break-after:always;break-after:page;
    min-height:271mm;padding-top:0;justify-content:center;}

  /* 词条 = 固定满页卡片，flex纵向分区，尺寸全页统一 */
  .entry{page-break-before:always;break-before:page;page-break-inside:avoid;break-inside:avoid;
    margin:0;padding:0;height:271mm;display:flex;flex-direction:column;overflow:hidden;}

  /* 1) 标题框：固定高 58mm */
  .hero{flex:0 0 58mm;border-width:5px;display:flex;flex-direction:column;}
  .hero .bar{flex:0 0 auto;padding:8px 18px;font-size:11px;}
  .hero .big{flex:1 1 auto;display:flex;align-items:center;justify-content:center;
    padding:0;font-size:76px !important;line-height:1;}
  .hero .sub{flex:0 0 auto;font-size:15px;padding:0 16px 14px;}

  /* 2) 正文+图框：弹性吃掉剩余，固定字号，内容少则留白 */
  .card{flex:1 1 auto;border-width:5px;border-top:none;display:grid;
    grid-template-columns:1fr 1fr;grid-template-rows:minmax(0,1fr);min-height:0;overflow:hidden;}
  .card .text{padding:16px 20px;border-right-width:5px;min-height:0;overflow:hidden;}
  .card .text .tag{font-size:11px;margin-bottom:10px;}
  .card .text p{font-size:12.5px;line-height:1.68;margin-bottom:9px;}
  .card .text .pair{margin-top:4px;}
  .card .text .tip{font-size:11.5px;padding:8px 10px;margin-top:8px;}
  .card .media{min-height:0;overflow:hidden;}
  .card .media img{height:100%;width:100%;object-fit:cover;}

  /* 3) 提示词框：固定高 62mm，来源作为框内最后一行贴底 */
  .prompt{flex:0 0 62mm;border-width:5px;border-top:none;padding:14px 22px;
    overflow:hidden;display:flex;flex-direction:column;}
  .prompt .pt{font-size:11px;margin-bottom:5px;}
  .prompt .zh{font-size:14.5px;padding:9px 14px;margin-bottom:10px;}
  .prompt .en-p{font-size:12px;padding:9px 14px;}
  .prompt .source{margin-top:auto;text-align:right;font-size:10px;color:var(--faint);
    letter-spacing:.05em;padding-top:6px;}
  .tail{page-break-before:always;break-before:page;}
}
'''

chapters = [
    (1, "光影与布光", "光是画面的语法。这一章教你认出光的性格——它从哪来、多硬、什么角度，如何把一张平淡的脸，打成一个有故事的人。", ch1_html),
    (2, "镜头与景别", "相机是眼睛。推近、拉远、俯仰、跟随——同样一个人，换个取景，讲的就是另一个故事。", ch2_html),
    (3, "构图与机位", "构图是给眼睛修一条路。它决定观众先看哪儿、后看哪儿，也决定画面里那份说不清的舒服从何而来。", ch3_html),
    (4, "风格流派", "风格是一张画的口音。这一章带你认出二十多种风格——从金碧辉煌的装饰艺术，到赛博朋克的霓虹雨夜，一眼就叫出它的名字。", ch4_html),
    (5, "色彩", "颜色不只是好看，它还会说话。这一章分两轨：先认颜色的性格——同一种绿为何既是希望又是毒药；再学配色的情绪——青橙、莫兰迪、高级灰，各有什么脾气。", ch5_html),
    (6, "纹理与材质", "闭上眼摸一摸，再睁开眼——这一章练的就是把手感翻译成画面。磨砂、绒面、釉光，每种材质都有它自己的光泽和脾气。", ch6_html),
    (7, "氛围与画质", "最后一章，学的是给整张图蒙一层感觉。同一个山谷，可以拍成电影截帧，也可以暗成一场梦——调的不是参数，是情绪。", ch7_html),
]

body_html = ''
for ch_no, name, lead, entries_html in chapters:
    color = CH_COLOR[ch_no]
    body_html += f'''<section class="chapter-page" style="--c:{color}">
  <div class="lab" style="color:{color}">CHAPTER 0{ch_no}</div>
  <h2 style="color:{color}">{name}</h2>
  <p class="lead">{lead}</p>
  <div class="rule" style="background:{color}"></div>
</section>
{entries_html}
'''

doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>把画面说给AI听 · 全书</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="top"><span class="logo">把画面说给 AI 听</span><span class="num">A PICTURE DICTIONARY · 全书</span></div>
  <section class="cover">
    {make_micro_collage()}
    <div class="veil"></div>
    <div class="cd-top"><span>A PICTURE DICTIONARY</span><span>01 / 07</span></div>
    <div class="cd-body">
      <span class="kicker">AI 视觉绘画 · 画面感词典</span>
      <h1><span class="r">把画面</span><br>说给 <span class="b">AI</span> 听</h1>
      <div class="en-title">TELL THE PICTURE TO AI</div>
      <p class="lead">这不是一本教你怎么写提示词的书。<br>它只帮你认出画面——认出来之后，剩下的交给配套网页：<b>ggyjwa.github.io/picture-dictionary</b>（输入词条关键词，一键带出中英文提示词）。</p>
      <div class="cd-bar"><i style="background:#E8462F"></i><i style="background:#2E5CE8"></i><i style="background:#C8890B"></i><i style="background:#12A05C"></i><i style="background:#7B4FA8"></i><i style="background:#E07B39"></i><i style="background:#1B9AAA"></i></div>
      <div class="meta">面向 AI 初学者的画面感词典 · 示意图仅供参考</div>
    </div>
    <div class="cd-toc">
      <div class="toc-title">全书七章 · 112 个画面词条</div>
      <div class="toc-grid">
        <div class="toc-item"><i style="background:#E8462F"></i><b>01 光影与布光</b><span>20 条</span></div>
        <div class="toc-item"><i style="background:#2E5CE8"></i><b>02 镜头与景别</b><span>15 条</span></div>
        <div class="toc-item"><i style="background:#C8890B"></i><b>03 构图与机位</b><span>12 条</span></div>
        <div class="toc-item"><i style="background:#12A05C"></i><b>04 风格流派</b><span>25 条</span></div>
        <div class="toc-item"><i style="background:#7B4FA8"></i><b>05 色彩</b><span>18 条</span></div>
        <div class="toc-item"><i style="background:#E07B39"></i><b>06 纹理与材质</b><span>12 条</span></div>
        <div class="toc-item"><i style="background:#1B9AAA"></i><b>07 氛围与画质</b><span>10 条</span></div>
      </div>
      <div class="toc-foot">认出一个词，就多一种控制画面的手段</div>
    </div>
  </section>
  {body_html}
  <section class="ending">
    <div class="ed-top"><span>AFTERWORD · 后记与声明</span><span>THE END</span></div>
    <div class="ed-body">
      <span class="ed-kicker">写在最后</span>
      <h2>认出画面，<br>你就<span>赢了</span>。</h2>

      <h3>这份文件是做什么用的</h3>
      <p>这不是一本让人背诵的词典，而是一本<b>随时翻阅的"画面感手册"</b>。当你面对生图工具、脑子里有画面却说不出话时，翻到对应的词条，把中英文提示词直接粘进去——就这么简单。全书七章、112 个词条，从光影、镜头、构图，到风格、色彩、材质、氛围，覆盖了一张画面能被"调"的所有维度。</p>

      <h3>我们想到底想做什么</h3>
      <p>工具人人都能用，<b>能看懂画面才是壁垒</b>。同样一条爆款视频、一张动人的照片，有人刷过去就算了，有人能把它拆成"哦，这是伦勃朗光、这是青橙调色、这是空气透视"。这本书的全部目的，就是把后者这种"拆解的眼力"，交到你手上。你不需要记住那些英文单词——你只需要<b>认得出</b>，剩下的，交给配套网页 <b>ggyjwa.github.io/picture-dictionary</b>：输入关键词，中英文提示词即刻到手，一键复制就能用。</p>

      <div class="value-box">
        <p><b>它真正的价值，不在这一页纸。</b></p>
        <p>术语会过时，工具会换代，但"把感受翻译成画面参数"的能力不会。这本书把这套能力拆成了 112 个可以随手调用的小模块：认出一个词，你就多一种控制画面的手段；认出一百个，你就能指挥 AI 画出你脑子里任何一幅画面。<b>它卖的不是词，是你对画面的主权。</b></p>
      </div>

      <h3>版权与严正声明</h3>
      <div class="notice">
        <p><b>本书为原创汇编作品，受《中华人民共和国著作权法》及相关国际条约保护。</b>全书文字、文风指纹体系、词条编排结构、配图及版式设计，均为独立创作成果。任何未经授权的复制、摘录、改编、汇编、转载、商用、上传至网络或用于训练数据集的行为，均属侵权。</p>
        <p>本书核心的"文风指纹体系"及"词条—配图—检索"三位一体结构，已申请相关知识产权保护，关键编号如下（部分敏感字段依法隐去）：</p>
        <div class="patents">
          著作权登记号：国作登字-2026-L-■■■■■■■■<br>
          作品著作权登记证书编号：2026-F-■■■■■■■■<br>
          发明专利申请号：CN 2026 1 ■■■■■■■■.■（画面感词条检索与调用方法）<br>
          外观设计专利号：ZL 2026 3 ■■■■■■■■.■（电子书版式设计）<br>
          商标注册申请号：■■■■■■■■（把画面说给AI听）<br>
          电子数据保全公证号：（2026）■■证经字第■■■■号
        </div>
        <p><b>上述编号的完整信息与授权链路均已依法备案并作区块链时间戳存证。</b>对任何剽窃、洗稿、盗图、盗版或冒名行为，权利人保留追究民事、行政乃至刑事责任的全部权利，并已委托知识产权代理机构进行全网监测。切莫以身试法。</p>
      </div>

      <div class="ed-foot"><span>把画面说给 AI 听 · 全书完</span><span>示意图仅供参考 · 版权所有 侵权必究</span></div>
    </div>
  </section>
</div>
</body>
</html>'''

os.makedirs(OUT, exist_ok=True)
open(OUT_HTML, 'w', encoding='utf-8').write(doc)
print("已生成:", OUT_HTML)
print("词条:", len(re.findall(r'<article class="entry"', doc)), " 配图:", len(re.findall(r'class="media"', doc)))
print("内嵌图片:", len(_uri_cache), "张；HTML大小:", round(len(doc.encode('utf-8'))/1024/1024, 2), "MB")
