from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import Add_Question, signup
from . import views
from rest_framework.routers import DefaultRouter
from django.urls import re_path
from django.views.static import serve

router = DefaultRouter()

urlpatterns = [
    # path('', include(router.urls)),
    path('', views.home, name='home'),
    path('api/', include(router.urls)), 
    path('signup/', views.signup, name='signup'),
    path('home/', views.home, name='home'),
    path('home_student/', views.home_student, name='home_student'),
    # path('student-view/', views.upload_answer, name='student_dashboard'),
    path('add_question/', Add_Question.as_view(), name='add_question'),
    path('question-bank/', views.question_bank, name='question_bank'),
    path('generate-test/', views.generate_test, name='generate_test'),
    path('download-test-pdf/', views.download_test_pdf, name='download_test_pdf'),
    # path('upload-xml/', views.upload_xml, name='upload_xml'),
    path('upload-file/', views.upload_file, name='upload_file'),
    path('upload_answer/', views.upload_answer, name='upload_answer'),
    path('download_answer_key/', views.download_answer_key, name='download_answer_key'),
    path('download_exam_results/', views.download_exam_results, name='download_exam_results'),
    path('login/', views.login_view, name='login'),
    path('get_exam_id_suggestions', views.get_exam_id_suggestions, name='get_exam_id_suggestions'),
    path('logout/', views.logout_view, name='logout'),
    path('answer_sheet/', views.answer_sheet_view, name='answer_sheet'),
    path('online-answer-test/', views.online_answer_test, name='online_answer_test'),
    path('answer_online_exam/', views.answer_online_exam, name='answer_online_exam'),
    path('exam_form/<str:set_id>/', views.exam_form, name='exam_form'),
    path('result/<int:result_id>/', views.result_page, name='result_page'),
    path('warning/', views.warning_page, name='warning_page'),
    path('get_subjects/', views.get_subjects, name='get_subjects'),
    path('get_testkeys_by_subject/', views.get_testkeys_by_subject, name='get_testkeys_by_subject'),
    path('download-answer/', views.download_answer_page, name='download_answer_page'),
    path('download_exam_results_page/', views.download_exam_results_page, name='download_exam_results_page'),
    path('download_exam_results/', views.download_exam_results, name='download_exam_results'),
    path('get_board_exams/', views.get_board_exams, name='get_board_exams'),
    path('get_subjects_by_board_exam/', views.get_subjects_by_board_exam, name='get_subjects_by_board_exam'),
    path('get_topics_by_subject/', views.get_topics_by_subject, name='get_topics_by_subject'),
    path('get_testkeys_by_topic/', views.get_testkeys_by_topic, name='get_testkeys_by_topic'),
    path('download_test_interface/', views.download_test_interface, name='download_test_interface'),
    path('download_existing_test_pdf/', views.download_existing_test_pdf, name='download_existing_test_pdf'),
    path('view-results/', views.view_results, name='view_results'),
    path('qanalytics/', views.question_analytics, name='question_analytics'),
    path('tanalytics/', views.test_analytics, name='test_analytics'),
    path('practice/start/', views.practice_start, name='practice_start'),
    path('practice/take/<uuid:session_id>/', views.practice_take, name='practice_take'),
    path('practice/submit/<uuid:session_id>/', views.practice_submit, name='practice_submit'),
    path('practice/result/<uuid:session_id>/', views.practice_result_page, name='practice_result_page'),
    path('answer-test-preview/<subject>/<board_exam>/<set_a_id>/<set_b_id>/', views.answer_test_preview, name='answer_test_preview'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     urlpatterns += [
#         re_path(r'^' + settings.MEDIA_URL.lstrip('/') + r'(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
#     ]
