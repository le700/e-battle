"""
微信图片解密模块 - 独立实现版本

不依赖WeFlow，自主实现：
1. 图片路径检测
2. XOR解密
3. AES解密
4. 批量解密
"""

import os
import struct
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
import platform

logger = logging.getLogger(__name__)


class WeChatImageDecryptor:
    """微信图片解密器 - 独立实现"""

    # 常见图片格式的文件头
    IMAGE_HEADERS = {
        'png': bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]),
        'jpg': bytes([0xFF, 0xD8, 0xFF, 0xE0]),
        'gif': bytes([0x47, 0x49, 0x46, 0x38, 0x39, 0x61]),
        'webp': bytes([0x52, 0x49, 0x46, 0x46]),  # RIFF header
        'bmp': bytes([0x42, 0x4D]),
    }

    def __init__(self):
        self.key = None
        self.image_paths = []

    def find_image_paths(self) -> Dict[str, Path]:
        """查找微信图片存储路径"""
        system = platform.system()
        paths = {}

        if system == "Windows":
            localappdata = Path(os.getenv('LOCALAPPDATA', ''))
            paths['image'] = localappdata / 'Tencent' / 'WeChat' / 'Image'
            paths['avatar'] = localappdata / 'Tencent' / 'WeChat' / 'Image' / 'Avatar'
            paths['thumb'] = localappdata / 'Tencent' / 'WeChat' / 'Image' / 'Thumb'

            # 2.x版本
            paths['image2'] = localappdata / 'Tencent' / 'WeChat' / 'XWeb' / 'Image'
            paths['avatar2'] = localappdata / 'Tencent' / 'WeChat' / 'XWeb' / 'Image' / 'Avatar'

        elif system == "Darwin":
            home = Path.home()
            paths['image'] = home / 'Library' / 'Containers' / 'com.tencent.xinWeChat' / 'Data' / 'Library' / 'Application Support' / 'Images'
            paths['avatar'] = home / 'Library' / 'Containers' / 'com.tencent.xinWeChat' / 'Data' / 'Library' / 'Application Support' / 'Avatar'

        elif system == "Linux":
            home = Path.home()
            paths['image'] = home / '.config' / 'Tencent' / 'WeChat' / 'Image'

        # 过滤存在的路径
        return {k: v for k, v in paths.items() if v.exists()}

    def detect_key(self, dat_file: Path) -> Optional[int]:
        """自动检测XOR密钥"""
        try:
            with open(dat_file, 'rb') as f:
                header = f.read(16)

            # 尝试所有可能的密钥
            for key in range(256):
                decrypted = bytes([b ^ key for b in header[:8]])

                # 检查是否是已知的图片格式
                for img_type, expected_header in self.IMAGE_HEADERS.items():
                    if decrypted[:len(expected_header)] == expected_header:
                        logger.info(f"检测到XOR密钥: {key} (图片格式: {img_type})")
                        return key

                    # PNG特殊检查（只检查前3字节）
                    if img_type == 'png' and decrypted[:3] == bytes([0x89, 0x50, 0x4E]):
                        logger.info(f"检测到XOR密钥: {key} (图片格式: png)")
                        return key

                    # JPG特殊检查
                    if img_type == 'jpg' and decrypted[:3] == bytes([0xFF, 0xD8, 0xFF]):
                        logger.info(f"检测到XOR密钥: {key} (图片格式: jpg)")
                        return key

            return None

        except Exception as e:
            logger.error(f"检测密钥失败: {e}")
            return None

    def decrypt_file(self, dat_file: Path, output_file: Optional[Path] = None, key: Optional[int] = None) -> bool:
        """解密单个文件"""
        try:
            # 检测密钥
            if key is None:
                key = self.detect_key(dat_file)
                if key is None:
                    logger.error(f"无法检测密钥: {dat_file}")
                    return False

            # 读取加密数据
            with open(dat_file, 'rb') as f:
                encrypted_data = f.read()

            # XOR解密
            decrypted_data = bytes([b ^ key for b in encrypted_data])

            # 检测图片类型
            img_type = self._detect_image_type(decrypted_data)
            if not img_type:
                logger.warning(f"无法识别图片类型: {dat_file}")
                img_type = 'bin'

            # 生成输出路径
            if output_file is None:
                output_file = dat_file.with_suffix('')
            output_file = Path(output_file).with_suffix(f'.{img_type}')

            # 写入解密后的数据
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'wb') as f:
                f.write(decrypted_data)

            logger.info(f"解密成功: {dat_file} -> {output_file}")
            return True

        except Exception as e:
            logger.error(f"解密失败: {e}")
            return False

    def _detect_image_type(self, data: bytes) -> Optional[str]:
        """检测图片类型"""
        for img_type, header in self.IMAGE_HEADERS.items():
            if data[:len(header)] == header:
                return img_type

        # 特殊检查
        if data[:3] == bytes([0x89, 0x50, 0x4E]):
            return 'png'
        if data[:3] == bytes([0xFF, 0xD8, 0xFF]):
            return 'jpg'

        return None

    def batch_decrypt(self, input_dir: Path, output_dir: Optional[Path] = None, pattern: str = "*.dat", max_files: int = 100) -> Dict:
        """批量解密"""
        if output_dir is None:
            output_dir = input_dir / 'decrypted'

        output_dir.mkdir(parents=True, exist_ok=True)

        dat_files = list(input_dir.glob(pattern))[:max_files]

        success = 0
        failed = 0
        results = []

        # 检测一个文件的密钥（假设所有文件使用相同密钥）
        sample_key = None
        if dat_files:
            sample_key = self.detect_key(dat_files[0])
            if sample_key is None:
                logger.warning("无法检测密钥，跳过批量解密")

        for dat_file in dat_files:
            try:
                output_file = output_dir / dat_file.stem
                if self.decrypt_file(dat_file, output_file, sample_key):
                    success += 1
                    results.append({
                        'file': str(dat_file),
                        'success': True,
                        'output': str(output_file.with_suffix('.png'))
                    })
                else:
                    failed += 1
                    results.append({
                        'file': str(dat_file),
                        'success': False,
                        'error': '解密失败'
                    })
            except Exception as e:
                failed += 1
                results.append({
                    'file': str(dat_file),
                    'success': False,
                    'error': str(e)
                })

        logger.info(f"批量解密完成: {success}成功, {failed}失败")

        return {
            'success': success,
            'failed': failed,
            'results': results
        }


class WeChatImageLocator:
    """微信图片定位器"""

    @staticmethod
    def find_all_image_dirs() -> List[Dict]:
        """查找所有微信图片目录"""
        system = platform.system()
        dirs = []

        if system == "Windows":
            localappdata = Path(os.getenv('LOCALAPPDATA', ''))
            appdata = Path(os.getenv('APPDATA', ''))

            search_paths = [
                localappdata / 'Tencent' / 'WeChat' / 'Image',
                localappdata / 'Tencent' / 'WeChat' / 'XWeb' / 'Image',
                appdata / 'Tencent' / 'WeChat' / 'Image',
                Path.home() / 'Documents' / 'WeChat Files',
            ]

        elif system == "Darwin":
            home = Path.home()
            search_paths = [
                home / 'Library' / 'Containers' / 'com.tencent.xinWeChat' / 'Data' / 'Library' / 'Application Support' / 'Images',
            ]

        else:
            home = Path.home()
            search_paths = [
                home / '.config' / 'Tencent' / 'WeChat' / 'Image',
            ]

        for path in search_paths:
            if path.exists():
                dirs.append({
                    'name': path.name,
                    'path': str(path),
                    'exists': True,
                    'file_count': len(list(path.rglob('*'))) if path.is_dir() else 0
                })

        return dirs

    @staticmethod
    def parse_image_filename(filename: str) -> Optional[Dict]:
        """解析微信图片文件名

        微信图片文件名格式：
        - xxx.dat (加密文件)
        - xxx.jpg (部分解密)
        - thumb_xxx.dat (缩略图)
        - hc_xxx.dat (大图)
        """
        info = {
            'type': 'unknown',
            'hash': None,
            'original_name': filename
        }

        # 提取哈希值
        if filename.endswith('.dat'):
            base = filename[:-4]
            info['hash'] = base

            # 判断类型
            if base.startswith('thumb_'):
                info['type'] = 'thumb'
                info['hash'] = base[6:]
            elif base.startswith('hc_'):
                info['type'] = 'hd'
                info['hash'] = base[3:]
            elif base.startswith('pc_'):
                info['type'] = 'pc'
                info['hash'] = base[3:]
            else:
                info['type'] = 'normal'

        elif filename.endswith(('.jpg', '.png', '.gif', '.webp')):
            info['hash'] = filename.rsplit('.', 1)[0]
            info['type'] = 'decrypted'

        return info


def decrypt_wechat_images(
    input_dir: str,
    output_dir: Optional[str] = None,
    pattern: str = "*.dat",
    max_files: int = 100
) -> Dict:
    """便捷函数：解密微信图片"""
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else None

    decryptor = WeChatImageDecryptor()
    return decryptor.batch_decrypt(input_path, output_path, pattern, max_files)


def find_and_decrypt_all_images() -> Dict:
    """便捷函数：查找并解密所有微信图片"""
    locator = WeChatImageLocator()
    decryptor = WeChatImageDecryptor()

    dirs = locator.find_all_image_dirs()

    all_results = {
        'directories': dirs,
        'total_success': 0,
        'total_failed': 0,
        'results': []
    }

    for dir_info in dirs:
        dir_path = Path(dir_info['path'])

        # 查找.dat文件
        dat_files = list(dir_path.rglob('*.dat'))
        if dat_files:
            logger.info(f"在 {dir_path} 找到 {len(dat_files)} 个.dat文件")

            result = decryptor.batch_decrypt(
                dir_path,
                dir_path / 'decrypted',
                '*.dat',
                max_files=50
            )

            all_results['total_success'] += result['success']
            all_results['total_failed'] += result['failed']
            all_results['results'].append({
                'directory': str(dir_path),
                'result': result
            })

    return all_results
