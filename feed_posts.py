"""피드 100개(디자인 10종 x 10개)의 사진·영상 선택과 문구.

- photo: Pic&Videos/모델촬영_셀렉 의 파일 이름(확장자 뺌). fx/fy = 남길 중심(0~1), zoom = 더 당겨 자르기
- video: Pic&Videos/영상 의 파일 이름(세로 영상). start/dur = 쓸 구간(초)
- color: make_feed.py 의 PAL 색 이름
- 캡션은 CAPTIONS.md 에 따로 있다 (규칙: caption.md)
규칙: 한 디자인 안에서 같은 사진·영상은 한 번만 쓴다.
      사진·영상에 보이는 것만 쓴다. 용량·온도·소음·가격 같은 사양은 근거 자료가 생기기 전까지 쓰지 않는다.
"""

POSTS = {
    # ------------------------------------------------------------ 01 스위스 포스터 (레어로우 청담 포스터)
    '01_스위스포스터': [
        dict(photo='BDC02027', fy=0.4, color='slate', side='r', head='라벨을\n읽는 시간', info='와인을 고르는\n가장 즐거운 순간', en='Reading the label'),
        dict(photo='BDC02121', fy=0.4, color='ivory', side='l', head='오늘의 와인은\n내가 고를게', info='손님이 오는 날\n와인 냉장고 앞', en="Tonight, I'll choose"),
        dict(photo='BDC02217', fy=0.4, color='terracotta', side='r', head='일이 끝나면\n한 잔', info='책상 옆에 둔\n와인 냉장고', en='One glass after work'),
        dict(photo='BDC02268', fy=0.45, color='butter', side='l', head='와인이 있는\n거실', info='소파와 테이블 사이\n한 자리', en='A living room with wine'),
        dict(photo='BDC02381', fy=0.4, color='ink', side='r', head='기대어 서는\n와인 냉장고', info='허리 높이의 상판\n잠시 쉬어 가는 자리', en='Lean on it'),
        dict(photo='BDC02068', fy=0.4, color='oak', side='l', head='오늘 저녁의\n한 병', info='고르고, 꺼내고\n여는 순간까지', en="Tonight's bottle"),
        dict(photo='BDC02136', fy=0.4, color='red', side='r', head='작은\n축하', info='특별한 날이 아니어도\n와인 한 병이면', en='No occasion needed'),
        dict(photo='BDC02417', fy=0.45, color='ivory', side='l', head='음악은 위에\n와인은 안에', info='상판 위의 턴테이블\n거실의 새 자리', en='Records on top'),
        dict(photo='BDC02017', fy=0.45, color='olive', side='r', head='부엌에\n와인의 자리를', info='조리대 곁에 두는\n와인 냉장고', en='Make room for wine'),
        dict(photo='BDC02168', fy=0.4, color='slate', side='l', head='천천히\n마시는 저녁', info='서두를 일 없는\n저녁의 한 잔', en='A slow evening'),
    ],

    # ------------------------------------------------------------ 02 세로 워드마크 (레어로우 EDITION 로고, 애플 PRO)
    '02_세로워드마크': [
        dict(photo='BDC02063', fy=0.5, head='지나가다\n한 병', en='Passing by'),
        dict(photo='BDC02080', fy=0.5, zoom=1.15, fx=0.6, head='가전보다\n가구에 가깝게', en='Less appliance, more furniture'),
        dict(photo='BDC02125', fy=0.5, zoom=1.1, fx=0.6, head='문틈으로\n보이는 저녁', en='Through the doorway'),
        dict(photo='BDC02162', fy=0.45, head='거실과\n다이닝 사이', en='Between rooms'),
        dict(photo='BDC02028', fy=0.5, zoom=1.1, fx=0.6, head='어떤 와인을\n열까', en='Which one tonight?'),
        dict(photo='BDC02260', fy=0.45, zoom=1.1, fx=0.6, head='하루의 끝에\n머무는 자리', en='End of the day'),
        dict(photo='BDC02283', fy=0.45, head='주말은\n느리게', en='Slow weekend'),
        dict(photo='BDC02314', fy=0.45, zoom=1.1, fx=0.6, head='한 사람은 고르고\n한 사람은 기다리고', en='One picks, one waits'),
        dict(photo='BDC02044', fy=0.45, zoom=1.1, fx=0.6, head='매일\n여는 문', en='The door you open daily'),
        dict(photo='BDC02200', fy=0.45, zoom=1.1, fx=0.6, head='손을 뻗으면\n닿는 와인', en='Within reach'),
    ],

    # ------------------------------------------------------------ 03 컬러 블록 (MMK·로코 색 면)
    '03_컬러블록': [
        dict(photo='BDC02199', fx=0.5, color='terracotta', head='문을 열면,\n한눈에', body='손잡이를 당기면 안에 둔\n와인들이 가지런히 보입니다.', en='OPEN, SEE IT ALL'),
        dict(photo='BDC02021', fx=0.45, color='slate', head='부엌 한쪽의\n와인 자리', body='조리대 곁에 두면\n요리와 와인이 한 동선에.', en='KITCHEN CORNER'),
        dict(photo='BDC02105', fx=0.55, color='ivory', head='둘이 마주 앉은\n식탁 곁에', body='다음 병을 꺼내러\n멀리 가지 않아도 됩니다.', en='TABLE FOR TWO'),
        dict(photo='BDC02240', fx=0.55, color='olive', head='책장을 넘기다\n한 잔', body='읽던 페이지를 덮지 않아도\n될 만큼 가까운 곳에.', en='READING HOUR'),
        dict(photo='BDC02278', fx=0.45, color='ink', head='좋아하는 자리에서\n좋아하는 와인을', body='가장 편한 자리 곁에\nTERUVA를 두어 보세요.', en='FAVORITE SEAT'),
        dict(photo='BDC02292', fx=0.5, color='butter', head='이야기가\n무르익는 오후', body='잔이 비면 몇 걸음,\n와인이 바로 곁에 있습니다.', en='LONG TALKS'),
        dict(photo='BDC02029', fx=0.5, color='oak', head='요리보다 먼저\n와인을 고르고', body='오늘 곁들일 와인을\n미리 골라 둡니다.', en='KITCHEN HOUR'),
        dict(photo='BDC02125', fx=0.55, color='slate', head='가까운 사이의\n저녁', body='가까운 사이의 저녁에는\n와인 한 병이면 충분합니다.', en='CLOSE COMPANY'),
        dict(photo='BDC02052', fx=0.5, color='red', head='한 병을\n꺼내는 순간', body='선반에 누운 와인 중\n오늘의 한 병을 꺼냅니다.', en='PICK ONE'),
        dict(photo='BDC02454', fx=0.5, color='ivory', head='TERUVA', body='공간에 놓이는 순간,\n가전이 아닌 가구가 됩니다.', en='WINE CELLAR'),
    ],

    # ------------------------------------------------------------ 04 매거진 커버
    '04_매거진커버': [
        dict(photo='BDC02068', fy=0.45, story='오늘 저녁의\n한 병', lines=[('COVER STORY', '고르고, 꺼내고, 여는 순간'), ('HOME', '가전이 아닌 가구')]),
        dict(photo='BDC02136', fy=0.45, story='식탁 위의\n작은 축하', lines=[('DINING', '특별한 날이 아니어도'), ('TABLE', '와인 한 병이면 충분한 저녁')]),
        dict(photo='BDC02168', fy=0.45, story='천천히\n마시는 저녁', lines=[('LIVING', '소파 곁의 와인 냉장고'), ('MOOD', '서두를 일 없는 밤')]),
        dict(photo='BDC02217', fy=0.45, story='일이 끝나면\n한 잔', lines=[('WORK & REST', '책상 옆에 둔 TERUVA'), ('ROUTINE', '하루를 마무리하는 법')]),
        dict(photo='BDC02381', fy=0.45, story='기대어 서는\n와인 냉장고', lines=[('DESIGN', '허리 높이의 상판'), ('STYLE', '와인 한 병과 잔 하나')]),
        dict(photo='BDC02121', fy=0.4, story='오늘의 와인은\n내가 고를게', lines=[('HOSTING', '손님이 오는 날'), ('TIP', '와인 냉장고 앞이 가장 바쁜 날')]),
        dict(photo='BDC02260', fy=0.45, story='하루의 끝에\n머무는 자리', lines=[('LIVING', '소파와 레코드와 와인'), ('EVENING', '오늘을 정리하는 한 잔')]),
        dict(photo='BDC02278', fy=0.45, story='좋아하는 자리,\n좋아하는 와인', lines=[('INTERIOR', '편한 자리 곁에 두기'), ('SLOW', '한 모금씩 천천히')]),
        dict(photo='BDC02163', fy=0.45, story='발끝까지\n편안한 오후', lines=[('WEEKEND', '아무것도 하지 않는 날'), ('LIVING', '와인은 손 닿는 곳에')]),
        dict(photo='BDC02028', fy=0.45, story='라벨을\n읽는 시간', lines=[('SELECTION', '어떤 와인을 열까'), ('KITCHEN', '창가의 와인 냉장고')]),
    ],

    # ------------------------------------------------------------ 05 전시 라벨 (레어로우 whynot 전시)
    '05_전시라벨': [
        dict(photo='BDC02017', work='부엌의 정물', work_en='Still life in a kitchen'),
        dict(photo='BDC02069', work='유리문 너머', work_en='Through the glass'),
        dict(photo='BDC02417', work='레코드와 와인', work_en='Records and wine'),
        dict(photo='BDC02453', work='와인을 위한 가구', work_en='Furniture for wine'),
        dict(photo='BDC02133', work='둘을 위한 식탁', work_en='A table for two'),
        dict(photo='BDC02295', work='긴 대화', work_en='A long conversation'),
        dict(photo='BDC02081', work='오후의 부엌', work_en='Kitchen, afternoon'),
        dict(photo='BDC02029', work='와인을 고르는 사람', work_en='Choosing'),
        dict(photo='BDC02268', work='거실의 오후', work_en='Afternoon in the living room'),
        dict(photo='BDC02461', work='모서리', work_en='The corner'),
    ],

    # ------------------------------------------------------------ 06 디테일 주석 (애플 제품 설명)
    # points: (점 x, 점 y, 글 x, 글 y, 'l'|'r' 글 방향, 영문, 국문) — 1080x1350 화면 좌표
    '06_디테일주석': [
        dict(photo='BDC02453', fy=0.55, zoom=1.25, sub='정면', ink=True, points=[
                (560, 130, 880, 230, 'r', 'TOP', '상판'), (650, 560, 880, 560, 'r', 'GLASS DOOR', '유리문'),
                (292, 640, 170, 640, 'l', 'HANDLE', '손잡이'), (780, 1060, 880, 1160, 'r', 'LEGS', '다리')]),
        dict(photo='BDC02456', fy=0.55, zoom=1.2, sub='문을 열면', ink=True, points=[
                (760, 420, 880, 330, 'r', 'SHELVES', '선반'), (600, 556, 880, 620, 'r', 'DISPLAY', '디스플레이'),
                (400, 1060, 130, 1160, 'r', 'LEGS', '다리')]),
        dict(photo='BDC02460', fy=0.5, sub='안쪽', points=[
                (950, 548, 700, 440, 'l', 'SHELVES', '선반'), (830, 1135, 700, 1000, 'l', 'DISPLAY', '디스플레이'),
                (440, 1198, 300, 1060, 'l', 'LOGO', '로고')]),
        dict(photo='BDC02424', fy=0.5, sub='디스플레이', points=[
                (760, 632, 880, 470, 'r', 'DISPLAY', '디스플레이'), (240, 712, 120, 520, 'r', 'LOGO', '로고'),
                (640, 1150, 760, 1060, 'r', 'RACK', '와인 선반')]),
        dict(photo='BDC02069', fy=0.5, sub='유리문', points=[
                (176, 560, 330, 440, 'r', 'HANDLE', '손잡이'), (620, 820, 760, 700, 'r', 'GLASS DOOR', '유리문'),
                (760, 160, 860, 270, 'r', 'TOP', '상판')]),
        dict(photo='BDC02199', fy=0.5, sub='손잡이', points=[
                (520, 800, 290, 880, 'l', 'HANDLE', '손잡이'), (690, 1000, 880, 1110, 'r', 'GLASS DOOR', '유리문'),
                (840, 580, 880, 330, 'r', 'TOP', '상판')]),
        dict(photo='BDC02381', fy=0.5, sub='상판', points=[
                (215, 752, 120, 600, 'r', 'TOP', '상판'), (440, 960, 640, 960, 'r', 'GLASS DOOR', '유리문'),
                (305, 1100, 640, 1150, 'r', 'HANDLE', '손잡이')]),
        dict(photo='BDC02417', fy=0.5, sub='상판 위', points=[
                (430, 466, 130, 330, 'r', 'TOP', '상판'), (452, 760, 130, 760, 'r', 'HANDLE', '손잡이'),
                (700, 942, 880, 1100, 'r', 'LEGS', '다리')]),
        dict(photo='BDC02044', fy=0.5, sub='위에서 본 모습', points=[
                (380, 612, 130, 500, 'r', 'TOP', '상판'), (560, 940, 130, 940, 'r', 'DISPLAY', '디스플레이'),
                (722, 1000, 860, 880, 'r', 'HANDLE', '손잡이')]),
        dict(photo='BDC02200', fy=0.5, sub='열기 전에', points=[
                (680, 1050, 860, 960, 'r', 'GLASS DOOR', '유리문'), (478, 1150, 150, 1250, 'r', 'HANDLE', '손잡이')]),
    ],

    # ------------------------------------------------------------ 07 마크 창 (TERUVA 로고 마크 모양 안에 사진)
    '07_마크창': [
        dict(photo='BDC02133', fy=0.62, color='ivory', head='와인이 머무는\n식탁', en='A table where wine stays'),
        dict(photo='BDC02105', fy=0.58, color='ink', head='둘이서\n한 병', en='One bottle, two glasses'),
        dict(photo='BDC02162', fy=0.55, color='paper', head='방과 방\n사이에', en='Between rooms'),
        dict(photo='BDC02292', fy=0.6, color='slate', head='대화가\n길어지는 오후', en='Long talks'),
        dict(photo='BDC02080', fy=0.55, color='butter', head='집의 풍경이\n되는 냉장고', en='Part of the view'),
        dict(photo='BDC02268', fy=0.58, color='terracotta', head='소파 곁\n와인 한 병', en='By the sofa'),
        dict(photo='BDC02029', fy=0.55, color='ivory', head='부엌에서\n시작되는 저녁', en='Evenings start in the kitchen'),
        dict(photo='BDC02314', fy=0.6, color='olive', head='고르는 사람,\n기다리는 사람', en='One picks, one waits'),
        dict(photo='BDC02125', fy=0.6, color='paper', head='문틈으로\n보이는 저녁', en='Through the doorway'),
        dict(photo='BDC02295', fy=0.6, color='ink', head='잔이 비면\n몇 걸음', en='A few steps to the next glass'),
    ],

    # ------------------------------------------------------------ 08 다이어그램 (로코 그래프 게시물)
    '08_다이어그램': [
        dict(photo='BDC02200', kind='peaks', title='기분이 좋아지는 순간',
             labels=['금요일 퇴근', '택배 도착', 'TERUVA 문을\n열 때']),
        dict(photo='BDC02454', kind='venn', title='TERUVA는 여기', left='가구', right='와인 냉장고',
             note='가구처럼 놓이고, 와인 냉장고처럼 쓰입니다.'),
        dict(photo='BDC02453', kind='scale', title='가전과 가구 사이,\n어디쯤?', left='가전', right='가구'),
        dict(photo='BDC02063', kind='timeline', title='평일 저녁의 타임라인',
             items=[('18:30', '퇴근'), ('19:00', '저녁 준비'), ('19:20', 'TERUVA 문 열기'), ('21:00', '레코드 한 장 더')], hi=2),
        dict(photo='BDC02052', kind='check', title='오늘 저녁 준비물',
             items=['잔 두 개', '치즈 조금', '좋아하는 음악', 'TERUVA에서 꺼낸 한 병']),
        dict(photo='BDC02044', kind='bars', title='이번 주 가장 많이\n열린 문',
             bars=[('현관문', 0.42), ('옷장', 0.3), ('TERUVA', 0.76)], note='* 우리 집 기준, 아주 주관적인 기록'),
        dict(photo='BDC02105', kind='matrix', title='언제 열어도 좋은 문',
             quads=['혼자, 평일\n책 한 권과 한 잔', '함께, 평일\n늦은 저녁 식사', '혼자, 주말\n레코드 한 장', '함께, 주말\n길어지는 점심']),
        dict(photo='BDC02283', kind='equation', title='일요일 오후의 공식', terms=['레코드', '소파'], result='일요일'),
        dict(photo='BDC02136', kind='pie', title='완벽한 저녁의 구성',
             parts=[('대화', 0.40), ('음악', 0.25), ('와인', 0.35)]),
        dict(photo='BDC02162', kind='plan', title='우리 집 지도'),
    ],

    # ------------------------------------------------------------ 09 시네마 프레임 (릴스)
    '09_시네마프레임': [
        dict(video='C3578', start=0.3, dur=6.5, title='A Kitchen by the Window', kr='창가의 부엌으로', en='Into the light'),
        dict(video='C3579', start=4, dur=8, title='Choosing', kr='오늘의 한 병을 고르는 시간', en='The best part of the evening'),
        dict(video='C3582', start=0.5, dur=8, title='Inside', kr='선반 위에 누운 와인들', en='Bottles at rest'),
        dict(video='C3587', start=0.3, dur=6.5, title='Lunch for Two', kr='둘이 마주 앉은 식탁', en='A table for two'),
        dict(video='C3591', start=0.5, dur=8, title='First Sip', kr='첫 모금의 표정', en='Worth the wait'),
        dict(video='C3592', start=3, dur=8, title='Host Mode', kr='손님이 오는 날', en='Hosting starts here'),
        dict(video='C3594', start=0.3, dur=7.5, title='Side A', kr='음악은 위에서, 와인은 안에서', en='Records on top'),
        dict(video='C3595', start=0.3, dur=6.5, title='The Door', kr='손잡이를 당기면', en='Pull the handle'),
        dict(video='C3584', start=1, dur=8, title='Every Bottle', kr='한 병 한 병, 제자리에', en='A place for every bottle'),
        dict(video='C3589', start=2, dur=8, title='Long Lunch', kr='점심이 길어지는 날', en='Stay a little longer'),
    ],

    # ------------------------------------------------------------ 10 컬러 프레임 (릴스)
    '10_컬러프레임': [
        dict(video='C3580', start=3, dur=8, color='terracotta', head='어떤 와인을\n열까', en='Which one tonight?'),
        dict(video='C3581', start=5, dur=8, color='slate', head='오늘은\n이 한 병으로', en='This one, tonight'),
        dict(video='C3583', start=0, dur=7.5, color='ivory', head='누워 있는\n와인들 사이에서', en='Among the bottles'),
        dict(video='C3585', start=2, dur=8, color='olive', head='손을 뻗으면\n닿는 와인', en='Reach in'),
        dict(video='C3586', start=0.5, dur=8, color='red', head='많은 와인 중\n오늘의 한 병', en='Pick one'),
        dict(video='C3588', start=1, dur=8, color='butter', head='아무 일도 없는\n오후의 와인', en='Nothing planned'),
        dict(video='C3590', start=6, dur=8, color='ink', head='잔이 빌 틈이\n없는 식탁', en='The glasses stay full'),
        dict(video='C3593', start=2, dur=8, color='oak', head='거실을 가로질러\n와인 쪽으로', en='Every path leads to the wine'),
        dict(video='C3596', start=0, dur=7.5, color='slate', head='한 병 꺼내고,\n문은 다시 닫고', en='One out, door closed'),
        dict(video='C3591', start=9.5, dur=8, color='terracotta', head='좋은 와인은\n웃음을 부릅니다', en='Good wine, good laughs'),
    ],
}
