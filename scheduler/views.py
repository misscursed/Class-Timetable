




# import logging
# import pandas as pd
# from django.shortcuts import render
# from django.http import JsonResponse
# from .timetable_logic import generate_timetable_logic

# logging.basicConfig(level=logging.DEBUG, filename='timetable.log', filemode='w')
# logger = logging.getLogger(__name__)

# def index(request):
#     if request.method == 'POST':
#         logger.debug("Received POST request")
#         if 'file' not in request.FILES:
#             return render(request, 'scheduler/index.html', {'error': 'No file uploaded'})
        
#         excel_file = request.FILES['file']
#         xls = pd.ExcelFile(excel_file)
#         logger.debug(f"Sheet names in uploaded file: {xls.sheet_names}")
#         post_data = {}

#         if 'Subjects' in xls.sheet_names:
#             df = pd.read_excel(xls, 'Subjects')
#             logger.debug(f"Subjects columns: {df.columns.tolist()}")
#             logger.debug(f"Subjects data:\n{df.to_string()}")
#             for idx, row in df.iterrows():
#                 post_data[f'subject_{idx+1}'] = str(row['Subject']) if pd.notna(row['Subject']) else ''
#                 post_data[f'teacher_{idx+1}'] = str(row['Teacher']) if pd.notna(row['Teacher']) else ''
#                 post_data[f'year_{idx+1}'] = str(row['Year']) if pd.notna(row['Year']) else ''
#                 post_data[f'hours_{idx+1}'] = str(row['Hours']) if pd.notna(row['Hours']) else '0'

#         if 'Venues' in xls.sheet_names:
#             df = pd.read_excel(xls, 'Venues')
#             logger.debug(f"Venues columns: {df.columns.tolist()}")
#             logger.debug(f"Venues data:\n{df.to_string()}")
#             for idx, row in df.iterrows():
#                 post_data[f'venue_{idx+1}'] = str(row['Venue']) if pd.notna(row['Venue']) else ''

#         if 'Fixed Lectures' in xls.sheet_names:
#             df = pd.read_excel(xls, 'Fixed Lectures')
#             logger.debug(f"Fixed Lectures columns: {df.columns.tolist()}")
#             logger.debug(f"Fixed Lectures data:\n{df.to_string()}")
#             for idx, row in df.iterrows():
#                 post_data[f'fixed_subject_{idx+1}'] = str(row['Subject']) if pd.notna(row['Subject']) else ''
#                 post_data[f'fixed_teacher_{idx+1}'] = str(row['Teacher']) if pd.notna(row['Teacher']) else ''
#                 post_data[f'fixed_year_{idx+1}'] = str(row['Year']) if pd.notna(row['Year']) else ''
#                 post_data[f'fixed_day_{idx+1}'] = str(row['Day']) if pd.notna(row['Day']) else ''
#                 post_data[f'fixed_start_{idx+1}'] = str(row['Start Hour']) if pd.notna(row['Start Hour']) else '0'
#                 post_data[f'fixed_end_{idx+1}'] = str(row['End Hour']) if pd.notna(row['End Hour']) else '0'
#                 post_data[f'fixed_venue_{idx+1}'] = str(row['Venue']) if pd.notna(row['Venue']) else ''

#         if 'Teacher Availability' in xls.sheet_names:
#             df = pd.read_excel(xls, 'Teacher Availability')
#             logger.debug(f"Teacher Availability columns: {df.columns.tolist()}")
#             logger.debug(f"Teacher Availability data:\n{df.to_string()}")
#             days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
#             for idx, row in df.iterrows():
#                 teacher = str(row['Teacher']) if pd.notna(row['Teacher']) else ''
#                 if teacher:
#                     for day in days:
#                         availability = str(row[day]) if pd.notna(row[day]) else ''
#                         if availability:
#                             post_data[f'teacher_availability_{teacher}_{day}'] = availability

#         if 'Venue Availability' in xls.sheet_names:
#             df = pd.read_excel(xls, 'Venue Availability')
#             logger.debug(f"Venue Availability columns: {df.columns.tolist()}")
#             logger.debug(f"Venue Availability data:\n{df.to_string()}")
#             days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
#             for idx, row in df.iterrows():
#                 venue = str(row['Venue']) if pd.notna(row['Venue']) else ''
#                 if venue:
#                     for day in days:
#                         availability = str(row[day]) if pd.notna(row[day]) else ''
#                         if availability:
#                             post_data[f'venue_availability_{venue}_{day}'] = availability

#         logger.debug(f"Parsed data: {post_data}")
#         try:
#             timetable_data = generate_timetable_logic(post_data)  # Returns dict like {'1st Year': [...], ...}
#             return JsonResponse({'timetable': timetable_data})
#         except ValueError as e:
#             logger.error(f"Error generating timetable: {e}")
#             return render(request, 'scheduler/index.html', {'error': str(e)})
#     return render(request, 'scheduler/index.html')











import logging
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .timetable_logic import generate_timetable_logic

logging.basicConfig(level=logging.DEBUG, filename='timetable.log', filemode='w')
logger = logging.getLogger(__name__)

@ensure_csrf_cookie
def index(request):
    if request.method == 'POST':
        logger.debug("Received POST request")
        if 'file' not in request.FILES or 'other_dept_file' not in request.FILES:
            return render(request, 'scheduler/index.html', {'error': 'Please upload both files'})
        
        excel_file = request.FILES['file']
        other_dept_file = request.FILES['other_dept_file']
        xls = pd.ExcelFile(excel_file)
        logger.debug(f"Sheet names in constraints file: {xls.sheet_names}")
        post_data = {}

        # Parse constraints file (timetable_data.xlsx)
        if 'Subjects' in xls.sheet_names:
            df = pd.read_excel(xls, 'Subjects')
            logger.debug(f"Subjects columns: {df.columns.tolist()}")
            logger.debug(f"Subjects data:\n{df.to_string()}")
            for idx, row in df.iterrows():
                post_data[f'subject_{idx+1}'] = str(row['Subject']) if pd.notna(row['Subject']) else ''
                post_data[f'teacher_{idx+1}'] = str(row['Teacher']) if pd.notna(row['Teacher']) else ''
                post_data[f'year_{idx+1}'] = str(row['Year']) if pd.notna(row['Year']) else ''
                post_data[f'hours_{idx+1}'] = str(row['Hours']) if pd.notna(row['Hours']) else '0'

        if 'Venues' in xls.sheet_names:
            df = pd.read_excel(xls, 'Venues')
            logger.debug(f"Venues columns: {df.columns.tolist()}")
            logger.debug(f"Venues data:\n{df.to_string()}")
            for idx, row in df.iterrows():
                post_data[f'venue_{idx+1}'] = str(row['Venue']) if pd.notna(row['Venue']) else ''

        if 'Fixed Lectures' in xls.sheet_names:
            df = pd.read_excel(xls, 'Fixed Lectures')
            logger.debug(f"Fixed Lectures columns: {df.columns.tolist()}")
            logger.debug(f"Fixed Lectures data:\n{df.to_string()}")
            for idx, row in df.iterrows():
                post_data[f'fixed_subject_{idx+1}'] = str(row['Subject']) if pd.notna(row['Subject']) else ''
                post_data[f'fixed_teacher_{idx+1}'] = str(row['Teacher']) if pd.notna(row['Teacher']) else ''
                post_data[f'fixed_year_{idx+1}'] = str(row['Year']) if pd.notna(row['Year']) else ''
                post_data[f'fixed_day_{idx+1}'] = str(row['Day']) if pd.notna(row['Day']) else ''
                post_data[f'fixed_start_{idx+1}'] = str(row['Start Hour']) if pd.notna(row['Start Hour']) else '0'
                post_data[f'fixed_end_{idx+1}'] = str(row['End Hour']) if pd.notna(row['End Hour']) else '0'
                post_data[f'fixed_venue_{idx+1}'] = str(row['Venue']) if pd.notna(row['Venue']) else ''

        if 'Teacher Availability' in xls.sheet_names:
            df = pd.read_excel(xls, 'Teacher Availability')
            logger.debug(f"Teacher Availability columns: {df.columns.tolist()}")
            logger.debug(f"Teacher Availability data:\n{df.to_string()}")
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            for idx, row in df.iterrows():
                teacher = str(row['Teacher']) if pd.notna(row['Teacher']) else ''
                if teacher:
                    for day in days:
                        availability = str(row[day]) if pd.notna(row[day]) else ''
                        if availability:
                            post_data[f'teacher_availability_{teacher}_{day}'] = availability

        if 'Venue Availability' in xls.sheet_names:
            df = pd.read_excel(xls, 'Venue Availability')
            logger.debug(f"Venue Availability columns: {df.columns.tolist()}")
            logger.debug(f"Venue Availability data:\n{df.to_string()}")
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            for idx, row in df.iterrows():
                venue = str(row['Venue']) if pd.notna(row['Venue']) else ''
                if venue:
                    for day in days:
                        availability = str(row[day]) if pd.notna(row[day]) else ''
                        if availability:
                            post_data[f'venue_availability_{venue}_{day}'] = availability

        # Parse other department courses (other_dept_courses.xlsx)
        other_dept_xls = pd.ExcelFile(other_dept_file)
        other_dept_courses = []
        if 'OtherDeptCourses' in other_dept_xls.sheet_names:
            df = pd.read_excel(other_dept_xls, 'OtherDeptCourses')
            logger.debug(f"OtherDeptCourses columns: {df.columns.tolist()}")
            logger.debug(f"OtherDeptCourses data:\n{df.to_string()}")
            for idx, row in df.iterrows():
                course = {
                    'student_group': str(row['Student/Group']) if pd.notna(row['Student/Group']) else '',
                    'course': str(row['Course']) if pd.notna(row['Course']) else '',
                    'department': str(row['Department']) if pd.notna(row['Department']) else '',
                    'day': str(row['Day']) if pd.notna(row['Day']) else '',
                    'start': int(row['Start Hour']) if pd.notna(row['Start Hour']) else 0,
                    'end': int(row['End Hour']) if pd.notna(row['End Hour']) else 0,
                    'venue': str(row['Venue']) if pd.notna(row['Venue']) else ''
                }
                if all([course['student_group'], course['course'], course['department'], course['day'], course['start'], course['end']]):
                    other_dept_courses.append(course)

        logger.debug(f"Parsed data: {post_data}")
        logger.debug(f"Other dept courses: {other_dept_courses}")

        try:
            timetable_data = generate_timetable_logic(post_data)
            # Handle extra lecture slot check
            extra_slot = request.POST.get('extra_slot_day', '')
            extra_start = request.POST.get('extra_start', '')
            extra_end = request.POST.get('extra_end', '')
            extra_teacher = request.POST.get('extra_teacher', '')
            extra_year = request.POST.get('extra_year', '')

            extra_slot_result = {'is_free': True, 'message': '', 'suggestion': None}
            if extra_slot and extra_start and extra_end and extra_teacher and extra_year:
                extra_start = int(extra_start)
                extra_end = int(extra_end)
                logger.debug(f"Checking extra slot: {extra_year}, {extra_slot}, {extra_start}-{extra_end}, {extra_teacher}")

                # Check CS timetable
                year_slots = timetable_data.get(extra_year, [])
                for slot in year_slots:
                    if slot['day'] == extra_slot:
                        for hour in range(extra_start, extra_end):
                            if slot['start'] <= hour < slot['end']:
                                extra_slot_result['is_free'] = False
                                extra_slot_result['message'] = f"Students not free in {extra_slot}, {extra_start}:00-{extra_end}:00 due to {slot['subject']}."
                                break

                # Check other department courses
                if extra_slot_result['is_free']:
                    for course in other_dept_courses:
                        if course['day'] == extra_slot:
                            for hour in range(extra_start, extra_end):
                                if course['start'] <= hour < course['end']:
                                    extra_slot_result['is_free'] = False
                                    extra_slot_result['message'] = f"Students not free in {extra_slot}, {extra_start}:00-{extra_end}:00 due to {course['course']} ({course['department']})."
                                    break

                # Suggest alternative slot if not free
                if not extra_slot_result['is_free']:
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                    hours = list(range(8, 12)) + list(range(13, 18))
                    teacher_availability = {}
                    for key, value in post_data.items():
                        if key.startswith(f'teacher_availability_{extra_teacher}_'):
                            day = key.split('_')[-1]
                            if day in days:
                                teacher_availability[day] = []
                                for slot in value.split(','):
                                    start, end = map(int, slot.split('-'))
                                    teacher_availability[day].append((start, end))

                    for day in days:
                        if day not in teacher_availability:
                            continue
                        for start, end in teacher_availability[day]:
                            for slot_start in range(start, end):
                                if slot_start in hours:
                                    slot_end = slot_start + (extra_end - extra_start)
                                    if slot_end <= end and slot_end in hours:
                                        is_free = True
                                        # Check CS timetable
                                        for slot in year_slots:
                                            if slot['day'] == day:
                                                for hour in range(slot_start, slot_end):
                                                    if slot['start'] <= hour < slot['end']:
                                                        is_free = False
                                                        break
                                        # Check other dept courses
                                        if is_free:
                                            for course in other_dept_courses:
                                                if course['day'] == day:
                                                    for hour in range(slot_start, slot_end):
                                                        if course['start'] <= hour < course['end']:
                                                            is_free = False
                                                            break
                                        if is_free:
                                            extra_slot_result['suggestion'] = {
                                                'day': day,
                                                'start': slot_start,
                                                'end': slot_end
                                            }
                                            break
                            if extra_slot_result['suggestion']:
                                break
                        if extra_slot_result['suggestion']:
                            break

                    if extra_slot_result['suggestion']:
                        extra_slot_result['message'] += f" Suggested slot: {extra_slot_result['suggestion']['day']}, {extra_slot_result['suggestion']['start']}:00-{extra_slot_result['suggestion']['end']}:00."
                    else:
                        extra_slot_result['message'] += " No alternative slot found where all students are free."

                else:
                    extra_slot_result['message'] = f"All students are free in {extra_slot}, {extra_start}:00-{extra_end}:00."

            return JsonResponse({
                'timetable': timetable_data,
                'extra_slot_result': extra_slot_result
            })
        except ValueError as e:
            logger.error(f"Error generating timetable: {e}")
            return render(request, 'scheduler/index.html', {'error': str(e)})
    return render(request, 'scheduler/index.html')