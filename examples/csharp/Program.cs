using OpenAI;
using OpenAI.Chat;

var client = new OpenAIClient(new OpenAIClientOptions
{
    ApiKey = "dummy",
    BaseUrl = new Uri("http://localhost:8000/v1")
});

var chat = client.GetChatClient("llama3.2:3b");

var completion = await chat.CompleteChatAsync(new[]
{
    ChatMessage.CreateSystemMessage("Responda em pt-BR."),
    ChatMessage.CreateUserMessage("Qual a vantagem de executar LLM local?")
});

Console.WriteLine(completion.Value.Content[0].Text);
