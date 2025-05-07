




# import logging
# import os
# import pandas as pd
# from django.http import JsonResponse
# from django.shortcuts import render
# from django.views.decorators.csrf import ensure_csrf_cookie
# from .generate_timetable import generate_timetable

# # Configure logging
# logging.basicConfig(
#     filename=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'timetable.log'),
#     level=logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# @ensure_csrf_cookie
# def index(request):
#     if request.method == 'GET':
#         logging.debug("GET request received, returning empty subject_teacher_pairs")
#         return JsonResponse({'subject_teacher_pairs': []})

#     elif request.method == 'POST':
#         logging.debug(f"POST request received with data: {request.POST}, files: {request.FILES}")
        
#         # Handle file upload for subject-teacher pairs
#         if 'excelFile' in request.FILES and 'subjects_list' not in request.POST:
#             excel_file = request.FILES['excelFile']
#             logging.debug(f"Received file: {excel_file.name}")

#             try:
#                 # Check available sheets
#                 xl = pd.ExcelFile(excel_file)
#                 logging.debug(f"Available sheets: {xl.sheet_names}")

#                 # Read the Subjects sheet
#                 if 'Subjects' not in xl.sheet_names:
#                     logging.error("No 'Subjects' sheet found in the Excel file")
#                     return JsonResponse({'subject_teacher_pairs': []}, status=400)

#                 subjects_df = pd.read_excel(excel_file, sheet_name='Subjects')
#                 logging.debug(f"Subjects sheet columns: {list(subjects_df.columns)}")
#                 logging.debug(f"Subjects sheet data: {subjects_df.to_dict()}")

#                 # Validate required columns
#                 if 'Subject' not in subjects_df.columns or 'Teacher' not in subjects_df.columns:
#                     logging.error("Missing 'Subject' or 'Teacher' column in Subjects sheet")
#                     return JsonResponse({'subject_teacher_pairs': []}, status=400)

#                 # Extract subject-teacher pairs
#                 subjects_df = subjects_df.dropna(subset=['Subject', 'Teacher'])
#                 subject_teacher_pairs = [
#                     f"{row['Subject']} - {row['Teacher']}"
#                     for _, row in subjects_df.iterrows()
#                 ]
#                 logging.debug(f"Subject-teacher pairs extracted: {subject_teacher_pairs}")

#                 # Reset file pointer for potential future use
#                 excel_file.seek(0)
#                 return JsonResponse({'subject_teacher_pairs': subject_teacher_pairs})

#             except Exception as e:
#                 logging.error(f"Error processing Excel file: {str(e)}")
#                 return JsonResponse({'subject_teacher_pairs': []}, status=500)

#         # Handle timetable generation
#         elif 'subjects_list' in request.POST:
#             try:
#                 subjects_list = request.POST.get('subjects_list')
#                 logging.debug(f"Generating timetable with subjects_list: {subjects_list}")
#                 if not subjects_list or subjects_list == '[]':
#                     logging.error("Empty or invalid subjects_list received")
#                     return JsonResponse({'timetables': [], 'error': 'Empty subjects_list'}, status=400)

#                 excel_file = request.FILES.get('excelFile') if 'excelFile' in request.FILES else None
#                 if excel_file:
#                     excel_file.seek(0)
#                     logging.debug(f"Excel file provided for timetable generation: {excel_file.name}")
#                 else:
#                     logging.warning("No Excel file provided for timetable generation, proceeding with defaults")

#                 timetables = generate_timetable(subjects_list, excel_file)
#                 logging.debug(f"Timetables generated: {timetables}")
#                 if not timetables:
#                     logging.error("Timetable generation returned empty result")
#                     return JsonResponse({'timetables': [], 'error': 'Failed to generate timetables'}, status=500)
#                 return JsonResponse({'timetables': timetables})
#             except Exception as e:
#                 logging.error(f"Error generating timetable: {str(e)}")
#                 return JsonResponse({'timetables': [], 'error': str(e)}, status=500)

#         else:
#             logging.error("POST request missing expected data: 'excelFile' or 'subjects_list'")
#             return JsonResponse({'error': 'Missing excelFile or subjects_list'}, status=400)

#     return JsonResponse({'error': 'Invalid request'}, status=400)






import logging
import os
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from .generate_timetable import generate_timetable

# Configure logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'timetable.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@ensure_csrf_cookie
def index(request):
    if request.method == 'GET':
        logging.debug("GET request received, returning empty subject_teacher_pairs")
        return JsonResponse({'subject_teacher_pairs': []})

    elif request.method == 'POST':
        logging.debug(f"POST request received with data: {request.POST}, files: {request.FILES}")
        
        # Handle file upload for subject-teacher pairs
        if 'excelFile' in request.FILES and 'subjects_list' not in request.POST:
            excel_file = request.FILES['excelFile']
            logging.debug(f"Received file: {excel_file.name}")

            try:
                # Check available sheets
                xl = pd.ExcelFile(excel_file)
                logging.debug(f"Available sheets: {xl.sheet_names}")

                # Read the Subjects sheet
                if 'Subjects' not in xl.sheet_names:
                    logging.error("No 'Subjects' sheet found in the Excel file")
                    return JsonResponse({'subject_teacher_pairs': []}, status=400)

                subjects_df = pd.read_excel(excel_file, sheet_name='Subjects')
                logging.debug(f"Subjects sheet columns: {list(subjects_df.columns)}")
                logging.debug(f"Subjects sheet data: {subjects_df.to_dict()}")

                # Validate required columns
                if 'Subject' not in subjects_df.columns or 'Teacher' not in subjects_df.columns:
                    logging.error("Missing 'Subject' or 'Teacher' column in Subjects sheet")
                    return JsonResponse({'subject_teacher_pairs': []}, status=400)

                # Extract subject-teacher pairs for backend, but send only subjects to frontend
                subjects_df = subjects_df.dropna(subset=['Subject', 'Teacher'])
                subject_teacher_pairs = [
                    f"{row['Subject']} - {row['Teacher']}"
                    for _, row in subjects_df.iterrows()
                ]
                subjects_only = [
                    row['Subject']
                    for _, row in subjects_df.iterrows()
                ]
                logging.debug(f"Subject-teacher pairs extracted: {subject_teacher_pairs}")
                logging.debug(f"Subjects only for frontend: {subjects_only}")

                # Reset file pointer for potential future use
                excel_file.seek(0)
                return JsonResponse({'subject_teacher_pairs': subjects_only, 'full_pairs': subject_teacher_pairs})

            except Exception as e:
                logging.error(f"Error processing Excel file: {str(e)}")
                return JsonResponse({'subject_teacher_pairs': []}, status=500)

        # Handle timetable generation
        elif 'subjects_list' in request.POST:
            try:
                subjects_list = request.POST.get('subjects_list')
                logging.debug(f"Generating timetable with subjects_list: {subjects_list}")
                if not subjects_list or subjects_list == '[]':
                    logging.error("Empty or invalid subjects_list received")
                    return JsonResponse({'timetables': [], 'error': 'Empty subjects_list'}, status=400)

                excel_file = request.FILES.get('excelFile') if 'excelFile' in request.FILES else None
                if excel_file:
                    excel_file.seek(0)
                    logging.debug(f"Excel file provided for timetable generation: {excel_file.name}")
                else:
                    logging.warning("No Excel file provided for timetable generation, proceeding with defaults")

                timetables = generate_timetable(subjects_list, excel_file)
                logging.debug(f"Timetables generated: {timetables}")
                if not timetables:
                    logging.error("Timetable generation returned empty result")
                    return JsonResponse({'timetables': [], 'error': 'Failed to generate timetables'}, status=500)
                return JsonResponse({'timetables': timetables})
            except Exception as e:
                logging.error(f"Error generating timetable: {str(e)}")
                return JsonResponse({'timetables': [], 'error': str(e)}, status=500)

        else:
            logging.error("POST request missing expected data: 'excelFile' or 'subjects_list'")
            return JsonResponse({'error': 'Missing excelFile or subjects_list'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)