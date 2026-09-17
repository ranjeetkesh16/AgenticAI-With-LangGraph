from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver   #newline
import sqlite3                                          #newline
from dotenv import load_dotenv


load_dotenv(override=True)
import os

def get_groq_llm():
    return ChatOpenAI(
        model="gpt-4.1",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.4,
        max_tokens=2000
    )

llm = get_groq_llm()

sqlite_conn =sqlite3.connect("bot_checkpoint.sqlite", check_same_thread=False)  #newline
memory = SqliteSaver(sqlite_conn)                                              #newline

class ChatState(TypedDict):
    messages: Annotated[List, add_messages]


def chatbot( state: ChatState):

    #take user query from state
    messages = state['messages']

    #send to llm
    response = llm.invoke(messages)

    #response store state
    return {'messages': [response]}


graph = StateGraph(ChatState)

#add nodes
graph.add_node("chatbot", chatbot)

#graph.add_edge(START,'chat_node')
graph.add_edge('chatbot',END)
graph.set_entry_point("chatbot")

chatapp = graph.compile(checkpointer=memory)            #newline

chatapp

config = {"configurable": {"thread_id":"1"}}

while True:
    user_input = input("User: ")
    if(user_input in ['exit', 'end']):
        break
    else:
        result = chatapp.invoke({
            "messages": [HumanMessage(content=user_input)]
        }, config=config)

    print("AI: "+result['messages'][-1].content)



