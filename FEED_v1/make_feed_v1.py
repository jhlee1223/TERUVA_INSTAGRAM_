"""TERUVA 인스타그램 피드 생성 — 레이아웃 8종 x 10개 = 80개.
사진 게시물은 1080x1350(4:5), 영상(릴스)은 1080x1920(9:16, 원본이 세로 영상).

사용:  python make_feed.py              전부 만들기
       python make_feed.py 05_포스터     한 레이아웃만 만들기
결과:  FEED/<레이아웃>/<번호>/post.jpg(또는 post.mp4 + cover.jpg), caption.txt
       FEED/<레이아웃>/_전체보기.jpg, FEED/_전체보기.jpg
필요:  pip install pillow playwright imageio-ffmpeg  (브라우저는 설치된 Edge를 씀)
글자 배치는 HTML로 짜서 Edge로 찍는다. 레이아웃별 수치는 FEED/<레이아웃>/LAYOUT.md 참고.
"""
import html
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageChops, ImageOps
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


def logo_white():
    """흰 배경 로고(Logo/TERUVA로고.png)를 투명 배경의 흰색 로고로."""
    path = CACHE / 'logo_white.png'
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        src = Image.open(ROOT / 'Logo' / 'TERUVA로고.png').convert('RGB')
        # 흰 바탕과 가장 많이 다른 채널을 불투명도로 쓴다 (검정 글자와 빨강 마크 모두 남도록)
        r, g, b = ImageChops.invert(src).split()
        out = Image.new('RGBA', src.size, (255, 255, 255, 0))
        out.putalpha(ImageChops.lighter(ImageChops.lighter(r, g), b))
        out.crop(out.getbbox()).save(path)
    return path


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
@font-face{{font-family:O;src:url({f}/Oswald-wght.woff2);font-weight:200 700}}
@font-face{{font-family:A;src:url({f}/Archivo-wdth.woff2);font-weight:100 900;font-stretch:62% 125%}}
html,body{{margin:0;width:{size[0]}px;height:{size[1]}px;overflow:hidden;background:transparent}}
.c{{position:absolute;inset:0;overflow:hidden;font-family:P;color:#fff;word-break:keep-all;-webkit-font-smoothing:antialiased}}
.bg{{position:absolute;inset:0;width:100%;height:100%;display:block}}
.a{{position:absolute}}
</style><div class="c">{body}</div>"""


def bg(p, **kw):
    return f'<img class="bg" src="{uri(photo(p["photo"], fx=p.get("fx", 0.5), fy=p.get("fy", 0.5), zoom=p.get("zoom", 1.0), **kw))}">'


# ---------------------------------------------------------------- 8가지 레이아웃
def l1_watermark(p, n):
    return bg(p) + (f'<img class="a" src="{uri(logo_white())}" '
                    'style="left:50%;top:81%;width:270px;transform:translate(-50%,-50%)">')


def l2_kr_caption(p, n):
    side = 'right:84px;text-align:right' if p.get('right') else 'left:84px'
    return bg(p) + (f'<div class="a" style="{side};bottom:118px;font-size:54px;font-weight:500;'
                    'line-height:1.48;letter-spacing:-0.015em;text-shadow:0 0 28px rgba(0,0,0,.22)">'
                    f'{br(p["text"])}</div>')


def l3_title_overlay(p):
    # 제목이 떠 있는 동안만 화면 가운데를 살짝 어둡게 (밝은 벽 위에서도 읽히도록)
    return ('<div class="a" style="inset:0;background:radial-gradient(ellipse 80% 42% at 50% 52%,'
            'rgba(0,0,0,.34),rgba(0,0,0,0) 100%)"></div>'
            '<div class="a" style="left:0;right:0;top:47%;transform:translateY(-50%);text-align:center;'
            'font-family:O;font-weight:500;font-size:100px;line-height:1.04;letter-spacing:.01em;'
            f'text-shadow:0 2px 30px rgba(0,0,0,.3)">{br(p["title"])}</div>'
            '<div class="a" style="left:0;right:0;top:66%;text-align:center;font-size:32px;font-weight:600;'
            f'letter-spacing:-0.01em;text-shadow:0 1px 14px rgba(0,0,0,.4)">{br(p["sub"])}</div>')


def l4_band_overlay():
    """자막 뒤에 영상 내내 깔리는 옅은 아래쪽 그림자."""
    return ('<div class="a" style="inset:0;background:linear-gradient(rgba(0,0,0,0) 48%,'
            'rgba(0,0,0,.28) 70%,rgba(0,0,0,.36) 100%)"></div>')


def l4_sub_overlay(kr, en):
    return ('<div class="a" style="left:70px;right:70px;top:66%;text-align:center;'
            'text-shadow:0 1px 12px rgba(0,0,0,.45)">'
            f'<div style="font-size:36px;font-weight:600;line-height:1.45">{br(kr)}</div>'
            f'<div style="margin-top:18px;font-size:31px;font-weight:600;line-height:1.35">{br(en)}</div></div>')


def l5_poster(p, n):
    return bg(p) + (
        '<div class="a" style="left:0;right:0;bottom:0;height:60%;background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.32))"></div>'
        '<div class="a" style="left:44px;right:44px;top:40px;display:flex;font-size:19px;font-weight:600;letter-spacing:.01em">'
        '<span style="flex:1">TERUVA</span><span style="flex:1;text-align:center">2026</span>'
        f'<span style="flex:1;text-align:right">WINE AT HOME {n:02d}/10</span></div>'
        '<div class="a" style="left:44px;right:44px;bottom:160px;font-size:116px;font-weight:800;line-height:1.1;'
        f'letter-spacing:-0.04em">{br(p["head"])}</div>'
        f'<div class="a" style="left:48px;bottom:112px;font-size:24px;font-weight:500">{html.escape(p["en"])}</div>'
        '<div class="a" style="left:44px;right:44px;bottom:44px;display:flex;justify-content:center;gap:40px;'
        'font-size:16px;font-weight:600;letter-spacing:.02em"><span>(TERUVA)</span><span>(WINE AT HOME)</span><span>(2026)</span></div>')


BOX_POS = {'bl': 'left:48px;bottom:64px', 'tl': 'left:48px;top:64px',
           'br': 'right:48px;bottom:64px', 'tr': 'right:48px;top:64px'}


def l6_feature_box(p, n):
    return bg(p) + (
        f'<div class="a" style="{BOX_POS[p["pos"]]};background:#fff;color:#111;border:2px solid #111;'
        'padding:14px 20px 16px;max-width:600px">'
        f'<div style="font-size:23px;font-weight:700;line-height:1.4;letter-spacing:-0.015em">{br(p["kr"])}</div>'
        f'<div style="margin-top:6px;font-size:21px;font-weight:700;line-height:1.3">{br(p["en"])}</div></div>')


def l7_hero(p, n):
    return bg(p) + (
        '<div class="a" style="left:0;right:0;bottom:0;height:45%;background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.22))"></div>'
        '<div class="a" style="left:0;right:0;top:71%;text-align:center;text-shadow:0 0 24px rgba(0,0,0,.2)">'
        f'<div style="font-size:18px;font-weight:700">{html.escape(p["cat"])}</div>'
        '<div style="margin-top:12px;font-family:A;font-stretch:125%;font-weight:600;font-size:48px;'
        f'letter-spacing:.02em;line-height:1.1">{html.escape(p["title"])}</div>'
        '<div style="display:inline-block;margin-top:30px;background:#fff;color:#000;font-size:16px;font-weight:700;'
        'padding:14px 30px;letter-spacing:.02em;text-shadow:none">teruva.io</div></div>')


def l8_tile(p, n):
    # 애플 홈페이지 타일: 위쪽은 #F5F5F7(어두운 타일은 #000) 단색, 아래로 갈수록 사진이 드러난다
    if p.get('dark'):
        fg, sub, c = '#f5f5f7', '#86868b', '0,0,0'
    else:
        fg, sub, c = '#1d1d1f', '#6e6e73', '245,245,247'
    if p.get('fit'):  # 흰 배경 제품 사진: 사진 전체를 놓고 가장자리를 사진의 벽색으로 흐리게
        ph = photo(p['photo'], w=900, h=1350)
        wall = Image.open(ph).crop((40, 700, 160, 900)).resize((1, 1), Image.BOX).getpixel((0, 0))
        c = '{},{},{}'.format(*wall)
        pic = (f'<div class="a" style="inset:0;background:rgb({c})"></div>'
               f'<img class="a" src="{uri(ph)}" style="left:90px;top:{p.get("top", 230)}px;width:900px;height:1350px;'
               '-webkit-mask-image:radial-gradient(ellipse 50% 50% at 50% 50%,#000 55%,rgba(0,0,0,0) 90%)">')
    else:
        pic = bg(p) + (f'<div class="a" style="inset:0;background:linear-gradient(rgb({c}) 0%,rgb({c}) 24%,'
                       f'rgba({c},0) 42%)"></div>')
    return pic + (
            f'<div class="a" style="left:0;right:0;top:118px;text-align:center;color:{fg}">'
            f'<div style="font-size:78px;font-weight:700;letter-spacing:-0.03em;line-height:1.1">{html.escape(p["title"])}</div>'
            f'<div style="margin-top:16px;font-size:34px;font-weight:500;letter-spacing:-0.015em">{html.escape(p["tag"])}</div>'
            f'<div style="margin-top:14px;font-size:24px;font-weight:500;color:{sub}">{html.escape(p["note"])}</div></div>')


IMAGE_LAYOUTS = {'01_워터마크': l1_watermark, '02_국문캡션': l2_kr_caption, '05_포스터': l5_poster,
                 '06_기능박스': l6_feature_box, '07_히어로': l7_hero, '08_타일': l8_tile}


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
        f = CACHE / 'html' / (out.parent.parent.name + '_' + out.parent.name + '_' + out.stem + '.html')
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
    """세로 영상을 1080x1920으로 줄이고 overlays=[(png, 나타날 초, 사라질 초)]를 얹는다.
    원본은 가로로 저장되고 '90도 회전' 표시만 붙어 있어서, 표시를 지우고 직접 돌린다
    (표시를 남겨 두면 일부 결과물에 회전 표시가 그대로 따라붙어 옆으로 누워 보인다)."""
    src = find_video(p['video'])
    dur = p['dur']
    cmd = [FF, '-y', '-v', 'error', '-display_rotation', '0', '-ss', str(p['start']), '-t', str(dur), '-i', str(src)]
    for png, _, _ in overlays:
        cmd += ['-loop', '1', '-t', str(dur), '-i', str(png)]
    f = f'[0:v]transpose=cclock,fps=30,scale={VW}:{VH}:flags=lanczos,setsar=1[v0]'
    for i, (_, t0, t1) in enumerate(overlays, 1):
        f += (f';[{i}:v]format=rgba,fade=t=in:st={t0}:d=0.5:alpha=1,'
              f'fade=t=out:st={t1 - 0.5}:d=0.5:alpha=1[o{i}];[v{i - 1}][o{i}]overlay=0:0:shortest=1[v{i}]')
    f += f';[v{len(overlays)}]format=yuv420p[out]'
    mp4 = out_dir / 'post.mp4'
    cmd += ['-filter_complex', f, '-map', '[out]', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19',
            '-movflags', '+faststart', str(mp4)]
    subprocess.run(cmd, check=True)
    subprocess.run([FF, '-y', '-v', 'error', '-ss', str(cover_t), '-i', str(mp4), '-frames:v', '1', '-q:v', '2',
                    str(out_dir / 'cover.jpg')], check=True)


def build(layout, posts, shooter):
    thumbs = []
    for n, p in enumerate(posts, 1):
        d = OUT / layout / f'{n:02d}'
        d.mkdir(parents=True, exist_ok=True)
        if layout in IMAGE_LAYOUTS:
            shooter.shot(IMAGE_LAYOUTS[layout](p, n), d / 'post.jpg')
            thumb = d / 'post.jpg'
        elif layout == '03_센터타이틀영상':
            png = CACHE / 'overlay' / f'{layout}_{n:02d}.png'
            png.parent.mkdir(parents=True, exist_ok=True)
            shooter.shot(l3_title_overlay(p), png, transparent=True, size=(VW, VH))
            make_video(p, [(png, 0.3, 4.2)], d, cover_t=1.5)
            thumb = d / 'cover.jpg'
        else:  # 04_자막영상
            half = p['dur'] / 2
            ov = CACHE / 'overlay'
            ov.mkdir(parents=True, exist_ok=True)
            band = ov / 'band.png'
            shooter.shot(l4_band_overlay(), band, transparent=True, size=(VW, VH))
            pngs = []
            for i, (kr, en) in enumerate(p['subs']):
                png = ov / f'{layout}_{n:02d}_{i + 1}.png'
                shooter.shot(l4_sub_overlay(kr, en), png, transparent=True, size=(VW, VH))
                pngs.append(png)
            make_video(p, [(band, 0, p['dur']), (pngs[0], 0.3, half), (pngs[1], half + 0.1, p['dur'] - 0.1)],
                       d, cover_t=1.5)
            thumb = d / 'cover.jpg'
        (d / 'caption.txt').write_text('\n'.join(p['caption']) + '\n', encoding='utf-8')
        thumbs.append(thumb)
        print(layout, n, 'ok', flush=True)
    sheet(thumbs, OUT / layout / '_전체보기.jpg', cols=5, w=360)


def sheet(files, out, cols, w):
    h = round(w * H / W)
    rows = (len(files) + cols - 1) // cols
    s = Image.new('RGB', (cols * w + (cols + 1) * 12, rows * h + (rows + 1) * 12), 'white')
    for i, f in enumerate(files):  # 릴스(9:16)는 인스타 피드 격자처럼 가운데를 잘라 보여 준다
        im = ImageOps.fit(Image.open(f).convert('RGB'), (w, h), Image.LANCZOS)
        s.paste(im, (12 + (i % cols) * (w + 12), 12 + (i // cols) * (h + 12)))
    s.save(out, quality=88)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    targets = sys.argv[1:] or list(POSTS)
    with Shooter() as s:
        for layout in targets:
            build(layout, POSTS[layout], s)
    allthumbs = []
    for layout in POSTS:
        for n in range(1, 11):
            d = OUT / layout / f'{n:02d}'
            t = d / 'post.jpg' if (d / 'post.jpg').exists() else d / 'cover.jpg'
            if t.exists():
                allthumbs.append(t)
    sheet(allthumbs, OUT / '_전체보기.jpg', cols=10, w=200)
