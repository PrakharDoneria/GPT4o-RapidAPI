from flask import Flask, request, jsonify
from g4f.client import Client
from apxr import AsyncProxier
import asyncio
from curl_cffi.requests import AsyncSession

app = Flask(__name__)

# Initialize AsyncProxier with desired settings (e.g., US proxies, HTTPS, anonymous)
proxier = AsyncProxier(country_id=['US'], https=True, anonym=True)

async def get_random_proxy():
    # Fetch and return an updated working proxy
    return await proxier.update()

async def fetch_with_proxy(url):
    # Perform an HTTP request using a proxy
    proxy = await get_random_proxy()
    async with AsyncSession(proxy=proxy) as session:
        try:
            response = await session.get(url)
            if response.status_code == 200:
                return response.text
            else:
                raise Exception('Proxy Error')
        except Exception as e:
            print(f"Proxy request failed: {str(e)}")
            # Update proxy on failure and retry
            await proxier.update(True)
            return None

@app.route('/')
def hello_world():
    return '<h1>Hello World</h1>'

@app.route('/gpt4o', methods=['GET'])
def gpt4o():
    # Run the async function in a synchronous Flask route
    result = asyncio.run(get_ai_response("gpt-4o"))
    return result

@app.route('/advance', methods=['POST'])
def advance():
    data = request.get_json()
    if not data or "messages" not in data:
        return jsonify({"error": "Invalid input, 'messages' field is required"}), 400

    try:
        result = asyncio.run(handle_advance(data["messages"]))
        return result
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

async def handle_advance(messages):
    try:
        client = Client()
        # Get the proxy and make a request to your AI service
        proxy = await get_random_proxy()
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            # Assuming client supports proxy use in some way
            proxies={"http": proxy, "https": proxy}
        )

        if response.choices:
            return jsonify({"response": response.choices[0].message.content})
        else:
            return jsonify({"error": "Failed to get response from the model"}), 500
    except KeyError as e:
        return jsonify({"error": f"KeyError: {str(e)}"}), 500
    except ValueError as e:
        return jsonify({"error": f"ValueError: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

async def get_ai_response(model_name):
    try:
        prompt = request.args.get('prompt')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        client = Client()
        proxy = await get_random_proxy()

        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            proxies={"http": proxy, "https": proxy}
        )

        if response.choices:
            return jsonify({"response": response.choices[0].message.content})
        else:
            return jsonify({"error": f"Failed to get response from {model_name}"}), 500
    except KeyError as e:
        return jsonify({"error": f"KeyError: {str(e)}"}), 500
    except ValueError as e:
        return jsonify({"error": f"ValueError: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)