import os, openai
openai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def start_research(query, webhook_url):
    return openai_client.responses.create(
        model="o3",
        background=True,
        store=True,
        input={"query": query},
        webhook={
            "url": webhook_url,
            "events": ["response.completed", "response.failed"],
        },
    )

def edit_snippet(original, instruction):
    res = openai_client.responses.create(
        model="gpt-4.1-mini",
        input={
            "messages": [
                {"role": "system", "content": "You are an expert editor."},
                {
                    "role": "user",
                    "content": f"Rewrite text:\n{original}\n\nInstruction: {instruction}",
                },
            ]
        },
    )
    return res.choices[0].message.content.strip()