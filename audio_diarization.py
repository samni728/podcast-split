import sys
import os
import glob
import json
import subprocess
from pyannote.audio.pipelines import SpeakerDiarization
from huggingface_hub import login

# 自动检测当前目录下的第一个 mp3 或 wav 文件
AUDIO_FILE = None
for ext in ('*.wav', '*.mp3'):
    files = glob.glob(ext)
    if files:
        AUDIO_FILE = files[0]
        break
if AUDIO_FILE is None:
    print("未找到音频文件（mp3/wav）")
    sys.exit(1)

# 以音频文件名（不含扩展名）创建同名目录
base_name = os.path.splitext(os.path.basename(AUDIO_FILE))[0]
out_dir = os.path.join(os.getcwd(), base_name)
os.makedirs(out_dir, exist_ok=True)

# 设置 HuggingFace 缓存到根目录 model 文件夹
root_model_dir = os.path.join(os.getcwd(), "model")
os.makedirs(root_model_dir, exist_ok=True)
os.environ["HF_HOME"] = root_model_dir
os.environ["TRANSFORMERS_CACHE"] = root_model_dir
os.environ["HF_HUB_CACHE"] = root_model_dir

# 获取 HuggingFace Token
# 安全提示: 不要在代码中硬编码您的令牌，使用环境变量或用户输入
# 访问 https://huggingface.co/settings/tokens 获取您的令牌
if "HUGGINGFACE_TOKEN" in os.environ:
    HUGGINGFACE_TOKEN = os.environ["HUGGINGFACE_TOKEN"]
else:
    HUGGINGFACE_TOKEN = input("请输入您的 HuggingFace 令牌 (从 https://huggingface.co/settings/tokens 获取): ")
    if not HUGGINGFACE_TOKEN:
        print("错误: 需要 HuggingFace 令牌才能继续。")
        sys.exit(1)

# 登录 HuggingFace
print("登录 HuggingFace...")
login(HUGGINGFACE_TOKEN)

# 如果输入为 mp3，自动转为 wav，输出到音频目录
input_path = AUDIO_FILE
if AUDIO_FILE.lower().endswith('.mp3'):
    wav_path = os.path.join(out_dir, base_name + '.wav')
    if not os.path.exists(wav_path):
        print(f"检测到 mp3，自动转换为 wav: {wav_path}")
        cmd = [
            'ffmpeg', '-y', '-i', AUDIO_FILE,
            '-ar', '16000', '-ac', '1', wav_path
        ]
        subprocess.run(cmd, check=True)
    input_path = wav_path

# 加载 pyannote 3.x 预训练 pipeline
print("加载预训练模型...")
pipeline = SpeakerDiarization.from_pretrained("pyannote/speaker-diarization-3.1")

# 进行说话人分离，强制聚类为2类
print(f"正在处理: {input_path}")
diarization = pipeline(input_path, num_speakers=2)

# 整理输出为 { "speakers": { "SPEAKER_00": [...], "SPEAKER_01": [...] } }
result = {"speakers": {}}
for segment, track, speaker in diarization.itertracks(yield_label=True):
    seg = {"start": round(segment.start, 3), "end": round(segment.end, 3)}
    if speaker not in result["speakers"]:
        result["speakers"][speaker] = []
    result["speakers"][speaker].append(seg)

# 输出到同名目录下的 diarization_timeline.json
json_path = os.path.join(out_dir, "diarization_timeline.json")
with open(json_path, "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"已输出: {json_path}") 