<h1>Agentic RAG (Retrieval Augmented Generation) with LangChain and Supabase</h1>

## Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Security](#security)
- [How to Contribute?](#how-to-contribute)
- [What's Next?](#whats-next)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Author](#author)

## About

This project demonstrates an agentic Retrieval-Augmented Generation (RAG) workflow. It ingests documents into a Supabase vector store, retrieves relevant context with a LangChain tool, and uses an OpenAI chat model to answer questions. A Streamlit interface is included for interactive conversations.

## Features

- Loads PDF documents from the `documents/` directory.
- Splits documents into overlapping chunks and stores embeddings in Supabase with pgvector.
- Retrieves the most relevant document chunks through an agent tool.
- Supports command-line and Streamlit chat experiences.
- Uses OpenAI's `text-embedding-3-small` embedding model.

## Tech Stack

- Python 3.11+
- LangChain and LangChain Classic
- OpenAI API
- Supabase with PostgreSQL and pgvector
- Streamlit

## Architecture

```text
PDF documents
    |
    v
ingest_in_db.py -> OpenAI embeddings -> Supabase pgvector
                                         |
User question -> LangChain agent -> retrieve tool -> relevant chunks
                                         |
                                         v
                                  OpenAI chat model -> response
```

## Project Structure

```text
.
├── agentic_rag.py             # Command-line agent example
├── agentic_rag_streamlit.py   # Streamlit chat application
├── ingest_in_db.py            # Document ingestion and vector storage
├── documents/                 # Source PDFs to ingest
├── requirements.txt           # Python dependencies
└── LICENSE
```

## Getting Started

### Prerequisites

- Python 3.11 or later
- A Supabase project
- An OpenAI API key

### Installation

```powershell
git clone https://github.com/ThomasJanssen-tech/Agentic-RAG-with-LangChain.git
cd Agentic-RAG-with-LangChain
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

On macOS or Linux, activate the virtual environment with `source venv/bin/activate`.

### Prepare Supabase

Run the following SQL in the Supabase SQL Editor:

```sql
create extension if not exists vector;

create table documents (
  id uuid primary key,
  content text,
  metadata jsonb,
  embedding vector(1536)
);

create function match_documents (
  query_embedding vector(1536),
  filter jsonb default '{}'
) returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
) language plpgsql as $$
#variable_conflict use_column
begin
  return query
  select
    id,
    content,
    metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where metadata @> filter
  order by documents.embedding <=> query_embedding;
end;
$$;
```

### Run the Project

Add PDF files to `documents/`, then ingest them and start one of the applications:

```powershell
python ingest_in_db.py
python agentic_rag.py
streamlit run agentic_rag_streamlit.py
```

## Configuration

Create a `.env` file in the repository root:

```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

The application uses the `documents` table and the `match_documents` search function by default.

## Security

- Never commit `.env` files, API keys, or Supabase service keys.
- Keep `SUPABASE_SERVICE_KEY` server-side; it has elevated database permissions.
- Use a restricted Supabase key and Row Level Security where the deployment requires user-level access.
- Rotate credentials immediately if they are exposed.

## How to Contribute?

1. Fork the repository and create a feature branch.
2. Make a focused change and verify it locally.
3. Update documentation when behavior or configuration changes.
4. Open a pull request describing the change and validation performed.

## What's Next?

- Add automated tests for ingestion and retrieval.
- Add support for additional document formats.
- Add source citations to generated answers.
- Add authentication and deployment configuration for a hosted Streamlit application.

## License

Distributed under the terms in [LICENSE](LICENSE).

## Acknowledgements

- [LangChain Supabase vector store integration](https://python.langchain.com/docs/integrations/vectorstores/supabase/)
- [LangChain OpenAI embeddings integration](https://python.langchain.com/docs/integrations/text_embedding/openai/)
- [OpenAI embeddings documentation](https://platform.openai.com/docs/guides/embeddings)
- [OpenAI embedding model announcement](https://openai.com/index/new-embedding-models-and-api-updates/)

## Author

Thomas Janssen