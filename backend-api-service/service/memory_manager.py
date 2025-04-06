from openai import AsyncOpenAI
from config import RAG_SERVICE_URL
import aiohttp
import asyncio
from . import crud
from . import models
from datetime import datetime, timedelta
from enum import StrEnum
from service.elevenlabs_api import load_memory_into_agent


class Mood(StrEnum):
    JOY = "U+1F604"
    STRESS = "U+1F630"
    TIRED = "U+1F62B"
    EXCITED = "U+1F929"
    A_BIT_SAD = "U+1F614"


class MemoryManager:
    def __init__(self, db):
        self.client = AsyncOpenAI()
        self.db = db
        self.session = None

    async def get_aiohttp_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def update_memory(
        self,
        agent_id: str,
        user_id: str,
        memory: str,
        last_conversation: str,
        elevenlabs_id: str = None,
    ):
        # Create a prompt that instructs the model to update the memory based
        # on the new conversation

        mood, updated_memory = await asyncio.gather(
            self.llm_sentiment_analysis_memory(last_conversation),
            self.llm_update_memory(agent_id, user_id, memory, last_conversation),
        )
        summary = await self.summarize_conversation(last_conversation, mood)

        crud.update_user_memory_by_agent_id(self.db, agent_id, updated_memory)

        crud.add_new_user_memory(self.db, user_id, agent_id, text=summary, mood=mood)

        load_memory_into_agent(elevenlabs_id, updated_memory)

        return updated_memory

    async def llm_update_memory(
        self, agent_id: str, user_id: str, memory: str, text: str
    ) -> str:
        """Update the memory using the LLM"""
        system_prompt = """
        You are an assistant that updates a user's memory document.
        Given the current memory and the latest conversation, update the memory
        adding information from the conversation. Bear in mind that you have to time by time update
        the memory of the user. For example you should iterate over the information that the user give you
        even if these information might not seem relevant at first. For example, if the user tells you
        that he is feeling tired, you should update the memory to reflect that. Initially also the long term memory
        might be affected by the conversation.
        Also, remember that the input structure of memory must not be changed:
        <long_term_memory>
        User's long term memory
        </long_term_memory>
        <short_term_memory>
        User's short term memory
        </short_term_memory>
        <last_conversation>
        The last conversation between the user and the assistant
        </last_conversation>
        Exclude any of your reasoning from the output, just return the updated memory.
        """

        user_prompt = f"""
        CURRENT MEMORY:
        {memory}

        LATEST CONVERSATION:
        {text}

        Please update with relevant information from this conversation.
        """

        # Call the OpenAI API with the updated client format
        response = await self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        # Extract the updated memory from the response
        updated_memory = response.choices[0].message.content

        return updated_memory

    async def llm_sentiment_analysis_memory(self, memory: str) -> Mood | None:
        """Analyze the sentiment of a memory"""
        system_prompt = """
        Analyze the following conversation to determine the mood of the user.
        The conversation is a list of messages between the user and the the assistant.

        One of these moods: Joy, Stress, Tired, Excited, or A Bit Sad. Based on the detected mood, output ONLY the corresponding emoji's Unicode code point (and nothing else).

        Mapping:
        - Joy: U+1F604
        - Stress: U+1F630
        - Tired: U+1F62B
        - Excited: U+1F929
        - A Bit Sad: U+1F614
        - Was Ok: U+1F610

        You must only output the emoji's Unicode code point.
        Example:
        - "I had a great day at the park with my family" -> "U+1F604"
        - "I had a stressful day at work" -> "U+1F630"
        - "I had a tired day" -> "U+1F62B"
        - "I had an exciting day" -> "U+1F929"
        - "I had a bit sad day" -> "U+1F614"
        - "My day was ok" -> "U+1F610"
        """

        user_prompt = f"""
        MEMORY:
        {memory}
        """

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        return response.choices[0].message.content

    async def summarize_conversation(self, conversation: str, mood: Mood) -> str:
        """Summarize the conversation"""
        system_prompt = f"""
        Summarize the following conversation between the user and the assistant.
        Bear in mind, this converation is for the user! Keep it clear, do not be too verbose.
        """

        user_prompt = f"""
        CONVERSATION:
        {conversation}
        """
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        return response.choices[0].message.content

    async def query_all_user_memories(self, user_id: int, query: str) -> str:
        """Query all memories of a user and run a query against them using ChatGPT"""
        # Get all memories for the user
        memories = (
            self.db.query(models.Memory).filter(models.Memory.user_id == user_id).all()
        )

        if not memories:
            return "No memories found for this user."

        # Concatenate all memory texts
        all_memory_text = "\n\n".join(
            [memory.text for memory in memories if memory.text]
        )

        if not all_memory_text:
            return "No memory content found for this user."

        # Create a prompt for ChatGPT
        system_prompt = """
        You are an assistant that retrieves relevant information from a user's memories.
        Given a collection of memories and a query, find and summarize the most relevant information.
        Be concise but comprehensive in your response.
        """

        user_prompt = f"""
        USER MEMORIES:
        {all_memory_text}

        QUERY:
        {query}

        Please provide the most relevant information from these memories that answers the query.
        """

        # Call the OpenAI API
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        # Extract the response
        return response.choices[0].message.content

    async def post_memory_update(self, memory: str):
        """Post the updated memory to the RAG service"""
        uri = f"{RAG_SERVICE_URL}/update_memory"
        session = await self.get_aiohttp_session()
        async with session.post(uri, json={"memory": memory}) as response:
            return await response.json()

    def get_last_month_memories_by_day(self, user_id: int):
        """
        Get all memories from the last month for a user, grouped by day.
        Returns a list of DailyMemoryItem objects.
        """
        # Calculate the date one month ago from today
        one_month_ago = datetime.now() - timedelta(days=30)

        # Query memories for this user from the last month
        memories = (
            self.db.query(models.Memory)
            .filter(
                models.Memory.user_id == user_id,
                models.Memory.created_at >= one_month_ago,
            )
            .order_by(models.Memory.created_at)
            .all()
        )

        # Group by day
        memory_by_day = {}
        mood_by_day = {}  # Track the mood of the last memory for each day
        for memory in memories:
            # Format day as ISO format date string (YYYY-MM-DD)
            day_str = memory.created_at.date().isoformat()

            if day_str not in memory_by_day:
                memory_by_day[day_str] = []

            # Only add if there's text content
            if memory.text:
                memory_by_day[day_str].append(memory.text)

            # Always update mood to keep the last one
            mood_by_day[day_str] = memory.mood

        # Format the response
        result = []
        for day, texts in memory_by_day.items():
            if texts:  # Only include days with memories
                result.append(
                    {
                        "day_timestamp": day,
                        "memory_text": "\n".join(texts),
                        "mood": mood_by_day.get(day),
                    }
                )

        return result
