from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Show(models.Model):
    """A single title (series, film, or documentary) in the catalog."""

    class Genre(models.TextChoices):
        CRIME = "Crime", "Crime"
        SCI_FI = "Sci-Fi", "Sci-Fi"
        DRAMA = "Drama", "Drama"
        FANTASY = "Fantasy", "Fantasy"
        HORROR = "Horror", "Horror"
        COMEDY = "Comedy", "Comedy"
        ACTION = "Action", "Action"
        ANIME = "Anime", "Anime"
        DOCUMENTARY = "Documentary", "Documentary"
        ROMANCE = "Romance", "Romance"

    class Maturity(models.TextChoices):
        ALL = "ALL", "All Ages"
        PG13 = "PG-13", "PG-13"
        TV14 = "TV-14", "TV-14"
        TVMA = "TV-MA", "TV-MA"
        R = "R", "R"

    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    tagline = models.CharField(max_length=160, blank=True)
    description = models.TextField()
    genre = models.CharField(max_length=20, choices=Genre.choices, default=Genre.DRAMA)
    cast = models.CharField(
        max_length=300, blank=True, help_text="Comma-separated list of lead cast members"
    )
    creator = models.CharField(max_length=120, blank=True)
    release_year = models.PositiveIntegerField(default=2024)
    seasons = models.PositiveSmallIntegerField(default=1)
    maturity_rating = models.CharField(
        max_length=10, choices=Maturity.choices, default=Maturity.TV14
    )
    match_score = models.PositiveSmallIntegerField(
        default=90, help_text="Simulated 'percent match' shown to viewers (0-100)"
    )
    poster_url = models.URLField(max_length=500)
    backdrop_url = models.URLField(max_length=500, blank=True)
    netflix_url = models.URLField(max_length=500, blank=True)
    trending = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    top10_rank = models.PositiveSmallIntegerField(null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-added_on"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:140]
        super().save(*args, **kwargs)

    @property
    def cast_list(self):
        return [c.strip() for c in self.cast.split(",") if c.strip()]


class Profile(models.Model):
    """Extra sign-up details collected on Register, kept separate from auth.User."""

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"
        UNSPECIFIED = "prefer_not", "Prefer not to say"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=30, blank=True)
    gender = models.CharField(max_length=15, choices=Gender.choices, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=60, blank=True)
    newsletter_opt_in = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile<{self.user.username}>"


class ContactMessage(models.Model):
    """Messages submitted via the Contact page."""

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=120)
    message = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Feedback(models.Model):
    """Feedback submitted via the Feedback page."""

    class FeedbackType(models.TextChoices):
        BUG = "bug", "Bug Report"
        SUGGESTION = "suggestion", "Suggestion / Feature Request"
        COMPLIMENT = "compliment", "Compliment"
        OTHER = "other", "Other"

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    feedback_type = models.CharField(
        max_length=15, choices=FeedbackType.choices, default=FeedbackType.SUGGESTION
    )
    rating = models.PositiveSmallIntegerField(default=3)
    category = models.CharField(max_length=80, blank=True)
    message = models.TextField()
    may_contact = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return f"{self.full_name} ({self.get_feedback_type_display()})"
