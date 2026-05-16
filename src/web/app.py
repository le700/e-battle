#!/usr/bin/env python3
"""
FriendBattle Web Application
支持多 AI 提供商选择，内置微信导出
"""

import os
import sys
import json
import yaml
import uuid
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.wechat_exporter import WeChatExporter, AIProvider
from src.clone import FriendCloner
from src.clone.manager import FriendManager
from src.debate import DebateEngine, get_skill
from src.export import export_chat, list_export_formats, get_exporter
from src.weflow import weflow_integrator, is_weflow_available, get_weflow_sessions, get_weflow_chat_history

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 最大文件上传

# 加载配置
CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "config.yaml"
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 全局变量
debate_engine = None
ai_provider = None
friend_manager = FriendManager()

# 存储辩论历史
debates = {}


def init_dirs():
    """初始化必要的目录"""
    for dir_name in ['chatlogs_dir', 'avatars_dir', 'profiles_dir', 'debates_dir']:
        dir_path = Path(config['data'][dir_name])
        dir_path.mkdir(parents=True, exist_ok=True)


init_dirs()

@app.route('/')
def index():
    providers = config['providers']
    return render_template('index.html', providers=providers)

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """获取支持的 AI 提供商列表"""
    return jsonify(config['providers'])

@app.route('/api/set_ai', methods=['POST'])
def set_ai_provider():
    """设置 AI 提供商"""
    global ai_provider
    
    data = request.json
    provider_name = data.get('provider', 'openai')
    api_key = data.get('api_key', '')
    base_url = data.get('base_url', '')
    
    ai_provider = AIProvider(provider_name, api_key, base_url)
    
    return jsonify({
        'success': True,
        'message': f'已切换到 {provider_name}',
        'provider': provider_name
    })

@app.route('/api/export_wechat', methods=['POST'])
def export_wechat():
    """导出微信聊天记录"""
    try:
        exporter = WeChatExporter()
        
        if exporter.is_wechat_running():
            return jsonify({
                'success': False,
                'message': '请先关闭微信再导出'
            })
        
        exported = exporter.export_chat_history()
        
        if exported:
            return jsonify({
                'success': True,
                'message': f'成功导出 {len(exported)} 个聊天记录文件',
                'files': exported
            })
        else:
            # 生成示例数据
            sample = exporter.generate_sample_data()
            return jsonify({
                'success': True,
                'message': '未找到微信数据，已生成示例聊天记录',
                'files': [sample]
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'导出失败: {str(e)}'
        })

@app.route('/api/clone', methods=['POST'])
def create_clone():
    """创建 AI 克隆角色"""
    try:
        data = request.json
        chat_log_path = data.get('chat_log_path')
        name = data.get('name')
        
        cloner = FriendCloner()
        profile = cloner.create_profile(chat_log_path, name)
        
        return jsonify({
            'success': True,
            'profile': profile,
            'message': f'成功创建 {name} 的 AI 克隆'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建失败: {str(e)}'
        })

@app.route('/api/avatars', methods=['GET', 'POST'])
def handle_avatars():
    """列出或创建AI角色"""
    if request.method == 'GET':
        avatars = []
        friends = friend_manager.list_friends()
        
        for friend in friends:
            profile = friend_manager.get_profile(friend)
            avatars.append({
                'id': friend,
                'name': profile.name if profile else friend,
                'language_style': profile.language_style if profile else '普通',
                'personality_traits': profile.personality_traits if profile else []
            })
        
        return jsonify({'avatars': avatars})
    else:
        try:
            # 处理文件上传
            if 'chat_log' not in request.files:
                return jsonify({'success': False, 'error': '请上传聊天记录文件'})
            
            file = request.files['chat_log']
            name = request.form.get('name', '')
            
            if not name:
                return jsonify({'success': False, 'error': '请输入角色名称'})
            
            if file.filename == '':
                return jsonify({'success': False, 'error': '请选择文件'})
            
            # 保存上传的文件
            ext = Path(file.filename).suffix
            safe_name = uuid.uuid4().hex
            temp_file = Path(config['data']['chatlogs_dir']) / f"{safe_name}{ext}"
            file.save(temp_file)
            
            # 导入好友
            profile = friend_manager.import_friend(temp_file, name, platform='auto', min_messages=5)
            
            # 返回成功结果
            return jsonify({
                'success': True,
                'message': f'成功创建 {name} 的AI克隆',
                'id': safe_name,
                'name': name,
                'profile': {
                    'name': profile.name,
                    'language_style': profile.language_style,
                    'personality_traits': profile.personality_traits
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})


@app.route('/api/debate/start', methods=['POST'])
def start_debate():
    """开始辩论 - 简化版本，使用模拟辩论"""
    global debate_engine
    
    try:
        data = request.json
        debater1_id = data.get('debater1')
        debater2_id = data.get('debater2')
        topic = data.get('topic')
        rounds = int(data.get('rounds', 5))
        skill1 = data.get('skill1', 'contrarian')
        skill2 = data.get('skill2', 'rational')
        
        # 获取辩手名称
        profile1 = friend_manager.get_profile(debater1_id)
        profile2 = friend_manager.get_profile(debater2_id)
        
        name1 = profile1.name if profile1 else "辩手1"
        name2 = profile2.name if profile2 else "辩手2"
        
        # 创建辩论ID
        debate_id = str(uuid.uuid4())
        
        # 生成模拟辩论内容
        turns = generate_mock_debate(name1, name2, topic, rounds, skill1, skill2)
        
        # 保存辩论
        debate_data = {
            'id': debate_id,
            'topic': topic,
            'debater1': name1,
            'debater2': name2,
            'rounds': rounds,
            'status': 'completed',
            'turns': turns,
            'created_at': datetime.now().isoformat()
        }
        
        debates[debate_id] = debate_data
        
        return jsonify({
            'success': True,
            'debate_id': debate_id,
            'message': '辩论生成完成！'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'启动失败: {str(e)}'
        })


def generate_mock_debate(name1, name2, topic, rounds, skill1, skill2):
    """生成模拟辩论内容"""
    turns = []
    
    responses = {
        'contrarian': [
            f"我完全不同意！{topic}根本就不是这样的！",
            f"等一下，我觉得恰恰相反！让我告诉你为什么...",
            f"你的观点完全站不住脚，我来反驳一下..."
        ],
        'rational': [
            f"关于{topic}，我认为应该理性来看待...",
            f"我们从事实出发来分析这个问题吧...",
            f"我理解你的想法，但我觉得应该考虑这些因素..."
        ],
        'humorous': [
            f"哈哈，{topic}这个问题太有意思了！让我来插一嘴...",
            f"说到这个，我想到一个笑话...",
            f"哎呀，这个问题嘛，我们还是开心地讨论吧..."
        ],
        'aggressive': [
            f"这个问题还用说？当然是我的观点对！",
            f"听好了，真相只有一个！",
            f"不要再争了，事实就摆在眼前！"
        ],
        'diplomatic': [
            f"其实我觉得双方都有道理...",
            f"我们是不是可以找到一个折中方案？",
            f"从不同角度看都有合理性..."
        ],
        'sarcastic': [
            f"哇哦，你说得真对呢～（手动狗头）",
            f"厉害厉害，你说得都对～",
            f"嗯嗯，你开心就好..."
        ],
        'scholar': [
            f"古语有云...关于{topic}...",
            f"从历史经验来看...",
            f"根据我的研究..."
        ],
        'joker': [
            f"恕我直言，这个问题有点...",
            f"算了吧，直接告诉你事实...",
            f"醒醒，别做梦了..."
        ],
        'lazy': [
            f"哎呀，都可以啦...",
            f"随便吧，我无所谓...",
            f"你说得对，就这样吧..."
        ]
    }
    
    for i in range(rounds):
        turn_num = i + 1
        
        # 正方
        response_list1 = responses.get(skill1, responses['rational'])
        content1 = response_list1[i % len(response_list1)]
        turns.append({
            'speaker': name1,
            'content': content1,
            'round_num': turn_num
        })
        
        # 反方
        response_list2 = responses.get(skill2, responses['rational'])
        content2 = response_list2[i % len(response_list2)]
        turns.append({
            'speaker': name2,
            'content': content2,
            'round_num': turn_num
        })
    
    return turns


@app.route('/api/debate/<debate_id>', methods=['GET'])
def get_debate(debate_id):
    """获取辩论详情"""
    if debate_id in debates:
        return jsonify(debates[debate_id])
    else:
        return jsonify({
            'success': False,
            'error': '辩论不存在'
        }), 404


@app.route('/api/debates', methods=['GET'])
def list_debates():
    """列出历史辩论"""
    result = []
    for debate_id, debate in debates.items():
        result.append({
            'id': debate_id,
            'topic': debate['topic'],
            'debater1': debate['debater1'],
            'debater2': debate['debater2'],
            'status': debate['status']
        })
    # 最新的在前
    result.reverse()
    return jsonify({'debates': result})


@app.route('/api/debate/<debate_id>/share', methods=['POST'])
def generate_share_image(debate_id):
    """生成分享图片"""
    if debate_id not in debates:
        return jsonify({
            'success': False,
            'error': '辩论不存在'
        }), 404
    
    try:
        # 这里我们简化处理，返回一个占位符
        return jsonify({
            'success': True,
            'image_url': '#',
            'message': '分享图片功能开发中'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/debate/step', methods=['POST'])
def debate_step():
    """执行一轮辩论"""
    global debate_engine
    
    if not debate_engine:
        return jsonify({
            'success': False,
            'message': '请先开始辩论'
        })
    
    try:
        response = debate_engine.next_round()
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'执行失败: {str(e)}'
        })

@app.route('/api/debate/end', methods=['POST'])
def end_debate():
    """结束辩论"""
    global debate_engine
    
    debate_engine = None
    
    return jsonify({
        'success': True,
        'message': '辩论已结束'
    })

@app.route('/api/share', methods=['POST'])
def generate_share():
    """生成分享图片"""
    try:
        data = request.json
        debate = data.get('debate')
        style = data.get('style', 'wechat')
        
        from src.share import ShareGenerator
        generator = ShareGenerator()
        image_path = generator.create_share_image(debate, style)
        
        return jsonify({
            'success': True,
            'image_path': image_path,
            'message': '分享图片已生成'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'生成失败: {str(e)}'
        })

@app.route('/export')
def export_page():
    """导出页面"""
    return render_template('export.html')

@app.route('/api/export/formats', methods=['GET'])
def get_export_formats():
    """获取支持的导出格式"""
    formats = list_export_formats()
    return jsonify({'formats': formats})

@app.route('/api/export', methods=['POST'])
def handle_export():
    """处理导出请求"""
    try:
        data = request.json
        
        format_name = data.get('format', 'chatlab')
        chat_name = data.get('chat_name', '聊天记录')
        message_filter = data.get('message_filter', 'all')
        time_range = data.get('time_range', 'all')
        theme = data.get('theme', 'light')
        
        # 获取好友的聊天记录
        friends = friend_manager.list_friends()
        if not friends:
            return jsonify({
                'success': False,
                'error': '没有可导出的聊天记录，请先创建好友'
            })
        
        # 使用第一个好友的聊天记录作为示例
        # 在实际使用中，应该根据用户选择的好友来导出
        sample_messages = [
            {
                "sender": "用户1",
                "content": "你好！",
                "timestamp": "2024-01-15 10:00:00"
            },
            {
                "sender": "用户2",
                "content": "你好啊，最近怎么样？",
                "timestamp": "2024-01-15 10:01:00"
            },
            {
                "sender": "用户1",
                "content": "挺好的，你呢？",
                "timestamp": "2024-01-15 10:02:00"
            },
            {
                "sender": "用户2",
                "content": "我也挺好的，周末有什么计划吗？",
                "timestamp": "2024-01-15 10:03:00"
            },
            {
                "sender": "用户1",
                "content": "打算去看看电影，有推荐吗？",
                "timestamp": "2024-01-15 10:04:00"
            }
        ]
        
        # 导出目录
        export_dir = Path(__file__).parent.parent.parent / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # 执行导出
        output_path = export_chat(
            messages=sample_messages,
            output_dir=export_dir,
            format_name=format_name,
            chat_name=chat_name,
            theme=theme
        )
        
        if output_path:
            return jsonify({
                'success': True,
                'filename': output_path.name,
                'filepath': str(output_path),
                'format': format_name,
                'message': f'成功导出为 {format_name.upper()} 格式'
            })
        else:
            return jsonify({
                'success': False,
                'error': '导出失败，请检查格式是否支持'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'导出失败: {str(e)}'
        })

@app.route('/api/export/preview', methods=['GET'])
def get_export_preview():
    """获取导出预览数据"""
    # 返回示例消息用于预览
    sample_messages = [
        {
            "sender": "用户1",
            "content": "你好！",
            "timestamp": "2024-01-15 10:00:00",
            "time": "10:00"
        },
        {
            "sender": "用户2",
            "content": "你好啊，最近怎么样？",
            "timestamp": "2024-01-15 10:01:00",
            "time": "10:01"
        },
        {
            "sender": "用户1",
            "content": "挺好的，你呢？",
            "timestamp": "2024-01-15 10:02:00",
            "time": "10:02"
        }
    ]
    
    return jsonify({'messages': sample_messages})

@app.route('/api/export/download', methods=['GET'])
def download_export():
    """下载导出的文件"""
    from flask import send_file
    
    file_path = request.args.get('path', '')
    file_path = Path(file_path)
    
    if not file_path.exists():
        return jsonify({'error': '文件不存在'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=file_path.name
    )

@app.route('/api/chatlogs', methods=['GET'])
def list_chatlogs():
    """列出聊天记录文件"""
    chatlogs_dir = Path(config['data']['chatlogs_dir'])
    files = []
    
    if chatlogs_dir.exists():
        for f in chatlogs_dir.iterdir():
            if f.is_file() and f.suffix in ['.json', '.html', '.txt']:
                files.append({
                    'name': f.name,
                    'path': str(f),
                    'size': f.stat().st_size,
                    'mtime': f.stat().st_mtime
                })
    
    return jsonify(files)

@app.route('/api/avatars', methods=['GET'])
def list_avatars():
    """列出已创建的 AI 角色"""
    avatars_dir = Path(config['data']['avatars_dir'])
    avatars = []
    
    if avatars_dir.exists():
        for f in avatars_dir.iterdir():
            if f.is_dir():
                avatars.append({
                    'name': f.name,
                    'path': str(f)
                })
    
    return jsonify(avatars)

@app.route('/weflow')
def weflow_page():
    """WeFlow集成页面"""
    return render_template('weflow.html')

@app.route('/api/weflow/status', methods=['GET'])
def get_weflow_status():
    """获取WeFlow状态"""
    status = weflow_integrator.check_weflow()
    return jsonify(status)

@app.route('/api/weflow/sessions', methods=['GET'])
def get_weflow_sessions_api():
    """获取WeFlow会话列表"""
    try:
        sessions = get_weflow_sessions()
        return jsonify({
            'success': True,
            'sessions': sessions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/weflow/import', methods=['POST'])
def import_from_weflow():
    """从WeFlow导入聊天记录"""
    try:
        data = request.json
        talker = data.get('talker')

        if not talker:
            return jsonify({
                'success': False,
                'error': '缺少会话ID'
            })

        # 获取聊天历史
        messages = get_weflow_chat_history(talker, limit=500)

        if not messages:
            return jsonify({
                'success': False,
                'error': '未找到聊天记录'
            })

        # 保存到临时文件
        temp_file = Path(config['data']['chatlogs_dir']) / f"weflow_{talker}.json"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

        # 获取联系人名称
        contact_info = weflow_integrator.get_contact_info(talker)
        name = contact_info.get('nickName', contact_info.get('remark', talker)) if contact_info else talker

        # 创建好友
        profile = friend_manager.import_friend(temp_file, name, platform='wechat', min_messages=10)

        return jsonify({
            'success': True,
            'message': f'成功导入 {name} 的聊天记录',
            'name': name,
            'message_count': len(messages)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/weflow/launch', methods=['POST'])
def launch_weflow():
    """启动WeFlow"""
    try:
        success = weflow_integrator.launch_weflow()
        return jsonify({
            'success': success,
            'message': 'WeFlow已启动' if success else '启动失败'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def main():
    global debate_engine

    # 初始化辩论引擎
    debate_engine = DebateEngine()

    host = config['web']['host']
    port = config['web']['port']

    print(f"🚀 FriendBattle 启动于 http://{host}:{port}")
    print(f"🔗 WeFlow集成: {weflow_integrator._weflow_path or '未找到WeFlow'}")
    app.run(host=host, port=port, debug=True)

if __name__ == '__main__':
    main()
