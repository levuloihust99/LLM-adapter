import asyncio
from core.llm.flow import llm_flow

with open("prompt.txt", "r", encoding="utf-8") as reader:
    PROMPT = reader.read()


async def launch():
    await llm_flow(prompt=PROMPT, completion_file="completion.txt")


def main():
    asyncio.run(launch())


if __name__ == "__main__":
    main()
