import json
from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import redirect, render

from .models import ContactMessage, Feedback, Profile, Show


def _show_payload(show):
    """Small dict used for the client-side search / modal / My List logic."""
    return {
        "id": show.id,
        "title": show.title,
        "tagline": show.tagline,
        "description": show.description,
        "genre": show.genre,
        "cast": show.cast_list,
        "creator": show.creator,
        "release_year": show.release_year,
        "seasons": show.seasons,
        "maturity_rating": show.maturity_rating,
        "match_score": show.match_score,
        "poster_url": show.poster_url,
        "backdrop_url": show.backdrop_url or show.poster_url,
        "netflix_url": show.netflix_url,
        "trending": show.trending,
        "top10_rank": show.top10_rank,
    }


def home(request):
    shows = list(Show.objects.all())

    if not shows:
        context = {"shows_json": "[]", "genre_rows": [], "top10": [], "hero_shows": []}
        return render(request, "index.html", context)

    hero_shows = [s for s in shows if s.featured] or shows[:5]
    top10 = sorted(
        [s for s in shows if s.top10_rank],
        key=lambda s: s.top10_rank,
    )[:10]
    trending = [s for s in shows if s.trending]

    genre_rows = []
    if trending:
        genre_rows.append({"label": "Trending Now", "shows": trending})
    for genre_value, genre_label in Show.Genre.choices:
        genre_shows = [s for s in shows if s.genre == genre_value]
        if genre_shows:
            genre_rows.append({"label": f"{genre_label} Picks", "shows": genre_shows})

    context = {
        "shows_json": json.dumps([_show_payload(s) for s in shows], cls=DjangoJSONEncoder),
        "genre_rows": genre_rows,
        "top10": top10,
        "hero_shows": hero_shows,
        "genres": Show.Genre.choices,
        "total_shows": len(shows),
    }
    return render(request, "index.html", context)


def my_list(request):
    """The 'My List' page. The actual list lives client-side (localStorage) and
    is rendered with JS against the full catalog embedded below."""
    shows = list(Show.objects.all())
    context = {
        "shows_json": json.dumps([_show_payload(s) for s in shows], cls=DjangoJSONEncoder),
    }
    return render(request, "MyList.html", context)


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "Login.html")


def logout_view(request):
    auth_logout(request)
    messages.success(request, "You've been signed out. See you soon!")
    return redirect("home")


def about(request):
    return render(request, "About.html", {"total_shows": Show.objects.count()})


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        subject = request.POST.get("subject", "").strip()
        message_text = request.POST.get("message", "").strip()

        if name and email and subject and message_text:
            ContactMessage.objects.create(
                name=name, email=email, phone=phone, subject=subject, message=message_text
            )
            messages.success(
                request, "Thanks! Your message has been sent — our team will get back to you soon."
            )
            return redirect("contact")
        messages.error(request, "Please fill in all required fields before sending.")

    return render(request, "Contact.html")


def form_view(request):
    if request.method == "POST":
        full_name = request.POST.get("fullName", "").strip()
        email = request.POST.get("email", "").strip()
        feedback_type = request.POST.get("feedbackType", Feedback.FeedbackType.SUGGESTION)
        rating = request.POST.get("rating", 3)
        category = request.POST.get("category", "").strip()
        message_text = request.POST.get("message", "").strip()
        may_contact = bool(request.POST.get("consent"))

        if full_name and email and message_text:
            Feedback.objects.create(
                full_name=full_name,
                email=email,
                feedback_type=feedback_type,
                rating=rating or 3,
                category=category,
                message=message_text,
                may_contact=may_contact,
            )
            messages.success(request, "Thank you! Your feedback helps us improve Netflix Tudum.")
            return redirect("form")
        messages.error(request, "Please complete the required fields before submitting.")

    return render(request, "form.html")


def register(request):
    if request.method == "POST":
        first_name = request.POST.get("firstName", "").strip()
        last_name = request.POST.get("lastName", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirmPassword", "")
        gender = request.POST.get("gender", "")
        country = request.POST.get("country", "")
        newsletter = bool(request.POST.get("newsletter"))
        month = request.POST.get("month")
        day = request.POST.get("day")
        year = request.POST.get("year")

        errors = []
        if not (first_name and last_name and email and password):
            errors.append("Please fill in all required fields.")
        if password and password != confirm_password:
            errors.append("Passwords do not match.")
        if password and len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if email and User.objects.filter(username=email).exists():
            errors.append("An account with this email already exists.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "Register.html")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        dob = None
        try:
            months = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December",
            ]
            if month in months and day and year:
                dob = date(int(year), months.index(month) + 1, int(day))
        except (ValueError, TypeError):
            dob = None

        Profile.objects.create(
            user=user,
            phone=phone,
            gender=gender,
            date_of_birth=dob,
            country=country,
            newsletter_opt_in=newsletter,
        )

        messages.success(request, "Account created! You can now sign in.")
        return redirect("login")

    return render(request, "Register.html")


def home_page(request):
    return redirect("my_list")
