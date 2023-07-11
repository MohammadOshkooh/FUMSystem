from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Student(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=25)
    student_id = models.CharField(max_length=10, unique=True)
    courses = models.ManyToManyField('Course', related_name='enrolled_students', blank=True)
    balance = models.CharField(max_length=15)
    total_credits_taken = models.IntegerField()
    term = models.ForeignKey('Term', on_delete=models.CASCADE)

    def __str__(self):
        return self.student_id

    def get_passed_courses(self):
        passed_courses = self.courses.filter(grade__grade__gte=10)
        course_numbers = passed_courses.values_list('code', flat=True)
        return course_numbers


class Professor(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=25)
    professor_id = models.CharField(max_length=10, unique=True)
    department = models.CharField(max_length=50)

    def __str__(self):
        return self.professor_id


class Term(models.Model):
    academic_year = models.PositiveIntegerField()
    semester = models.CharField(max_length=10, choices=[
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ])
    credits_taken = models.PositiveIntegerField(default=0)
    overall_gpa = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.academic_year} - {self.get_semester_display()}"


class Food(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    meal = models.CharField(choices=(('lunch', 'lunch'), ('breakfast', 'breakfast'), ('dinner', 'dinner')),
                            max_length=15)
    day = models.CharField(max_length=15, choices=[
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ])
    date = models.DateTimeField()

    def __str__(self):
        return self.name


class FoodReservation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    is_taken = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.is_taken:
            student = self.student
            student.balance -= self.food.price
            student.save()

        super().save(*args, **kwargs)


class ProfessorRating(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.student} - {self.professor}'


class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=50)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student, related_name='courses_taken', blank=True)
    credits = models.IntegerField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new_course = self._state.adding

        super().save(*args, **kwargs)

        if not is_new_course:
            self.update_examination_schedule()

    def delete(self, *args, **kwargs):
        self.update_examination_schedule()

        super().delete(*args, **kwargs)

    def update_examination_schedule(self):
        enrolled_students = self.enrolled_students.all()

        for student in enrolled_students:
            student.examinationschedule_set.filter(course=self).delete()

            examination_schedule = ExaminationSchedule(
                student=student,
                course=self,
                date=self.get_exam_date(),
                room=self.get_exam_room(),
                seat_number=self.get_seat_number(),
                description=self.get_exam_description(),
            )
            examination_schedule.save()

    def get_exam_date(self):
        exam_schedule = ExaminationSchedule.objects.get(course=self)
        exam_date = exam_schedule.date
        return exam_date

    def get_exam_room(self):
        exam_schedule = ExaminationSchedule.objects.get(course=self)
        room = exam_schedule.room
        return room

    def get_seat_number(self):
        enrolled_students = self.students.all()
        seat_number = enrolled_students.count() + 1
        return seat_number

    def get_exam_description(self):
        exam_schedule = ExaminationSchedule.objects.get(course=self)
        description = exam_schedule.description

        return description


class Day(models.Model):
    name = models.CharField(max_length=10, choices=[
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ])

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name


class Class(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    days = models.ManyToManyField(Day)

    def __str__(self):
        return self.room


class StudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_num = models.ForeignKey(Class, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    is_present = models.BooleanField()

    def __str__(self):
        return f'{self.student} - {self.class_num}'


class CourseRegistration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.student} - {self.course}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        student = self.student
        student.term.last().credits_taken += self.course.credits
        student.save()

        # Update examination schedule before selecting a course
        self.update_examination_schedule(student)

    def delete(self, *args, **kwargs):
        student = self.student

        # Update examination schedule before deleting a course
        self.update_examination_schedule(student)

        super().delete(*args, **kwargs)

    def update_examination_schedule(self, student):
        courses_taken = student.courses_taken.all()

        student.examinationschedule_set.all().delete()

        for course in courses_taken:
            examination_schedule = ExaminationSchedule(
                course=course,
                date=course.get_exam_date(),
                room=course.get_exam_room(),
                seat_number=course.get_seat_number(),
                description=course.get_exam_description(),
            )
            examination_schedule.save()


class Department(models.Model):
    name = models.CharField(max_length=50)
    head = models.OneToOneField(Professor, on_delete=models.SET_NULL, null=True, related_name='head_of_department')
    course_selection_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.FloatField(validators=[MaxValueValidator(20), MinValueValidator(0)])
    date = models.DateTimeField(auto_now_add=True)
    have_digital_signature = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.student} - {self.course}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.have_digital_signature:
            student = self.student
            student.total_credits_taken += self.course.credits
            student.save()

            # Calculate the new overall GPA
            grades = Grade.objects.filter(student=student, have_digital_signature=True)
            total_credits = sum(grade.course.credits for grade in grades)
            total_grade_points = sum(grade.grade * grade.course.credits for grade in grades)
            overall_gpa = total_grade_points / total_credits if total_credits != 0 else 0

            # Update the student's overall GPA
            student.overall_gpa = overall_gpa
            student.save()


class Announcement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateTimeField()


class ExaminationSchedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    seat_number = models.IntegerField()
    description = models.CharField(max_length=300)


class Messages(models.Model):
    sender = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='messages_sent')
    receiver = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='messages_received')
    subject = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
