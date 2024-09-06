from flask import Flask, request, jsonify
from g4f.client import Client
from fp.fp import FreeProxy

app = Flask(__name__)

def get_random_proxy():
    
    proxy = FreeProxy().get()
    return {"http": proxy, "https": proxy}

@app.route('/')
def hello_world():
    return '<h1>Hello World</h1>'

@app.route('/gpt4o', methods=['GET'])
def gpt4o():
    return get_ai_response("gpt-4o")

@app.route('/advance', methods=['POST'])
def advance():
    try:
        data = request.get_json()
        if not data or "messages" not in data:
            return jsonify({"error": "Invalid input, 'messages' field is required"}), 400

        client = Client()
        proxy = get_random_proxy()

        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=data["messages"],
            proxies=proxy  
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

def get_ai_response(model_name):
    try:
        prompt = request.args.get('prompt')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        client = Client()
        proxy = get_random_proxy()

        
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            proxies=proxy 
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
