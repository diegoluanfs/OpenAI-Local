using OpenAI;
using OpenAI.Chat;

var apiKey = Environment.GetEnvironmentVariable("LOCAL_LLM_API_KEY")
    ?? Environment.GetEnvironmentVariable("API_KEY");
if (string.IsNullOrWhiteSpace(apiKey))
{
    throw new InvalidOperationException("Set LOCAL_LLM_API_KEY or API_KEY before running the example.");
}

var model = Environment.GetEnvironmentVariable("LOCAL_LLM_MODEL")
    ?? Environment.GetEnvironmentVariable("DEFAULT_MODEL")
    ?? "llama3.2:3b";

var client = new OpenAIClient(new OpenAIClientOptions
{
    ApiKey = apiKey,
    BaseUrl = new Uri("http://localhost:8000/v1")
});

var chat = client.GetChatClient(model);

var completion = await chat.CompleteChatAsync(new[]
{
    ChatMessage.CreateSystemMessage("Responda em pt-BR."),
    ChatMessage.CreateUserMessage("Qual a vantagem de executar LLM local?")
});

Console.WriteLine(completion.Value.Content[0].Text);
