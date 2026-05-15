# 📦 FriendBattle 打包指南

## 目标

创建一个可以直接下载运行的 `.exe` 文件，用户双击即可启动。

## 打包方法

### 方法一：使用打包脚本（推荐）

**Windows 用户：**
```cmd
build_exe.bat
```

**Linux/Mac 用户（用于交叉编译）：**
```bash
bash build_exe.sh
```

### 方法二：手动打包

```cmd
pip install pyinstaller
pyinstaller pyinstaller.spec --clean
```

### 方法三：GitHub Actions 自动构建

已配置 GitHub Actions，每次 push 会自动构建：
- 构建产物位于 `dist/FriendBattle.exe`
- 可在 Release 页面下载

## 打包依赖

```bash
pip install pyinstaller
pip install -r requirements.txt
```

## 输出文件

```
dist/
├── FriendBattle.exe      # 主程序（约 500MB）
└── FriendBattle/         # 解压后的文件（可选）
```

## 使用方法

1. **下载** `FriendBattle.exe`
2. **双击运行**
3. **等待** 程序启动（首次启动可能需要下载模型）
4. **访问** http://localhost:3000

## 注意事项

### 首次启动

首次启动需要下载 AI 模型（约 2-5GB），请确保网络畅通。

### 性能要求

- **最低配置**：8GB 内存，6GB 显存
- **推荐配置**：16GB+ 内存，12GB+ 显存

### 防火墙提示

首次运行时，Windows 防火墙可能会提示允许网络访问，请点击"允许"。

## 构建问题排查

### 问题 1：缺少 DLL 文件

**解决方案**：确保安装了 Visual Studio 运行时库

### 问题 2：模型下载失败

**解决方案**：手动下载模型并放入 `models/` 目录

### 问题 3：启动后闪退

**解决方案**：运行 `FriendBattle.exe --debug` 查看错误日志

## 版本说明

| 版本 | 大小 | 说明 |
|------|------|------|
| Full | ~500MB | 包含所有依赖 |
| Lite | ~100MB | 需要联网下载模型 |

## 发布建议

### GitHub Release

1. 创建 Release
2. 上传 `FriendBattle.exe`
3. 添加更新说明

### 自动更新

建议使用 GitHub Release API 实现自动更新检查。

---

*打包指南创建于 2026-05-15*
