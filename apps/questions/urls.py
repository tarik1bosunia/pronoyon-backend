from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.questions.views import (
    ClassViewSet,
    SubjectViewSet,
    ChapterViewSet,
    TopicViewSet,
    QuestionViewSet,
    UserDraftViewSet
)

app_name = 'questions'

router = DefaultRouter()
router.register(r'classes', ClassViewSet, basename='class')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'drafts', UserDraftViewSet, basename='draft')

urlpatterns = [
    path('', include(router.urls)),
]
