# serializers.py
from rest_framework import serializers
from app.models import Messages, Course, Student, Class, Professor, Term


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ['sender', 'receiver', 'subject', 'content', 'timestamp']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class StudentPassCourseSerializer(serializers.ModelSerializer):
    passed_courses = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['student_id', 'passed_courses']

    def get_passed_courses(self, obj):
        return obj.get_passed_courses()


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'


class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ['professor_id', 'first_name', 'last_name']


class TermSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)
    professors = ProfessorSerializer(many=True, read_only=True)

    class Meta:
        model = Term
        fields = ['academic_year', 'semester', 'courses', 'professors']


