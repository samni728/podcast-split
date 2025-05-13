# 播客一男一女分轨自动化工具（极简高效版）

本工具可自动将一男一女播客音频分离为独立音轨，支持命令行交互和 API 参数调用，极致高效，无需采样、样本、embedding。

## 功能特点

- 一键自动分离两位说话人音轨（基于 pyannote.audio 3.x pipeline，num_speakers=2）
- 支持 mp3/wav 输入，自动输出 output_A.mp3、output_B.mp3
- 支持菜单交互与命令行参数调用，适合自动化和 API 集成
- 全流程无需采样、样本、embedding，极致高效
- 依赖极简，环境易部署

## 安装依赖

建议使用 Python 3.8-3.10。

```bash
pip install -r requirements.txt
```

> **注意：当前版本仅支持 CPU 推理，未做 CUDA/GPU 适配。如需 GPU 支持请关注后续版本。**

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

## 常见问题

- **未设置 HUGGINGFACE_TOKEN**：请按上文设置环境变量。
- **模型授权失败**：请确认已在 HuggingFace 获得 pyannote/speaker-diarization-3.1 访问权限。
- **分离精度有限**：开源模型对中文播客、多人插话等复杂场景有一定局限，建议保证音频清晰。
- **采样/样本/embedding**：本工具已彻底移除相关流程，无需采样、无需样本。

## 版本声明

- 当前版本为极简高效版，仅保留自动分轨核心功能，采样/样本/embedding 相关内容已全部移除。
- 适合播客分轨自动化和 API 集成。
