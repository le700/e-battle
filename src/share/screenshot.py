"""
ShareGenerator - 分享图片生成器

生成适合不同平台的精美分享图片
"""

import uuid
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from ..debate.engine import Debate, DebateTurn


class ShareGenerator:
    """分享图片生成器"""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        初始化生成器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir or Path("data/shares")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_share_image(
        self,
        debate: Debate,
        style: str = "朋友圈",
        theme: str = "light"
    ) -> Path:
        """
        创建分享图片

        Args:
            debate: 辩论记录
            style: 分享风格 (朋友圈/微博/小红书)
            theme: 主题色 (light/dark)

        Returns:
            图片路径
        """
        if style == "朋友圈":
            return self._create_wechat_image(debate, theme)
        elif style == "微博":
            return self._create_weibo_image(debate, theme)
        elif style == "小红书":
            return self._create_xiaohongshu_image(debate, theme)
        else:
            return self._create_wechat_image(debate, theme)

    def _create_wechat_image(
        self,
        debate: Debate,
        theme: str
    ) -> Path:
        """创建微信朋友圈风格图片"""
        width = 1080
        height = 1920
        bg_color = "#F5F5F5" if theme == "light" else "#1A1A1A"
        text_color = "#333333" if theme == "light" else "#FFFFFF"

        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            content_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        draw.rectangle([(40, 40), (width - 40, 300)], fill="#667EEA")
        draw.text(
            (width // 2, 170),
            "🎭 AI 辩论大赛",
            font=title_font,
            fill="white",
            anchor="mm"
        )

        draw.text(
            (60, 340),
            f"📌 {debate.topic}",
            font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40),
            fill=text_color
        )

        turns = [t for t in debate.turns if t.speaker != "System"][:6]

        y_offset = 450
        for i, turn in enumerate(turns):
            speaker_color = "#667EEA" if turn.speaker == debate.debater1 else "#F5576C"

            draw.ellipse(
                [(60, y_offset), (100, y_offset + 40)],
                fill=speaker_color
            )

            draw.text(
                (120, y_offset),
                turn.speaker,
                font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32),
                fill=text_color
            )

            content = turn.content[:80] + "..." if len(turn.content) > 80 else turn.content
            draw.text(
                (120, y_offset + 50),
                content,
                font=content_font,
                fill=text_color
            )

            y_offset += 200

            if y_offset > height - 300:
                break

        draw.text(
            (width // 2, height - 150),
            f"✨ 共 {len([t for t in debate.turns if t.speaker != 'System'])} 轮精彩辩论",
            font=small_font,
            fill="#999999",
            anchor="mm"
        )

        draw.text(
            (width // 2, height - 80),
            "🤖 由 FriendDebate AI 生成",
            font=small_font,
            fill="#CCCCCC",
            anchor="mm"
        )

        filename = f"debate_{debate.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        output_path = self.output_dir / filename
        img.save(output_path, "PNG")

        return output_path

    def _create_weibo_image(
        self,
        debate: Debate,
        theme: str
    ) -> Path:
        """创建微博风格图片"""
        width = 1080
        height = 1080
        bg_color = "white"

        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
            content_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        except:
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()

        draw.rectangle([(0, 0), (width, 120)], fill="#E6162D")
        draw.text(
            (width // 2, 60),
            "🔴 微博热评",
            font=title_font,
            fill="white",
            anchor="mm"
        )

        draw.text(
            (60, 160),
            f"辩论话题：{debate.topic}",
            font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36),
            fill="#333333"
        )

        turns = [t for t in debate.turns if t.speaker != "System"][:4]

        y_offset = 240
        for turn in turns:
            draw.text(
                (60, y_offset),
                f"💬 {turn.speaker}：",
                font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28),
                fill="#E6162D"
            )

            content = turn.content[:60] + "..." if len(turn.content) > 60 else turn.content
            draw.text(
                (80, y_offset + 40),
                content,
                font=content_font,
                fill="#333333"
            )

            y_offset += 160

        draw.text(
            (width // 2, height - 80),
            f"🔥 {len([t for t in debate.turns if t.speaker != 'System'])}万+ 围观",
            font=content_font,
            fill="#E6162D",
            anchor="mm"
        )

        filename = f"debate_weibo_{debate.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        output_path = self.output_dir / filename
        img.save(output_path, "PNG")

        return output_path

    def _create_xiaohongshu_image(
        self,
        debate: Debate,
        theme: str
    ) -> Path:
        """创建小红书风格图片"""
        width = 1080
        height = 1440
        bg_color = "#FFF9F5"

        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
            content_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        except:
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()

        draw.rectangle([(0, 0), (width, 200)], fill="#FF2442")
        draw.text(
            (width // 2, 100),
            "📕 小红书",
            font=title_font,
            fill="white",
            anchor="mm"
        )

        draw.text(
            (60, 250),
            f"💬 {debate.topic}",
            font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40),
            fill="#333333"
        )

        turns = [t for t in debate.turns if t.speaker != "System"][:5]

        y_offset = 350
        for turn in turns:
            draw.ellipse(
                [(60, y_offset), (100, y_offset + 40)],
                fill="#FF2442"
            )

            draw.text(
                (120, y_offset),
                turn.speaker,
                font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32),
                fill="#FF2442"
            )

            content = turn.content[:70] + "..." if len(turn.content) > 70 else turn.content
            draw.text(
                (60, y_offset + 60),
                content,
                font=content_font,
                fill="#333333"
            )

            y_offset += 180

        draw.text(
            (width // 2, height - 120),
            f"❤️ {len([t for t in debate.turns if t.speaker != 'System'])} 轮精彩辩论",
            font=content_font,
            fill="#FF2442",
            anchor="mm"
        )

        draw.text(
            (width // 2, height - 60),
            "✨ FriendDebate",
            font=content_font,
            fill="#999999",
            anchor="mm"
        )

        filename = f"debate_xhs_{debate.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        output_path = self.output_dir / filename
        img.save(output_path, "PNG")

        return output_path
