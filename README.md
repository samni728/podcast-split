# 播客一男一女分轨自动化工具

这是一个专为播客制作者设计的自动化工具，用于将一男一女对话的播客音频分离成独立音轨。该工具支持自动检测说话人，生成时间轴，并输出高质量的独立音轨，整个流程完全自动化。

## 功能特点

- **全自动说话人检测**：使用 pyannote.audio 3.x 自动检测并区分两个说话人
- **自动生成时间轴**：无需手动创建 JSON 文件，系统自动分析并生成标准时间轴
- **智能目录处理**：自动检测音频和时间轴文件位置，无需手动指定路径
- **高质量音轨分离**：将每个说话人的部分提取为独立音轨，其余时间为静音
- **音量一致性保证**：分离后的音轨保持与原始音频相同的音量，无累加或阶梯变化
- **健壮错误处理**：完善的依赖检查和错误提示，确保流程稳定可靠

## 系统要求

- Python 3.8-3.10
- FFmpeg（用于音频处理）
- jq（用于 JSON 解析）
- bc（用于数学计算）
- 适用于 macOS、Linux（Windows 下需使用 WSL）

## 组件说明

### 1. `audio_diarization.py`

自动检测音频中的说话人并生成时间轴 JSON 文件。

**主要功能**：

- 自动检测当前目录下的音频文件（支持 mp3/wav）
- 使用 pyannote.audio 分析说话人，强制聚类为两人
- 输出标准格式的时间轴 JSON 文件到以音频文件名命名的目录
- 自动将 MP3 转换为 WAV（如需要）
- 模型缓存和输出文件管理

**使用方法**：

```bash
python audio_diarization.py
```

### 2. `split_audio.sh`

基于时间轴 JSON 文件将原始音频分割为独立音轨。

**主要功能**：

- 智能目录检测：自动查找音频和 JSON 文件
- 高质量分轨：确保音量与原始一致，无阶梯变化
- 解析 JSON 时间轴，生成说话段和静音段
- 使用 FFmpeg concat 分离器拼接为完整音轨
- 输出为高质量 MP3 格式

**使用方法**：

```bash
chmod +x split_audio.sh
./split_audio.sh
```

### 3. `requirements.txt`

项目依赖管理文件。

**主要依赖**：

- pyannote.audio>=2.1.1（及其相关依赖）
- 其他依赖会自动安装（torch、numpy 等）

**安装依赖**：

```bash
pip install -r requirements.txt
```

## 完整工作流程

1. **环境准备**

   ```bash
   pip install -r requirements.txt
   ```

2. **获取 HuggingFace Token**

   - 访问 https://huggingface.co/settings/tokens 获取令牌
   - 设置环境变量（推荐）或在运行时输入

   ```bash
   # 设置环境变量（推荐做法）
   export HUGGINGFACE_TOKEN=你的token值
   ```

3. **自动生成时间轴**

   ```bash
   python audio_diarization.py
   ```

   这将在当前目录检测音频，并在同名子目录下生成 `diarization_timeline.json`

4. **分轨处理**
   ```bash
   ./split_audio.sh
   ```
   这将自动检测音频和 JSON，并在 `<音频名>_split` 目录下生成分轨文件：
   - `output_speaker00_track.mp3`
   - `output_speaker01_track.mp3`

## 输出结构

```
原始目录/
  └── 音频文件.mp3
  └── 音频文件/                    (由audio_diarization.py生成)
       └── 音频文件.wav           (如原始为mp3)
       └── diarization_timeline.json
  └── 音频文件_split/              (由split_audio.sh生成)
       └── output_speaker00_track.mp3
       └── output_speaker01_track.mp3
```

## 常见问题与排错

1. **模型下载失败**

   - 检查网络连接
   - 确认 HuggingFace Token 是否有效
   - 查看模型缓存目录权限

2. **分轨音量异常**

   - 这是最常见的问题，但当前版本已通过 concat 方法解决
   - 如输出音量仍有问题，检查临时目录权限

3. **"找不到音频文件"错误**

   - 确认当前目录或子目录中存在 mp3/wav 文件
   - 文件名不应含有特殊字符

4. **依赖问题**
   - 确认已安装 FFmpeg、jq 和 bc
   - 对于 macOS：`brew install ffmpeg jq bc`
   - 对于 Ubuntu：`apt install ffmpeg jq bc`

## 扩展与自定义

- **支持多人**：修改 `audio_diarization.py` 中的 `num_speakers` 参数
- **调整输出质量**：修改 `split_audio.sh` 中的 FFmpeg 参数，如 `-q:a` 值
- **自定义分轨名称**：修改 `split_audio.sh` 中的输出文件名

## 技术实现细节

- 使用 pyannote.audio 3.x 进行说话人分离，基于预训练的深度学习模型
- 自动生成标准格式 JSON 时间轴文件，无需任何手动标注或辅助
- 采用 FFmpeg 的 concat 分离器而非 filter_complex，避免拼接过多片段时的缓冲问题
- 分轨流程为：提取说话段 → 生成静音段 → 合并为完整音轨 → 转码为 mp3
- 全流程采用绝对路径处理，避免目录切换导致的路径问题

## 许可与致谢

- 本工具仅用于合法音频处理
- 基于 pyannote.audio：https://github.com/pyannote/pyannote-audio
- 感谢 FFmpeg 项目提供强大的音频处理功能

## 安全提示

1. **不要在代码中硬编码敏感信息**

   - HuggingFace Token 等敏感信息应通过环境变量传递
   - 避免将含有敏感信息的代码提交到公开仓库

2. **使用 .gitignore**
   - 项目包含 `.gitignore` 文件，确保敏感文件不会被上传
   - 模型缓存和大型音频文件不应上传到 GitHub

## GitHub 使用说明

首次上传到 GitHub：

```bash
# 创建GitHub仓库后，添加远程仓库
git remote add origin https://github.com/您的用户名/仓库名.git

# 推送代码到GitHub
git push -u origin master
git push --tags
```

后续更新：

```bash
# 提交更改
git add .
git commit -m "更新说明"

# 推送到GitHub
git push

# 添加新版本标签
git tag -a v1.x -m "版本说明"
git push --tags
```
