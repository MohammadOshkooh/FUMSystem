from rest_framework.generics import UpdateAPIView, ListAPIView, RetrieveAPIView
from app.models import *
from .serializers import CourseSerializer, StudentSerializer, ClassSerializer, TermSerializer

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class FoodReservationView(APIView):
    def post(self, request, student_id, food_id):
        student = get_object_or_404(Student, student_id=student_id)
        food = get_object_or_404(Food, id=food_id)

        if food in student.foodreservation_set.all():
            return Response({"message": "Food already reserved by the student"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a FoodReservation object
        reservation = FoodReservation(student=student, food=food, is_taken=False)
        reservation.save()

        return Response({"message": "Food reserved successfully"}, status=status.HTTP_201_CREATED)

    def delete(self, request, student_id, food_id):
        student = get_object_or_404(Student, student_id=student_id)
        food = get_object_or_404(Food, id=food_id)

        reservation = get_object_or_404(FoodReservation, student=student, food=food)

        reservation.delete()

        return Response({"message": "Food reservation deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# مشاهده برنامه کلاسی
class ClassScheduleView(APIView):
    def get(self, request, student_id):
        student = get_object_or_404(Student, student_id=student_id)
        courses = student.courses_taken.all()
        class_schedule = []

        for course in courses:
            class_schedule.append({
                'course_code': course.code,
                'course_title': course.title,
                'professor': f'{course.professor.first_name} {course.professor.last_name}',
                'class_number': course.class_set.first().room.name,
                # 
            })

        return Response(class_schedule, status=status.HTTP_200_OK)


# انتخاب واحد
class CourseSelectionView(APIView):
    def post(self, request, student_id, course_id):
        student = get_object_or_404(Student, student_id=student_id)
        course = get_object_or_404(Course, id=course_id)

        if course in student.courses_taken.all():
            return Response({"message": "Course already selected"}, status=status.HTTP_400_BAD_REQUEST)

        # else add course
        course.students.add(student)

        return Response({"message": "Course selected successfully"}, status=status.HTTP_201_CREATED)

    def delete(self, request, student_id, course_id):
        student = get_object_or_404(Student, student_id=student_id)
        course = get_object_or_404(Course, id=course_id)

        if course not in student.courses_taken.all():
            return Response({"message": "Course not selected by the student"}, status=status.HTTP_400_BAD_REQUEST)

        # else remove course
        course.students.remove(student)

        return Response({"message": "Course deselected successfully"}, status=status.HTTP_204_NO_CONTENT)


# حذف تکدرس در زمان مشخص
class ClassDeletionView(APIView):
    def delete(self, request, student_id, class_id):
        student = get_object_or_404(Student, student_id=student_id)
        class_obj = get_object_or_404(Class, id=class_id)

        if class_obj.course not in student.courses_taken.all():
            return Response({"message": "Student is not enrolled in the course"}, status=status.HTTP_400_BAD_REQUEST)

        # remove student from class
        class_obj.students.remove(student)

        return Response({"message": "Class deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# ویرایش مشخصات فردی

class StudentProfileUpdateView(UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'student_id'


# مشاهده هر واحد درسی
class CourseDetailView(APIView):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        class_list = []

        for class_obj in course.class_set.all():
            class_list.append({
                'class_number': class_obj.room.name,
                'professor': f'{class_obj.course.professor.first_name} {class_obj.course.professor.last_name}',
                'department': class_obj.course.professor.department,
                'course_title': class_obj.course.title
            })

        return Response(class_list, status=status.HTTP_200_OK)


# مشاهده کارنامه
class TranscriptView(APIView):
    def get(self, request, student_id):
        student = get_object_or_404(Student, student_id=student_id)
        grades = Grade.objects.filter(student=student)
        transcript = []

        for grade in grades:
            transcript.append({
                'course_code': grade.course.code,
                'course_title': grade.course.title,
                'grade': grade.grade
            })

        return Response(transcript, status=status.HTTP_200_OK)


# مشاهده حضور و غیاب های خود 
class AttendanceView(APIView):
    def get(self, request, student_id):
        student = get_object_or_404(Student, student_id=student_id)
        attendances = Attendance.objects.filter(student=student)
        attendance_list = []

        for attendance in attendances:
            attendance_list.append({
                'class_number': attendance.class_num.room.name,
                'date': attendance.date,
                'is_present': attendance.is_present
            })

        return Response(attendance_list, status=status.HTTP_200_OK)


# ارزشیابی اساتید
class ProfessorRatingView(APIView):
    def post(self, request, student_id, professor_id):
        student = get_object_or_404(Student, student_id=student_id)
        professor = get_object_or_404(Professor, professor_id=professor_id)
        rating = request.data.get('rating')

        professor_rating = ProfessorRating.objects.get_or_create(student=student, professor=professor)
        professor_rating.rating = rating
        professor_rating.save()

        return Response({"message": "Professor rating saved successfully"}, status=status.HTTP_201_CREATED)


# مشاهده برنامه امتحانی
class ExaminationScheduleView(APIView):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        exam_schedule = ExaminationSchedule.objects.filter(course=course)
        schedule_list = []

        for exam in exam_schedule:
            schedule_list.append({
                'date': exam.date,
                'room': exam.room.name,
                'seat_number': exam.seat_number,
                'description': exam.description
            })

        return Response(schedule_list, status=status.HTTP_200_OK)


class MessageView(APIView):
    def post(self, request, sender_id, receiver_id):
        sender = get_object_or_404(Student, id=sender_id)
        receiver = get_object_or_404(Professor, id=receiver_id)
        message_text = request.data.get('message_text')

        message = Messages(sender=sender, receiver=receiver, message_text=message_text)
        message.save()

        return Response({"message": "Message sent successfully"}, status=status.HTTP_201_CREATED)


class TermListView(ListAPIView):
    queryset = Term.objects.all()
    serializer_class = TermSerializer


class StudentDetailView(RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'student_id'
    lookup_url_kwarg = 'student_id'


class StudentsWithAlifView(ListAPIView):
    serializer_class = StudentSerializer

    def get_queryset(self):
        year_of_entry = self.request.query_params.get('year_of_entry', None)
        if year_of_entry is not None:
            queryset = Student.objects.filter(grade__grade__gt=17, term__academic_year=year_of_entry)
        else:
            queryset = Student.objects.none()
        return queryset
