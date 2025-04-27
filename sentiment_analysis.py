from openai import OpenAI
import json
import get_book_content as book

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

def analyse_text(book_snippet, reading_index):
    messages = [
        {"role": "system", "content": 
         """You are an AI that helps create ambient music for readers based on the book content they are currently reading. Your task is to suggest music changes based on the tone and atmosphere of the text. You do not include anything else in your responses but the expected data output. You cannot use markdown or unicode signs.
        Use the following for your responses:
         - trigger string should be a short but unique string of words for identifying where the music change should occur (aim for 5-10 words, don't bother with punctuation)
         - sentiment should be one of the following descriptive sentiments (do not include the number) DO NOT MIX SENTIMENTS. CHOOSE ONE.:
            1. melancholy
            2. tense
            3. ethereal
            4. triumphant
            5. mysterious
            6. upbeat
            7. eerie
            8. driven
            9. neutral (this one should be playing most of the time unless there is something notable)
         - intensity is how loud the music is... how intensely the music fits the scene. Be conservative. Notably you may choose to use lower intensity in certain intense situations depending on the context (such as quieter sadness vs great weeping) even if the scene fully embodies the sentiment. This data should be between 0 (silent) and 10 (blasting). 5 is default.
         - order your responses in the order they occur in the text: first occurrance comes first... else it will not work. YOU MUST DO THIS. BE VERY CAREFUL TO ORDER THEM CORRECTLY.
         - be really really sparse about your music changes. The music stays in the sentiment you last left it indefinitely. Only pass a few changes, and at the keyword where the change is done, revert it to neutral. You don't want to disturb the reader, instead provide them with a nice ambient reading experience. If there is nothing notable happening, revert to neutral with an appropriate intensity (could be 5)
         """},
        {"role": "user", "content": f"Based on the following text, suggest music that matches the tone and atmosphere: {book_snippet}"}
    ]

    sentiment_schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "changes",
            "schema": {
                "type": "object",
                "properties": {
                    "changes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "trigger string": {"type": "string"},
                                "sentiment": {"type": "string"},
                                "strength": {"type": "integer"},
                            },
                            "required": ["trigger string", "sentiment", "strength"]
                        },
                        "minItems": 1,
                    }
                },
                "required": ["music changes"]
            },
        }
    }

    response = client.chat.completions.create(
        model="meta-llama-3.1-8b-instruct",
        messages=messages,
        response_format=sentiment_schema,
    )

    results = json.loads(response.choices[0].message.content)

    parsed_results = []

    for change in results["changes"]:
        trigger_string = change["trigger string"]
        sentiment = change["sentiment"]
        intensity = change["strength"]

        position = book.get_index(trigger_string, reading_index)
        print("change position: " + str(position))
        parsed_results.append((position, trigger_string, sentiment, intensity))

    parsed_results.sort(key=lambda x: x[0])

    # parsed_results = [(trigger, sentiment, intensity) for _, trigger, sentiment, intensity in parsed_results]

    # parsed_results = [(change["trigger string"], change["sentiment"], change["strength"]) for change in results["changes"]]

    print(parsed_results)
    print("analysis done")

    return parsed_results