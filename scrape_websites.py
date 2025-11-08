# import basics
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# import langchain
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

# import supabase
from supabase.client import Client, create_client

# load environment variables
load_dotenv()

# initiate supabase db
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# initiate embeddings model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def get_all_links(base_url, max_pages=50):
    """
    Crawl a website and get all internal links
    """
    visited = set()
    to_visit = [base_url]
    all_links = []

    domain = urlparse(base_url).netloc

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)

        if url in visited:
            continue

        try:
            print(f"Crawling: {url}")
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            visited.add(url)
            all_links.append(url)

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all links on the page
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                parsed = urlparse(full_url)

                # Only follow internal links
                if parsed.netloc == domain and full_url not in visited and full_url not in to_visit:
                    # Avoid common non-content pages
                    if not any(x in full_url.lower() for x in ['#', 'javascript:', 'mailto:', '.pdf', '.jpg', '.png', '.gif']):
                        to_visit.append(full_url)

            time.sleep(0.5)  # Be polite to the server

        except Exception as e:
            print(f"Error crawling {url}: {e}")
            continue

    return all_links


def scrape_websites():
    """
    Scrape both Carver Financial Services and Raymond James websites
    """
    websites = [
        "https://carverfinancialservices.com/",
        "https://www.raymondjames.com/"
    ]

    all_documents = []

    for website in websites:
        print(f"\n{'='*50}")
        print(f"Scraping {website}")
        print(f"{'='*50}\n")

        # Get all links from the website
        links = get_all_links(website, max_pages=30)
        print(f"\nFound {len(links)} pages to scrape")

        # Load content from each page
        for link in links:
            try:
                loader = WebBaseLoader(link)
                docs = loader.load()

                # Add source metadata
                for doc in docs:
                    doc.metadata['source_website'] = website
                    doc.metadata['url'] = link

                all_documents.extend(docs)
                print(f"✓ Scraped: {link}")

            except Exception as e:
                print(f"✗ Error loading {link}: {e}")
                continue

    print(f"\n{'='*50}")
    print(f"Total documents scraped: {len(all_documents)}")
    print(f"{'='*50}\n")

    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    docs = text_splitter.split_documents(all_documents)

    print(f"Split into {len(docs)} chunks")

    # Clear existing documents from the database (optional)
    print("\nClearing existing documents from database...")
    try:
        supabase.table("documents").delete().neq('id', 0).execute()
    except Exception as e:
        print(f"Note: Could not clear existing documents: {e}")

    # Store chunks in vector store
    print("\nStoring documents in Supabase vector store...")
    vector_store = SupabaseVectorStore.from_documents(
        docs,
        embeddings,
        client=supabase,
        table_name="documents",
        query_name="match_documents",
        chunk_size=500,
    )

    print("\n✓ Successfully scraped and stored all website content!")
    print(f"Total chunks stored: {len(docs)}")


if __name__ == "__main__":
    scrape_websites()
