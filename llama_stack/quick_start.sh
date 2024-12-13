#!/bin/bash
# https://llama-stack.readthedocs.io/en/latest/getting_started/index.html
set -euo pipefail

export INFERENCE_MODEL="meta-llama/Llama-3.2-3B-Instruct"
# ollama names this model differently, and we must use the ollama name when loading the model
export OLLAMA_INFERENCE_MODEL="llama3.2:3b-instruct-fp16"
export LLAMA_STACK_PORT=5001

#ollama run $OLLAMA_INFERENCE_MODEL --keepalive 60m

docker run \
  -it \
  -p $LLAMA_STACK_PORT:$LLAMA_STACK_PORT \
  -v ~/.llama:/root/.llama \
  --name llama_stack \
  llamastack/distribution-ollama \
  --port $LLAMA_STACK_PORT \
  --env INFERENCE_MODEL=$INFERENCE_MODEL \
  --env OLLAMA_URL=http://host.docker.internal:11434