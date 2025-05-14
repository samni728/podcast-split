# Podcast 播客分轨自动化工具（针对 NotebookLM）

> 目前大概 90% 以上的识别能力

本工具可自动将一男一女播客音频分离为独立音轨，支持命令行交互和 API 参数调用，极致高效，无需采样、样本、embedding。

## 功能特点

- 一键自动分离两位说话人音轨（基于 pyannote.audio 3.x pipeline，num_speakers=2）
- 支持 mp3/wav 输入，自动输出 output_A.mp3、output_B.mp3
- 支持菜单交互与命令行参数调用，适合自动化和 API 集成
- 全流程无需采样、样本、embedding，极致高效
- 依赖极简，环境易部署

## 推荐环境配置（conda）

建议优先使用 conda 创建独立环境，避免依赖冲突。

```bash
# 1. 创建并激活 conda 环境（推荐 Python 3.8-3.10）
conda create -n podcast-split python=3.9 -y
conda activate podcast-split

# 2. 安装 ffmpeg（音频处理必需）
conda install -c conda-forge ffmpeg

# 3. 安装项目依赖
pip install -r requirements.txt
```

## 依赖安装（pip 方式，补充）

如无 conda，也可直接用 pip 安装（需提前自行安装 ffmpeg）：

```bash
pip install -r requirements.txt
```

## HuggingFace 模型授权

1. 注册并登录 [Hugging Face](https://huggingface.co/) 账号
2. 访问 [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) 申请模型访问权限
3. 获批后，在 [Settings - Tokens](https://huggingface.co/settings/tokens) 创建访问令牌
4. 设置环境变量：

- **Mac/Linux (bash/zsh/conda)：**
  ```bash
  export HUGGINGFACE_TOKEN=你的token值
  ```
- **Windows (cmd)：**
  ```cmd
  set HUGGINGFACE_TOKEN=你的token值
  ```
- **Windows (PowerShell)：**
  ```powershell
  $env:HUGGINGFACE_TOKEN="你的token值"
  ```

设置后在同一终端窗口运行脚本即可。

## 使用方法

### 交互模式（推荐新手）

```bash
python podcast_diarize.py
```

- 按提示选择音频文件和输出格式，全自动完成分轨。

### 命令行参数模式（适合自动化/批量处理）

```bash
python podcast_diarize.py --audio_file 你的音频文件.mp3 --output mp3
```

- 支持 mp3/wav 输入，--output 可选 mp3、wav 或 mp3 wav（空格分隔）。

## 输出说明

- 输出文件位于与音频同名目录下，如 `output_A.mp3`、`output_B.mp3`
- 同时生成分离时间轴 `diarization_timeline.json`

## 依赖说明

详见 requirements.txt，核心依赖：

- pyannote.audio>=2.1.1（推荐 3.x）
- torch>=1.9.0
- pydub>=0.25.1
- huggingface_hub>=0.14.1

> **当前依赖仅支持 CPU 版本的 PyTorch。无需安装 CUDA/GPU 相关依赖。**

---

## Windows + CUDA + GPU 加速环境搭建（可选）

如你在 Win11 + NVIDIA 显卡（如 3090/4090）环境下，想用 GPU 加速推理，可参考以下步骤：

1. **创建 conda 环境（推荐 Python 3.9/3.10）**
   ```bash
   conda create -n podcast-cuda python=3.9 -y
   conda activate podcast-cuda
   ```
2. **安装 CUDA 版 PyTorch**
   ```bash
   # 以 CUDA 11.8 为例（推荐，兼容性好）
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
   > 如需 CUDA 12.x，可参考 PyTorch 官网选择合适的 wheel。
3. **安装其它依赖**
   ```bash
   pip install -r requirements.txt
   ```
4. **安装 ffmpeg（可用 conda 或下载 Windows 版）**
   ```bash
   conda install -c conda-forge ffmpeg
   ```
5. **设置 HuggingFace Token（cmd 示例）**
   ```cmd
   set HUGGINGFACE_TOKEN=你的token值
   ```
6. **运行脚本**
   ```bash
   python podcast_diarize.py
   ```

### 检查 GPU 是否可用

在 Python 里测试：

```python
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
```

如输出 True 和你的显卡型号，说明 GPU 可用。

### 常见问题

- 若遇到"CUDA 版本不兼容"或"DLL 加载失败"，请检查 CUDA 驱动和 torch 版本是否匹配。
- 只要你用的是 CUDA 版 torch，pyannote.audio 会自动用 GPU 推理，无需修改代码。

---

## 常见问题

- **未设置 HUGGINGFACE_TOKEN**：请按上文设置环境变量。
- **模型授权失败**：请确认已在 HuggingFace 获得 pyannote/speaker-diarization-3.1 访问权限。
- **分离精度有限**：开源模型对中文播客、多人插话等复杂场景有一定局限，建议保证音频清晰。
- **采样/样本/embedding**：本工具已彻底移除相关流程，无需采样、无需样本。

## 版本声明

- 当前版本为极简高效版，仅保留自动分轨核心功能，采样/样本/embedding 相关内容已全部移除。
- 适合播客分轨自动化和 API 集成。

## 项目未来计划与创新功能

### 1. 分轨+字幕辅助校正+可视化修正+再分轨

- 初步分轨后，自动生成 json 时间轴和两个人声轨音频。
- Whisper 自动转写生成带时间戳的字幕。
- WebUI 可视化展示字幕与分轨时间轴，用户可通过字幕快速定位分轨错误。
- 支持滑块/拖拽等交互，用户可直接调整某段的说话人归属（如将 A 片段中的一句话划给 B）。
- 校正后自动更新 json 时间轴。
- 支持用修正后的 json 再次导出精准分离的音轨。
- 结合 AI 自动与人工校正，极大提升分轨精度。

## WebUI（Gradio 图形界面）

本项目支持基于 Gradio 的 WebUI，方便用户通过网页上传音频、选择输出格式、分离音轨并下载结果。

### 依赖安装

请确保已安装 gradio：

```bash
pip install gradio>=4.0.0
```

### 启动 WebUI

```bash
python webui.py
```

默认端口为 7999，可通过 http://localhost:7999 访问。

### WebUI 功能

- 支持上传 podcast 音频（mp3/wav）
- 选择输出格式（mp3/wav/两者）
- 点击"开始分离"后显示进度条
- 分离完成后可在线播放/下载两个人声轨音频和 json 时间轴文件
- 所有输出文件默认生成到程序目录下的 temp/子目录，子目录名为上传音频文件名
