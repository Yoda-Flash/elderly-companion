import requests
from fastmcp import FastMCP
import json

mcp = FastMCP("Elderly Companion API Call Server")

@mcp.tool
def uselessFactOfTheDay() -> str:
    response = requests.get("https://api.viewbits.com/v1/uselessfacts?mode=today")
    try:
        return response.json()['text']
    except json.decoder.JSONDecodeError:
        return "Too many requests! Try again in a few seconds."

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)