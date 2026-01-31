import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "gpt-4o-mini",  # You can use other OpenRouter models
                "messages": [{"role": "user", "content": user_message}],
                "temperature": 0.7
            }

            response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
            result = response.json()

            # Extract the chatbot's reply
            reply = result.get("choices", [{}])[0].get("message", {}).get("content", "No response from OpenRouter")

            return JsonResponse({"reply": reply})

        except Exception as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"message": "Chatbot API running"})

# Chat page
def chat_page(request):
    return render(request, "pilot/chat.html")
