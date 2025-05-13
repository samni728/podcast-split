#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
播客一男一女分轨自动化工具（极简高效版）

用法:
    python podcast_diarize.py
"""

import os
import sys
import json
import argparse
from pathlib import Path
from pyannote.audio.pipelines import SpeakerDiarization
from huggingface_hub import login
from pydub import AudioSegment

# 设置 HuggingFace 缓存目录到本地 model 文件夹
root_model_dir = os.path.join(os.getcwd(), "model")
os.makedirs(root_model_dir, exist_ok=True)
os.environ["HF_HOME"] = root_model_dir
os.environ["TRANSFORMERS_CACHE"] = root_model_dir
os.environ["HF_HUB_CACHE"] = root_model_dir

def list_audio_files():
    files = []
    for root, dirs, filenames in os.walk('.'):
        for f in filenames:
            if f.lower().endswith(('.mp3', '.wav')):
                files.append(os.path.relpath(os.path.join(root, f), '.'))
    return files

def menu_select_audio():
    files = list_audio_files()
    if not files:
        print("当前目录下未找到音频文件（mp3/wav）")
        sys.exit(1)
    print("请选择主音频文件：")
    for idx, f in enumerate(files):
        print(f"  {idx+1}. {f}")
    while True:
        sel = input(f"输入序号(1-{len(files)}): ")
        if sel.isdigit() and 1 <= int(sel) <= len(files):
            return files[int(sel)-1]
        print("无效选择，请重新输入。")

def menu_select_output():
    print("请选择输出格式：")
    print("  1. mp3")
    print("  2. wav")
    print("  3. mp3+wav")
    while True:
        sel = input("输入序号(1-3): ")
        if sel in ('1', '2', '3'):
            if sel == '1': return ['mp3']
            if sel == '2': return ['wav']
            if sel == '3': return ['mp3', 'wav']
        print("无效选择，请重新输入。")

def run_diarization(audio_file, out_dir):
    print(f"[模型缓存] 当前模型缓存目录: {os.environ.get('HF_HOME')}")
    hf_token = os.environ.get("HUGGINGFACE_TOKEN")
    if not hf_token:
        print("请先设置环境变量 HUGGINGFACE_TOKEN"); sys.exit(1)
    login(hf_token)
    pipeline = SpeakerDiarization.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=hf_token)
    diarization = pipeline(audio_file, num_speakers=2)
    result = {"speakers": {}}
    for segment, _, speaker in diarization.itertracks(yield_label=True):
        seg = {"start": round(segment.start, 3), "end": round(segment.end, 3)}
        if speaker not in result["speakers"]:
            result["speakers"][speaker] = []
        result["speakers"][speaker].append(seg)
    json_path = os.path.join(out_dir, "diarization_timeline.json")
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"[分离] 已输出分离结果到: {json_path}")
    return result, json_path

def export_tracks(audio_file, diarization_json, out_dir, output_types=['mp3']):
    audio = AudioSegment.from_file(audio_file)
    for idx, speaker in enumerate(diarization_json["speakers"]):
        segments = diarization_json["speakers"][speaker]
        track = AudioSegment.silent(duration=len(audio))
        for seg in segments:
            start_ms = int(seg["start"] * 1000)
            end_ms = int(seg["end"] * 1000)
            track = track.overlay(audio[start_ms:end_ms], position=start_ms)
        for ext in output_types:
            out_path = os.path.join(out_dir, f"output_{chr(65+idx)}.{ext}")
            track.export(out_path, format=ext)
            print(f"[导出] 已输出: {out_path}")

def interactive_main():
    print("==== 播客分轨自动化工具 交互模式 ====")
    audio_file = menu_select_audio()
    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    out_dir = os.path.join(os.getcwd(), base_name)
    os.makedirs(out_dir, exist_ok=True)
    output_types = menu_select_output()
    print(f"\n参数确认：")
    print(f"音频文件: {audio_file}")
    print(f"输出格式: {output_types}")
    if input("确认无误，开始处理？ (y/n) [y]: ").strip().lower() not in ('', 'y'):
        print("已取消。"); sys.exit(0)
    result, json_path = run_diarization(audio_file, out_dir)
    export_tracks(audio_file, result, out_dir, output_types)
    print("[完成] 全流程处理完成！")

def parse_args():
    parser = argparse.ArgumentParser(description="播客一男一女分轨自动化工具")
    parser.add_argument("--audio_file", help="要处理的音频文件")
    parser.add_argument("--output", nargs="*", choices=["mp3", "wav"], help="输出格式")
    return parser.parse_args()

def main():
    args = parse_args()
    if not args.audio_file:
        interactive_main()
        return
    audio_file = args.audio_file
    out_dir = os.path.splitext(os.path.basename(audio_file))[0]
    out_dir = os.path.join(os.getcwd(), out_dir)
    os.makedirs(out_dir, exist_ok=True)
    output_types = args.output if args.output else ['mp3']
    result, json_path = run_diarization(audio_file, out_dir)
    export_tracks(audio_file, result, out_dir, output_types)
    print("[完成] 全流程处理完成！")

if __name__ == "__main__":
    main() 