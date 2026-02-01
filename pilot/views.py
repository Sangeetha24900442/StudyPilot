import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import get_user_model,authenticate, login
from .models import StudyMaterial
from PyPDF2 import PdfReader
from django.contrib.auth.decorators import login_required




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
# PDF UPLOAD & PROCESSING
#---------------------------------------------------------------

def upload_material(request):
    material = None
    extracted_text = None

    if request.method == "POST":
        title = request.POST.get("title")
        pdf_file = request.FILES.get("pdf")

        material = StudyMaterial.objects.create(
            student=request.user,
            title=title,
            pdf=pdf_file
        )

        text = ""
        reader = PdfReader(material.pdf.path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        material.extracted_text = text
        material.cleaned_text = text.strip()
        material.save()

        extracted_text = text[:3000]

        messages.success(
            request,
            "PDF uploaded and text extracted successfully"
        )
        return redirect("material_view")

    return render(
        request,
        "pilot/upload_material.html",
        {
            "material": material,
            "extracted_text": extracted_text
        }
    )

def material_view(request):
    materials = StudyMaterial.objects.filter(
        student=request.user
    ).order_by("-uploaded_at")

    return render(
        request,
        "pilot/material_view.html",
        {
            "materials": materials
        }
    )
@login_required
def material_answer(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request method"})

    try:
        data = json.loads(request.body)
        material_id = data.get("material_id")

        material = StudyMaterial.objects.get(
            id=material_id,
            student=request.user
        )

        if not material.extracted_text:
            return JsonResponse({"reply": "No extracted text found."})

        prompt = f"""
Explain the following study notes in a very simple,
easy-to-understand way for a student.

Use bullet points if possible.

STUDY NOTES:
{material.extracted_text[:12000]}
"""

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-5.2-codex",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=40
        )

        result = response.json()

        # 🔴 SAFETY CHECK (THIS WAS MISSING)
        if "choices" not in result:
            return JsonResponse({
                "reply": "AI did not return a valid response."
            })

        reply = result["choices"][0]["message"]["content"]

        return JsonResponse({"reply": reply})

    except Exception as e:
        return JsonResponse({
            "reply": f"Error generating answer: {str(e)}"
        })
    
@login_required
def quiz_page(request, material_id):
    material = StudyMaterial.objects.get(
        id=material_id,
        student=request.user
    )

    return render(
        request,
        "pilot/quiz.html",
        {"material_id": material_id, "title": material.title}
    )


@login_required
def generate_quiz(request, material_id):
    material = StudyMaterial.objects.get(
        id=material_id,
        student=request.user
    )

    if not material.extracted_text:
        return JsonResponse({
            "error": "No extracted text found for this material."
        })

    prompt = f"""
You are an academic quiz generator.

Generate EXACTLY 5 multiple-choice questions
from the study notes below.

Rules:
- 4 options per question
- 1 correct answer
- Questions ONLY from the notes
- Return ONLY valid JSON

Format:
[
  {{
    "question": "Question text",
    "options": ["A", "B", "C", "D"],
    "answer": 0
  }}
]

STUDY NOTES:
{material.extracted_text[:12000]}
"""

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-5.2-codex",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=40
    )

    result = response.json()

    quiz = json.loads(
        result["choices"][0]["message"]["content"]
    )

    return JsonResponse({"quiz": quiz})

@login_required
def quiz_result(request, material_id):
    score = request.GET.get("score", 0)
    total = request.GET.get("total", 0)

    return render(
        request,
        "pilot/quiz_result.html",
        {"score": score, "total": total}
    )

def profile_page(request):
    return render(request, "pilot/profile.html")








# --------------------------------------------------------------
# CHAT INTEGRATION
#---------------------------------------------------------------

#OpenRouter API endpoint
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