from django.urls import path
from .views import FoodReservationView, ClassScheduleView, CourseSelectionView, ClassDeletionView, \
    StudentProfileUpdateView, CourseDetailView, TranscriptView, AttendanceView, ProfessorRatingView, \
    ExaminationScheduleView, MessageView, TermListView, StudentDetailView

urlpatterns = [
    path('food/reservation/<int:student_id>/<int:food_id>/', FoodReservationView.as_view(), name='food_reservation'),
    path('class/schedule/<int:student_id>/', ClassScheduleView.as_view(), name='class_schedule'),
    path('course/selection/<int:student_id>/<int:course_id>/', CourseSelectionView.as_view(), name='course_selection'),
    path('class/deletion/<int:student_id>/<int:class_id>/', ClassDeletionView.as_view(), name='class_deletion'),
    path('student/profile/update/<int:student_id>/', StudentProfileUpdateView.as_view(), name='student_profile_update'),
    path('course/detail/<int:course_id>/', CourseDetailView.as_view(), name='course_detail'),
    path('transcript/<int:student_id>/', TranscriptView.as_view(), name='transcript'),
    path('attendance/<int:student_id>/', AttendanceView.as_view(), name='attendance'),
    path('professor/rating/<int:student_id>/<int:professor_id>/', ProfessorRatingView.as_view(),
         name='professor_rating'),
    path('examination/schedule/<int:course_id>/', ExaminationScheduleView.as_view(), name='examination_schedule'),
    path('message/send/<int:sender_id>/<int:receiver_id>/', MessageView.as_view(), name='message_send'),
    path('terms/', TermListView.as_view(), name='term-list'),
    path('students/<str:student_id>/', StudentDetailView.as_view(), name='student-detail'),
]
