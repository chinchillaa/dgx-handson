import sys, torch, json, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'chapter3'))
from agent_kit import parse_tool_calls, LocalChatModel, TraceHandler, run_python, workspace_path
from transformers import AutoTokenizer
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# parse
c, calls, bad = parse_tool_calls('考えます\n<tool_call>\n{"name": "add", "arguments": {"a": 1, "b": 2}}\n</tool_call>\n<tool_call>{"name": "x", "arguments": "{\\"q\\": 1}"}</tool_call><tool_call>{bad json}</tool_call>')
assert c == '考えます' and [t['name'] for t in calls] == ['add', 'x'] and calls[1]['args'] == {'q': 1} and len(bad) == 1, (c, calls, bad)

tok = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B-Instruct')
class Scripted:
    device = 'cpu'
    def __init__(self, texts): self.texts = list(texts)
    def generate(self, input_ids, **kw):
        add = tok(self.texts.pop(0) + '<|im_end|>', return_tensors='pt', add_special_tokens=False)['input_ids']
        return torch.cat([input_ids, add], dim=1)

@tool
def add(a: int, b: int) -> int:
    """2 つの整数を足す"""
    return a + b

script = ['<tool_call>\n{"name": "add", "arguments": {"a": 3, "b": 4}}\n</tool_call>', '答えは 7 です。']
llm = LocalChatModel(model=Scripted(script), tokenizer=tok).bind_tools([add])
print(llm.render_prompt([HumanMessage('3+4')])[:300])
def agent(state): return {'messages': [llm.invoke(state['messages'])]}
g = StateGraph(MessagesState); g.add_node('agent', agent); g.add_node('tools', ToolNode([add]))
g.add_edge(START, 'agent'); g.add_conditional_edges('agent', tools_condition); g.add_edge('tools', 'agent')
graph = g.compile()
trace = TraceHandler()
res = graph.invoke({'messages': [HumanMessage('3 と 4 を足して')]}, config={'callbacks': [trace]})
print([ (m.type, m.content) for m in res['messages']])
assert res['messages'][-1].content == '答えは 7 です。' and res['messages'][2].content == '7'
trace.print_table()
t = trace.totals(); assert t['LLM の呼び出し回数'] == 2 and t['ツールの呼び出し回数'] == 1, t
# 2 回目のプロンプトに tool の結果が入っているか
print(llm.render_prompt(res['messages'][:3])[-200:])
try:
    print(graph.get_graph().draw_ascii())
except Exception as e:
    print('draw_ascii:', type(e).__name__, e)
print(graph.get_graph().draw_mermaid()[:300])
ws = Path(tempfile.mkdtemp())
assert run_python('print(2**10)', ws) == '1024'
assert 'TimeoutExpired' not in run_python('while True: pass', ws, timeout=1)
try: workspace_path(ws, '../x'); raise SystemExit('should fail')
except ValueError as e: print('ok guard:', e)
print('ALL OK')
