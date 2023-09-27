import pandas as pd
import openai

def ChatGptEngine(apiKey,input_string,prompt):
    # openai.api_key = apiKey
    try:
        openai.api_key = "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"
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": input_string +prompt}
        ],
        timeout=60
        )
        return completion.choices[0].message.content
    except Exception as e:
        return e