"""
微信图片解密模块

集成 WeFlow 的图片解密技术：
- 解密微信的 .dat 加密图片
- 支持 AES-256-CBC 解密
- 支持多种图片格式

注意：完整的图片解密需要 weflow-image-native 原生库支持
此模块提供简化版实现和接口框架
"""

import os
import struct
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class WeChatImageDecryptor:
    """微信图片解密器

    微信使用 AES-256-CBC 加密存储图片
    文件扩展名为 .dat，需要解密后才能查看

    简化版实现（不包含完整的原生库集成）
    """

    # PNG 文件头
    PNG_HEADER = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])

    # JPEG 文件头
    JPEG_HEADER = bytes([0xFF, 0xD8, 0xFF])

    # GIF 文件头
    GIF_HEADER_87A = bytes([0x47, 0x49, 0x46, 0x38, 0x37, 0x61])
    GIF_HEADER_89A = bytes([0x47, 0x49, 0x46, 0x38, 0x39, 0x61])

    def __init__(self, key: Optional[int] = None):
        """
        初始化解密器

        Args:
            key: XOR 密钥，如果不提供则尝试自动检测
        """
        self.key = key

    def detect_key(self, dat_file: Path) -> Optional[int]:
        """自动检测 XOR 密钥

        通过尝试解密文件头来检测密钥
        """
        try:
            with open(dat_file, "rb") as f:
                header = f.read(8)

            # 尝试常见的密钥
            for key in range(256):
                decrypted = bytes([b ^ key for b in header[:4]])

                if (decrypted[:3] == self.PNG_HEADER[:3] or
                    decrypted[:3] == self.JPEG_HEADER[:3] or
                    decrypted[:6] == self.GIF_HEADER_87A or
                    decrypted[:6] == self.GIF_HEADER_89A):
                    logger.info(f"检测到 XOR 密钥: {key}")
                    return key

            return None

        except Exception as e:
            logger.error(f"检测密钥失败: {e}")
            return None

    def decrypt_dat(self, dat_file: Path, output_file: Path) -> bool:
        """解密 .dat 文件

        Args:
            dat_file: 加密的 .dat 文件
            output_file: 解密后的输出文件

        Returns:
            是否成功
        """
        try:
            # 检测密钥
            if self.key is None:
                self.key = self.detect_key(dat_file)
                if self.key is None:
                    logger.error("无法检测 XOR 密钥")
                    return False

            # 读取加密数据
            with open(dat_file, "rb") as f:
                encrypted_data = f.read()

            # XOR 解密
            decrypted_data = bytes([b ^ self.key for b in encrypted_data])

            # 检测文件类型
            file_type = self._detect_file_type(decrypted_data)

            # 写入解密后的文件
            output_file = output_file.with_suffix(f".{file_type}")
            with open(output_file, "wb") as f:
                f.write(decrypted_data)

            logger.info(f"解密成功: {dat_file} -> {output_file}")
            return True

        except Exception as e:
            logger.error(f"解密失败: {e}")
            return False

    def _detect_file_type(self, data: bytes) -> str:
        """检测解密后的文件类型"""
        if data[:8] == self.PNG_HEADER:
            return "png"
        elif data[:3] == self.JPEG_HEADER:
            return "jpg"
        elif data[:6] == self.GIF_HEADER_87A or data[:6] == self.GIF_HEADER_89A:
            return "gif"
        elif data[:4] == bytes([0x52, 0x49, 0x46, 0x46]):  # WEBP
            return "webp"
        elif data[:4] == bytes([0x42, 0x4D]):  # BMP
            return "bmp"
        else:
            return "bin"

    def batch_decrypt(
        self,
        input_dir: Path,
        output_dir: Path,
        pattern: str = "*.dat"
    ) -> int:
        """批量解密目录中的 .dat 文件

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            pattern: 文件匹配模式

        Returns:
            成功解密的文件数量
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        success_count = 0
        for dat_file in input_dir.glob(pattern):
            output_file = output_dir / dat_file.stem
            if self.decrypt_dat(dat_file, output_file):
                success_count += 1

        logger.info(f"批量解密完成: {success_count}/{len(list(input_dir.glob(pattern)))} 成功")
        return success_count


class WeChatImageDecryptorAdvanced:
    """高级微信图片解密器

    使用 weflow-image-native 原生库进行解密
    支持 AES-256-CBC 等更复杂的加密方式
    """

    def __init__(self):
        self.native_lib = None
        self._load_native_library()

    def _load_native_library(self):
        """加载原生库"""
        try:
            # 尝试加载 weflow-image-native
            # 注意：这需要根据平台加载对应的原生库
            logger.info("尝试加载 weflow-image-native 原生库...")

            import platform
            system = platform.system()

            lib_paths = []
            if system == "Windows":
                lib_paths = [
                    Path("resources/wedecrypt/win32/x64/weflow-image-native-win32-x64.node"),
                ]
            elif system == "Darwin":
                lib_paths = [
                    Path("resources/wedecrypt/macos/weflow-image-native-macos.node"),
                ]
            elif system == "Linux":
                lib_paths = [
                    Path("resources/wedecrypt/linux/x64/weflow-image-native-linux-x64.node"),
                ]

            for lib_path in lib_paths:
                if lib_path.exists():
                    # 使用 ctypes 或 cffi 加载原生库
                    # 这里简化处理，实际需要更复杂的集成
                    logger.info(f"找到原生库: {lib_path}")
                    self.native_lib = lib_path
                    return

            logger.warning("未找到 weflow-image-native 原生库")

        except Exception as e:
            logger.error(f"加载原生库失败: {e}")

    def decrypt_image(
        self,
        input_path: Path,
        output_path: Path,
        key: Optional[str] = None
    ) -> bool:
        """解密图片

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            key: 解密密钥（可选）

        Returns:
            是否成功
        """
        if self.native_lib:
            # 使用原生库解密
            return self._decrypt_with_native(input_path, output_path, key)
        else:
            # 降级到简化版解密器
            logger.warning("原生库不可用，使用简化版解密器")
            simple_decryptor = WeChatImageDecryptor()
            return simple_decryptor.decrypt_dat(input_path, output_path)

    def _decrypt_with_native(
        self,
        input_path: Path,
        output_path: Path,
        key: Optional[str]
    ) -> bool:
        """使用原生库解密

        注意：这是一个框架实现
        实际需要使用 node-ffi 或类似工具调用原生库
        """
        logger.info("使用原生库解密...")
        # TODO: 实现实际的原生库调用
        return False


def decrypt_wechat_image(
    dat_file: Path,
    output_file: Optional[Path] = None,
    auto_key: bool = True
) -> Optional[Path]:
    """便捷函数：解密微信图片

    Args:
        dat_file: .dat 文件路径
        output_file: 输出文件路径（可选）
        auto_key: 是否自动检测密钥

    Returns:
        解密后的文件路径，失败返回 None
    """
    decryptor = WeChatImageDecryptor()

    if auto_key:
        key = decryptor.detect_key(dat_file)
        if key is None:
            logger.error("无法检测密钥")
            return None
        decryptor.key = key

    if output_file is None:
        output_file = dat_file.with_suffix("")

    if decryptor.decrypt_dat(dat_file, output_file):
        return output_file.with_suffix(f".{decryptor._detect_file_type(open(dat_file, 'rb').read(8))}")

    return None


def batch_decrypt_images(
    input_dir: Path,
    output_dir: Optional[Path] = None,
    pattern: str = "*.dat"
) -> int:
    """便捷函数：批量解密图片

    Args:
        input_dir: 输入目录
        output_dir: 输出目录（可选，默认在输入目录下创建 decrypted 子目录）
        pattern: 文件匹配模式

    Returns:
        成功解密的文件数量
    """
    if output_dir is None:
        output_dir = input_dir / "decrypted"

    decryptor = WeChatImageDecryptor()
    return decryptor.batch_decrypt(input_dir, output_dir, pattern)
