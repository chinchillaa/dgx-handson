"""Qwen2.5-7B-Instruct の代わりに、同じ形式のチャットテンプレートを持つ小さなランダム重みのモデルを置く（検証用）"""
import sys, hashlib, shutil
from pathlib import Path
from tokenizers import Tokenizer, models, pre_tokenizers, trainers, decoders
from transformers import PreTrainedTokenizerFast, Qwen2Config, Qwen2ForCausalLM
import torch

HUB = Path(sys.argv[1]) / 'hub'
rid = 'Qwen/Qwen2.5-7B-Instruct'
corpus = [p.read_text() for p in Path(__file__).resolve().parents[2].glob('**/*.md')]
tok = Tokenizer(models.BPE()); tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False); tok.decoder = decoders.ByteLevel()
specials = ['<|endoftext|>', '<|im_start|>', '<|im_end|>', '<tool_call>', '</tool_call>']
tok.train_from_iterator(corpus, trainers.BpeTrainer(vocab_size=3000, special_tokens=specials, initial_alphabet=pre_tokenizers.ByteLevel.alphabet()))
T = r"""{%- if tools %}<|im_start|>system
{% if messages[0]['role'] == 'system' %}{{ messages[0]['content'] }}{% else %}You are Qwen, created by Alibaba Cloud. You are a helpful assistant.{% endif %}

# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>{% for tool in tools %}
{{ tool | tojson }}{% endfor %}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call><|im_end|>
{%- elif messages[0]['role'] == 'system' %}<|im_start|>system
{{ messages[0]['content'] }}<|im_end|>
{%- endif %}
{%- for m in messages %}{%- if m.role == 'system' %}{%- elif m.role == 'user' %}
<|im_start|>user
{{ m.content }}<|im_end|>{%- elif m.role == 'assistant' %}
<|im_start|>assistant
{%- if m.content %}
{{ m.content }}{%- endif %}{%- for tc in m.tool_calls | default([]) %}
<tool_call>
{"name": "{{ tc.function.name }}", "arguments": {{ tc.function.arguments | tojson }}}
</tool_call>{%- endfor %}<|im_end|>{%- elif m.role == 'tool' %}
<|im_start|>user
<tool_response>
{{ m.content }}
</tool_response><|im_end|>{%- endif %}{%- endfor %}
{%- if add_generation_prompt %}
<|im_start|>assistant
{% endif %}"""
pt = PreTrainedTokenizerFast(tokenizer_object=tok, eos_token='<|im_end|>', pad_token='<|endoftext|>', model_max_length=32768)
pt.chat_template = T
out = Path(sys.argv[1]) / '_qwen'; shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
pt.save_pretrained(out)
torch.manual_seed(0)
Qwen2ForCausalLM(Qwen2Config(vocab_size=len(pt), hidden_size=64, intermediate_size=128, num_hidden_layers=2, num_attention_heads=4,
    num_key_value_heads=2, max_position_embeddings=4096, eos_token_id=pt.eos_token_id, pad_token_id=pt.pad_token_id)).save_pretrained(out)
d = HUB / f"models--{rid.replace('/', '--')}"; sha = hashlib.sha1(rid.encode()).hexdigest(); snap = d / 'snapshots' / sha
shutil.rmtree(d, ignore_errors=True); snap.mkdir(parents=True); (d / 'refs').mkdir(); (d / 'refs' / 'main').write_text(sha)
for f in out.iterdir(): shutil.copy(f, snap / f.name)
shutil.rmtree(out); print('placed', rid)
