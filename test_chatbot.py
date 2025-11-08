"""
Test script for Carver Financial Services Chatbot
This script allows you to test the chatbot locally via command line
"""

import os
from dotenv import load_dotenv
import sys

# Import langchain components
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

# Import supabase
from supabase.client import Client, create_client

# Load environment variables
load_dotenv()


def test_connection():
    """Test database and API connections"""
    print("\n" + "="*60)
    print("TESTING CONNECTIONS")
    print("="*60)

    # Check environment variables
    print("\n1. Checking environment variables...")
    openai_key = os.environ.get("OPENAI_API_KEY")
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")

    if not openai_key:
        print("   ❌ OPENAI_API_KEY not found in .env file")
        return False
    else:
        print(f"   ✓ OpenAI API Key found: {openai_key[:10]}...")

    if not supabase_url:
        print("   ❌ SUPABASE_URL not found in .env file")
        return False
    else:
        print(f"   ✓ Supabase URL found: {supabase_url}")

    if not supabase_key:
        print("   ❌ SUPABASE_SERVICE_KEY not found in .env file")
        return False
    else:
        print(f"   ✓ Supabase Key found: {supabase_key[:10]}...")

    # Test Supabase connection
    print("\n2. Testing Supabase connection...")
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        result = supabase.table("documents").select("count").limit(1).execute()
        print("   ✓ Successfully connected to Supabase")

        # Check if documents exist
        count_result = supabase.table("documents").select("*", count="exact").limit(0).execute()
        doc_count = count_result.count if hasattr(count_result, 'count') else 0
        print(f"   ✓ Found {doc_count} documents in database")

        if doc_count == 0:
            print("   ⚠️  Warning: No documents in database. Run scrape_websites.py first!")

    except Exception as e:
        print(f"   ❌ Failed to connect to Supabase: {e}")
        return False

    # Test OpenAI connection
    print("\n3. Testing OpenAI connection...")
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        test_response = llm.invoke("Say 'Connection successful' in exactly those words.")
        print(f"   ✓ Successfully connected to OpenAI")
    except Exception as e:
        print(f"   ❌ Failed to connect to OpenAI: {e}")
        return False

    print("\n" + "="*60)
    print("✓ ALL CONNECTIONS SUCCESSFUL")
    print("="*60 + "\n")
    return True


def create_chatbot():
    """Initialize the chatbot"""
    # Load environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")

    # Initialize Supabase
    supabase: Client = create_client(supabase_url, supabase_key)

    # Initialize embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Initialize vector store
    vector_store = SupabaseVectorStore(
        embedding=embeddings,
        client=supabase,
        table_name="documents",
        query_name="match_documents",
    )

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # System prompt with safety guardrails
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

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create retriever tool
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

    # Create agent
    tools = [retrieve]
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

    return agent_executor


def chat_loop():
    """Interactive chat loop"""
    print("\n" + "="*60)
    print("CARVER FINANCIAL SERVICES CHATBOT - TEST MODE")
    print("="*60)
    print("\nType your questions below. Type 'quit' or 'exit' to stop.")
    print("Type 'clear' to clear chat history.\n")

    # Create chatbot
    try:
        agent_executor = create_chatbot()
    except Exception as e:
        print(f"\n❌ Error creating chatbot: {e}")
        print("\nMake sure you have:")
        print("1. Set up your .env file with API keys")
        print("2. Created the Supabase database tables")
        print("3. Run scrape_websites.py to populate the database\n")
        return

    chat_history = []

    while True:
        # Get user input
        try:
            user_input = input("\n👤 You: ").strip()
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            break

        # Check for exit commands
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break

        # Check for clear command
        if user_input.lower() == 'clear':
            chat_history = []
            print("\n✓ Chat history cleared.")
            continue

        # Skip empty input
        if not user_input:
            continue

        # Add to history
        chat_history.append(HumanMessage(content=user_input))

        # Get response
        try:
            print("\n🏦 Assistant: ", end="", flush=True)
            result = agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history[-10:]  # Keep last 10 messages
            })

            response = result["output"]
            print(response)

            # Add to history
            chat_history.append(AIMessage(content=response))

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or check your configuration.\n")


def main():
    """Main function"""
    print("\n" + "="*60)
    print("CARVER FINANCIAL SERVICES CHATBOT - TEST UTILITY")
    print("="*60)

    # Check if we should run tests or go straight to chat
    if len(sys.argv) > 1 and sys.argv[1] == '--skip-test':
        chat_loop()
    else:
        # Test connections first
        if test_connection():
            chat_loop()
        else:
            print("\n❌ Connection tests failed. Please fix the issues above and try again.\n")
            print("Quick troubleshooting:")
            print("1. Make sure .env file exists with correct values")
            print("2. Run: pip install -r requirements.txt")
            print("3. Set up Supabase database (see QUICKSTART.md)")
            print("4. Run: python scrape_websites.py\n")


if __name__ == "__main__":
    main()
