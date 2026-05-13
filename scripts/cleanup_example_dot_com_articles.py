"""Remove dummy articles from the live database.

This utility deletes all sentiment logs and articles whose source domain is
``example.com``. It is intentionally conservative and requires an explicit
``--confirm`` flag before making changes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import delete, select

from src.data.database import SessionLocal
from src.data.models import Article, NewsSource, SentimentLog


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete dummy articles from source domain example.com"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually delete rows. Without this flag, the script only reports counts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    with SessionLocal() as db:
        source_ids = db.execute(
            select(NewsSource.id).where(NewsSource.domain == "example.com")
        ).scalars().all()

        article_ids = []
        if source_ids:
            article_ids = db.execute(
                select(Article.id).where(Article.source_id.in_(source_ids))
            ).scalars().all()

        print(f"example.com sources found: {len(source_ids)}")
        print(f"articles to delete: {len(article_ids)}")

        if not args.confirm:
            print("Dry run only. Re-run with --confirm to delete rows.")
            return 0

        deleted_sentiment_logs = 0
        deleted_articles = 0

        if article_ids:
            deleted_sentiment_logs = db.execute(
                delete(SentimentLog).where(SentimentLog.article_id.in_(article_ids))
            ).rowcount or 0
            deleted_articles = db.execute(
                delete(Article).where(Article.id.in_(article_ids))
            ).rowcount or 0

        db.commit()

        print(f"deleted sentiment logs: {deleted_sentiment_logs}")
        print(f"deleted articles: {deleted_articles}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())