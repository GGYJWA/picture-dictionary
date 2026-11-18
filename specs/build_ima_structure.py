# -*- coding: utf-8 -*-
"""生成前三章的 ima 检索结构化版：从章节文件提取词条，生成 标题=【提示词】+别名 的结构。"""
import re, os

BASE = "/Users/mac/WorkBuddy/2026-11-18-10-09-49"
OUT = os.path.join(BASE, "把画面说给AI听_ima检索版_前三章.md")

# 别名补充（中文俗称/白描/英文）——从 build_ebook 的 EN_MAP 思路扩展
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
}

def parse(text):
    entries, cur = [], None
    for line in text.split('\n'):
        m = re.match(r'^## (\d{2})\s+(.+)$', line)
        if m:
            if cur: entries.append(cur)
            cur = {'num':m.group(1),'title':m.group(2),'lines':[]}
        elif cur is not None:
            cur['lines'].append(line)
    if cur: entries.append(cur)
    return entries

def extract(e):
    title = e['title']
    name = title.split('：',1)[0] if '：' in title else title
    alias = ALIAS.get(name, '')
    en = ''
    cn = ''
    for ln in e['lines']:
        s = ln.strip()
        if s.startswith('**中文版**'):
            continue
        if s.startswith('> ') and '提示词' not in s:
            c = s[2:].strip().strip('`')
            if not cn and re.search(r'[\u4e00-\u9fff]', c): cn = c
            elif not en: en = c
    return name, alias, cn, en

files = ["第1章_光影与布光_16条.md","第2章_镜头与景别_15条.md","第3章_构图与机位_11条.md"]
sample = parse(open(os.path.join(BASE,"白皮书样板_人读版_v2.md"),encoding='utf-8').read())
all_entries = [e for e in sample if e['num'] in ('01','02','03','04')]
for f in files:
    all_entries += parse(open(os.path.join(BASE,f),encoding='utf-8').read())
all_entries += [e for e in sample if e['num']=='09']

out = ["# 把画面说给AI听 · ima 检索结构化版（前三章47条）","",
       "> 每条一节，标题=【提示词】+术语名+别名，便于大白话/英文命中。检索到后用「中文/英文提示词」字段直接抄进生图框。",""]
for e in all_entries:
    name, alias, cn, en = extract(e)
    head = f"## 【提示词】{name} {alias}".strip()
    out.append(head)
    out.append("")
    out.append(f"提示词（中文版，国产工具用）：{cn}")
    out.append(f"提示词（英文版，给AI）：{en}")
    out.append("")

open(OUT,'w',encoding='utf-8').write('\n'.join(out))
print("已生成:",OUT," 词条:",len(all_entries))
