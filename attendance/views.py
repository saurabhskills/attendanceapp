from django.shortcuts import render, redirect
from .models import Student, Class, Attendance
from django.http import HttpResponse
import pandas as pd

def mark_attendance(request):
    students = Student.objects.all()
    classes = Class.objects.all()
    
    if request.method == 'POST':
        selected_class = request.POST['class_id']
        date = request.POST['date']
        for student in students:
            attendance = Attendance(
                student=student,
                class_attended=Class.objects.get(id=selected_class),
                date=date,
                is_present=request.POST.get(f"student_{student.id}", "off") == "on"
            )
            attendance.save()
        return redirect('attendance_report')
    
    return render(request, 'attendance/mark_attendance.html', {'students': students, 'classes': classes})

def attendance_report(request):
    classes = Class.objects.all()
    selected_class = request.GET.get('class_id', None)
    date_from = request.GET.get('date_from', None)
    date_to = request.GET.get('date_to', None)
    
    if selected_class and date_from and date_to:
        attendance_records = Attendance.objects.filter(
            class_attended=selected_class,
            date__range=[date_from, date_to]
        )
        
        # Create an Excel report
        if 'export_excel' in request.GET:
            df = pd.DataFrame(list(attendance_records.values('student__first_name', 'student__last_name', 'date', 'is_present')))
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename=attendance_{selected_class}.xlsx'
            df.to_excel(response, index=False)
            return response
        
        return render(request, 'attendance/reports.html', {'attendance_records': attendance_records})
    return render(request, 'attendance/reports.html', {'classes': classes})
