#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import oss2

REPO_DIR = Path(__file__).resolve().parent
API_DIR = REPO_DIR / "api"
PORTFOLIO_FILE = API_DIR / "portfolio.json"

BUCKET_NAME = os.getenv("OSS_BUCKET", "videos-aigc-cw")
OSS_REGION = os.getenv("OSS_REGION", "oss-cn-shenzhen")
ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID", "").strip()
ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET", "").strip()
SIGNED_URL_EXPIRES = int(os.getenv("OSS_SIGNED_URL_EXPIRES", "3600"))

@dataclass(frozen=True)
class WorkItem:
    title: str
    category: str
    year: str
    duration: str
    desc: str
    color: str
    object_name: str

WORKS: list[WorkItem] = [
    WorkItem("故宫活宝团圆夜AIGC广告", "商业广告 AIGC", "2026", "—", "宫灯、暖金与东方叙事交织，呈现节庆质感的品牌影像。", "Commercial campaign", "videos/故宫活宝团圆夜AIGC广告.m4v"),
    WorkItem("蒙牛软牛奶广告", "商业广告 AIGC", "2026", "—", "明亮纯净的乳白基调，强调产品光泽与干净的商业节奏。", "Commercial campaign", "videos/蒙牛软牛奶广告.mp4"),
    WorkItem("蒙牛软牛奶AIGC广告", "商业广告 AIGC", "2026", "—", "柔和高光与轻盈氛围感，突出奶感、口感和流动光影。", "Commercial campaign", "videos/蒙牛软牛奶AIGC广告.mp4"),
    WorkItem("蒙牛优骨牛奶AIGC广告", "商业广告 AIGC", "2026", "—", "健康、活力与通透光效结合，打造高级品牌视觉。", "Commercial campaign", "videos/蒙牛优骨牛奶AIGC广告.mp4"),
    WorkItem("仁和牌清火胶囊AIGC广告", "商业广告 AIGC", "2026", "—", "以清爽光线和强对比构图，营造药品广告的专业可信感。", "Commercial campaign", "videos/仁和牌清火胶囊AIGC广告.mp4"),
    WorkItem("阿玛尼美妆篇", "个人创作 AIGC", "2026", "—", "克制、精致、带有时装大片式的明暗交界与肤感细节。", "Personal creation", "videos/阿玛尼美妆篇.mp4"),
    WorkItem("古风武侠篇", "个人创作 AIGC", "2026", "—", "水墨、剑气、日照与雾气交织成具有叙事感的画面。", "Personal creation", "videos/古风武侠篇.mp4"),
    WorkItem("科幻动作篇", "个人创作 AIGC", "2026", "—", "蓝白色能量感和高速镜头语言，塑造未来动作氛围。", "Personal creation", "videos/科幻动作篇.mp4"),
    WorkItem("香奈儿时尚篇", "个人创作 AIGC", "2026", "—", "优雅、简洁、光影分层清晰，具有时尚广告片的精致质感。", "Personal creation", "videos/香奈儿时尚篇.mp4"),
    WorkItem("战术特工篇", "个人创作 AIGC", "2026", "—", "低饱和冷感与战术化构图，让动作张力更具电影性。", "Personal creation", "videos/战术特工篇.mp4"),
]


def require_env() -> None:
    missing = [name for name, value in (("OSS_ACCESS_KEY_ID", ACCESS_KEY_ID), ("OSS_ACCESS_KEY_SECRET", ACCESS_KEY_SECRET)) if not value]
    if missing:
        raise SystemExit(f"Missing environment variables: {', '.join(missing)}")


def make_bucket() -> oss2.Bucket:
    auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
    endpoint = f"https://{OSS_REGION}.aliyuncs.com"
    return oss2.Bucket(auth, endpoint, BUCKET_NAME)


def main() -> None:
    require_env()
    bucket = make_bucket()

    items = []
    for index, work in enumerate(WORKS, start=1):
        signed_url = bucket.sign_url("GET", work.object_name, SIGNED_URL_EXPIRES)
        items.append({
            "title": work.title,
            "category": work.category,
            "year": work.year,
            "duration": work.duration,
            "desc": work.desc,
            "color": work.color,
            "object_name": work.object_name,
            "video": work.object_name,
            "video_url": signed_url,
            "order": index,
        })

    API_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "_refreshed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "_count": len(items),
        "items": items,
    }
    PORTFOLIO_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(items)} items to {PORTFOLIO_FILE}")


if __name__ == "__main__":
    main()
