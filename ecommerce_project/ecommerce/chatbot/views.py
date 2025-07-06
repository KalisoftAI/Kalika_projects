# chatbot/views.py
import os
import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Configure the Gemini API with your API key
# Ensure GEMINI_API_KEY is loaded from environment variables in settings.py
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY not found. Chatbot functionality may be limited.")

# Initialize the Gemini model (using gemini-2.0-flash as per instructions)
# It's good practice to initialize this once globally or per request as needed.
model = genai.GenerativeModel('gemini-2.0-flash')

@csrf_exempt # Use this decorator for simplicity, but consider more robust CSRF handling for production APIs
def chat_with_gemini(request):
    """
    Handles chat messages, interacts with the Gemini API, and returns responses.
    Maintains chat history in the session.
    """
    if request.method == 'POST':
        try:
            # Get the message from the frontend (expecting JSON payload)
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()

            if not user_message:
                return JsonResponse({'error': 'No message provided.'}, status=400)

            # Retrieve or initialize chat history from session
            # This acts as our "Model Context Protocol" (MCP) server for maintaining context
            chat_history = request.session.get('chat_history', [])

            # Start a chat session with the model
            # The `start_chat` method handles the context management for the model
            convo = model.start_chat(history=chat_history)

            # Send the user message to the Gemini model
            response = convo.send_message(user_message)

            # Update chat history in the session for future interactions
            # We store the parts that `start_chat` expects: role and parts (text)
            chat_history.append({"role": "user", "parts": [{"text": user_message}]})
            chat_history.append({"role": "model", "parts": [{"text": response.text}]})
            request.session['chat_history'] = chat_history

            # Return the bot's response
            return JsonResponse({'response': response.text})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)
        except Exception as e:
            # Log the error for debugging
            print(f"Error during Gemini API call: {e}")
            return JsonResponse({'error': 'An error occurred while processing your request. Please try again.'}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)

# You can add another view to clear chat history if needed
def clear_chat_history(request):
    """
    Clears the chat history from the session.
    """
    if 'chat_history' in request.session:
        del request.session['chat_history']
    return JsonResponse({'message': 'Chat history cleared.'})