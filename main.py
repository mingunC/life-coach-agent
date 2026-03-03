import asyncio
import streamlit as st
from agents import Agent, Runner, SQLiteSession
from agents.tools.search import duckduckgo_search 

if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name="Life Coach Agent",
        instructions="당신은 유저를 격려하고 성장을 돕는 라이프 코치입니다. 필요시 웹 검색을 활용하세요.",
        tools=[duckduckgo_search]
    )
agent = st.session_state["agent"]

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "chat-gpt-clone-memory.db"
    )
session = st.session_state["session"]

async def paint_history():
    items = await session.get_items()
    for item in items:
        role = "human" if item.role == "user" else "ai"
        with st.chat_message(role):
            st.write(item.content)

async def run_agent(message):
    full_response = ""

    message_placeholder = st.chat_message("ai").empty()
    
    stream = Runner.run_streamed(agent, message, session=session)
    async for event in stream.stream_events():
        if event.type == "raw_response_event":
            # 오타 수정: output_textj -> output_text
            if event.data.type == "response.output_text.delta":
                full_response += event.data.delta            
                message_placeholder.markdown(full_response + "▌")
    
    message_placeholder.markdown(full_response)

asyncio.run(paint_history())

prompt = st.chat_input("Write a message for assistant")

if prompt:
   with st.chat_message("human"):
      st.write(prompt)
   
   asyncio.run(run_agent(prompt)) 

with st.sidebar:
    
    reset = st.button("Reset Memory")
    if reset:
       asyncio.run(session.clear_session())
       st.rerun() 
    
    st.write("현재 저장된 메시지 수:")
    st.write(len(asyncio.run(session.get_items())))