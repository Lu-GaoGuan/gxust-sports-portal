from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, UnidentifiedImageError

from .seed_confirmed_content import (
    ACTIVITIES,
    FAQS,
    MEMBERS,
    POLICY_NOTICE,
)


CATEGORY_LABELS = {
    "sports": "体育赛事",
    "welcome": "迎新活动",
    "team_building": "团建活动",
    "birthday": "部门生日会",
    "volunteer": "志愿服务",
    "meeting": "会议与学习",
    "other": "其他活动",
}


def sql_value(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def insert_statement(table, columns, values):
    rendered = ", ".join(sql_value(value) for value in values)
    return (
        f"INSERT OR REPLACE INTO {table} ({', '.join(columns)}) "
        f"VALUES ({rendered});"
    )


class Command(BaseCommand):
    help = "Export confirmed portal content as a Cloudflare D1 seed migration."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="migrations/0002_seed.sql",
            help="Output path relative to the project root.",
        )

    def handle(self, *args, **options):
        project_root = Path(settings.BASE_DIR).parent
        confirmed_root = settings.BASE_DIR / "media" / "activities" / "confirmed"
        output_path = project_root / options["output"]
        statements = [
            "-- Generated from seed_confirmed_content.py; do not edit by hand.",
            insert_statement(
                "department_profile",
                (
                    "id",
                    "introduction",
                    "welcome_slogan",
                    "recruitment_info",
                    "contact_info",
                    "qq_group_qr_code",
                ),
                (
                    1,
                    "体育部是学院体育活动的策划者与组织者，始终以“服务师生、丰富校园体育文化”为宗旨，"
                    "用认真与热爱把每一场赛事、每一次活动办得有声有色。",
                    "以热爱集结，为青春开赛",
                    "体育部现面向2026级新生开展第七届成员招新。第七届成员尚未产生，"
                    "具体时间、地点和报名方式以学院通知为准。",
                    "",
                    None,
                ),
            ),
        ]

        for member_id, item in enumerate(MEMBERS, start=1):
            statements.append(
                insert_statement(
                    "members",
                    (
                        "id",
                        "name",
                        "major_class",
                        "position",
                        "generation",
                        "tenure",
                        "introduction",
                        "welcome_message",
                        "photo",
                        "sort_order",
                        "is_visible",
                    ),
                    (
                        member_id,
                        item["name"],
                        item["major_class"],
                        item["position"],
                        item["generation"],
                        item["tenure"],
                        item.get("introduction", ""),
                        item.get("welcome_message", ""),
                        None,
                        item["generation"] * 100 + member_id,
                        True,
                    ),
                )
            )

        media_id = 0
        for activity_id, item in enumerate(ACTIVITIES, start=1):
            media_rows = []
            cover = None
            for media_index, source_name in enumerate(item["media"], start=1):
                suffix = Path(source_name).suffix.lower()
                relative_path = Path(item["key"]) / f"{media_index:02d}{suffix}"
                source_path = confirmed_root / relative_path
                if not source_path.exists():
                    self.stderr.write(f"Missing confirmed media: {relative_path}")
                    continue
                media_type = (
                    "video"
                    if suffix in {".mp4", ".mov", ".webm"}
                    else "image"
                )
                width = height = None
                if media_type == "image":
                    try:
                        with Image.open(source_path) as image:
                            width, height = image.size
                    except (OSError, UnidentifiedImageError):
                        pass
                public_url = (
                    "/media/activities/confirmed/" + relative_path.as_posix()
                )
                if cover is None and media_type == "image":
                    cover = public_url
                media_id += 1
                media_rows.append(
                    (
                        media_id,
                        activity_id,
                        public_url,
                        media_type,
                        f"[确认资料] {source_name}",
                        width,
                        height,
                        media_index * 10,
                    )
                )

            category = str(item["category"])
            statements.append(
                insert_statement(
                    "activities",
                    (
                        "id",
                        "name",
                        "category",
                        "category_label",
                        "activity_date",
                        "introduction",
                        "cover",
                        "sort_order",
                        "is_visible",
                    ),
                    (
                        activity_id,
                        item["name"],
                        category,
                        CATEGORY_LABELS[category],
                        None,
                        item["introduction"],
                        cover,
                        activity_id * 10,
                        bool(item["media"]),
                    ),
                )
            )
            for row in media_rows:
                statements.append(
                    insert_statement(
                        "activity_media",
                        (
                            "id",
                            "activity_id",
                            "file",
                            "media_type",
                            "description",
                            "width",
                            "height",
                            "sort_order",
                        ),
                        row,
                    )
                )

        for faq_id, (question, answer, needs_confirmation) in enumerate(
            FAQS, start=1
        ):
            if needs_confirmation:
                answer = f"{POLICY_NOTICE}\n\n{answer}"
            statements.append(
                insert_statement(
                    "faqs",
                    ("id", "question", "answer", "sort_order", "is_visible"),
                    (faq_id, question, answer, faq_id * 10, True),
                )
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(statements) + "\n", encoding="utf-8")
        self.stdout.write(
            self.style.SUCCESS(
                f"Exported {len(MEMBERS)} members, {len(ACTIVITIES)} activities, "
                f"{media_id} media records, and {len(FAQS)} FAQs to {output_path}."
            )
        )
