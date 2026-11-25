# 25 November 2026: 52 stories, a CIA cyberattack cover and a market plunge

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/aryatrifebrian423/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/aryatrifebrian423/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

One image summing up Wednesday 25 November 2026 in world news: 52
verified stories across 7 regions. The cover carries the day's biggest
story — a cyberattack hitting the CIA and the US spy chief's office,
reported by CNN — and the markets strip carries the day's biggest
numbers: KOSPI -5.3%, Taiwan -5.1%, Nikkei -2.9% on fresh US tariff
threats, Bitcoin at $59,257.

## How it works

`main.py` is pure Python 3.13 standard library — no Pillow, no numpy,
no network. It draws the poster with an embedded 5×7 bitmap font and
a hand-built PNG encoder (`zlib` + `struct`), and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`).
Output is fully deterministic: two runs write byte-identical files.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Verification

Every story is sourced in `SOURCES.md`, with the method and the
wrong-day items that were dropped. The image is 1024×1024 and under
1 MiB.

## License

MIT — see `LICENSE`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=x9vj0gh6&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
