from decouple import config
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from tools import all_tools

tools_by_name = {t.name: t for t in all_tools}

llm = ChatOllama(model=config("OLLAMA_MODEL", default="qwen2.5:7b")).bind_tools(all_tools)

system_prompt = """You are LogSense, an intelligent log analysis assistant for homelab and server environments.

You have direct access to tools that can read logs from Docker containers and remote servers. Use them immediately without asking for permission.

Your capabilities:
- Fetch logs from any running Docker container
- Read system log files on the remote server (/var/log/syslog, /var/log/auth.log, nginx/apache logs, journald, etc.)
- Search logs for specific patterns, errors, or time ranges
- Correlate events across multiple log sources

Rules:
- Always use your tools immediately. Never ask for permission before fetching logs.
- Never ask which server or container to check. You have one configured target, always use it.
- When analyzing logs, look for: error spikes, OOM kills, segfaults, failed services, repeated 4xx/5xx HTTP errors, failed SSH attempts, disk full warnings, and unexpected restarts.
- When something looks wrong, explain it clearly: what happened, when, how often, and what likely caused it.
- Be concise. Lead with the most important finding. Use markdown tables or lists when presenting multiple events.
- If logs are clean, say so in one sentence.
- When asked about a time range, filter aggressively — don't dump raw logs, summarize what happened.
- Correlate across sources when relevant: if nginx is throwing 502s, check if the upstream container crashed around the same time."""

history = []
  
async def agent_chat(user_message: str) -> str:
    global history
    history.append(HumanMessage(user_message))
    messages = [SystemMessage(system_prompt)] + history[-3:]
 
    while True:
        response = await llm.ainvoke(messages)
        print("tool_calls:", response.tool_calls)
        print("content:", response.content)
        messages.append(response)
 
        if response.tool_calls:
            for call in response.tool_calls:
                result = tools_by_name[call["name"]].invoke(call["args"])
                messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
        else:
            history.append(AIMessage(response.content))
            return response.content

def clear_history():
    global history
    history = []