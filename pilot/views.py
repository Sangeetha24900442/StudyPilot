import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import get_user_model,authenticate, login



User = get_user_model()

# ---------- PAGE VIEWS ----------

def home(request):
    return render(request, "pilot/home.html")

def login_page(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid email or password")
        return redirect("login")

    return render(request, "pilot/login.html")


def register_page(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        if hasattr(user, "full_name"):
            user.full_name = name
            user.save()

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(request, "pilot/register.html")

def dashboard(request):
    return render(request, "pilot/dashboard.html")












# --------------------------------------------------------------
# CHAT INTEGRATION
#---------------------------------------------------------------

# OpenRouter API endpoint
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        try:
            # Load user message from request
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"reply": "Please enter a message."})

            # Debug: print API key to check if loaded (remove in production)
            print("OpenRouter API Key:", settings.OPENROUTER_API_KEY)

            # Headers for OpenRouter request
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            # Payload for the API
            payload = {
                "model": "gpt-4o-mini",  # Change model if needed
                "messages": [{"role": "user", "content": user_message}],
                "temperature": 0.7
            }

            # Send POST request to OpenRouter
            response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)

            # Debug: print raw response
            print("OpenRouter raw response:", response.text)

            # Parse response JSON
            result = response.json()

            # Extract chatbot reply safely
            reply = result.get("choices", [{}])[0].get("message", {}).get("content", None)

            if not reply:
                # Return full API response for debugging if reply is empty
                return JsonResponse({
                    "reply": "No response from OpenRouter",
                    "debug": result
                })

            # Return the chatbot reply
            return JsonResponse({"reply": reply})

        except Exception as e:
            # Return any exceptions
            return JsonResponse({"error": str(e)})

    # If GET request
    return JsonResponse({"message": "Chatbot API running"})

# Render chat page
def chat_page(request):
    return render(request, "pilot/chat.html")