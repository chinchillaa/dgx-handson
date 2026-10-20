"""第3章で使う共通の部品

ノートブックから `from agent_kit import ...` で読み込む。中身はすべて、ハンズオン①の Part 2〜3 で
手で書いた処理をまとめたもの（ブラックボックスではない）。

- LocalChatModel   手元の HF モデルを、ツール呼び出しのできる LangChain のチャットモデルにする
- parse_tool_calls モデルが書いた <tool_call>{...}</tool_call> を読み取る
- TraceHandler     LLM とツールの呼び出しを記録し、トークン数・時間を集計する（観測性・コスト管理）
- run_python       Python のコードを別プロセスで実行する（タイムアウトつき）
- workspace_path   ファイル操作を作業ディレクトリの中に閉じ込める

langchain_huggingface の ChatHuggingFace は、ローカルのモデル（HuggingFacePipeline）では
bind_tools() してもツールの定義をプロンプトに渡さず、出力からツール呼び出しも読み取らない（2026-10 時点）。
そのため、チャットテンプレートにツールを渡し、出力を自分で読む小さなラッパーを用意している。
"""

import json
import re
import subprocess
import sys
import time
import unicodedata
import uuid
from pathlib import Path
from typing import Any, Optional

import torch
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import ConfigDict

# Qwen2.5 などは、ツールを呼ぶときに <tool_call>{"name": ..., "arguments": {...}}</tool_call> と書く
TOOL_CALL_RE = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.S)


# ───────────────────────── ツール呼び出しの読み取り ─────────────────────────

def parse_tool_calls(text: str) -> tuple[str, list[dict], list[dict]]:
    """モデルの出力から、本文・ツール呼び出し・読み取れなかった呼び出しを取り出す

    戻り値:
        content            <tool_call> を除いた本文
        tool_calls         [{'name': ..., 'args': {...}, 'id': ...}, ...]（LangChain の形式）
        invalid_tool_calls JSON として読めなかったもの（{'name', 'args'（文字列）, 'id', 'error'}）
    """
    tool_calls, invalid = [], []
    for raw in TOOL_CALL_RE.findall(text):
        call_id = f"call_{uuid.uuid4().hex[:8]}"
        try:
            obj = json.loads(raw)
            args = obj.get("arguments", {})
            if isinstance(args, str):          # 引数を文字列の JSON で書くモデルもある
                args = json.loads(args)
            tool_calls.append({"name": obj["name"], "args": args, "id": call_id, "type": "tool_call"})
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
            invalid.append({"name": None, "args": raw, "id": call_id, "error": f"{type(e).__name__}: {e}",
                            "type": "invalid_tool_call"})
    content = TOOL_CALL_RE.sub("", text).strip()
    return content, tool_calls, invalid


def to_hf_messages(messages: list[BaseMessage]) -> list[dict]:
    """LangChain のメッセージを、transformers のチャットテンプレートが読む辞書のリストにする"""
    out = []
    for m in messages:
        if m.type == "system":
            out.append({"role": "system", "content": m.content})
        elif m.type == "human":
            out.append({"role": "user", "content": m.content})
        elif m.type == "ai":
            d = {"role": "assistant", "content": m.content or ""}
            if getattr(m, "tool_calls", None):
                d["tool_calls"] = [{"type": "function", "function": {"name": tc["name"], "arguments": tc["args"]}}
                                   for tc in m.tool_calls]
            out.append(d)
        elif m.type == "tool":
            out.append({"role": "tool", "content": str(m.content), "name": getattr(m, "name", None)})
        else:
            raise ValueError(f"対応していないメッセージの種類です: {m.type}")
    return out


# ───────────────────────── チャットモデル ─────────────────────────

class LocalChatModel(BaseChatModel):
    """手元の HF モデルを、ツール呼び出しのできる LangChain のチャットモデルとして使う

    使い方:
        llm = LocalChatModel(model=model, tokenizer=tokenizer)
        llm_with_tools = llm.bind_tools([search_docs, run_python])
        ai_message = llm_with_tools.invoke([HumanMessage('...')])
        ai_message.tool_calls   # → [{'name': 'search_docs', 'args': {...}, 'id': ...}]
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    model: Any
    tokenizer: Any
    tools: list[dict] = []
    max_new_tokens: int = 512

    @property
    def _llm_type(self) -> str:
        return "local-hf-chat"

    def bind_tools(self, tools: list, **kwargs) -> "LocalChatModel":
        """ツールの定義（名前・説明・引数の型）を JSON にして持たせたコピーを返す"""
        return self.model_copy(update={"tools": [convert_to_openai_tool(t) for t in tools]})

    def render_prompt(self, messages: list[BaseMessage]) -> str:
        """モデルに実際に渡す文字列（ツールの定義も、チャットテンプレートがここに書き込む）"""
        return self.tokenizer.apply_chat_template(
            to_hf_messages(messages), tools=self.tools or None, add_generation_prompt=True, tokenize=False,
        )

    def _generate(self, messages: list[BaseMessage], stop: Optional[list[str]] = None,
                  run_manager=None, **kwargs) -> ChatResult:
        prompt = self.render_prompt(messages)
        inputs = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(self.model.device)
        n_in = inputs["input_ids"].shape[1]
        with torch.no_grad():
            out = self.model.generate(
                **inputs, max_new_tokens=self.max_new_tokens, do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
            )
        new_ids = out[0, n_in:]
        # <tool_call> を消さないよう、特殊トークンを残してデコードし、終了トークンだけを取り除く
        text = self.tokenizer.decode(new_ids, skip_special_tokens=False)
        for t in {self.tokenizer.eos_token, self.tokenizer.pad_token, "<|im_end|>", "<|endoftext|>"} - {None}:
            text = text.replace(t, "")
        content, tool_calls, invalid = parse_tool_calls(text)
        message = AIMessage(
            content=content,
            tool_calls=tool_calls,
            invalid_tool_calls=invalid,
            usage_metadata={"input_tokens": n_in, "output_tokens": len(new_ids), "total_tokens": n_in + len(new_ids)},
            response_metadata={"raw_text": text},
        )
        return ChatResult(generations=[ChatGeneration(message=message)])


# ───────────────────────── 観測性・コスト管理 ─────────────────────────

def _pad(s, width: int, right: bool = False) -> str:
    """全角文字を2文字ぶんとして数え、表示幅をそろえる（表の桁ずれ防止）"""
    s = str(s)
    w = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)
    space = " " * max(width - w, 0)
    return space + s if right else s + space


class TraceHandler(BaseCallbackHandler):
    """LLM とツールの呼び出しを 1 件ずつ記録する

    使い方:
        trace = TraceHandler()
        graph.invoke({...}, config={'callbacks': [trace]})
        trace.print_table()    # 呼び出しの一覧
        trace.totals()         # 回数・トークン数・時間の合計
    """

    def __init__(self):
        self.records: list[dict] = []
        self._open: dict = {}

    def _start(self, run_id, kind: str, name: str, detail: str):
        self._open[run_id] = {"kind": kind, "name": name, "start": time.perf_counter(), "input": detail,
                              "input_tokens": 0, "output_tokens": 0, "output": "", "error": None}

    def _end(self, run_id, **fields):
        rec = self._open.pop(run_id, None)
        if rec is None:
            return
        rec.update(fields)
        rec["seconds"] = time.perf_counter() - rec.pop("start")
        self.records.append(rec)

    # LLM
    def on_chat_model_start(self, serialized, messages, *, run_id, **kwargs):
        last = messages[0][-1] if messages and messages[0] else None
        self._start(run_id, "LLM", (serialized or {}).get("name") or "LLM",
                    f"{len(messages[0])} 件のメッセージ（最後: {last.type if last else '-'}）")

    def on_llm_end(self, response, *, run_id, **kwargs):
        msg = response.generations[0][0].message
        usage = getattr(msg, "usage_metadata", None) or {}
        calls = ", ".join(tc["name"] for tc in getattr(msg, "tool_calls", []) or [])
        self._end(run_id, input_tokens=usage.get("input_tokens", 0), output_tokens=usage.get("output_tokens", 0),
                  output=f"ツール呼び出し: {calls}" if calls else (msg.content or "")[:80])

    def on_llm_error(self, error, *, run_id, **kwargs):
        self._end(run_id, error=f"{type(error).__name__}: {error}")

    # ツール
    def on_tool_start(self, serialized, input_str, *, run_id, **kwargs):
        self._start(run_id, "ツール", (serialized or {}).get("name") or "tool", str(input_str)[:80])

    def on_tool_end(self, output, *, run_id, **kwargs):
        content = getattr(output, "content", output)
        self._end(run_id, output=str(content)[:80])

    def on_tool_error(self, error, *, run_id, **kwargs):
        self._end(run_id, error=f"{type(error).__name__}: {error}")

    # 集計
    def totals(self) -> dict:
        llm = [r for r in self.records if r["kind"] == "LLM"]
        tools = [r for r in self.records if r["kind"] == "ツール"]
        return {
            "LLM の呼び出し回数": len(llm),
            "ツールの呼び出し回数": len(tools),
            "エラーの回数": sum(r["error"] is not None for r in self.records),
            "入力トークン数": sum(r["input_tokens"] for r in llm),
            "出力トークン数": sum(r["output_tokens"] for r in llm),
            "LLM の時間（秒）": round(sum(r["seconds"] for r in llm), 1),
            "ツールの時間（秒）": round(sum(r["seconds"] for r in tools), 1),
        }

    def print_table(self):
        print(f"{'#':>2}  {_pad('種類', 6)} {_pad('名前', 16)} {'秒':>5} {'入力tok':>7} {'出力tok':>7}  結果")
        for i, r in enumerate(self.records, 1):
            result = f"❌ {r['error']}" if r["error"] else r["output"].replace("\n", " ")
            tok_in = r["input_tokens"] if r["kind"] == "LLM" else ""
            tok_out = r["output_tokens"] if r["kind"] == "LLM" else ""
            print(f"{i:>2}  {_pad(r['kind'], 6)} {_pad(r['name'][:16], 16)} {r['seconds']:>5.1f} {tok_in:>7} {tok_out:>7}  {result[:60]}")
        print()
        for k, v in self.totals().items():
            print(f"  {k}: {v}")


# ───────────────────────── ツールの実装で使う道具 ─────────────────────────

def workspace_path(workspace: Path, filename: str) -> Path:
    """ファイル名を作業ディレクトリの中のパスにする。外へ出ようとしたら（../ や絶対パス）エラーにする"""
    workspace = Path(workspace).resolve()
    path = (workspace / filename).resolve()
    if workspace != path and workspace not in path.parents:
        raise ValueError(f"作業ディレクトリ（{workspace.name}/）の外のファイルは扱えません: {filename}")
    return path


def run_python(code: str, workspace: Path, timeout: int = 10) -> str:
    """Python のコードを別プロセスで実行し、標準出力と標準エラーを返す（長すぎる出力は切り詰める）"""
    Path(workspace).mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=workspace, capture_output=True, text=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return f"エラー: {timeout} 秒以内に終わりませんでした（無限ループの可能性があります）"
    out = (r.stdout + (f"\n[stderr]\n{r.stderr}" if r.stderr else "")).strip()
    if not out:
        out = "（出力なし。結果を見るには print() で表示してください）"
    return out[:2000] + ("\n…（以下省略）" if len(out) > 2000 else "")
