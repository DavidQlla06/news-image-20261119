# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/DavidQlla06/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/DavidQlla06/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

A single image that sums up the world's news of Thursday 19 November 2026: the first-ever Trump–Xi–Putin trilateral in Shenzhen, the Crimea bridge hit again, Israel's Gaza ground operation, Anthropic's record $81.3B IPO, Cyclone Akvan bearing down on India — plus GTA VI's global rollout and Voyager 1 nearing one light-day from Earth. Drawn as a newspaper front page by `generate.py` (Pillow, a local build step only) from the seven stories in `stories.json`, and shipped as `entry.png`.

## How it is built

```sh
python3 generate.py   # reads stories.json, paints entry.png (1024x1024)
```

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` only copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`, byte for byte.

---

<sub>Entered on [make.fun](https://make.fun/?ref=56285tn4&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
