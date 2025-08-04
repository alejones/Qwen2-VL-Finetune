#!/bin/bash

MODEL_NAME="Qwen/Qwen2.5-VL-7B-Instruct"
# MODEL_NAME="Qwen/Qwen2.5-VL-3B-Instruct"
# MODEL_NAME="Qwen/Qwen2-VL-2B-Instruct"

export PYTHONPATH=src:$PYTHONPATH

python src/merge_lora_weights.py \
    --model-path output/sept_sample/v2_7b \
    --model-base $MODEL_NAME  \
    --save-model-path output/sept_sample/v2_7b/merged_full \
    --safe-serialization