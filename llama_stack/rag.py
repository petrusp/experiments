import asyncio
import os

from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.types import Attachment
from llama_stack_client.types.agent_create_params import AgentConfig


async def run_main():
    urls = ["chat.rst", "llama3.rst", "datasets.rst", "lora_finetune.rst"]
    attachments = [
        Attachment(
            content=f"https://raw.githubusercontent.com/pytorch/torchtune/main/docs/source/tutorials/{url}",
            mime_type="text/plain",
        )
        for i, url in enumerate(urls)
    ]

    client = LlamaStackClient(base_url=f"http://localhost:{os.environ['LLAMA_STACK_PORT']}")

    agent_config = AgentConfig(
        model=os.environ["INFERENCE_MODEL"],
        instructions="You are a helpful assistant",
        tools=[{"type": "memory"}],  # enable Memory aka RAG
        enable_session_persistence=True,
    )

    agent = Agent(client, agent_config)
    session_id = agent.create_session("test-session")
    print(f"Created session_id={session_id} for Agent({agent.agent_id})")
    user_prompts = [
        (
            "I am attaching documentation for Torchtune. Help me answer questions I will ask next.",
            attachments,
        ),
        (
            "What are the top 5 topics that were explained? Only list succinct bullet points.",
            None,
        ),
    ]
    for prompt, attachments in user_prompts:
        response = agent.create_turn(
            messages=[{"role": "user", "content": prompt}],
            attachments=attachments,
            session_id=session_id,
        )
        for log in EventLogger().log(response):
            log.print()


if __name__ == "__main__":
    asyncio.run(run_main())