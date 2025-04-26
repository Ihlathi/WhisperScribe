from openai import OpenAI
import json

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

def analyse_text(book_snippet):
    messages = [
        {"role": "system", "content": 
         """You are an AI that helps create ambient music for readers based on the book content they are currently reading. Your task is to suggest music changes based on the tone and atmosphere of the text. You do not include anything else in your responses but the expected data output. You cannot use markdown or unicode signs.
        Use the following for your responses:
         - trigger string should be a short but unique string of words for identifying where the music change should occur
         - sentiment should be one of the following descriptive sentiments (do not include the number):
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
         - order your responses in the order they occur in the text: first occurrance comes first... else it will not work
         - be quite sparse about your music changes. You don't want to disturb the reader, instead provide them with a nice ambient reading experience. If there is nothing notable happening, revert to neutral with an appropriate intensity (could be 5)
         """},
        {"role": "user", "content": f"Based on the following text, suggest music that matches the tone and atmosphere: {book_snippet}"}
    ]

    sentiment_schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "music changes",
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

    parsed_results = [(change["trigger string"], change["sentiment"], change["strength"]) for change in results["changes"]]

    print(json.dumps(results, indent=2))
    print(parsed_results)

    return parsed_results

if __name__ == "__main__":
    print("hi")
    index = analyse_text("am convinced that it is the will of Heaven that all mankind should live as one family. This is brilliant, Daniella writes in response to my turnaround. You are so wonderfully easy to work with. Most authors are pickier about killing their darlings. This makes me beam. I want my editor to like me. I want her to think I’m easy to work with, that I’m not a stubborn diva, that I’m capable of making any changes she asks for. It’ll make her more likely to sign me on for future projects. It’s not all about pandering to authority. I do think we’ve made the book better, more accessible, more streamlined. The original draft made you feel dumb, alienated at times, and frustrated with the self-righteousness of it all. It stank of all the most annoying things about Athena. The new version is a universally relatable story, a story that anyone can see themselves in. The whole process takes three editorial rounds over four months. By the end, I’ve become so familiar with the project that I can’t tell where Athena ends and I begin, or which words belong to whom. I’ve done the research. I’ve read a dozen books now on Asian racial politics and the history of Chinese labor at the front. I’ve lingered over every word, every sentence, and every paragraph so many times that I nearly know them by heart—hell, I’ve probably been over this novel more times than Athena herself. What this whole experience teaches me is that I can write. Some of Daniella’s favorite passages are the ones original to me. There’s one part, for instance, where a poor French family wrongly accuses a group of Chinese laborers of stealing a hundred francs from their house. The laborers, determined to make a good impression of their race and nation, collect two hundred francs among them and gift it to the family even though it’s clear they are innocent. Athena’s draft only made a brief mention of the wrongful accusation, but my version turns it into a heartwarming illustration of Chinese virtue and honesty. All of my confidence and verve, dashed after my horrific debut experience, come rushing back. I’m brilliant with words. I’ve studied writing for nearly a decade now; I know what makes a direct, punchy sentence, and I know how to structure a story so that the reader stays riveted all the way through. I’ve labored for years to learn my craft. Perhaps the core idea of this novel wasn’t mine, but I’m the one who rescued it, who freed the diamond from the rough. But the thing is, no one will ever understand how much I put into this novel. If news ever breaks that Athena wrote the first draft, the whole world will look at all the work I did, all those beautiful sentences I produced, and all they’ll ever see is Athena Liu. But no one ever has to know, do they? THE BEST WAY TO HIDE A LIE IS IN PLAIN SIGHT. I lay the groundwork long before the novel is out, before early versions of it are off to reviewers and book bloggers. I’ve never made a secret of my relationship to Athena, and I’m even less subtle about it now. I am, after all, currently best known as the person who was at her side when she died. So I play up our connection. I mention her name in every interview. My grief over her death becomes a cornerstone of my origin story. All right, maybe I exaggerate the details a bit. Quarterly drinks become monthly")
