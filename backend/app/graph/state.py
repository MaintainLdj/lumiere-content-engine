from typing import TypedDict


class AgentState(TypedDict):
    topic_direction: str
    target_audience: str
    generated_topics: list[str]
    selected_topic: str
    article_content: str
    review_feedback: str
    visual_points: list[str]
    image_urls: list[str]
    status: str
