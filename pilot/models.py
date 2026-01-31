from django.db import models
from django.contrib.auth.models import AbstractUser

# ==================================================
# STUDENT (CUSTOM USER)
# ==================================================
class Student(AbstractUser):
    total_points = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    level = models.CharField(max_length=20, default="Beginner")

    def __str__(self):
        return self.username


# ==================================================
# STUDY MATERIAL (PDF)
# ==================================================
class StudyMaterial(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    pdf = models.FileField(upload_to="pdfs/")
    extracted_text = models.TextField(blank=True)
    cleaned_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ==================================================
# TOPICS & CONCEPTS
# ==================================================
class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Concept(models.Model):
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    difficulty = models.IntegerField(default=1)
    weight = models.FloatField(default=1.0)

    def __str__(self):
        return self.name


# ==================================================
# KNOWLEDGE GRAPH
# ==================================================
class ConceptRelation(models.Model):
    RELATION_CHOICES = [
        ('prerequisite', 'Prerequisite'),
        ('similar', 'Similar'),
        ('same_topic', 'Same Topic'),
    ]

    from_concept = models.ForeignKey(
        Concept, related_name='from_concept', on_delete=models.CASCADE
    )
    to_concept = models.ForeignKey(
        Concept, related_name='to_concept', on_delete=models.CASCADE
    )
    relation_type = models.CharField(max_length=20, choices=RELATION_CHOICES)

    def __str__(self):
        return f"{self.from_concept} → {self.to_concept}"


# ==================================================
# QUIZ SYSTEM
# ==================================================
class Question(models.Model):
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1)
    difficulty = models.IntegerField()

    def __str__(self):
        return self.question_text[:50]


class QuizAttempt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.IntegerField()
    time_taken = models.IntegerField()  # seconds
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.score}"


# ==================================================
# PERFORMANCE ANALYTICS
# ==================================================
class ConceptPerformance(models.Model):
    STATUS_CHOICES = [
        ('weak', 'Weak'),
        ('average', 'Average'),
        ('strong', 'Strong'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    mastery = models.FloatField(default=0.0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.student} - {self.concept} ({self.status})"


# ==================================================
# REVISION RECOMMENDATION
# ==================================================
class RevisionRecommendation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    priority = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.student} → {self.concept}"


# ==================================================
# GAMIFICATION
# ==================================================
class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class StudentBadge(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.badge}"


# ==================================================
# LEARNING SESSIONS
# ==================================================
class LearningSession(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    duration = models.IntegerField()  # seconds

    def __str__(self):
        return f"{self.student} - {self.date}"


# ==================================================
# CHATBOT HISTORY
# ==================================================
class ChatHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:40]