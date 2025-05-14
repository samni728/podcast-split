import os
import shutil
import gradio as gr
from pathlib import Path
from podcast_diarize import run_diarization, export_tracks

TEMP_DIR = os.path.join(os.getcwd(), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)

def process(audio_file, output_types, progress=gr.Progress()):
    # audio_file 是上传文件的本地路径
    audio_path = Path(audio_file)
    base_name = audio_path.stem
    out_dir = os.path.join(TEMP_DIR, base_name)
    os.makedirs(out_dir, exist_ok=True)
    temp_audio_path = os.path.join(out_dir, audio_path.name)
    # 复制上传的临时文件到目标目录
    shutil.copy(audio_file, temp_audio_path)
    progress(0.1, desc="正在进行说话人分离...")
    # 分离
    result, json_path = run_diarization(temp_audio_path, out_dir)
    progress(0.6, desc="正在导出音轨...")
    export_tracks(temp_audio_path, result, out_dir, output_types)
    progress(0.9, desc="准备输出...")
    # 输出文件路径
    outputs = []
    for idx, ext in enumerate(output_types):
        track_path = os.path.join(out_dir, f"output_{chr(65+idx)}.{ext}")
        outputs.append(track_path)
    # 只保留前两个音轨（A、B）
    audio_a = outputs[0] if len(outputs) > 0 else None
    audio_b = outputs[1] if len(outputs) > 1 else None
    return (
        audio_a, audio_b, json_path
    )

def get_audio_name(file):
    if file is None:
        return "未选择文件"
    return Path(file).stem

def build_ui():
    with gr.Blocks(title="播客分轨自动化 WebUI") as demo:
        gr.Markdown("# 🎙️ 播客一男一女分轨自动化工具 WebUI\n上传音频，选择输出格式，一键分离！")
        with gr.Row():
            audio_input = gr.File(label="上传音频文件 (mp3/wav)", type="filepath")
            output_type = gr.Radio(["mp3", "wav", "mp3+wav"], value="mp3", label="输出格式")
        start_btn = gr.Button("开始分离")
        with gr.Row():
            audio_a = gr.Audio(label="音轨A（可播放/下载）", interactive=False)
            audio_b = gr.Audio(label="音轨B（可播放/下载）", interactive=False)
        json_file = gr.File(label="分离时间轴JSON", interactive=False)
        
        def output_type_list(val):
            if val == "mp3": return ["mp3"]
            if val == "wav": return ["wav"]
            return ["mp3", "wav"]
        
        start_btn.click(
            fn=process,
            inputs=[audio_input, output_type],
            outputs=[audio_a, audio_b, json_file],
            preprocess=False,
            postprocess=False
        )
    return demo

if __name__ == "__main__":
    ui = build_ui()
    ui.launch(server_port=7999) 