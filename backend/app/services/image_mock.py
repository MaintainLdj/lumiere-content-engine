"""Mock 图片服务：返回占位符图片 URL。"""

from __future__ import annotations


class MockImageService:
    """模拟绘图，返回小红书竖图比例的占位符。"""

    async def generate_images(self, visual_points: list[str]) -> list[str]:
        return [
            f"https://placehold.co/1080x1350/png?text=Card+{i + 1}"
            for i in range(len(visual_points))
        ]


mock_image = MockImageService()
