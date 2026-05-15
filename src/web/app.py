"""
FriendDebate Web App - Web界面应用

提供Web界面来管理辩论、查看历史记录、分享等功能
"""

import os
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

from ..debate import DebateEngine, get_skill
from ..clone import FriendCloner, AvatarStorage
from ..share import ShareGenerator


def create_app(config: dict = None):
    """
    创建Flask应用

    Args:
        config: 配置字典

    Returns:
        Flask应用实例
    """
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    CORS(app)

    app.config["DATA_DIR"] = Path(config.get("data_dir", "data"))
    app.config["UPLOAD_FOLDER"] = app.config["DATA_DIR"] / "chatlogs"
    app.config["AVATARS_DIR"] = app.config["DATA_DIR"] / "avatars"
    app.config["DEBATES_DIR"] = app.config["DATA_DIR"] / "debates"
    app.config["SHARES_DIR"] = app.config["DATA_DIR"] / "shares"

    for dir_path in [
        app.config["UPLOAD_FOLDER"],
        app.config["AVATARS_DIR"],
        app.config["DEBATES_DIR"],
        app.config["SHARES_DIR"]
    ]:
        dir_path.mkdir(parents=True, exist_ok=True)

    avatar_storage = AvatarStorage(app.config["DATA_DIR"])
    share_generator = ShareGenerator(app.config["SHARES_DIR"])

    @app.route("/")
    def index():
        """首页"""
        return render_template("index.html")

    @app.route("/api/avatars", methods=["GET"])
    def list_avatars():
        """获取角色列表"""
        avatars = avatar_storage.list_avatars()
        return jsonify({"avatars": avatars})

    @app.route("/api/avatars", methods=["POST"])
    def create_avatar():
        """创建新角色"""
        if "chat_log" not in request.files:
            return jsonify({"error": "请上传聊天记录"}), 400

        chat_log = request.files["chat_log"]
        name = request.form.get("name", "未命名")
        platform = request.form.get("platform", "telegram")

        if chat_log.filename == "":
            return jsonify({"error": "未选择文件"}), 400

        upload_dir = app.config["UPLOAD_FOLDER"] / name
        upload_dir.mkdir(parents=True, exist_ok=True)
        chat_log.save(upload_dir / chat_log.filename)

        try:
            cloner = FriendCloner(platform=platform)
            profile = cloner.create_profile(
                chat_log_path=upload_dir,
                name=name,
                output_dir=app.config["AVATARS_DIR"]
            )
            avatar_storage.save_avatar(profile)

            return jsonify({
                "success": True,
                "avatar": {
                    "id": name.lower().replace(" ", "_"),
                    "name": name,
                    "language_style": profile.language_style,
                    "personality_traits": profile.personality_traits
                }
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/avatars/<avatar_id>", methods=["DELETE"])
    def delete_avatar(avatar_id):
        """删除角色"""
        success = avatar_storage.delete_avatar(avatar_id)
        return jsonify({"success": success})

    @app.route("/api/skills", methods=["GET"])
    def list_skills():
        """获取可用策略列表"""
        from ..debate.skills import list_skills
        skills = list_skills()
        return jsonify({"skills": skills})

    @app.route("/api/debate/start", methods=["POST"])
    def start_debate():
        """开始辩论"""
        data = request.json

        debater1_id = data.get("debater1")
        debater2_id = data.get("debater2")
        topic = data.get("topic")
        rounds = data.get("rounds", 5)
        skill1_name = data.get("skill1", "contrarian")
        skill2_name = data.get("skill2", "rational")

        if not all([debater1_id, debater2_id, topic]):
            return jsonify({"error": "缺少必要参数"}), 400

        if debater1_id == debater2_id:
            return jsonify({"error": "两个辩手不能相同"}), 400

        profile1 = avatar_storage.load_avatar(debater1_id)
        profile2 = avatar_storage.load_avatar(debater2_id)

        if not profile1 or not profile2:
            return jsonify({"error": "角色不存在"}), 400

        engine = DebateEngine(output_dir=app.config["DEBATES_DIR"])

        engine.add_debater(
            name=profile1["name"],
            profile_data=profile1,
            skill=get_skill(skill1_name)()
        )

        engine.add_debater(
            name=profile2["name"],
            profile_data=profile2,
            skill=get_skill(skill2_name)()
        )

        try:
            debate = engine.start(
                topic=topic,
                rounds=rounds,
                max_tokens=data.get("max_tokens", 300),
                temperature=data.get("temperature", 0.8)
            )

            return jsonify({
                "success": True,
                "debate_id": debate.id,
                "topic": debate.topic,
                "debater1": debate.debater1,
                "debater2": debate.debater2,
                "turns_count": len([t for t in debate.turns if t.speaker != "System"])
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/debate/<debate_id>", methods=["GET"])
    def get_debate(debate_id):
        """获取辩论详情"""
        debate_file = app.config["DEBATES_DIR"] / f"{debate_id}.json"

        if not debate_file.exists():
            return jsonify({"error": "辩论不存在"}), 404

        with open(debate_file, "r", encoding="utf-8") as f:
            debate_data = json.load(f)

        return jsonify(debate_data)

    @app.route("/api/debate/<debate_id>/share", methods=["POST"])
    def share_debate(debate_id):
        """生成分享图片"""
        data = request.json
        style = data.get("style", "朋友圈")
        theme = data.get("theme", "light")

        debate_file = app.config["DEBATES_DIR"] / f"{debate_id}.json"

        if not debate_file.exists():
            return jsonify({"error": "辩论不存在"}), 404

        with open(debate_file, "r", encoding="utf-8") as f:
            from ..debate.engine import Debate
            import uuid
            from datetime import datetime

            debate_dict = json.load(f)

            status_map = {
                "pending": "pending",
                "in_progress": "in_progress",
                "completed": "completed",
                "cancelled": "cancelled"
            }
            from ..debate.engine import DebateStatus

            debate = Debate(
                id=debate_dict["id"],
                topic=debate_dict["topic"],
                status=DebateStatus.COMPLETED,
                created_at=datetime.fromisoformat(debate_dict["created_at"]),
                debater1=debate_dict["debater1"],
                debater2=debate_dict["debater2"],
                skill1=debate_dict["skill1"],
                skill2=debate_dict["skill2"]
            )

            from ..debate.engine import DebateTurn
            for turn_dict in debate_dict["turns"]:
                debate.turns.append(DebateTurn(
                    round_num=turn_dict["round_num"],
                    speaker=turn_dict["speaker"],
                    content=turn_dict["content"],
                    timestamp=datetime.fromisoformat(turn_dict["timestamp"]),
                    skill_used=turn_dict.get("skill_used", "")
                ))

        try:
            image_path = share_generator.create_share_image(
                debate=debate,
                style=style,
                theme=theme
            )

            return jsonify({
                "success": True,
                "image_url": f"/api/shares/{image_path.name}"
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/shares/<filename>")
    def serve_share(filename):
        """提供分享图片"""
        return send_from_directory(app.config["SHARES_DIR"], filename)

    @app.route("/api/debate/<debate_id>/export", methods=["GET"])
    def export_debate(debate_id):
        """导出辩论"""
        format_type = request.args.get("format", "json")

        debate_file = app.config["DEBATES_DIR"] / f"{debate_id}.json"

        if not debate_file.exists():
            return jsonify({"error": "辩论不存在"}), 404

        with open(debate_file, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))

    @app.route("/api/debates", methods=["GET"])
    def list_debates():
        """获取辩论历史"""
        debates = []
        for debate_file in app.config["DEBATES_DIR"].glob("*.json"):
            with open(debate_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                debates.append({
                    "id": data["id"],
                    "topic": data["topic"],
                    "debater1": data["debater1"],
                    "debater2": data["debater2"],
                    "status": data["status"],
                    "created_at": data["created_at"]
                })

        debates.sort(key=lambda x: x["created_at"], reverse=True)
        return jsonify({"debates": debates})

    @app.route("/health", methods=["GET"])
    def health():
        """健康检查"""
        return jsonify({"status": "ok"})

    return app


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="FriendDebate Web App")
    parser.add_argument("--host", default="0.0.0.0", help="主机地址")
    parser.add_argument("--port", type=int, default=3000, help="端口号")
    parser.add_argument("--data-dir", default="data", help="数据目录")
    parser.add_argument("--debug", action="store_true", help="调试模式")

    args = parser.parse_args()

    config = {
        "data_dir": args.data_dir,
    }

    app = create_app(config)
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
