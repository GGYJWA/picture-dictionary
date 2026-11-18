# -*- coding: utf-8 -*-
"""检测PDF打印样式下，哪些词条正文框内容溢出（会被遮挡/裁剪）。"""
import re, subprocess, tempfile, os

BASE = "/Users/mac/WorkBuddy/2026-11-18-10-09-49"
SRC = os.path.join(BASE, "白皮书成品/把画面说给AI听_前四章.html")
html = open(SRC, encoding='utf-8').read()

# 提取 @media print 块内容，提升为全局样式以在screen下模拟打印
m = re.search(r'@media print\{(.*?)\n\}', html, re.S)
print_css = m.group(1) if m else ''
# 移除其中的分页属性（screen下无意义）
print_css = re.sub(r'page-break[^;]*;|break-[^;]*;', '', print_css)
# 注入：把打印样式放到style末尾覆盖
html2 = html.replace('</style>', print_css + '\n</style>', 1)

# 注入检测脚本：测量每个 .text 的溢出，结果写入 #detect-result
js = r'''
<script>
window.addEventListener('load', function(){
  var out=[];
  document.querySelectorAll('.entry').forEach(function(e,i){
    var t=e.querySelector('.card .text');
    if(!t) return;
    var name=e.querySelector('.big')?e.querySelector('.big').textContent:'?';
    var over=t.scrollHeight-t.clientHeight;
    var p=e.querySelector('.prompt');
    var pover=p?(p.scrollHeight-p.clientHeight):0;
    if(over>2 || pover>2) out.push(name+'|正文溢出'+over+'px|提示词溢出'+pover+'px|'+t.clientHeight);
  });
  var d=document.createElement('div');
  d.id='detect-result';
  d.textContent=out.join(';;;');
  document.body.appendChild(d);
});
</script>
'''
html2 = html2.replace('</body>', js + '</body>', 1)

tmp = os.path.join(BASE, "_detect.html")
open(tmp, 'w', encoding='utf-8').write(html2)

chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
r = subprocess.run([chrome,'--headless','--disable-gpu','--no-sandbox',
                    '--virtual-time-budget=8000','--dump-dom','file://'+tmp],
                   capture_output=True, text=True, timeout=120)
dom = r.stdout
mm = re.search(r'<div id="detect-result">(.*?)</div>', dom, re.S)
if mm:
    res = mm.group(1).strip()
    if not res:
        print("✅ 无溢出：所有词条正文框和提示词框内容都装得下")
    else:
        items = res.split(';;;')
        print(f"⚠️ 发现 {len(items)} 个词条溢出：")
        for it in items:
            print("  ", it)
else:
    print("未获取到检测结果，DOM片段:", dom[-500:])
os.remove(tmp)
