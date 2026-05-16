# pip install --upgrade langchain langchain-community langgraph

# pip install langchain-ollama

from typing import List, Dict
from langgraph.graph import StateGraph, START, END
from langchain_ollama.llms import OllamaLLM


# Step 1: Define State
class State(Dict):  # chat bot memory
    messages: List[Dict[str, str]]    # A list of messages, where each message is a dictionary with "role" (either "user" or "assistant") and "content" (the text of the message). This structure allows us to keep track of the conversation history, which is essential for maintaining context in a chatbot interaction.


# Step 2: Initialize StateGraph
graph_builder = StateGraph(State)  # Initialize StateGraph with the defined State. This stage graph is the state machine that will manage the flow of the conversation. It will keep track of the messages exchanged between the user and the assistant, allowing us to maintain context throughout the interaction.

# Initialize the LLM  
# llm = OllamaLLM(model="llama3")
llm = OllamaLLM(model="phi3")


# Define chatbot function
def chatbot(state: State):
    response = llm.invoke(state["messages"])
    state["messages"].append({"role": "assistant", "content": response})  # Treat response as a string
    return {"messages": state["messages"]}



# Add nodes and edges
# add_node fn is used for adding a node to the graph. The first argument is the name of the node, and the second argument is the function that will be executed when that node is reached in the graph. In this case, we are adding a node named "chatbot" that will execute the chatbot function we defined earlier.
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")  # we need the starting point of the graph to be the chatbot node, so we add an edge from START to "chatbot". This means that when the graph execution begins, it will start at the "chatbot" node.
graph_builder.add_edge("chatbot", END)

# workflow:
# start -> chatbot -> end

# Compile the graph
graph = graph_builder.compile()


# Stream updates
def stream_graph_updates(user_input: str):    
    state = {"messages": [{"role": "user", "content": user_input}]}
    for event in graph.stream(state):
        for value in event.values():
            print("Assistant:", value["messages"][-1]["content"])



# Run chatbot in a loop
if __name__ == "__main__":
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            stream_graph_updates(user_input)
        except Exception as e:
            print(f"An error occurred: {e}")
            break