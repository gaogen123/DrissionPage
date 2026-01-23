import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pdd_langgraph_agent import graph
import webbrowser

app = FastAPI()

class Query(BaseModel):
    message: str
    thread_id: str = "default_thread"

@app.post("/api/chat")
async def chat_endpoint(query: Query):
    try:
        # User input directly to the agent
        user_input = query.message
        thread_id = query.thread_id
        
        # Determine if this is a new conversation or continuing one
        # Because we use checkpointer, we don't pass the full history manually anymore.
        # We just pass the NEW message, and the graph loads the rest from memory using thread_id.
        
        config = {"configurable": {"thread_id": thread_id}}
        
        input_message = {"messages": [("user", user_input)]}
        
        last_msg = ""
        
        # Stream events from the graph with the config
        for event in graph.stream(input_message, config=config):
            for value in event.values():
                if "messages" in value:
                    last_msg = value['messages'][-1].content
                    
        return {"response": last_msg, "thread_id": thread_id}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{thread_id}")
async def get_history(thread_id: str):
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state_snapshot = graph.get_state(config)
        
        history = []
        if state_snapshot.values and "messages" in state_snapshot.values:
            for msg in state_snapshot.values["messages"]:
                # Filter out system messages or tool calls if needed, 
                # but for now let's show user and ai messages.
                role = "unknown"
                if msg.type == "human":
                    role = "user"
                elif msg.type == "ai":
                    # skip tool calls themselves from display if they are empty content
                    if not msg.content:
                        continue
                    role = "agent"
                elif msg.type == "tool":
                    # We usually don't show raw tool outputs in the chat bubble unless requested
                    continue
                
                history.append({"role": role, "content": msg.content})
                
        return {"history": history}
    except Exception as e:
        print(f"Error fetching history: {e}")
        return {"history": []}

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    print("🚀 Starting Web Server on http://localhost:8000")
    # Auto open browser
    webbrowser.open("http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
