"""TERUVA 인스타그램 피드 생성 — 디자인 10종 x 10개 = 100개.
사진 게시물은 1080x1350(4:5), 릴스는 1080x1920(9:16, 원본이 세로 영상).

사용:  python make_feed.py                   전부 만들기
       python make_feed.py 01_스위스포스터    한 디자인만 만들기
       python make_feed.py --captions        caption.txt만 다시 쓰기 (CAPTIONS.md를 고친 뒤)
결과:  FEED/<디자인>/<번호>/post.jpg(또는 post.mp4 + cover.jpg), caption.txt
       FEED/<디자인>/_전체보기.jpg, FEED/_전체보기.jpg
캡션은 CAPTIONS.md(규칙은 caption.md), 사진·영상 선택과 이미지 속 문구는 feed_posts.py.
필요:  pip install pillow playwright imageio-ffmpeg  (브라우저는 설치된 Edge를 씀)
글자·도형은 HTML/SVG로 짜서 Edge로 찍는다. 디자인별 수치는 FEED/<디자인>/LAYOUT.md 참고.
"""
import html
import math
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

import imageio_ffmpeg
from PIL import Image, ImageOps
from playwright.sync_api import sync_playwright

from feed_posts import POSTS

ROOT = Path(__file__).resolve().parent
PHOTOS = ROOT / 'Pic&Videos' / '모델촬영_셀렉'
VIDEOS = ROOT / 'Pic&Videos' / '영상'
OUT = ROOT / 'FEED'
CACHE = ROOT / '.cache'
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1080, 1350      # 사진 게시물
VW, VH = 1080, 1920    # 릴스

# 사진에서 뽑은 색 + 로고 빨강
PAL = {
    'ivory': '#EFEAE1', 'paper': '#F6F3ED', 'butter': '#E7DCC3',
    'ink': '#1C1B19', 'slate': '#6E7D89', 'terracotta': '#A65A42',
    'oak': '#A97C4F', 'olive': '#76745A', 'red': '#DE4A37',
}
DARK = {'ink', 'slate', 'terracotta', 'oak', 'olive', 'red'}
INK, LIGHT, RED = '#1C1B19', '#F4F0E8', '#DE4A37'

# 로고 마크(빨간 도형): 원의 위를 평평하게, 아래를 물결로 자른 모양. Logo/TERUVA로고.png 에서 따라 그림
MARK_W, MARK_H = 166.88, 87.2
MARK_D = ('M12.14 0 L154.74 0 A83.44 83.44 0 0 1 156.3 84 C146 80 128 72 116 72 '
          'C95 72 78 87 55 87 C35 87 18 76 5.4 73 A83.44 83.44 0 0 1 12.14 0 Z')


def fg(color):
    return LIGHT if color in DARK else INK


# ---------------------------------------------------------------- 캡션
# caption.md 4번: 모든 게시글 마지막에 그대로 붙이는 고정 문구
FOOTER = """.
.
.
.
.
#TERUVA #Wine #WineCellar #WineCabinet #와인냉장고
URL: https://teruva.io
"""


def load_captions():
    """CAPTIONS.md를 {디자인: [[문장, ...], ...]}로 읽는다. '## 디자인', '### 번호' 아래 줄이 캡션."""
    caps, design, cur = {}, None, None
    for line in (ROOT / 'CAPTIONS.md').read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            design = line[3:].strip()
            caps[design] = []
            cur = None
        elif line.startswith('### ') and design:
            cur = []
            caps[design].append(cur)
        elif cur is not None and line.strip():
            cur.append(line.strip())
    for design, posts in POSTS.items():
        got = caps.get(design, [])
        if len(got) != len(posts):
            raise SystemExit(f'CAPTIONS.md: {design} 캡션이 {len(got)}개 (게시물 {len(posts)}개)')
        for n, lines in enumerate(got, 1):
            if not 3 <= len(lines) <= 5:
                raise SystemExit(f'CAPTIONS.md: {design} {n:02d}번이 {len(lines)}줄 (3~5줄이어야 함)')
    return caps


def write_caption(path, lines):
    path.write_text('\n'.join(lines) + '\n' + FOOTER, encoding='utf-8')


# ---------------------------------------------------------------- 소스 준비
def photo(name, w=W, h=H, fx=0.5, fy=0.5, zoom=1.0):
    """사진을 w x h로 꽉 채워 자른 파일 경로. (fx, fy)는 남길 중심(0~1)."""
    path = CACHE / 'photo' / f'{name}_{w}x{h}_{fx}_{fy}_{zoom}.jpg'
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        im = Image.open(PHOTOS / f'{name}.jpg')
        im.draft('RGB', (int(w * zoom * 1.5), int(h * zoom * 1.5)))
        im = ImageOps.exif_transpose(im).convert('RGB')
        scale = max(w / im.width, h / im.height) * zoom
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        x = min(max(round(im.width * fx - w / 2), 0), im.width - w)
        y = min(max(round(im.height * fy - h / 2), 0), im.height - h)
        im.crop((x, y, x + w, y + h)).save(path, quality=95)
    return path


def logo_file(kind):
    """흰 배경 로고를 투명 배경으로. kind='color'(검정 글자+빨강 마크) 또는 'white'(전부 흰색)."""
    path = CACHE / f'logo_{kind}.png'
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        src = Image.open(ROOT / 'Logo' / 'TERUVA로고.png').convert('RGB')
        out = Image.new('RGBA', src.size)
        sp, op = src.load(), out.load()
        for y in range(src.height):
            for x in range(src.width):
                r, g, b = sp[x, y]
                a = max(255 - r, 255 - g, 255 - b)
                if a == 0:
                    continue
                if kind == 'white':
                    op[x, y] = (255, 255, 255, a)
                else:  # 흰 바탕과 섞인 색을 되돌린다
                    k = a / 255
                    op[x, y] = tuple(min(255, max(0, round((v - 255 * (1 - k)) / k))) for v in (r, g, b)) + (a,)
        out.crop(out.getbbox()).save(path)
    return path


def logo(kind, width, style):
    return f'<img class="a" src="{uri(logo_file(kind))}" style="{style};width:{width}px">'


def logo_ratio():
    im = Image.open(logo_file('white'))
    return im.height / im.width


def mark(width, color, style):
    h = width * MARK_H / MARK_W
    return (f'<svg class="a" style="{style};width:{width}px;height:{h:.1f}px" viewBox="0 0 {MARK_W} {MARK_H}">'
            f'<path d="{MARK_D}" fill="{color}"/></svg>')


def mark_mask_css():
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {MARK_W} {MARK_H}' preserveAspectRatio='none'>"
           f"<path d='{MARK_D}'/></svg>")
    url = "url('data:image/svg+xml," + quote(svg) + "')"  # style="..." 안에 들어가므로 작은따옴표
    return f'-webkit-mask-image:{url};-webkit-mask-size:100% 100%;-webkit-mask-repeat:no-repeat'


def find_video(name):
    found = list(VIDEOS.rglob(f'{name}.MP4'))
    if not found:
        raise FileNotFoundError(name)
    return found[0]


# ---------------------------------------------------------------- HTML
def uri(p):
    return Path(p).as_uri()


def br(text):
    return html.escape(text).replace('\n', '<br>')


def page(body, size):
    f = uri(ROOT / 'fonts')
    return f"""<!doctype html><meta charset="utf-8"><style>
@font-face{{font-family:P;src:url({f}/PretendardVariable.woff2);font-weight:45 920}}
@font-face{{font-family:A;src:url({f}/Archivo-wdth.woff2);font-weight:100 900;font-stretch:62% 125%}}
@font-face{{font-family:S;src:url({f}/InstrumentSerif-Regular.ttf)}}
@font-face{{font-family:S;src:url({f}/InstrumentSerif-Italic.ttf);font-style:italic}}
@font-face{{font-family:SK;src:url({f}/NotoSerifKR-Regular.ttf)}}
html,body{{margin:0;width:{size[0]}px;height:{size[1]}px;overflow:hidden;background:transparent}}
.c{{position:absolute;inset:0;overflow:hidden;font-family:P;color:#fff;word-break:keep-all;-webkit-font-smoothing:antialiased}}
.bg{{position:absolute;inset:0;width:100%;height:100%;display:block}}
.a{{position:absolute}}
.sh{{text-shadow:0 0 22px rgba(0,0,0,.25)}}
</style><div class="c">{body}</div>"""


def full(p, **kw):
    ph = photo(p['photo'], fx=p.get('fx', 0.5), fy=p.get('fy', 0.5), zoom=p.get('zoom', 1.0), **kw)
    return f'<img class="bg" src="{uri(ph)}">'


def img(p, x, y, w, h, extra=''):
    ph = photo(p['photo'], w, h, p.get('fx', 0.5), p.get('fy', 0.5), p.get('zoom', 1.0))
    return f'<img class="a" src="{uri(ph)}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{extra}">'


def rule(style, color, opacity=.5):
    return f'<div class="a" style="{style};height:1px;background:{color};opacity:{opacity}"></div>'


# ---------------------------------------------------------------- 01 스위스 포스터
def d01_swiss(p, n):
    c, t = PAL[p['color']], fg(p['color'])
    right = p['side'] == 'r'
    px, ix = (295, 40) if right else (40, 805)
    m = mark(36, LIGHT if p['color'] == 'red' else RED, f'left:{ix}px;top:762px')
    return (
        f'<div class="a" style="inset:0;background:{c}"></div>'
        f'<div class="a" style="left:40px;right:40px;top:38px;display:grid;grid-template-columns:repeat(4,1fr);'
        f'column-gap:20px;font-size:17px;font-weight:600;color:{t}"><span>TERUVA</span><span>Wine Cellar</span>'
        f'<span>2026</span><span style="text-align:right">No. {n:02d}</span></div>'
        + rule('left:40px;right:40px;top:76px', t)
        + img(p, px, 110, 745, 690)
        + f'<div class="a" style="left:{ix}px;top:104px;width:235px;font-size:19px;font-weight:500;line-height:1.5;color:{t}">'
          f'{br(p["info"])}</div>' + m
        + f'<div class="a" style="left:34px;right:30px;bottom:122px;font-size:132px;font-weight:800;line-height:1.06;'
          f'letter-spacing:-0.045em;color:{t}">{br(p["head"])}</div>'
        + rule('left:40px;right:40px;bottom:94px', t)
        + f'<div class="a" style="left:40px;right:40px;bottom:48px;display:flex;justify-content:space-between;'
          f'font-size:19px;font-weight:500;color:{t}"><span>{html.escape(p["en"])}</span>'
          f'<span>(TERUVA)&nbsp;&nbsp;&nbsp;(WINE AT HOME)&nbsp;&nbsp;&nbsp;(2026)</span></div>')


# ---------------------------------------------------------------- 02 세로 워드마크
def d02_wordmark(p, n):
    L = 1270
    h = L * logo_ratio()
    return (
        full(p)
        + '<div class="a" style="inset:0;background:linear-gradient(90deg,rgba(0,0,0,.30),rgba(0,0,0,0) 30%)"></div>'
        + '<div class="a" style="inset:0;background:linear-gradient(rgba(0,0,0,0) 58%,rgba(0,0,0,.38))"></div>'
        + f'<img class="a" src="{uri(logo_file("white"))}" style="left:0;top:0;width:{L}px;height:{h:.1f}px;'
          f'transform-origin:0 0;transform:translate(42px,{40 + L}px) rotate(-90deg)">'
        + f'<div class="a sh" style="right:48px;top:44px;text-align:right;font-size:17px;font-weight:600;line-height:1.5">'
          f'No. {n:02d}<br>WINE AT HOME</div>'
        + f'<div class="a sh" style="right:48px;bottom:56px;text-align:right">'
          f'<div style="font-size:46px;font-weight:700;line-height:1.25;letter-spacing:-0.03em">{br(p["head"])}</div>'
          f'<div style="margin-top:14px;font-size:20px;font-weight:500">{html.escape(p["en"])}</div></div>')


# ---------------------------------------------------------------- 03 컬러 블록
def d03_block(p, n):
    c, t = PAL[p['color']], fg(p['color'])
    seam = mark(96, LIGHT if p['color'] == 'red' else RED, 'left:392px;top:1150px')
    return (
        f'<div class="a" style="inset:0;background:{c}"></div>'
        + img(p, 440, 0, 640, 1350)
        + f'<div class="a" style="left:40px;top:30px;font-family:A;font-stretch:125%;font-weight:800;font-size:170px;'
          f'line-height:1;letter-spacing:-0.02em;color:{t}">{n:02d}</div>'
        + f'<div class="a" style="left:44px;width:352px;top:236px;height:2px;background:{t}"></div>'
        + f'<div class="a" style="left:44px;width:356px;top:278px;color:{t}">'
          f'<div style="font-size:50px;font-weight:700;line-height:1.24;letter-spacing:-0.035em">{br(p["head"])}</div>'
          f'<div style="margin-top:30px;font-size:21px;font-weight:400;line-height:1.7;opacity:.85">{br(p["body"])}</div>'
          f'<div style="margin-top:28px;font-size:15px;font-weight:700;letter-spacing:.16em">{html.escape(p["en"])}</div></div>'
        + logo('white' if p['color'] in DARK else 'color', 170, 'left:44px;bottom:58px')
        + f'<div class="a" style="left:44px;bottom:108px;font-size:16px;font-weight:500;color:{t};opacity:.7">teruva.io</div>'
        + seam)


# ---------------------------------------------------------------- 04 매거진 커버
def d04_magazine(p, n):
    lines = ''.join(
        f'<div style="margin-bottom:34px"><div style="font-size:14px;font-weight:700;letter-spacing:.2em">{html.escape(a)}</div>'
        f'<div style="margin-top:8px;font-size:30px;font-weight:600;line-height:1.3;letter-spacing:-0.02em">{br(b)}</div></div>'
        for a, b in p['lines'])
    return (
        full(p)
        + '<div class="a" style="inset:0;background:linear-gradient(rgba(0,0,0,.40),rgba(0,0,0,0) 32%)"></div>'
        + '<div class="a" style="inset:0;background:linear-gradient(rgba(0,0,0,0) 52%,rgba(0,0,0,.45))"></div>'
        + f'<div class="a" style="left:0;right:0;top:40px;text-align:center;font-size:15px;font-weight:600;letter-spacing:.28em">'
          f'TERUVA JOURNAL&nbsp;&nbsp;·&nbsp;&nbsp;No. {n:02d}&nbsp;&nbsp;·&nbsp;&nbsp;OCTOBER 2026</div>'
        + '<div class="a" style="left:0;right:0;top:62px;text-align:center;font-family:S;font-size:178px;line-height:1;'
          'letter-spacing:-0.015em">Wine at Home</div>'
        + f'<div class="a sh" style="left:52px;top:330px;width:420px">{lines}</div>'
        + f'<div class="a sh" style="left:52px;bottom:118px">'
          f'<div style="font-size:14px;font-weight:700;letter-spacing:.2em;margin-bottom:16px">COVER STORY</div>'
          f'<div style="font-size:88px;font-weight:800;line-height:1.1;letter-spacing:-0.04em">{br(p["story"])}</div></div>'
        + rule('left:52px;width:120px;bottom:84px', '#fff', 1)
        + logo('white', 150, 'right:52px;bottom:70px'))


# ---------------------------------------------------------------- 05 전시 라벨
def d05_exhibit(p, n):
    wall, base = '#EBE6DC', '#DED7CB'
    return (
        f'<div class="a" style="inset:0;background:{wall}"></div>'
        f'<div class="a" style="left:0;right:0;bottom:0;height:120px;background:{base}"></div>'
        + rule('left:0;right:0;bottom:120px', '#000', .12)
        + '<div class="a" style="left:66px;top:150px;width:640px;height:800px;padding:22px;background:#FBFAF7;'
          'box-shadow:0 26px 50px rgba(0,0,0,.16),0 3px 8px rgba(0,0,0,.08)"></div>'
        + img(p, 88, 172, 640, 800)
        + f'<div class="a" style="left:780px;width:250px;top:150px;color:{INK}">'
          '<div style="font-size:34px;font-weight:700;line-height:1.05;letter-spacing:-0.02em">teruva<br>at home</div>'
          '<div style="margin-top:6px;font-family:S;font-style:italic;font-size:34px;line-height:1.05">a still life<br>with wine</div>'
          '<div style="margin-top:44px;font-size:18px;line-height:1.65;opacity:.8">와인 냉장고는 부엌 구석이 아니라 '
          '생활의 한가운데 놓입니다. 거실, 부엌, 식탁 곁 — TERUVA가 놓인 열 개의 장면.</div>'
          '<div style="margin-top:14px;font-size:16px;line-height:1.5;opacity:.7">Ten scenes of everyday life, with TERUVA.</div></div>'
        + f'<div class="a" style="left:780px;width:250px;top:806px;color:{INK}">'
          f'<div style="font-size:14px;font-weight:700;letter-spacing:.16em">No. {n:02d}</div>'
          f'<div style="margin-top:10px;font-family:SK;font-size:30px;line-height:1.3;letter-spacing:-0.02em">{br(p["work"])}</div>'
          f'<div style="margin-top:6px;font-family:S;font-style:italic;font-size:25px;line-height:1.2">{html.escape(p["work_en"])}</div>'
          '<div style="margin-top:14px;font-size:14px;line-height:1.6;opacity:.7">TERUVA, 2026<br>와인 냉장고, 생활 공간</div></div>'
        + mark(40, RED, 'left:780px;top:1150px')
        + logo('color', 140, 'right:50px;bottom:48px'))


# ---------------------------------------------------------------- 06 디테일 주석
def d06_notes(p, n):
    ink = p.get('ink')  # 흰 배경 사진은 선·제목을 검정으로
    line = INK if ink else '#fff'
    svg, labels = [], []
    for x, y, lx, ly, side, en, kr in p['points']:
        svg.append(f'<line x1="{x}" y1="{y}" x2="{lx}" y2="{ly}" stroke="{line}" stroke-width="2"/>'
                   f'<circle cx="{x}" cy="{y}" r="9" fill="{line}"/>'
                   f'<circle cx="{x}" cy="{y}" r="20" fill="none" stroke="{line}" stroke-width="1.5" opacity=".75"/>')
        pos = f'left:{lx}px' if side == 'r' else f'right:{W - lx}px'
        labels.append(f'<div class="a" style="{pos};top:{ly - 34}px;background:#fff;color:{INK};border:2px solid {INK};'
                      f'padding:9px 14px 10px;text-align:{"left" if side == "r" else "right"}">'
                      f'<div style="font-size:13px;font-weight:700;letter-spacing:.16em">{html.escape(en)}</div>'
                      f'<div style="margin-top:3px;font-size:24px;font-weight:700;letter-spacing:-0.02em">{html.escape(kr)}</div></div>')
    shade = '' if ink else (
        '<div class="a" style="inset:0;background:rgba(0,0,0,.08)"></div>'
        '<div class="a" style="inset:0;background:linear-gradient(rgba(0,0,0,.30),rgba(0,0,0,0) 26%)"></div>')
    shadow = '' if ink else ';filter:drop-shadow(0 0 5px rgba(0,0,0,.35))'
    return (
        full(p) + shade
        + f'<svg class="a" style="inset:0{shadow}" width="{W}" height="{H}">{"".join(svg)}</svg>'
        + ''.join(labels)
        + f'<div class="a{"" if ink else " sh"}" style="left:52px;top:42px;color:{INK if ink else "#fff"}">'
          f'<span style="font-family:S;font-style:italic;font-size:76px;line-height:1">Details</span>'
          f'<span style="margin-left:14px;font-size:18px;font-weight:600">No. {n:02d}</span>'
          f'<div style="margin-top:6px;font-size:24px;font-weight:600">{html.escape(p["sub"])}</div></div>'
        + logo('color' if ink else 'white', 130, 'right:52px;bottom:56px'))


# ---------------------------------------------------------------- 07 마크 창
def d07_markwindow(p, n):
    c, t = PAL[p['color']], fg(p['color'])
    mw = 1000  # 마크의 둥근 양옆까지 다 보이게
    mh = round(mw * MARK_H / MARK_W)
    ph = photo(p['photo'], mw, mh, p.get('fx', 0.5), p.get('fy', 0.5), p.get('zoom', 1.0))
    return (
        f'<div class="a" style="inset:0;background:{c}"></div>'
        f'<div class="a" style="left:52px;right:52px;top:46px;display:flex;justify-content:space-between;'
        f'font-size:17px;font-weight:600;color:{t}"><span>TERUVA</span><span>No. {n:02d} — WINE AT HOME</span></div>'
        f'<img class="a" src="{uri(ph)}" style="left:{(W - mw) // 2}px;top:160px;width:{mw}px;height:{mh}px;{mark_mask_css()}">'
        f'<div class="a" style="left:52px;right:52px;top:790px;color:{t}">'
        f'<div style="font-size:76px;font-weight:700;line-height:1.16;letter-spacing:-0.04em">{br(p["head"])}</div>'
        f'<div style="margin-top:20px;font-size:23px;font-weight:500;opacity:.8">{html.escape(p["en"])}</div></div>'
        + logo('white' if p['color'] in DARK else 'color', 210, 'left:52px;bottom:58px')
        + f'<div class="a" style="right:52px;bottom:60px;font-size:17px;font-weight:500;color:{t};opacity:.7">teruva.io</div>')


# ---------------------------------------------------------------- 08 다이어그램
def d08_diagram(p, n):
    k = p['kind']
    s, h = [], []  # SVG 조각, HTML 조각

    def text(x, y, body, size=28, weight=500, color=INK, align='center', extra=''):
        tx = {'center': f'left:{x - 400}px;width:800px;text-align:center', 'left': f'left:{x}px',
              'right': f'right:{W - x}px;text-align:right'}[align]
        body = body if '<span' in body else br(body)
        h.append(f'<div class="a" style="{tx};top:{y}px;font-size:{size}px;font-weight:{weight};color:{color};'
                 f'line-height:1.35;letter-spacing:-0.02em;{extra}">{body}</div>')

    def pic(x, y, w, hh, radius):
        h.append(img(p, x, y, w, hh, f'border-radius:{radius}'))

    if k == 'peaks':
        s.append('<polyline points="80,1000 190,1000 250,860 310,1000 450,1000 520,720 590,1000 740,1000 820,470 900,1000 1000,1000" '
                 f'fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="miter"/>')
        pic(705, 215, 230, 230, '50%')
        for x, lab, last in zip((250, 520, 820), p['labels'], (False, False, True)):
            text(x, 1030, lab, 27, 700 if last else 500, RED if last else INK)
    elif k == 'venn':
        s.append(f'<circle cx="400" cy="690" r="290" fill="none" stroke="{INK}" stroke-width="4"/>'
                 f'<circle cx="680" cy="690" r="290" fill="none" stroke="{INK}" stroke-width="4"/>')
        text(240, 668, p['left'], 36, 700)
        text(840, 668, p['right'], 36, 700)
        pic(450, 600, 180, 180, '50%')
        text(540, 800, 'TERUVA', 28, 800, RED)
        text(540, 1040, p['note'], 26, 500)
    elif k == 'scale':
        s.append(f'<line x1="120" y1="960" x2="960" y2="960" stroke="{INK}" stroke-width="5"/>')
        for i in range(11):
            x = 120 + i * 84
            s.append(f'<line x1="{x}" y1="944" x2="{x}" y2="976" stroke="{INK}" stroke-width="{3 if i % 5 else 5}"/>')
        s.append(f'<line x1="792" y1="880" x2="792" y2="948" stroke="{RED}" stroke-width="4"/>'
                 f'<circle cx="792" cy="960" r="18" fill="{RED}"/>')
        pic(632, 420, 320, 450, '20px')
        text(120, 1000, p['left'], 32, 700, align='left')
        text(960, 1000, p['right'], 32, 700, align='right')
        text(792, 1060, 'TERUVA', 28, 800, RED)
    elif k == 'timeline':
        s.append(f'<line x1="150" y1="300" x2="150" y2="1150" stroke="{INK}" stroke-width="4"/>')
        for i, (tm, what) in enumerate(p['items']):
            y = 330 + i * 250
            hi = i == p['hi']
            s.append(f'<circle cx="150" cy="{y}" r="{18 if hi else 11}" fill="{RED if hi else INK}"/>')
            text(190, y - 34, tm, 22, 700, RED if hi else INK, 'left')
            text(190, y - 4, what, 36 if hi else 32, 800 if hi else 500, RED if hi else INK, 'left')
        pic(600, 470, 400, 520, '20px')
        s.append(f'<line x1="470" y1="{330 + p["hi"] * 250}" x2="600" y2="{330 + p["hi"] * 250}" stroke="{RED}" stroke-width="3"/>')
    elif k == 'check':
        for i, item in enumerate(p['items']):
            y = 360 + i * 150
            last = i == len(p['items']) - 1
            col = RED if last else INK
            s.append(f'<rect x="80" y="{y}" width="52" height="52" rx="6" fill="none" stroke="{col}" stroke-width="4"/>'
                     f'<polyline points="92,{y + 27} 103,{y + 39} 122,{y + 14}" fill="none" stroke="{col}" stroke-width="6" '
                     f'stroke-linecap="round" stroke-linejoin="round"/>')
            text(160, y + 2, item, 34, 700 if last else 500, col, 'left')
        pic(640, 330, 360, 560, '20px')
    elif k == 'bars':
        for i, (lab, v) in enumerate(p['bars']):
            y = 420 + i * 190
            last = i == len(p['bars']) - 1
            col = RED if last else INK
            text(80, y - 52, lab, 30, 700 if last else 500, col, 'left')
            s.append(f'<rect x="80" y="{y}" width="{round(820 * v)}" height="64" fill="{col}"/>')
        last_end = 80 + round(820 * p['bars'][-1][1])
        pic(last_end + 24, 747, 170, 170, '50%')
        text(80, 1110, p['note'], 20, 500, '#77736B', 'left')
    elif k == 'matrix':
        s.append(f'<line x1="140" y1="700" x2="940" y2="700" stroke="{INK}" stroke-width="3"/>'
                 f'<line x1="540" y1="290" x2="540" y2="1110" stroke="{INK}" stroke-width="3"/>')
        text(540, 245, '함께', 24, 700)
        text(540, 1120, '혼자', 24, 700)
        text(70, 684, '평일', 24, 700, align='left')
        text(1010, 684, '주말', 24, 700, align='right')
        q = p['quads']  # 혼자평일, 함께평일, 혼자주말, 함께주말
        text(330, 880, q[0], 26)
        text(330, 440, q[1], 26)
        text(750, 880, q[2], 26)
        text(750, 440, q[3], 26)
        s.append(f'<circle cx="540" cy="700" r="128" fill="{RED}"/>')
        pic(422, 582, 236, 236, '50%')
    elif k == 'equation':
        a, b = p['terms']
        text(540, 300, f'{a} + {b} +', 88, 800)
        pic(360, 450, 360, 460, '20px')
        text(540, 950, f'= <span style="color:{RED}">{p["result"]}</span>', 104, 800)
    elif k == 'pie':
        r, cx, cy, start = 260, 540, 690, -90
        cols = [INK, '#9C978D', RED]
        for (lab, v), col in zip(p['parts'], cols):
            end = start + v * 360
            a0, a1 = math.radians(start), math.radians(end)
            x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
            x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
            s.append(f'<path d="M{x0:.1f} {y0:.1f} A{r} {r} 0 {1 if v > .5 else 0} 1 {x1:.1f} {y1:.1f}" fill="none" '
                     f'stroke="{col}" stroke-width="110"/>')
            mid = math.radians((start + end) / 2)
            lx, ly = cx + (r + 120) * math.cos(mid), cy + (r + 120) * math.sin(mid)
            text(round(lx), round(ly) - 30, f'{lab}\n{round(v * 100)}%', 28, 700, RED if col == RED else INK)
            start = end
        pic(cx - 190, cy - 190, 380, 380, '50%')
    elif k == 'plan':
        s.append(f'<rect x="100" y="270" width="880" height="640" fill="none" stroke="{INK}" stroke-width="6"/>'
                 f'<line x1="540" y1="270" x2="540" y2="910" stroke="{INK}" stroke-width="4"/>'
                 f'<line x1="100" y1="560" x2="980" y2="560" stroke="{INK}" stroke-width="4"/>'
                 f'<circle cx="560" cy="820" r="30" fill="none" stroke="{RED}" stroke-width="3" opacity=".5"/>'
                 f'<circle cx="560" cy="820" r="15" fill="{RED}"/>'
                 f'<polyline points="560,835 560,1000 690,1000" fill="none" stroke="{RED}" stroke-width="3"/>')
        text(320, 395, '현관', 30, 600)
        text(760, 395, '부엌', 30, 600)
        text(320, 715, '거실', 30, 600)
        text(760, 715, '식탁', 30, 600)
        pic(700, 940, 280, 300, '20px')
        text(536, 940, 'TERUVA\n여기!', 32, 800, RED, 'right')
    return (
        '<div class="a" style="inset:0;background:#FAF8F4"></div>'
        f'<div class="a" style="left:64px;top:62px;font-size:58px;font-weight:700;line-height:1.2;letter-spacing:-0.035em;'
        f'color:{INK}">{br(p["title"])}</div>'
        f'<svg class="a" style="inset:0" width="{W}" height="{H}">{"".join(s)}</svg>'
        + ''.join(h)
        + f'<div class="a" style="left:64px;bottom:60px;font-size:17px;font-weight:500;color:{INK};opacity:.6">teruva.io</div>'
        + logo('color', 130, 'right:64px;bottom:58px'))


# ---------------------------------------------------------------- 09 시네마 프레임 (릴스 위에 얹는 그림)
def d09_cinema(p, n):
    bar = '#121211'
    corners = ''
    for x, y, dx, dy in ((60, 370, 1, 1), (1020, 370, -1, 1), (60, 1550, 1, -1), (1020, 1550, -1, -1)):
        corners += (f'<polyline points="{x},{y + 44 * dy} {x},{y} {x + 44 * dx},{y}" fill="none" '
                    f'stroke="#fff" stroke-width="3" opacity=".85"/>')
    return (
        f'<div class="a" style="left:0;right:0;top:0;height:330px;background:{bar}"></div>'
        f'<div class="a" style="left:0;right:0;bottom:0;height:330px;background:{bar}"></div>'
        f'<svg class="a" style="inset:0" width="{VW}" height="{VH}">{corners}</svg>'
        f'<div class="a" style="left:60px;right:60px;top:66px;display:flex;justify-content:space-between;'
        f'font-size:15px;font-weight:700;letter-spacing:.3em;color:{LIGHT};opacity:.75">'
        f'<span>TERUVA FILM</span><span>No. {n:02d} — 2026</span></div>'
        f'<div class="a" style="left:0;right:0;top:146px;text-align:center;font-family:S;font-style:italic;'
        f'font-size:84px;line-height:1;color:{LIGHT}">{html.escape(p["title"])}</div>'
        f'<div class="a" style="left:0;right:0;top:1650px;text-align:center;color:{LIGHT}">'
        f'<div style="font-size:32px;font-weight:500;letter-spacing:-0.02em">{html.escape(p["kr"])}</div>'
        f'<div style="margin-top:10px;font-family:S;font-style:italic;font-size:34px;opacity:.8">{html.escape(p["en"])}</div></div>'
        f'<div class="a" style="left:0;right:0;top:1836px;text-align:center;font-size:15px;font-weight:600;'
        f'letter-spacing:.3em;color:{LIGHT};opacity:.5">TERUVA.IO</div>')


# ---------------------------------------------------------------- 10 컬러 프레임 (릴스 위에 얹는 그림 2장: 테두리, 글)
B = 72  # 테두리 두께


def d10_frame(p, n):
    c, t = PAL[p['color']], fg(p['color'])
    edge = f'font-size:16px;font-weight:700;letter-spacing:.3em;color:{t};white-space:nowrap'
    return (
        f'<div class="a" style="left:0;right:0;top:0;height:{B}px;background:{c}"></div>'
        f'<div class="a" style="left:0;right:0;bottom:0;height:{B}px;background:{c}"></div>'
        f'<div class="a" style="left:0;top:0;bottom:0;width:{B}px;background:{c}"></div>'
        f'<div class="a" style="right:0;top:0;bottom:0;width:{B}px;background:{c}"></div>'
        f'<div class="a" style="left:0;right:0;top:27px;text-align:center;{edge}">(TERUVA)&nbsp;&nbsp;&nbsp;(WINE AT HOME)&nbsp;&nbsp;&nbsp;(2026)</div>'
        f'<div class="a" style="left:0;right:0;bottom:25px;text-align:center;{edge}">TERUVA.IO</div>'
        f'<div class="a" style="left:{B // 2}px;top:{VH // 2}px;transform:translate(-50%,-50%) rotate(-90deg);{edge}">No. {n:02d}</div>'
        f'<div class="a" style="left:{VW - B // 2}px;top:{VH // 2}px;transform:translate(-50%,-50%) rotate(90deg);{edge}">와인이 있는 집</div>'
        + mark(46, LIGHT if p['color'] == 'red' else RED, f'left:{(B - 46) // 2}px;top:{(B - 24) // 2}px')
        + mark(46, LIGHT if p['color'] == 'red' else RED, f'right:{(B - 46) // 2}px;bottom:{(B - 24) // 2}px'))


def d10_text(p, n):
    return (f'<div class="a" style="left:{B}px;right:{B}px;bottom:{B}px;height:760px;'
            'background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.42))"></div>'
            f'<div class="a" style="left:{B + 52}px;bottom:{B + 150}px">'
            f'<div style="font-size:84px;font-weight:700;line-height:1.16;letter-spacing:-0.04em">{br(p["head"])}</div>'
            f'<div style="margin-top:20px;font-size:26px;font-weight:500;opacity:.9">{html.escape(p["en"])}</div></div>')


IMAGE_DESIGNS = {'01_스위스포스터': d01_swiss, '02_세로워드마크': d02_wordmark, '03_컬러블록': d03_block,
                 '04_매거진커버': d04_magazine, '05_전시라벨': d05_exhibit, '06_디테일주석': d06_notes,
                 '07_마크창': d07_markwindow, '08_다이어그램': d08_diagram}


# ---------------------------------------------------------------- 찍기
class Shooter:
    def __enter__(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(channel='msedge')
        self.page = self.browser.new_page(viewport={'width': W, 'height': H})
        return self

    def __exit__(self, *a):
        self.browser.close()
        self.pw.stop()

    def shot(self, body, out, transparent=False, size=(W, H)):
        f = CACHE / 'html' / (out.stem + '.html')
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(page(body, size), encoding='utf-8')
        self.page.set_viewport_size({'width': size[0], 'height': size[1]})
        self.page.goto(f.as_uri(), wait_until='load')
        self.page.evaluate('document.fonts.ready')
        if transparent:
            self.page.screenshot(path=str(out), omit_background=True)
        else:
            self.page.screenshot(path=str(out), type='jpeg', quality=95)


def make_video(p, overlays, out_dir, cover_t):
    """세로 영상을 1080x1920으로 줄이고 overlays=[(png, 나타날 초, 사라질 초, 페이드 여부)]를 얹는다.
    원본은 가로로 저장되고 '90도 회전' 표시만 붙어 있어서, 표시를 지우고 직접 돌린다
    (표시를 남겨 두면 일부 결과물에 회전 표시가 그대로 따라붙어 옆으로 누워 보인다)."""
    src = find_video(p['video'])
    dur = p['dur']
    cmd = [FF, '-y', '-v', 'error', '-display_rotation', '0', '-ss', str(p['start']), '-t', str(dur), '-i', str(src)]
    for png, *_ in overlays:
        cmd += ['-loop', '1', '-t', str(dur), '-i', str(png)]
    f = f'[0:v]transpose=cclock,fps=30,scale={VW}:{VH}:flags=lanczos,setsar=1[v0]'
    for i, (_, t0, t1, fade) in enumerate(overlays, 1):
        fx = (f',fade=t=in:st={t0}:d=0.5:alpha=1,fade=t=out:st={t1 - 0.5}:d=0.5:alpha=1' if fade else '')
        f += f';[{i}:v]format=rgba{fx}[o{i}];[v{i - 1}][o{i}]overlay=0:0:shortest=1[v{i}]'
    f += f';[v{len(overlays)}]format=yuv420p[out]'
    mp4 = out_dir / 'post.mp4'
    cmd += ['-filter_complex', f, '-map', '[out]', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19',
            '-movflags', '+faststart', str(mp4)]
    subprocess.run(cmd, check=True)
    subprocess.run([FF, '-y', '-v', 'error', '-ss', str(cover_t), '-i', str(mp4), '-frames:v', '1', '-q:v', '2',
                    str(out_dir / 'cover.jpg')], check=True)


def build(design, posts, shooter, caps):
    thumbs = []
    ov = CACHE / 'overlay'
    ov.mkdir(parents=True, exist_ok=True)
    for n, p in enumerate(posts, 1):
        d = OUT / design / f'{n:02d}'
        d.mkdir(parents=True, exist_ok=True)
        tag = f'{design}_{n:02d}'
        if design in IMAGE_DESIGNS:
            shooter.shot(IMAGE_DESIGNS[design](p, n), d / 'post.jpg')
            thumb = d / 'post.jpg'
        elif design == '09_시네마프레임':
            png = ov / f'{tag}.png'
            shooter.shot(d09_cinema(p, n), png, transparent=True, size=(VW, VH))
            make_video(p, [(png, 0, p['dur'], False)], d, cover_t=1.5)
            thumb = d / 'cover.jpg'
        else:  # 10_컬러프레임
            frame, text = ov / f'{tag}_frame.png', ov / f'{tag}_text.png'
            shooter.shot(d10_frame(p, n), frame, transparent=True, size=(VW, VH))
            shooter.shot(d10_text(p, n), text, transparent=True, size=(VW, VH))
            make_video(p, [(frame, 0, p['dur'], False), (text, 0.4, p['dur'] + 1, True)], d, cover_t=1.5)
            thumb = d / 'cover.jpg'
        write_caption(d / 'caption.txt', caps[design][n - 1])
        thumbs.append(thumb)
        print(design, n, 'ok', flush=True)
    sheet(thumbs, OUT / design / '_전체보기.jpg', cols=5, w=360)


def sheet(files, out, cols, w):
    h = round(w * H / W)
    rows = (len(files) + cols - 1) // cols
    s = Image.new('RGB', (cols * w + (cols + 1) * 12, rows * h + (rows + 1) * 12), 'white')
    for i, f in enumerate(files):  # 릴스(9:16)는 인스타 피드 격자처럼 가운데를 잘라 보여 준다
        im = ImageOps.fit(Image.open(f).convert('RGB'), (w, h), Image.LANCZOS)
        s.paste(im, (12 + (i % cols) * (w + 12), 12 + (i // cols) * (h + 12)))
    s.save(out, quality=88)


def check_unique():
    """한 디자인 안에서 같은 사진·영상을 두 번 쓰지 않았는지 확인."""
    for design, posts in POSTS.items():
        keys = [(p.get('photo') or p.get('video')) for p in posts]
        dup = {k for k in keys if keys.count(k) > 1}
        if dup:
            raise SystemExit(f'{design}: 같은 소스를 두 번 씀 {dup}')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    check_unique()
    caps = load_captions()
    if sys.argv[1:] == ['--captions']:
        for design, posts in POSTS.items():
            for n in range(1, len(posts) + 1):
                write_caption(OUT / design / f'{n:02d}' / 'caption.txt', caps[design][n - 1])
        print('caption.txt', sum(len(p) for p in POSTS.values()), '개 다시 씀')
        sys.exit()
    targets = sys.argv[1:] or list(POSTS)
    with Shooter() as s:
        for design in targets:
            build(design, POSTS[design], s, caps)
    allthumbs = []
    for design in POSTS:
        for n in range(1, 11):
            d = OUT / design / f'{n:02d}'
            t = d / 'post.jpg' if (d / 'post.jpg').exists() else d / 'cover.jpg'
            if t.exists():
                allthumbs.append(t)
    sheet(allthumbs, OUT / '_전체보기.jpg', cols=10, w=200)
