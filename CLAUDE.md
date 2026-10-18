# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

# TERUVA 인스타그램 프로젝트 가이드

와인 냉장고 브랜드 TERUVA의 비즈니스 인스타그램 계정에 올릴 홍보 피드를 만드는 작업 폴더입니다.
사진·영상·로고 소스로 하루 1개 수준의 피드(이미지·릴스 + 캡션)를 만들어 `FEED/`에 쌓습니다. 캡션은 `caption.md` 규칙을 따릅니다 (2026-10-18~, 예전 "3줄 이하 코멘트" 규칙 대신).
무엇을 어떻게 만드는지는 [INSTAGRAM_FEED.md](INSTAGRAM_FEED.md)가 기준입니다.

## 폴더 구조

| 경로 | 내용 |
|---|---|
| `Pic&Videos/` | 원본 사진·영상. 사진은 **`모델촬영_셀렉`만** 씁니다 (2026-10-18 JH 지시, `INSTAGRAM_FEED.md`의 "보정" 폴더 대신). 영상은 `영상/` |
| `Logo/` | 회사·제품 로고 |
| `FEED/` | 만든 게시물 (디자인 10종 × 10개). `FEED/<디자인>/<번호>/`, 디자인마다 `LAYOUT.md`(세부 규격). 전체 안내는 [FEED/README.md](FEED/README.md) |
| `FEED_v1/` | 이전 버전(기능별 8종 × 10개)과 그때 스크립트 사본 |
| `make_feed.py` | 피드 생성 스크립트 (글자·도형은 HTML/SVG로 짜서 Edge로 찍고, 영상은 ffmpeg) |
| `feed_posts.py` | 게시물 100개의 사진·영상 선택과 이미지 속 문구 |
| `CAPTIONS.md` | 게시물 100개의 캡션 원문. 고친 뒤 `python make_feed.py --captions` |
| `caption.md` | 캡션 규칙 (JH 작성): 제품 소개 3~5줄 + 고정 문구·해시태그·URL |
| `fonts/` | Pretendard, Archivo, Instrument Serif, Noto Serif KR, Oswald(v1용) — 모두 OFL |
| `reference/` | 참고 채널·홈페이지 캡처와 코멘트 원문 (타사 자료라 git 제외) |
| `.cache/` | 생성 중간 파일 (git 제외) |
| `INSTAGRAM_FEED.md` | 피드 제작 요구사항 (방식, 소스, 디자인 포맷, 코멘트) |

## 레퍼런스는 반드시 실제로 보고 따릅니다

> [!IMPORTANT]
> "참고 채널 느낌"을 기억으로 지어내지 않습니다. 2026-10-18 첫 시안을 기억만으로 만들었다가 "촌스럽다"는 평을 받았습니다. 레이아웃·코멘트를 만들기 전에 실제 게시물과 홈페이지를 보고, 어떤 게시물을 따랐는지 `LAYOUT.md`에 링크로 남깁니다.

- 화면 없이 돌리는 브라우저(headless)는 샤넬이 막고(Access Denied), 인스타그램은 요청을 막습니다(429).
- 대신 **원격 조작 포트를 연 Edge 창**을 띄워 쓰면 됩니다: `Start-Process msedge.exe --remote-debugging-port=9333 --user-data-dir=<임시폴더>` → Python `playwright`의 `connect_over_cdp('http://127.0.0.1:9333')`로 이동·스크롤·캡처합니다. bash의 백그라운드 실행으로 띄우면 창이 바로 닫히니 PowerShell `Start-Process`를 씁니다.
- 인스타그램은 로그인해야 게시물을 충분히 볼 수 있습니다. 그 Edge 창에서 **사용자가 직접 로그인**합니다(비밀번호를 클로드가 다루지 않음). 계정 보호를 위해 게시물 사이에 몇 초씩 쉬어 갑니다.

## 영상 주의사항
- `Pic&Videos/영상`의 원본은 모두 **세로 영상**인데, 가로(3840×2160)로 저장되고 "90도 회전" 표시만 붙어 있습니다. ffmpeg에 그대로 넣으면 일부 결과물에 회전 표시가 따라붙어 옆으로 누워 보입니다. `-display_rotation 0`으로 표시를 지우고 `transpose=cclock`으로 직접 돌립니다 (`make_feed.py`의 `make_video`).
- 영상 장면을 미리 볼 때 썸네일 칸을 가로로 잡으면 세로 화면의 윗부분만 보여 내용을 잘못 알게 됩니다. 세로로 돌린 뒤 전체 화면을 봅니다.
- ffmpeg는 `pip install imageio-ffmpeg`에 들어 있는 것을 씁니다 (PC에 따로 설치돼 있지 않음).

## Bash 명령 승인창 설명 표기

> [!IMPORTANT]
> 사용자는 코드를 잘 모릅니다. Bash 명령을 실행할 때 뜨는 "Allow this bash command?" 승인창의 설명(description)은 **명령어를 영어로 요약하거나 그대로 옮겨적지 말고**, "지금 뭘 하려는 건지"를 한국어로 짧게 적어주세요. (예: "npm install some-pkg" → "패키지 설치 중" O, "Install some-pkg dependency" X)
>
> 되돌리기 어려운 작업(원격 push, 파일 덮어쓰기·삭제, 인스타그램 실제 게시)은 **그 사실이 설명에 드러나야** 합니다. (예: "FEED 폴더 비우는 중 (되돌릴 수 없음)")

## 작업 규칙

### 소통
- **답변·보고·질문(선택지 포함)은 항상 한국어로 합니다.**
- **사용자가 직접 해야 하는 일과 클로드가 할 일을 나눠 적습니다.** (예: 인스타그램 계정 로그인·게시, 소스 추가는 사용자 몫)
- **안전장치가 막은 명령은 돌려서 다시 시도하지 않습니다.** 무엇을 왜 하려 했는지 알리고, 같은 결과를 내는 더 안전한 방법이 있으면 그쪽으로 합니다.

### 디자인
- **레이아웃은 기능(캡션형·워터마크형…)이 아니라 디자인으로 나눕니다 (2026-10-18 JH).** 사진·영상 일부를 색 면·큰 글자·도형·로고로 덮어도 됩니다. 사진 전체를 보존할 필요는 없습니다.
- **한 디자인 안에서는 같은 사진·영상을 두 번 쓰지 않습니다 (2026-10-18 JH).** 파일이 달라도 거의 같은 장면(예: BDC02080·BDC02081)은 한 디자인에 같이 넣지 않습니다.
- **디자인은 말로 묻지 말고 실제 시안으로 보여주고 정합니다.** 카드 레이아웃·톤앤매너는 실제 사진·로고·글꼴로 만든 시안을 **한 파일에 나란히** 담아 보여준 뒤 묻습니다. 각 안 아래 장단점을 한 줄로 적습니다.
- **원본은 고치지 않습니다.** `Pic&Videos/`·`Logo/`의 파일은 읽기만 하고, 자르거나 보정한 결과는 `FEED/`에 새로 저장합니다.

### 게시물 내용
- **확인 안 된 사실을 그럴듯하게 채우지 않습니다.** 제품 사양·가격·인증·수상 같은 내용은 사용자가 준 근거가 있을 때만 씁니다.
- **내부 메모를 게시물에 남기지 않습니다.** "확인 필요", "준비 중", 촬영·보정 뒷이야기, TODO는 고객이 보는 이미지·코멘트에 넣지 않습니다.

### 개발 환경 (Windows)
- **Bash 도구의 heredoc은 백슬래시를 반으로 줄입니다.** `\\d` → `\d` 가 되고, 비-raw 문자열 안에서는 `\1`이 8진 이스케이프로 바뀌어 **조용히 잘못된 코드가 저장됩니다.** 정규식·치환 문자열·윈도우 경로가 든 내용은 Write/Edit 도구로 씁니다.
- 폴더 이름에 `&`·공백·한글이 들어 있습니다(`Pic&Videos`, `바탕 화면`). 명령에 경로를 쓸 때는 항상 따옴표로 감쌉니다.

## Git

- 저장소: `https://github.com/jhlee1223/TERUVA_INSTAGRAM_` — JH 혼자 쓰며 `main` 브랜치에서 작업합니다.
- **`Pic&Videos/`의 원본 사진·영상은 git에 올리지 않습니다.** 수십 GB라 GitHub 용량 제한(파일당 100MB)을 넘습니다.
- **커밋할 때는 내가 고친 파일만 골라 `git add` 합니다** (`git add -A` 금지).

> [!IMPORTANT]
> **Claude Code(에이전트)는 사용자가 명시적으로 요청한 경우에만 원격 저장소(`origin`)로 push합니다.** 로컬 커밋까지는 자유롭게 진행하되, `git push`는 사용자 요청 없이 임의로 실행하지 않습니다.
>
> 보고 끝에 **"올릴까요?"라고 묻지 않습니다.** 대기 중인 커밋이 있으면 "로컬에 커밋 N개 대기 중"이라고 한 줄만 알리고 넘어갑니다. 사용자가 "올려줘"라고 할 때 올립니다.
