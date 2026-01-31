from django.contrib import admin
from .models import *


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'total_points', 'streak', 'level')
    search_fields = ('username', 'email')


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'uploaded_at')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic', 'difficulty', 'weight')
    list_filter = ('difficulty', 'topic')


@admin.register(ConceptRelation)
class ConceptRelationAdmin(admin.ModelAdmin):
    list_display = ('from_concept', 'relation_type', 'to_concept')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'concept', 'difficulty')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'score', 'time_taken', 'created_at')


@admin.register(ConceptPerformance)
class ConceptPerformanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'concept', 'mastery', 'status')


@admin.register(RevisionRecommendation)
class RevisionRecommendationAdmin(admin.ModelAdmin):
    list_display = ('student', 'concept', 'priority')


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    list_display = ('student', 'badge', 'earned_at')


@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'duration')


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'created_at')