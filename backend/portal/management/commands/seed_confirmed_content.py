from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from portal.models import Activity, ActivityMedia, DepartmentProfile, FAQ, Member


POLICY_NOTICE = "【需要学院确认】以下内容依据现有学校文件及学院修改校对材料整理，具体以学院当年正式通知和个人培养要求为准。"

MEMBERS = (
    {"generation": 1, "name": "廖朝瑞", "position": "部长", "major_class": "通信202", "tenure": "2020—2022"},
    {"generation": 2, "name": "吴家超", "position": "部长", "major_class": "电科211", "tenure": "2022—2023"},
    {
        "generation": 3,
        "name": "苏小曼",
        "position": "部长",
        "major_class": "通信222",
        "tenure": "2023—2024",
        "welcome_message": "大学是一个全新的起点。请保持好奇心和开放心态，勇敢追求梦想；每一次挑战都是成长的机会，每一次努力都值得被尊重。",
    },
    {
        "generation": 4,
        "name": "黄流广",
        "position": "部长",
        "major_class": "通信232",
        "tenure": "2024—2025",
        "introduction": "性格活泼开朗，喜欢听歌和旅游；曾任校全媒体干事、学院文体部干事和部长，曾获校电赛三等奖。",
        "welcome_message": "时间会留下最真的痕迹，愿你的大学之路，每一步都坚实有力，饱含喜悦与成长。",
    },
    {"generation": 5, "name": "卢小梦", "position": "部长", "major_class": "通信242", "tenure": "2025—2026"},
    {"generation": 6, "name": "韦佳宜", "position": "部长", "major_class": "", "tenure": "2026—2027"},
    {"generation": 6, "name": "车江潮", "position": "副部长", "major_class": "", "tenure": "2026—2027"},
    {"generation": 6, "name": "周春合", "position": "副部长", "major_class": "", "tenure": "2026—2027"},
    {"generation": 6, "name": "黄惠烨", "position": "副部长", "major_class": "", "tenure": "2026—2027"},
    {"generation": 6, "name": "农金红", "position": "副部长", "major_class": "", "tenure": "2026—2027"},
    {"generation": 6, "name": "莫大深", "position": "副部长", "major_class": "", "tenure": "2026—2027"},
    {"generation": 6, "name": "苏光良", "position": "副部长", "major_class": "", "tenure": "2026—2027"},
)

ACTIVITIES = (
    {"key": "welcome-2025", "name": "2025级新生迎新", "category": Activity.Category.WELCOME, "introduction": "参与学院新生迎新，为新同学提供现场引导和服务保障。", "media": ()},
    {"key": "recruitment", "name": "干事招新与面试", "category": Activity.Category.WELCOME, "introduction": "通过公开、公平的招新与面试，让新成员了解部门并加入团队。", "media": ()},
    {"key": "welcome-meeting-2025", "name": "2025级新生见面会", "category": Activity.Category.WELCOME, "introduction": "通过见面会帮助新成员认识伙伴、了解工作并融入集体。", "media": ()},
    {"key": "college-sports", "name": "院运会", "category": Activity.Category.SPORTS, "introduction": "统筹赛事策划、项目安排、人员分工和现场组织。", "media": ()},
    {
        "key": "sports-work-2025",
        "name": "2025年运动会工作记录",
        "category": Activity.Category.SPORTS,
        "introduction": "记录运动会期间的现场工作、协作与集体时刻。",
        "media": (
            "2025年运动会群体照片.jpeg",
            "2025年运动会工作的照片.jpeg",
            "2025年运动会工作照.jpeg",
            "2025年运动会兄弟照.jpeg",
        ),
    },
    {
        "key": "school-sports-2025",
        "name": "2025年校运会",
        "category": Activity.Category.SPORTS,
        "introduction": "组织参赛、人员联络、秩序安排和物资保障，为运动员顺利参赛提供支持。",
        "media": (
            "25年校运会拔河照片.jpeg",
            "25年校运会工作照片1.jpeg",
            "25年校运会群体聚餐照片.jpeg",
            "25年校运会偷懒照片.jpeg",
            "25年校运会聚餐视频.mp4",
            "25年校运会聚餐跳舞视频.mp4",
        ),
    },
    {"key": "freshman-cup", "name": "新生杯", "category": Activity.Category.SPORTS, "introduction": "组织和协助学院新生参加球类赛事，为同学提供展示与交流的平台。", "media": ()},
    {
        "key": "birthday-2025",
        "name": "2025年部门生日会",
        "category": Activity.Category.BIRTHDAY,
        "introduction": "在工作之外送上集体祝福，记录属于部门的温暖时刻。",
        "media": (
            "2025年部门生日会群体照片.jpeg",
            "2025年部门生日会群体游戏照片1.jpeg",
            "2025年部门生日会风景照片.jpeg",
            "2025年部门生日会打麻将的照片.jpeg",
            "2025年部门生日会蛋糕照片.jpeg",
            "2025年部门生日会唱歌照片.jpeg",
            "2025年部门生日会唱歌照片1.jpeg",
            "2025年部门生日会三国杀群体游戏照片.jpeg",
            "2025年部门生日会烧烤照片.jpeg",
            "2025年部门生日会唱歌视频.mp4",
        ),
    },
    {
        "key": "handover-2025",
        "name": "2025年体育部换届大会",
        "category": Activity.Category.MEETING,
        "introduction": "总结阶段工作、完成工作交接，将经验与责任传递给新一届成员。",
        "media": (
            "2025年换届大会群体照片.jpg",
            "2025年换届大会部长小梦姐照片.jpg",
            "2025年换届大会视频.mp4",
        ),
    },
    {"key": "sunshine-run", "name": "紫荆花阳光跑", "category": Activity.Category.SPORTS, "introduction": "组织春季阳光跑，做好名单确认、活动安排和现场协调。", "media": ()},
    {"key": "march-third", "name": "三月三民族运动会", "category": Activity.Category.SPORTS, "introduction": "参与民族体育活动的组织与保障，让成员在真实任务中锻炼能力。", "media": ()},
    {"key": "electronic-cup", "name": "电子杯", "category": Activity.Category.SPORTS, "introduction": "结合班级和参赛人数制定赛程，保障赛事按计划开展。", "media": ()},
    {
        "key": "training-2025",
        "name": "2025年团学素质拓展",
        "category": Activity.Category.TEAM_BUILDING,
        "introduction": "在协作任务中认识伙伴，提升沟通、组织与团队协作能力。",
        "media": ("25团学素质拓展群体照片1.jpeg", "25团学素质拓展游戏照片1.jpeg"),
    },
    {
        "key": "third-birthday",
        "name": "第三届部门生日会",
        "category": Activity.Category.BIRTHDAY,
        "introduction": "第三届体育部成员共同庆祝和记录的部门生日会。",
        "media": ("第三届部门生日会蛋糕照片.jpeg", "第三届部门生日会.mp4"),
    },
    {
        "key": "winter-solstice-2024",
        "name": "2024年冬至活动",
        "category": Activity.Category.TEAM_BUILDING,
        "introduction": "成员一起包饺子、煮汤圆，在冬至活动中增进交流。",
        "media": ("2024年冬至聚会群体照片.jpeg", "2024年冬至饺子照片1.jpeg", "2024年冬至汤圆照片1.jpeg"),
    },
    {
        "key": "fun-sports-2026",
        "name": "2026年趣味活动",
        "category": Activity.Category.SPORTS,
        "introduction": "通过轻松有趣的运动项目，让更多同学参与并感受运动乐趣。",
        "media": ("2026年趣味活动.jpeg", "2026年趣味活动2.jpeg"),
    },
    {
        "key": "sports-2024",
        "name": "2024年运动会",
        "category": Activity.Category.SPORTS,
        "introduction": "记录体育部成员参与和保障运动会的集体时刻。",
        "media": ("2024年运动会群体照片.jpeg", "2024年运动会聚餐视频.mp4"),
    },
    {
        "key": "birthday-2024",
        "name": "2024年部门生日会",
        "category": Activity.Category.BIRTHDAY,
        "introduction": "记录2024年部门生日会的集体合影与共同回忆。",
        "media": ("2024年部门生日群体照片.jpeg", "2024年部门生日烧烤照片.jpeg"),
    },
    {
        "key": "mid-autumn-2024",
        "name": "2024年中秋团建",
        "category": Activity.Category.TEAM_BUILDING,
        "introduction": "成员在中秋团建中分享节日零食、交流近况，增进团队了解。",
        "media": (
            "2024年中秋团建群体照片.jpeg",
            "2024年中秋团建零食照片.jpeg",
            "2024年中秋团建零食照片2.jpeg",
        ),
    },
    {
        "key": "welcome-meeting-2024",
        "name": "2024届迎新见面会",
        "category": Activity.Category.WELCOME,
        "introduction": "记录2024届迎新见面会的部门集体合影。",
        "media": ("2024届迎新见面会群体照片.jpeg",),
    },
    {
        "key": "birthday-2023",
        "name": "2023年部门生日会",
        "category": Activity.Category.BIRTHDAY,
        "introduction": "记录2023年部门生日会的集体合影和生日蛋糕。",
        "media": (
            "2023年部门生日群体照片1.jpeg",
            "2023年部门生日群体照片2.jpeg",
            "2023年部门生日群体照片3.jpeg",
            "2023年部门生体蛋糕照片.jpeg",
        ),
    },
    {
        "key": "sports-2023",
        "name": "2023届运动会",
        "category": Activity.Category.SPORTS,
        "introduction": "记录2023届运动会期间的赛事服务和部门集体时刻。",
        "media": (
            "2023届运动会群体照片3.jpeg",
            "2023届运动会群体照片4.jpeg",
            "2023届运动会聚餐照片.jpeg",
        ),
    },
    {
        "key": "welcome-meeting-2023",
        "name": "2023届新生见面会",
        "category": Activity.Category.WELCOME,
        "introduction": "通过新生见面会帮助新成员了解体育部并认识伙伴。",
        "media": ("2023届见面会群体照片2.jpeg",),
    },
    {
        "key": "meeting-2023",
        "name": "2023届部门例会",
        "category": Activity.Category.MEETING,
        "introduction": "记录部门成员沟通工作、明确分工和交流经验的例会。",
        "media": ("2023届例会照片.jpeg",),
    },
    {
        "key": "welcome-meeting-2022",
        "name": "2022届新生见面会",
        "category": Activity.Category.WELCOME,
        "introduction": "记录2022届新生见面会的部门集体合影。",
        "media": ("2022届新生见面会.jpeg",),
    },
    {
        "key": "meeting-2022",
        "name": "2022届部门例会",
        "category": Activity.Category.MEETING,
        "introduction": "记录部门成员开展工作交流和任务讨论的例会。",
        "media": ("2022届例会照片.jpeg",),
    },
    {
        "key": "online-community",
        "name": "部门线上交流记录",
        "category": Activity.Category.OTHER,
        "introduction": "记录部门用于线上内容交流的平台入口；页面仅按用户提供的素材名称归档展示。",
        "media": ("部门抖音群.jpeg",),
    },
    {"key": "team-building", "name": "部门团建", "category": Activity.Category.TEAM_BUILDING, "introduction": "通过见面、协作和集体活动增进了解、凝聚感情。", "media": ()},
)

FAQS = (
    ("学院学生会有哪些部门？", "现有需求资料列出了组织部、团委秘书部、实践部、学检部、体育部、文艺部、外联部、全媒体中心和青年志愿者协会；具体名称以学院最新组织架构为准。", False),
    ("综合测评由什么组成？", "综合测评由德育、智育、体育、美育和劳动教育五部分组成。学校2022年正式办法规定，五部分占比分别为20%、50%、10%、10%和10%。", True),
    ("学院校对表中，德育活动具体怎样计分？", "学院2026修改校对材料拟定：认可的校级、院级德育活动参加5次且至少1次为院级活动，思想品德表现基础分为100分；4次90分、3次80分、2次70分、1次60分。认可活动另拟按0.2分/次计入德育加分，德育加分总额不超过20分。", True),
    ("体育部任职具体能加多少分？", "学校正式办法规定，院学生会执行主席4.5分、主席团成员4分、部门主要负责人3分、部门其他工作人员2.5分、干事1分，须任职满1学期、认真履职并考核合格。学院修改校对表对身兼数职另有拟定认定规则。", True),
    ("参加体育活动具体怎样计分？", "学院修改校对表拟定了校级、院级竞赛类体育活动、跑步活动和观众参与的分值，并对报名后无故缺席设置扣分。所有项目须以学院出具的证明和当年正式通知为准。", True),
    ("体育比赛获奖具体加多少分？", "学校正式办法规定：自治区级及以上比赛前八名依次加18至11分；市、校级运动会前八名依次加10至3分；学院赛事前八名依次加4至0.5分。体育加分最高20分，同一次比赛多项名次只取最高分，集体项目个人加分减半。", True),
    ("学习和科技竞赛获奖具体加多少分？", "现有办法列出了国家级、自治区级、市校级和学院级竞赛分值，智育加分最高20分。学院修改校对材料还对认可赛事范围、团队排序递减和同赛项不重复加分作了拟定说明。", True),
    ("志愿服务具体怎样计入劳育？", "学院修改校对材料拟定了志愿时数基础分、超过8小时后的加分和星级志愿者分值，其中额外时数加分上限为10分。", True),
    ("第二课堂各学年具体要求是多少？毕业需要多少分？", "学院修改校对表拟定：相应学年各模块达到大一2.5学分、大二5学分、大三7.5学分时，德育加3分。现有材料没有写明毕业所需第二课堂总学分，毕业要求不能据此确定。", True),
    ("荣誉称号怎样加分，能重复计算吗？", "学校办法规定了不同级别个人荣誉分值。学院修改校对材料注明个人先进荣誉不重复计同类最高项，集体荣誉与个人荣誉可按规则累计，荣誉相关总分不超过10分；奖学金类证书和勤工助学奖不作为荣誉加分。", True),
    ("综合测评和奖学金、评奖评优有什么关系？", "学校正式办法明确，每学年综合测评平均分是评优评先的重要依据。现有材料没有规定具体奖学金金额，也没有给出某类奖学金的固定综测门槛。", True),
    ("为什么加入体育部？", "这里有赛事组织的实践机会，也有往届学长学姐的经验传承。你可以认识伙伴，并在一次次活动中提升沟通、组织和协作能力。", False),
    ("没有体育特长也可以报名吗？", "可以。体育部工作包括策划、组织、协调和现场保障，更看重责任心、沟通能力与参与热情。", False),
)

LEGACY_ACTIVITY_NAMES = (
    "校运会 · 拔河现场",
    "校运会 · 服务保障",
    "团学素质拓展",
    "趣味运动活动",
    "新生见面会",
    "部门生日会",
    "体育部换届大会",
)


class Command(BaseCommand):
    help = "将审校确认后的首期网站内容幂等导入数据库。"

    def add_arguments(self, parser):
        parser.add_argument(
            "--activities-only",
            action="store_true",
            help="仅同步活动、封面和活动媒体，不修改部门资料、成员或常见问题。",
        )
        parser.add_argument(
            "--if-empty",
            action="store_true",
            help="仅当数据库尚无体育部资料时执行完整初始化。",
        )

    def _store_source(self, source, target_name):
        if source.exists():
            if default_storage.exists(target_name):
                default_storage.delete(target_name)
            with source.open("rb") as source_file:
                return default_storage.save(target_name, File(source_file))
        if default_storage.exists(target_name):
            return target_name
        else:
            self.stderr.write(self.style.WARNING(f"Missing media: {source.name}"))
            return ""

    def _sync_activities(self, photo_root):
        Activity.objects.filter(name__in=LEGACY_ACTIVITY_NAMES).delete()
        for index, item in enumerate(ACTIVITIES, start=1):
            activity, _ = Activity.objects.update_or_create(
                name=item["name"],
                defaults={
                    "category": item["category"],
                    "activity_date": None,
                    "introduction": item["introduction"],
                    "sort_order": index * 10,
                    "is_visible": bool(item["media"]),
                },
            )
            confirmed_media = activity.media.filter(
                description__startswith="[确认资料]"
            )
            confirmed_media.delete()
            activity.cover = None
            for media_index, source_name in enumerate(item["media"], start=1):
                source = photo_root / source_name
                suffix = source.suffix.lower()
                target = f"activities/confirmed/{item['key']}/{media_index:02d}{suffix}"
                stored_name = self._store_source(source, target)
                if not stored_name:
                    continue
                media_type = (
                    ActivityMedia.MediaType.VIDEO
                    if suffix in {".mp4", ".mov", ".webm"}
                    else ActivityMedia.MediaType.IMAGE
                )
                ActivityMedia.objects.create(
                    activity=activity,
                    file=stored_name,
                    media_type=media_type,
                    description=f"[确认资料] {source_name}",
                    sort_order=media_index * 10,
                )
                if not activity.cover and media_type == ActivityMedia.MediaType.IMAGE:
                    activity.cover.name = stored_name
            activity.save(update_fields=("cover", "updated_at"))

    def handle(self, *args, **options):
        project_root = Path(settings.BASE_DIR).parent
        photo_root = project_root / "部门照片"

        if options["if_empty"] and DepartmentProfile.objects.exists():
            self.stdout.write("Initial content already exists; skipping seed.")
            return

        if options["activities_only"]:
            self._sync_activities(photo_root)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Activity sync complete: {len(ACTIVITIES)} activities."
                )
            )
            return

        profile = DepartmentProfile.objects.first() or DepartmentProfile()
        profile.introduction = (
            "体育部是学院体育活动的策划者与组织者，始终以“服务师生、丰富校园体育文化”为宗旨，"
            "用认真与热爱把每一场赛事、每一次活动办得有声有色。"
        )
        profile.welcome_slogan = "以热爱集结，为青春开赛"
        profile.recruitment_info = (
            "体育部现面向2026级新生开展第七届成员招新。第七届成员尚未产生，具体时间、地点和报名方式以学院通知为准。"
        )
        profile.save()

        for index, item in enumerate(MEMBERS, start=1):
            defaults = {
                "position": item["position"],
                "major_class": item["major_class"],
                "tenure": item["tenure"],
                "introduction": item.get("introduction", ""),
                "welcome_message": item.get("welcome_message", ""),
                "sort_order": item["generation"] * 100 + index,
                "is_visible": True,
            }
            Member.objects.update_or_create(
                generation=item["generation"], name=item["name"], defaults=defaults
            )

        self._sync_activities(photo_root)

        for index, (question, answer, needs_confirmation) in enumerate(FAQS, start=1):
            if needs_confirmation:
                answer = f"{POLICY_NOTICE}\n\n{answer}"
            FAQ.objects.update_or_create(
                question=question,
                defaults={"answer": answer, "sort_order": index * 10, "is_visible": True},
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: 1 profile, {len(MEMBERS)} members, "
                f"{len(ACTIVITIES)} activities, {len(FAQS)} FAQs."
            )
        )
