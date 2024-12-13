import json
import re
import requests
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv(".env", override=True)
OPEN_WEATHER_APPID = os.getenv('OPEN_WEATHER_APPID')
if OPEN_WEATHER_APPID is None:
    raise Exception("OPEN_WEATHER_APPID is not set")

client = OpenAI(api_key="none", base_url="http://localhost:9008/v1")


def query(messages):
    chat_completion = client.chat.completions.create(
        model="/cache/Meta-Llama-3.1-8B-Instruct",
        messages=messages,
    )

    return chat_completion.choices[0].message.content.strip()


system_prompt = """You are a helpful and friendly climate expert."""
user_prompt = "What is the weather in Langebaan?"

weather_tool = {
    "name": "get_current_weather",
    "description": "Get the current weather in a given location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g. San Francisco, CA",
            },
        },
        "required": ["location"],
    },
}

tool_prompt = f"""You have access to the following functions:

Use the function '{weather_tool["name"]}' to '{weather_tool["description"]}':
{weather_tool}

If you choose to call a function ONLY reply in the following format with no prefix or suffix:

<function=example_function_name>{{"example_name": "example_value"}}</function>

Reminder:
- If looking for real time information use relevant functions before falling back to brave_search
- Function calls MUST follow the specified format, start with <function= and end with </function>
- Required parameters MUST be specified
- Only call one function at a time
- Put the entire function call reply on one line
"""

messages = [ 
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt},
    {"role": "user", "content": tool_prompt},
]

response = query(messages)
print("\n")
print(f"Model response:\t\t{response}")

def parse_tool_response(response: str):
    function_regex = r"<function=(\w+)>(.*?)</function>"
    match = re.match(function_regex, response)

    if match:
        function_name, args_string = match.groups()
        try:
            args = json.loads(args_string)
            return {
                "function_name": function_name,
                "args": args,
            }
        except json.JSONDecodeError as error:
            print(f"Error parsing function arguments: {error}")
            return None

    return None

parsed_response = parse_tool_response(response)
print(f"Parsed response:\t{parsed_response}")
print("\n")

def get_current_weather(location: str):
    api_url = "http://api.openweathermap.org/data/2.5/weather"
    api_params = {
        "q": location,
        "APPID": OPEN_WEATHER_APPID,
        "units": "metric",
    }

    response = requests.get(api_url, params=api_params)
    return response.json()

if parsed_response and parsed_response["function_name"] == weather_tool["name"]:
    args = parsed_response["args"]
    location = args["location"]
    weather_data = get_current_weather(location)
    print(f"Weather data for {location}:")
    print(json.dumps(weather_data, indent=4))
else:
    print("Function call not recognized.")
print("\n")

system_prompt = """You are a helpful and friendly climate expert.

Answer the user's question by using the data provided."""
user_prompt = "What is the weather in Langebaan?"
context_prompt = json.dumps(weather_data)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt},
    {"role": "user", "content": context_prompt},
]

response = query(messages)
print(f"Final response:\t\t{response}")
print("\n")
