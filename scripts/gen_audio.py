#!/usr/bin/env python3
"""일본어 단어 글의 표에서 단어와 예문 음성(mp3)을 만든다.

- 입력: _posts/*japanese-vocab*.md 의 표 (# | 한자 | 히라가나 | 뜻 | 예문)
- 출력: assets/audio/<글 slug>/w01.mp3 (단어, 히라가나 읽기), s01.mp3 (예문)
- 이미 있는 파일은 건너뛴다. 다시 만들려면 파일을 지우거나 --force 를 쓴다.
- 목소리: Microsoft 신경망 음성 ja-JP-NanamiNeural (edge-tts)

사용법:
  python scripts/gen_audio.py            # 없는 음성만 생성
  python scripts/gen_audio.py --dry-run  # 만들 목록만 출력
  python scripts/gen_audio.py --force    # 전부 다시 생성
"""
import argparse
import asyncio
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTS = ROOT / "_posts"
OUT = ROOT / "assets" / "audio"

VOICE = "ja-JP-NanamiNeural"
RATE_WORD = "+0%"
RATE_SENTENCE = "-10%"  # 학습용이라 예문은 약간 천천히
CONCURRENCY = 3
RETRIES = 3

RUBY = re.compile(r"<ruby>(.*?)<rt>.*?</rt></ruby>", re.S)
TAG = re.compile(r"<[^>]+>")


def clean_sentence(cell: str) -> str:
    """예문 칸에서 일본어 문장만 뽑는다 (후리가나 제거, 한글 번역 제외)."""
    jp = re.split(r"<br\s*/?>", cell, maxsplit=1)[0]
    jp = RUBY.sub(r"\1", jp)
    jp = TAG.sub("", jp)
    return html.unescape(jp).strip()


def clean_word(cell: str) -> str:
    return html.unescape(TAG.sub("", cell)).strip()


def parse_post(path: pathlib.Path):
    """표의 데이터 행을 순서대로 (번호, 단어읽기, 예문) 으로 돌려준다."""
    rows = []
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            if in_table:
                break
            continue
        in_table = True
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 5:
            continue
        if set(cells[0]) <= set("-: ") or cells[0] == "#":
            continue  # 구분선, 머리글
        rows.append((len(rows) + 1, clean_word(cells[2]), clean_sentence(cells[4])))
    return rows


def slug_of(path: pathlib.Path) -> str:
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)


def collect(force: bool):
    jobs = []
    for post in sorted(POSTS.glob("*japanese-vocab*.md")):
        slug = slug_of(post)
        for idx, word, sentence in parse_post(post):
            for kind, text, rate in (("w", word, RATE_WORD), ("s", sentence, RATE_SENTENCE)):
                if not text:
                    continue
                dest = OUT / slug / f"{kind}{idx:02d}.mp3"
                if force or not dest.exists() or dest.stat().st_size == 0:
                    jobs.append((dest, text, rate))
    return jobs


async def synth(sem, dest: pathlib.Path, text: str, rate: str) -> bool:
    import edge_tts

    async with sem:
        for attempt in range(1, RETRIES + 1):
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                tmp = dest.with_suffix(".tmp")
                await edge_tts.Communicate(text, VOICE, rate=rate).save(str(tmp))
                if tmp.stat().st_size == 0:
                    raise RuntimeError("empty audio")
                tmp.replace(dest)
                return True
            except Exception as e:  # noqa: BLE001
                if attempt == RETRIES:
                    print(f"::warning::{dest.relative_to(ROOT)} 실패: {e}")
                    return False
                await asyncio.sleep(2 * attempt)
    return False


async def run(jobs):
    sem = asyncio.Semaphore(CONCURRENCY)
    results = await asyncio.gather(*(synth(sem, d, t, r) for d, t, r in jobs))
    return sum(results)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    jobs = collect(args.force)
    print(f"생성할 음성 {len(jobs)}개")
    if args.dry_run:
        for d, t, r in jobs[:10]:
            print(" ", d.relative_to(ROOT), "|", t)
        if len(jobs) > 10:
            print("  ...")
        return 0
    if not jobs:
        return 0
    ok = asyncio.run(run(jobs))
    print(f"완료 {ok}/{len(jobs)}")
    return 0  # 일부 실패해도 나머지는 커밋한다. 빠진 음성은 다음 실행에서 다시 시도한다.


if __name__ == "__main__":
    sys.exit(main())
