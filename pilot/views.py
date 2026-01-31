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










# --------------------------------------------------------------
# CHAT INTEGRATION
#---------------------------------------------------------------

# OpenRouter API endpoint
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        try:
            # 🔹 Load request data (material id)
            data = json.loads(request.body)
            material_id = data.get("material_id")

            if not material_id:
                return JsonResponse({
                    "reply": "Material not specified."
                })

            # 🔹 Fetch the material
            material = StudyMaterial.objects.get(
                id=material_id,
                student=request.user
            )

            extracted_text = material.extracted_text.strip()

            if not extracted_text:
                return JsonResponse({
                    "reply": "No extracted text available for this material."
                })

            # 🔹 THIS IS THE PROMPT (your requirement)
            prompt = f"""
You are a study assistant.

Analyze the following extracted study notes and do the following:
- Explain the content clearly
- Summarize key points
- Keep it simple and exam-oriented

STUDY NOTES:
{extracted_text[:12000]}
"""

            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }

            response = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=30
            )

            result = response.json()
            reply = result.get("choices", [{}])[0].get(
                "message", {}
            ).get("content")

            if not reply:
                return JsonResponse({
                    "reply": "No response from AI."
                })

            return JsonResponse({"reply": reply})

        except StudyMaterial.DoesNotExist:
            return JsonResponse({
                "reply": "Material not found."
            })

        except Exception as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"message": "Chatbot API running"})

# Render chat page
def chat_page(request):
    return render(request, "pilot/chat.html")