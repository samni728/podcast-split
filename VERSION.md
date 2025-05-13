# 播客一男一女分轨自动化工具 - 版本记录

## v1.0 版本 (2023 年 8 月 18 日)

### 版本说明

第一个稳定版本，包含完整的播客一男一女分轨自动化功能，实现了从音频文件到独立音轨的全流程自动处理。

### 核心功能

- 全自动说话人检测（基于 pyannote.audio 3.x）
- 自动生成 JSON 时间轴文件
- 智能目录检测和处理
- 高质量音轨分离（保持原始音量）
- 完善的错误处理和依赖检查

### 组件列表

1. `audio_diarization.py` - 自动说话人检测和时间轴生成
2. `split_audio.sh` - 基于时间轴的音频分轨处理
3. `requirements.txt` - 项目依赖管理
4. `README.md` - 项目文档

### 技术特点

- 采用 FFmpeg concat 分离器而非 filter_complex
- 全流程使用绝对路径，避免目录切换问题
- 分轨流程：提取说话段 → 生成静音段 → 拼接 → 转码

### 回滚到 v1.0 方法

如需回滚到此版本，请执行以下命令：

```bash
# 查看当前状态
git status

# 如有未提交更改，先处理（提交或stash）
git add .
git commit -m "保存当前更改"  # 或者 git stash

# 回滚到v1.0标签
git checkout v1.0
```

要返回到最新版本：

```bash
git checkout master
```
