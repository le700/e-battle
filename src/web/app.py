#!/usr/bin/env python3
"""
FriendBattle Web Application
支持多 AI 提供商选择，内置微信导出
"""

import os
import sys
import json
import yaml
from pathlib import Path

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS

# 添加 src 目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from src.wechat_exporter import WeChatExporter, AIProvider
from src.clone import FriendCloner
from src.debate import DebateEngine, get_skill

app = Flask(__name__)
CORS(app)

# 加载配置
CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.yaml"
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 全局变量
debate_engine = None
ai_provider = None

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

@app.route('/api/debate/start', methods=['POST'])
def start_debate():
    """开始辩论"""
    global debate_engine
    
    try:
        data = request.json
        debater1 = data.get('debater1')
        debater2 = data.get('debater2')
        topic = data.get('topic')
        rounds = data.get('rounds', 5)
        strategy1 = data.get('strategy1', 'contrarian')
        strategy2 = data.get('strategy2', 'rational')
        
        debate_engine = DebateEngine(ai_provider=ai_provider)
        debate_engine.add_debater(debater1, skill=get_skill(strategy1)())
        debate_engine.add_debater(debater2, skill=get_skill(strategy2)())
        
        debate = debate_engine.start(topic, rounds)
        
        return jsonify({
            'success': True,
            'debate': debate,
            'message': '辩论已开始！'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'启动失败: {str(e)}'
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

def main():
    global debate_engine
    
    # 初始化辩论引擎
    debate_engine = DebateEngine()
    
    host = config['web']['host']
    port = config['web']['port']
    
    print(f"🚀 FriendBattle 启动于 http://{host}:{port}")
    app.run(host=host, port=port, debug=True)

if __name__ == '__main__':
    main()
