# import basics
import os
from dotenv import load_dotenv
from typing import List, Dict

# import FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# import langchain
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

# import supabase db
from supabase.client import Client, create_client

# load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Carver Financial Services Chatbot API")

# Configure CORS to allow embedding from any domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initiating supabase
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# initiating embeddings model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# initiating vector store
vector_store = SupabaseVectorStore(
    embedding=embeddings,
    client=supabase,
    table_name="documents",
    query_name="match_documents",
)

# initiating llm
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Custom prompt with safety guardrails
SYSTEM_PROMPT = """You are a helpful customer service assistant for Carver Financial Services.

IMPORTANT GUIDELINES:
1. You can ONLY provide information that is available on carverfinancialservices.com and raymondjames.com
2. You MUST NOT provide personalized financial advice, investment recommendations, or tax advice
3. You MUST NOT make predictions about market performance or specific investment outcomes
4. You MUST NOT recommend specific securities, funds, or investment strategies
5. If asked for financial advice, politely redirect users to contact a financial advisor directly
6. Always cite the source of your information when possible
7. If you don't have information about something, admit it and suggest contacting Carver Financial Services directly

Your role is to:
- Answer questions about the services offered by Carver Financial Services
- Provide general information about Raymond James as their broker-dealer
- Help users navigate the website and find information
- Explain general financial concepts (but not personalized advice)
- Direct users to appropriate contact information for specific needs

Always be professional, courteous, and helpful while staying within these boundaries.
"""

# Create custom prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# creating the retriever tool
@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information from Carver Financial Services and Raymond James websites."""
    retrieved_docs = vector_store.similarity_search(query, k=3)
    serialized = "\n\n".join(
        (f"Source URL: {doc.metadata.get('url', 'Unknown')}\n"
         f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

# combining all tools
tools = [retrieve]

# initiating the agent
agent = create_tool_calling_agent(llm, tools, prompt)

# create the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# Pydantic models for request/response
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    chat_history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []


# Session storage (in production, use Redis or similar)
sessions: Dict[str, List] = {}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Carver Financial Services Chatbot",
        "version": "1.0.0"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    """
    try:
        # Convert chat history to LangChain messages
        chat_history = []
        for msg in request.chat_history[-10:]:  # Keep last 10 messages for context
            if msg.role == "user":
                chat_history.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                chat_history.append(AIMessage(content=msg.content))

        # Check for potentially harmful requests
        harmful_keywords = [
            "buy", "sell", "invest in", "should i invest",
            "stock pick", "which stock", "investment advice",
            "tax advice", "how much should i"
        ]

        user_message_lower = request.message.lower()
        if any(keyword in user_message_lower for keyword in harmful_keywords):
            # Add extra context to prevent giving advice
            enhanced_input = f"{request.message}\n\n[Note: User may be seeking financial advice. Remind them to contact a licensed financial advisor.]"
        else:
            enhanced_input = request.message

        # Invoke the agent
        result = agent_executor.invoke({
            "input": enhanced_input,
            "chat_history": chat_history
        })

        ai_message = result["output"]

        # Extract sources from the intermediate steps if available
        sources = []
        if "intermediate_steps" in result:
            for step in result["intermediate_steps"]:
                if len(step) > 1 and hasattr(step[1], 'metadata'):
                    url = step[1].metadata.get('url')
                    if url and url not in sources:
                        sources.append(url)

        return ChatResponse(
            response=ai_message,
            sources=sources
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
