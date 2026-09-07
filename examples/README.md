# Client examples

These examples call the local OpenAI-compatible API at `http://localhost:8000/v1`.
Start the application with Docker Compose before running them:

```powershell
docker compose up --build -d
```

Set the same API key configured in the project's `.env` file. The examples read
`LOCAL_LLM_API_KEY` first and fall back to `API_KEY`. They read `LOCAL_LLM_MODEL`
first and fall back to `DEFAULT_MODEL`.

## Python

```powershell
$env:LOCAL_LLM_API_KEY="your-local-key"
$env:LOCAL_LLM_MODEL="llama3.2:3b"
pip install openai
python examples/python/client.py
```

## Node.js

```powershell
$env:LOCAL_LLM_API_KEY="your-local-key"
npm install openai
node examples/node/client.mjs
```

## C#

Create a console project and install the official OpenAI client package:

```powershell
dotnet new console -n LocalLlmExample
cd LocalLlmExample
dotnet add package OpenAI
Copy-Item ..\examples\csharp\Program.cs .\Program.cs
$env:LOCAL_LLM_API_KEY="your-local-key"
dotnet run
```

If anonymous requests are enabled for a local experiment, the clients still
require a non-empty key because the OpenAI SDKs expect one. Any value is accepted
only when the server is configured to allow anonymous requests.
