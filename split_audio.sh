#!/bin/bash

# --- 智能检测音频和JSON所在目录 ---
find_work_dir() {
    # 检查当前目录
    local audio_file json_file
    audio_file=$(ls *.mp3 *.wav 2>/dev/null | head -n 1)
    json_file=$(ls diarization_timeline.json 2>/dev/null | head -n 1)
    if [[ -n "$audio_file" && -n "$json_file" ]]; then
        echo "$(pwd)"
        return
    fi
    # 检查一级子目录
    for d in */; do
        [ -d "$d" ] || continue
        cd "$d"
        audio_file=$(ls *.mp3 *.wav 2>/dev/null | head -n 1)
        json_file=$(ls diarization_timeline.json 2>/dev/null | head -n 1)
        if [[ -n "$audio_file" && -n "$json_file" ]]; then
            echo "$(pwd)"
            cd - >/dev/null
            return
        fi
        cd - >/dev/null
    done
    echo ""
}

WORK_DIR=$(find_work_dir)
if [ -z "$WORK_DIR" ]; then
    echo "Error: 当前目录及一级子目录下未找到音频文件（mp3/wav）和 diarization_timeline.json。"
    exit 1
fi

cd "$WORK_DIR"
echo "工作目录: $(pwd)"

# --- 自动检测音频文件（支持 mp3/wav） ---
AUDIO_FILE=$(ls *.mp3 *.wav 2>/dev/null | head -n 1)
if [ -z "$AUDIO_FILE" ]; then
    echo "Error: 未找到音频文件（mp3/wav）"
    exit 1
fi
AUDIO_FILE="$WORK_DIR/$AUDIO_FILE"  # 使用绝对路径
BASENAME=$(basename "$AUDIO_FILE" | sed 's/\.[^.]*$//')
echo "音频文件: $AUDIO_FILE"

JSON_FILE="$WORK_DIR/diarization_timeline.json"   # 使用绝对路径
if [ ! -f "$JSON_FILE" ]; then
    echo "Error: JSON file '$JSON_FILE' not found."
    exit 1
fi
echo "JSON文件: $JSON_FILE"

# --- 检查依赖 ---
for cmd in ffmpeg jq ffprobe bc; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: $cmd is not installed."
        exit 1
    fi
done

# --- 获取音频属性 ---
TOTAL_DURATION=$(ffprobe -i "$AUDIO_FILE" -show_entries format=duration -v quiet -of csv="p=0")
AUDIO_RATE=$(ffprobe -i "$AUDIO_FILE" -show_entries stream=sample_rate -select_streams a:0 -v quiet -of csv="p=0")
AUDIO_CHANNELS=$(ffprobe -i "$AUDIO_FILE" -show_entries stream=channels -select_streams a:0 -v quiet -of csv="p=0")
echo "音频时长: ${TOTAL_DURATION}秒, 采样率: ${AUDIO_RATE}Hz, 声道数: $AUDIO_CHANNELS"

if [ "$AUDIO_CHANNELS" -eq 1 ]; then
    ANULLSRC_CHANNEL_OPT="cl=mono"
elif [ "$AUDIO_CHANNELS" -eq 2 ]; then
    ANULLSRC_CHANNEL_OPT="cl=stereo"
else
    echo "Error: Unsupported number of audio channels (${AUDIO_CHANNELS})"
    exit 1
fi

# --- 输出目录 ---
OUTDIR="$WORK_DIR/${BASENAME}_split"
mkdir -p "$OUTDIR"
TMPDIR="$OUTDIR/tmp"
rm -rf "$TMPDIR"
mkdir -p "$TMPDIR"
echo "输出目录: $OUTDIR, 临时目录: $TMPDIR"

# --- 处理函数 ---
process_speaker() {
    local SPK=$1
    local SEGMENTS="$TMPDIR/segments_${SPK}.txt"
    > "$SEGMENTS"  # 清空segments文件
    
    local IDX=0
    local LAST_END=0
    
    # 读取说话区间
    COUNT=$(jq ".speakers.${SPK} | length" "$JSON_FILE")
    echo "$SPK 说话片段数: $COUNT"
    
    for ((i=0;i<$COUNT;i++)); do
        START=$(jq -r ".speakers.${SPK}[$i].start" "$JSON_FILE")
        END=$(jq -r ".speakers.${SPK}[$i].end" "$JSON_FILE")
        
        # 静音段
        if (( $(echo "$START > $LAST_END" | bc -l) )); then
            DUR_SIL=$(awk "BEGIN {print $START - $LAST_END}")
            local SIL_FILE="${TMPDIR}/${SPK}_sil_${IDX}.wav"
            echo "  生成静音段[$IDX]: ${LAST_END}s - ${START}s (${DUR_SIL}s)"
            ffmpeg -y -f lavfi -i anullsrc=r=${AUDIO_RATE}:${ANULLSRC_CHANNEL_OPT} -t $DUR_SIL "$SIL_FILE" -loglevel error
            echo "file '$SIL_FILE'" >> "$SEGMENTS"
            IDX=$((IDX+1))
        fi
        
        # 说话段
        DUR_SEG=$(awk "BEGIN {print $END - $START}")
        local SEG_FILE="${TMPDIR}/${SPK}_seg_${IDX}.wav"
        echo "  生成说话段[$IDX]: ${START}s - ${END}s (${DUR_SEG}s)"
        ffmpeg -y -i "$AUDIO_FILE" -ss $START -t $DUR_SEG -acodec pcm_s16le "$SEG_FILE" -loglevel error
        echo "file '$SEG_FILE'" >> "$SEGMENTS"
        IDX=$((IDX+1))
        LAST_END=$END
    done
    
    # 结尾静音
    if (( $(echo "$LAST_END < $TOTAL_DURATION" | bc -l) )); then
        DUR_SIL=$(awk "BEGIN {print $TOTAL_DURATION - $LAST_END}")
        local SIL_FILE="${TMPDIR}/${SPK}_sil_${IDX}.wav"
        echo "  生成结尾静音段[$IDX]: ${LAST_END}s - ${TOTAL_DURATION}s (${DUR_SIL}s)"
        ffmpeg -y -f lavfi -i anullsrc=r=${AUDIO_RATE}:${ANULLSRC_CHANNEL_OPT} -t $DUR_SIL "$SIL_FILE" -loglevel error
        echo "file '$SIL_FILE'" >> "$SEGMENTS"
    fi
    
    echo "生成segments文件完成: $SEGMENTS"
    echo "segments文件内容(前3行):"
    head -n 3 "$SEGMENTS"
}

# --- 处理 SPEAKER_00 和 SPEAKER_01 ---
echo "正在处理 SPEAKER_00..."
process_speaker SPEAKER_00
echo "正在处理 SPEAKER_01..."
process_speaker SPEAKER_01

# --- 拼接并转码 ---
echo "开始拼接并转码..."
for SPK in SPEAKER_00 SPEAKER_01; do
    SPK_LOWER=$(echo "$SPK" | tr 'A-Z' 'a-z')
    OUT_WAV="$OUTDIR/output_${SPK_LOWER}_track.wav"
    OUT_MP3="$OUTDIR/output_${SPK_LOWER}_track.mp3"
    
    echo "拼接 $SPK 音轨 -> $OUT_WAV"
    ffmpeg -y -f concat -safe 0 -i "$TMPDIR/segments_${SPK}.txt" -c copy "$OUT_WAV" -loglevel error
    
    if [ ! -f "$OUT_WAV" ]; then
        echo "Error: $OUT_WAV 未生成，拼接失败。"
        # 调试信息
        echo "检查segments文件(前5行):"
        head -n 5 "$TMPDIR/segments_${SPK}.txt"
        exit 1
    fi
    
    # 转码为mp3
    echo "转码 $OUT_WAV -> $OUT_MP3"
    ffmpeg -y -i "$OUT_WAV" -c:a libmp3lame -q:a 2 "$OUT_MP3" -loglevel error
    
    if [ ! -f "$OUT_MP3" ]; then
        echo "Error: $OUT_MP3 未生成，转码失败。"
        exit 1
    fi
    
    echo "$SPK音频完成: $OUT_MP3"
done

# --- 清理临时文件 ---
echo "清理临时文件..."
rm -rf "$TMPDIR"

# --- 完成 ---
echo "音频拆分完成！输出目录: $OUTDIR"
echo "SPEAKER_00: $OUTDIR/output_speaker_00_track.mp3"
echo "SPEAKER_01: $OUTDIR/output_speaker_01_track.mp3"