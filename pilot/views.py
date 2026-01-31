import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import get_user_model,authenticate, login



User = get_user_model()

# ---------- PAGE VIEWS ----------

def home(request):
    return render(request, "pilot/dashboard.html")

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

        # Optional: store full name properly
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
