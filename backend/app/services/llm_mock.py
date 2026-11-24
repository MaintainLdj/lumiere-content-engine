"""Mock LLM 服务：模拟美妆内容生成，不接入真实 LLM。"""

from __future__ import annotations

# 合规红线禁用词（生成文案时需规避）
BANNED_WORDS: list[str] = [
    "最好", "第一", "顶级", "唯一", "全网最", "最佳",
    "治疗", "治愈", "药用", "特效", "消炎", "修复皮肤",
]


_MOCK_ARTICLE = """秋冬换季，敏感肌最容易闹情绪——泛红、起皮、紧绷轮番上阵。
这季节保湿精华该怎么挑？今天从成分和肤感两个维度，帮你理清思路。

一、看懂核心成分
秋冬敏感肌首选温和保湿成分：透明质酸（玻尿酸）负责抓水，神经酰胺负责修补皮肤屏障，
角鲨烷则在皮肤表面形成一层轻薄的锁水膜。三者搭配，补水与锁水兼顾。
需要提醒的是，烟酰胺虽是热门成分，但浓度过高对敏感肌不友好，建议从低浓度开始建立耐受。

二、按肤质对号入座
干敏皮：选质地偏润、含角鲨烷或植物油的精华，保湿续航更久。
油敏皮：选水感质地、含透明质酸为主的清爽精华，避免厚重的矿物油。
混合皮：分区护理，T 区轻薄、两颊加强保湿。

三、使用步骤要点
洁面后先用爽肤水打底，趁皮肤微湿时上精华，掌心搓热按压上脸更易吸收。
最后一定要用面霜或乳液封层，否则精华里的水分蒸发更快。

四、避坑提醒
敏感肌新品建议先在耳后或下颌做 48 小时测试；含酸类成分的产品不要和烟酰胺叠加使用，
避免刺激。本季节护肤的核心不是堆产品，而是做减法＋稳定屏障。
（本文为示例内容，不涉及任何医疗建议。）"""


class MockLLMService:
    """模拟 LLM，固定返回美妆向内容，便于快速跑通工作流。"""

    async def plan_topics(
        self, topic_direction: str, target_audience: str
    ) -> list[str]:
        return [
            "秋冬敏感肌保湿精华推荐",
            "平价彩妆好物清单｜学生党必看",
            "烟酰胺成分科普｜美白真相",
            "早C晚A护肤步骤详解",
            "通勤5分钟妆容教程",
        ]

    async def write_draft(
        self, selected_topic: str, review_feedback: str = ""
    ) -> str:
        prefix = ""
        if review_feedback and review_feedback != "APPROVE":
            prefix = "【根据意见已修改】\n\n"
        return prefix + _MOCK_ARTICLE

    async def extract_visuals(self, article_content: str) -> list[str]:
        return [
            "核心成分解析｜透明质酸·神经酰胺·角鲨烷",
            "适用肤质说明｜干敏皮 / 油敏皮 / 混合皮",
            "使用步骤要点｜打底→精华→封层",
            "避坑提醒｜耳后测试·勿叠加酸类",
        ]


mock_llm = MockLLMService()
