# from django.shortcuts import render
# from django.http import HttpResponse
# from .forms import TimetableForm
# from .timetable_logic import generate_timetable_logic

# def index(request):
#     if request.method == 'POST':
#         form = TimetableForm(request.POST)
#         if form.is_valid():
#             try:
#                 timetable_file, filename = generate_timetable_logic(request.POST)
#                 with open(timetable_file, 'rb') as f:
#                     response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#                     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#                     return response
#             except Exception as e:
#                 return render(request, 'scheduler/index.html', {'form': form, 'error': str(e)})
#         else:
#             return render(request, 'scheduler/index.html', {'form': form, 'error': 'Invalid form data'})
#     return render(request, 'scheduler/index.html', {'form': TimetableForm()})




# from django.shortcuts import render
# from django.http import HttpResponse
# from .forms import TimetableUploadForm
# from .timetable_logic import generate_timetable_logic
# import pandas as pd
# import os
# import logging

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# def index(request):
#     if request.method == 'POST':
#         form = TimetableUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             uploaded_file = request.FILES['file']
#             try:
#                 if uploaded_file.name.endswith('.xlsx'):
#                     data = parse_excel_file(uploaded_file)
#                 elif uploaded_file.name.endswith('.csv'):
#                     data = parse_csv_file(uploaded_file)
#                 else:
#                     return render(request, 'scheduler/index.html', {
#                         'form': form,
#                         'error': 'Please upload a .xlsx or .csv file'
#                     })

#                 # Log the parsed data
#                 logger.debug("Parsed data: %s", data)

#                 timetable_file, filename = generate_timetable_logic(data)
#                 with open(timetable_file, 'rb') as f:
#                     response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#                     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#                     return response
#             except Exception as e:
#                 logger.error("Error: %s", str(e))
#                 return render(request, 'scheduler/index.html', {
#                     'form': form,
#                     'error': f"Error processing file: {str(e)}"
#                 })
#     else:
#         form = TimetableUploadForm()
#     return render(request, 'scheduler/index.html', {'form': form})

# def parse_excel_file(file):
#     xls = pd.ExcelFile(file)
#     data = {}
#     if 'Subjects' in xls.sheet_names:
#         df = pd.read_excel(xls, 'Subjects')
#         for _, row in df.iterrows():
#             key = f"subject_{row.name + 1}"
#             data[key] = row['Subject']
#             data[f"teacher_{row.name + 1}"] = row['Teacher']
#             data[f"year_{row.name + 1}"] = row['Year']
#             data[f"hours_{row.name + 1}"] = str(row['Hours'])
#     if 'Teacher Availability' in xls.sheet_names:
#         df = pd.read_excel(xls, 'Teacher Availability')
#         for _, row in df.iterrows():
#             key = f"teacher_availability_{row['Teacher']}_{row['Day']}"
#             data[key] = row['Availability']
#     if 'Venues' in xls.sheet_names:
#         df = pd.read_excel(xls, 'Venues')
#         for idx, row in df.iterrows():
#             data[f"venue_{idx + 1}"] = row['Venue']
#     if 'Venue Availability' in xls.sheet_names:
#         df = pd.read_excel(xls, 'Venue Availability')
#         for _, row in df.iterrows():
#             key = f"venue_availability_{row['Venue']}_{row['Day']}"
#             data[key] = row['Availability']
#     if 'Fixed Lectures' in xls.sheet_names:
#         df = pd.read_excel(xls, 'Fixed Lectures')
#         for idx, row in df.iterrows():
#             data[f"fixed_subject_{idx + 1}"] = row['Subject']
#             data[f"fixed_teacher_{idx + 1}"] = row['Teacher']
#             data[f"fixed_year_{idx + 1}"] = row['Year']
#             data[f"fixed_day_{idx + 1}"] = row['Day']
#             data[f"fixed_start_{idx + 1}"] = str(row['Start Hour'])
#             data[f"fixed_end_{idx + 1}"] = str(row['End Hour'])
#             data[f"fixed_venue_{idx + 1}"] = row['Venue']
#     return data

# def parse_csv_file(file):
#     raise NotImplementedError("CSV parsing not implemented yet!")




import logging
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from .timetable_logic import generate_timetable_logic

logging.basicConfig(level=logging.DEBUG, filename='timetable.log', filemode='w')
logger = logging.getLogger(__name__)

def index(request):
    if request.method == 'POST':
        logger.debug("Received POST request")
        if 'file' not in request.FILES:
            return render(request, 'scheduler/index.html', {'error': 'No file uploaded'})
        
        excel_file = request.FILES['file']
        xls = pd.ExcelFile(excel_file)
        logger.debug(f"Sheet names in uploaded file: {xls.sheet_names}")
        post_data = {}

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

        logger.debug(f"Parsed data: {post_data}")
        try:
            timetable_data = generate_timetable_logic(post_data)  # Returns dict like {'1st Year': [...], ...}
            return JsonResponse({'timetable': timetable_data})
        except ValueError as e:
            logger.error(f"Error generating timetable: {e}")
            return render(request, 'scheduler/index.html', {'error': str(e)})
    return render(request, 'scheduler/index.html')