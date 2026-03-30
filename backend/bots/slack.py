import asyncio
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from decouple import config

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import agent_chat

app = AsyncApp(token=config("SLACK_BOT_TOKEN"))

@app.message("log:")
async def handle_message(message, say):
    query = message["text"].replace("log:", "").strip()
    await say("_thinking..._")
    response = await agent_chat(query)
    await say(response)

async def main():
    handler = AsyncSocketModeHandler(app, config("SLACK_APP_TOKEN"))
    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(main())