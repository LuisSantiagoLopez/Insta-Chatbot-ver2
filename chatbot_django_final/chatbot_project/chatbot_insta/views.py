from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Ideas
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate
from chatbotpf.create_idea import trends, create_idea


def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "signup.html")

        user = User.objects.create_user(username, email, password)
        user.save()

        return redirect("signin")

    return render(request, "signup.html")


def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)

        if user is not None:
            print("User authenticated and logged in successfully.")
            login(request, user)
            return redirect("chatbot")

        else:
            print(
                f"Failed to authenticate user with username {username} and password {password}."
            )
            messages.error(request, "Bad credentials")
            return redirect("home")

    return render(request, "signin.html")


def signout(request):
    return render(request, "signout.html")


@login_required
def chatbot_view(request):
    if request.method == "GET":
        return render(request, "chat.html")

    elif request.method == "POST":
        if not request.body:
            return JsonResponse({"error": "Empty request body"}, status=400)
        try:
            data = json.loads(request.body)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Retrieve the necessary data from the request
        action = data.get("action")

        # Based on the action, call the appropriate view function
        if action == "create_idea":
            response = create_idea_view(request)
        elif action == "choose_another_idea":
            response = choose_another_idea(request)
        elif action == "normalize_idea":
            response = normalize_idea(request)
        elif action == "manipulate_idea":
            response = manipulate_idea(request)
        else:
            return JsonResponse({"error": "Invalid action"}, status=400)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


@login_required
@require_POST
def create_idea_view(request):
    trends = trends_view(request)
    result = create_idea(request, trends)

    # Create a new instance in the Ideas model
    for idea in result["three_ideas"]:
        Ideas.objects.create(
            user=request.user,
            instagram_idea=idea["Instagram Idea"],
            caption=idea["Caption"],
            illustration=idea["Illustration"],
            News=idea["News"],
        )

        # Get the last 3 ideas added to the database for the current user
        latest_ideas = Ideas.objects.filter(user=request.user).order_by("-user_id")[:3]

        # Prepare the data for JSON response
        ideas_data = [
            [idea.instagram_idea, idea.illustration, idea.caption]
            for idea in latest_ideas
        ]

        # Return JSON data
        return JsonResponse({"ideas": ideas_data})


@login_required
def trends_view(request):
    # Call the trends function
    trends_results = trends(request)

    # Return JSON data
    return JsonResponse({"trends": trends_results})


@login_required
@require_POST
def choose_another_idea(request):
    # Extract the data from the request
    data = json.loads(request.body)
    user = data.user

    # Get the current idea
    current_idea = Ideas.objects.filter(user=user, chosen=True).first()

    # If there is a current idea, set it to not chosen
    if current_idea:
        current_idea.chosen = False
        current_idea.save()

    # Get the new idea
    new_idea = Ideas.objects.filter(user=user, chosen=False).first()

    # If there is a new idea, set it to chosen
    if new_idea:
        new_idea.chosen = True
        new_idea.save()
        return JsonResponse({"message": "Idea chosen successfully"}, status=200)
    else:
        return JsonResponse({"error": "No more ideas available"}, status=400)


@login_required
@require_POST
def normalize_idea(request):
    user_idea = request.POST.get("user_idea")
    target_segment = request.POST.get("target_segment")
    program_description = request.POST.get("program_description")

    # Call the normalize_idea function
    result = normalize_idea(user_idea, target_segment, program_description)

    # Render the template to show the normalized idea
    return JsonResponse({"idea": result["idea"]})


@login_required
@require_POST
def manipulate_idea(request):
    user_idea = request.POST.get("user_idea")

    # Call the manipulate_idea function
    result = manipulate_idea(user_idea)

    # Render the template to show the manipulated idea
    return JsonResponse({"idea": result["idea"]})
