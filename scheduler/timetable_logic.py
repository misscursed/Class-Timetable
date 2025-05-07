
# import os
# import pandas as pd
# from ortools.sat.python import cp_model
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)

# def get_input_from_form(data):
#     teachers = set()
#     subjects = set()
#     years = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
#     venues = set()
#     subject_schedule = {}
#     teacher_availability = {}
#     venue_availability = {}
#     fixed_lectures = []

#     for key, value in data.items():
#         if key.startswith('subject_'):
#             idx = key.split('_')[1]
#             subject = value.strip()
#             teacher = data.get(f'teacher_{idx}', '').strip()
#             year = data.get(f'year_{idx}', '').strip()
#             num_hours = data.get(f'hours_{idx}', '0').strip()
#             if subject and teacher and year in years and num_hours:
#                 teachers.add(teacher)
#                 subjects.add(subject)
#                 num_hours = int(num_hours)
#                 if subject not in subject_schedule:
#                     subject_schedule[subject] = []
#                 subject_schedule[subject].append((teacher, year, num_hours))

#         elif key.startswith('venue_'):
#             venue = value.strip()
#             if venue:
#                 venues.add(venue)

#         elif key.startswith('teacher_availability_'):
#             parts = key.split('_')
#             if len(parts) >= 4:
#                 teacher = parts[2]
#                 day = '_'.join(parts[3:])
#                 if teacher and day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
#                     teachers.add(teacher)
#                     if teacher not in teacher_availability:
#                         teacher_availability[teacher] = {}
#                     availability_slots = []
#                     for slot in value.split(','):
#                         start, end = map(int, slot.split('-'))
#                         availability_slots.append((start, end))
#                     teacher_availability[teacher][day] = availability_slots

#         elif key.startswith('venue_availability_'):
#             parts = key.split('_')
#             if len(parts) >= 4:
#                 venue = parts[2]
#                 day = '_'.join(parts[3:])
#                 if venue and day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
#                     venues.add(venue)
#                     if venue not in venue_availability:
#                         venue_availability[venue] = {}
#                     availability_slots = []
#                     for slot in value.split(','):
#                         start, end = map(int, slot.split('-'))
#                         availability_slots.append((start, end))
#                     venue_availability[venue][day] = availability_slots

#         elif key.startswith('fixed_subject_'):
#             idx = key.split('_')[2]
#             subject = value.strip()
#             teacher = data.get(f'fixed_teacher_{idx}', '').strip()
#             year = data.get(f'fixed_year_{idx}', '').strip()
#             day = data.get(f'fixed_day_{idx}', '').strip()
#             start_hour = int(data.get(f'fixed_start_{idx}', '0'))
#             end_hour = int(data.get(f'fixed_end_{idx}', '0'))
#             venue = data.get(f'fixed_venue_{idx}', '').strip()
#             if all([subject, teacher, year in years, day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], start_hour, end_hour, venue]):
#                 fixed_lectures.append((subject, teacher, year, day, start_hour, end_hour, venue))
#                 teachers.add(teacher)
#                 subjects.add(subject)
#                 venues.add(venue)

#     class_hours = list(range(8, 12)) + list(range(13, 18))
#     days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
#     max_consecutive_classes = 3

#     for teacher in teachers:
#         if teacher not in teacher_availability:
#             teacher_availability[teacher] = {day: [(8, 12), (13, 18)] for day in days}
#         else:
#             for day in days:
#                 if day not in teacher_availability[teacher]:
#                     teacher_availability[teacher][day] = [(8, 12), (13, 18)]

#     for venue in venues:
#         if venue not in venue_availability:
#             venue_availability[venue] = {day: [(8, 12), (13, 18)] for day in days}
#         else:
#             for day in days:
#                 if day not in venue_availability[venue]:
#                     venue_availability[venue][day] = [(8, 12), (13, 18)]

#     teachers = list(teachers)
#     subjects = list(subjects)
#     venues = list(venues)

#     return (
#         teachers, subjects, years, venues, class_hours, days, max_consecutive_classes,
#         teacher_availability, subject_schedule, venue_availability, fixed_lectures
#     )

# def validate_fixed_lectures(fixed_lectures, teacher_availability, venue_availability, class_hours, days):
#     conflicts = []
#     for subject, teacher, year, day, start_hour, end_hour, venue in fixed_lectures:
#         if day not in days:
#             conflicts.append(f"Invalid day '{day}' for fixed lecture {subject}")
#             continue
#         if teacher not in teacher_availability:
#             conflicts.append(f"Teacher {teacher} not in teacher list for fixed lecture {subject}")
#             continue
#         if venue not in venue_availability:
#             conflicts.append(f"Venue {venue} not in venue list for fixed lecture {subject}")
#             continue
        
#         teacher_hours = set()
#         for start, end in teacher_availability[teacher][day]:
#             teacher_hours.update(range(start, end))
#         venue_hours = set()
#         for start, end in venue_availability[venue][day]:
#             venue_hours.update(range(start, end))
        
#         for hour in range(start_hour, end_hour):
#             if hour not in class_hours:
#                 conflicts.append(f"Fixed lecture {subject} at {hour}:00 on {day} is outside class hours {class_hours}")
#             if hour not in teacher_hours:
#                 conflicts.append(f"Teacher {teacher} unavailable for {subject} at {hour}:00 on {day}")
#             if hour not in venue_hours:
#                 conflicts.append(f"Venue {venue} unavailable for {subject} at {hour}:00 on {day}")
    
#     if conflicts:
#         raise ValueError("Fixed lecture constraints cannot be satisfied: " + "; ".join(conflicts))

# def generate_timetable_logic(post_data):
#     teachers, subjects, years, venues, class_hours, days, max_consecutive_classes, teacher_availability, subject_schedule, venue_availability, fixed_lectures = get_input_from_form(post_data)
    
#     validate_fixed_lectures(fixed_lectures, teacher_availability, venue_availability, class_hours, days)

#     model = cp_model.CpModel()

#     timetable_vars = {}
#     venue_vars = {}
#     for day in days:
#         for hour in class_hours:
#             for year in years:
#                 for subject in subjects:
#                     timetable_vars[(day, hour, year, subject)] = model.NewBoolVar(f'timetable_{day}_{hour}_{year}_{subject}')
#                 for venue in venues:
#                     venue_vars[(day, hour, year, venue)] = model.NewBoolVar(f'venue_{day}_{hour}_{year}_{venue}')

#     fixed_slots = set()
#     for subject, teacher, year, day, start_hour, end_hour, venue in fixed_lectures:
#         for hour in range(start_hour, end_hour):
#             if hour in class_hours:
#                 slot = (day, hour, year)
#                 fixed_slots.add(slot)
#                 model.Add(timetable_vars[(day, hour, year, subject)] == 1)
#                 model.Add(venue_vars[(day, hour, year, venue)] == 1)
#                 for other_subject in subjects:
#                     if other_subject != subject:
#                         model.Add(timetable_vars[(day, hour, year, other_subject)] == 0)
#                 for other_venue in venues:
#                     if other_venue != venue:
#                         model.Add(venue_vars[(day, hour, year, other_venue)] == 0)

#     for teacher in teachers:
#         for day in days:
#             available_hours = set()
#             for start, end in teacher_availability[teacher][day]:
#                 available_hours.update(range(start, end))
#             for hour in class_hours:
#                 if hour not in available_hours:
#                     for year in years:
#                         slot = (day, hour, year)
#                         if slot not in fixed_slots:
#                             for subject in subjects:
#                                 if any(t == teacher for t, _, _ in subject_schedule.get(subject, [])):
#                                     model.Add(timetable_vars[(day, hour, year, subject)] == 0)

#     for venue in venues:
#         for day in days:
#             available_hours = set()
#             for start, end in venue_availability[venue][day]:
#                 available_hours.update(range(start, end))
#             for hour in class_hours:
#                 if hour not in available_hours:
#                     for year in years:
#                         slot = (day, hour, year)
#                         if slot not in fixed_slots:
#                             model.Add(venue_vars[(day, hour, year, venue)] == 0)

#     for subject, teachers_hours in subject_schedule.items():
#         for teacher, year, hours in teachers_hours:
#             fixed_hours = sum(
#                 1 for s, t, y, d, start_h, end_h, _ in fixed_lectures
#                 if s == subject and t == teacher and y == year
#                 for h in range(start_h, end_h) if h in class_hours
#             )
#             remaining_hours = max(0, hours - fixed_hours)
#             bool_vars = [timetable_vars[(day, hour, year, subject)] 
#                          for day in days for hour in class_hours 
#                          if (day, hour, year) not in fixed_slots
#                          and any(t == teacher for t, _, _ in subject_schedule[subject])]
#             model.Add(sum(bool_vars) == remaining_hours)

#     for day in days:
#         for hour in class_hours:
#             for year in years:
#                 model.Add(sum(timetable_vars[(day, hour, year, subject)] for subject in subjects) <= 1)

#     for day in days:
#         for hour in class_hours:
#             for year in years:
#                 scheduled_subjects = sum(timetable_vars[(day, hour, year, subject)] for subject in subjects)
#                 scheduled_venues = sum(venue_vars[(day, hour, year, venue)] for venue in venues)
#                 model.Add(scheduled_subjects == scheduled_venues)
#                 model.Add(scheduled_venues <= 1)

#     for teacher in teachers:
#         for day in days:
#             for hour in class_hours:
#                 teacher_slots = []
#                 for year in years:
#                     for subject in subjects:
#                         if any(t == teacher for t, _, _ in subject_schedule.get(subject, [])):
#                             teacher_slots.append(timetable_vars[(day, hour, year, subject)])
#                 model.Add(sum(teacher_slots) <= 1)

#     day_class_count = {}
#     for day in days:
#         day_class_count[day] = sum(timetable_vars[(day, hour, year, subject)] 
#                                   for hour in class_hours for year in years for subject in subjects)
#     max_classes = model.NewIntVar(0, len(class_hours) * len(years) * len(subjects), 'max_classes')
#     for day in days:
#         model.Add(max_classes >= day_class_count[day])
#     model.Minimize(max_classes)

#     solver = cp_model.CpSolver()
#     status = solver.Solve(model)
#     logger.debug("Solver status: %s", solver.StatusName(status))

#     if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
#         logger.debug("Solver found a solution")
#         for var in timetable_vars:
#             if solver.Value(timetable_vars[var]) == 1:
#                 logger.debug(f"Scheduled: {var}")
#         for var in venue_vars:
#             if solver.Value(venue_vars[var]) == 1:
#                 logger.debug(f"Venue: {var}")

#         timetable = {}
#         for year in years:
#             timetable[year] = []

#         # Add fixed lectures with full duration
#         for subject, teacher, year, day, start_hour, end_hour, venue in fixed_lectures:
#             logger.debug(f"Adding fixed lecture: {subject}, {teacher}, {year}, {day}, {start_hour}-{end_hour}, {venue}")
#             timetable[year].append({
#                 'subject': subject,
#                 'teacher': teacher,
#                 'day': day,
#                 'start': start_hour,
#                 'end': end_hour,
#                 'venue': venue
#             })

#         # Add scheduled lectures (non-fixed)
#         for day in days:
#             for hour in class_hours:
#                 for year in years:
#                     for subject in subjects:
#                         if solver.Value(timetable_vars[(day, hour, year, subject)]) == 1:
#                             for teacher, y, _ in subject_schedule.get(subject, []):
#                                 if y == year:
#                                     for venue in venues:
#                                         if solver.Value(venue_vars[(day, hour, year, venue)]) == 1:
#                                             is_fixed = any(
#                                                 fl[2] == year and fl[3] == day and fl[4] <= hour < fl[5]
#                                                 for fl in fixed_lectures
#                                             )
#                                             if not is_fixed:
#                                                 logger.debug(f"Adding scheduled lecture: {subject}, {teacher}, {year}, {day}, {hour}-{hour+1}, {venue}")
#                                                 timetable[year].append({
#                                                     'subject': subject,
#                                                     'teacher': teacher,
#                                                     'day': day,
#                                                     'start': hour,
#                                                     'end': hour + 1,  # 1-hour slots for non-fixed
#                                                     'venue': venue
#                                                 })
#                                             break
#                                     break

#         logger.debug("Timetable before return: %s", timetable)
#         return timetable

#     else:
#         logger.error("No solution found. Solver status: %s", solver.StatusName(status))
#         raise ValueError(f"No solution found. Solver status: {solver.StatusName(status)}")







import os
import pandas as pd
from ortools.sat.python import cp_model
from django.conf import settings

class TimetableCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables, max_solutions=3):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.variables = variables
        self.max_solutions = max_solutions
        self.solutions = []
    
    def on_solution_callback(self):
        solution = {}
        for var in self.variables:
            solution[var] = self.Value(var)
        self.solutions.append(solution)
        if len(self.solutions) >= self.max_solutions:
            self.StopSearch()
    
    def stop(self):
        self.StopSearch()

def parse_availability(availability_str):
    if pd.isna(availability_str):
        return []
    slots = availability_str.split(',')
    hours = []
    for slot in slots:
        start, end = map(int, slot.split('-'))
        hours.extend(range(start, end))
    return hours

def generate_multiple_timetables(subjects_list):
    try:
        # Read Excel data
        excel_path = os.path.join(settings.MEDIA_ROOT, 'timetable_data.xlsx')
        subjects_df = pd.read_excel(excel_path, sheet_name='Subjects')
        venues_df = pd.read_excel(excel_path, sheet_name='Venues')
        fixed_lectures_df = pd.read_excel(excel_path, sheet_name='Fixed Lectures')
        teacher_availability_df = pd.read_excel(excel_path, sheet_name='Teacher Availability')

        # Initialize model
        model = cp_model.CpModel()
        solver = cp_model.CpSolver()

        # Define variables
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        hours = list(range(8, 18))  # 8 AM to 6 PM
        years = ['1st Year', '2nd Year']
        venues = venues_df['Venue'].tolist()

        # Variables: subject_teacher_year_day_hour_venue
        variables = {}
        for subject in subjects_list:
            subject_teacher = subject['subject_teacher']
            hours_needed = int(subject['hours'])
            year = subject['year']
            for day in days:
                for hour in hours:
                    for venue in venues:
                        var_name = f"{subject_teacher}_{year}_{day}_{hour}_{venue}"
                        variables[var_name] = model.NewBoolVar(var_name)

        # Constraint 1: Each subject gets required hours
        for subject in subjects_list:
            subject_teacher = subject['subject_teacher']
            hours_needed = int(subject['hours'])
            year = subject['year']
            total_hours = sum(
                variables[f"{subject_teacher}_{year}_{day}_{hour}_{venue}"]
                for day in days
                for hour in hours
                for venue in venues
            )
            model.Add(total_hours == hours_needed)

        # Constraint 2: No overlapping lectures in same venue/hour
        for day in days:
            for hour in hours:
                for venue in venues:
                    lectures = [
                        variables[f"{subject['subject_teacher']}_{subject['year']}_{day}_{hour}_{venue}"]
                        for subject in subjects_list
                    ]
                    model.Add(sum(lectures) <= 1)

        # Constraint 3: Add fixed lectures
        for _, row in fixed_lectures_df.iterrows():
            subject_teacher = f"{row['Subject']} - {row['Teacher']}"
            year = row['Year']
            day = row['Day']
            start_hour = int(row['Start Hour'])
            end_hour = int(row['End Hour'])
            venue = row['Venue']
            for hour in range(start_hour, end_hour):
                var_name = f"{subject_teacher}_{year}_{day}_{hour}_{venue}"
                if var_name in variables:
                    model.Add(variables[var_name] == 1)

        # Constraint 4: Teacher availability
        for _, row in teacher_availability_df.iterrows():
            teacher = row['Teacher']
            for day in days:
                available_hours = parse_availability(row[day])
                for subject in subjects_list:
                    subject_teacher = subject['subject_teacher']
                    if teacher not in subject_teacher:
                        continue
                    year = subject['year']
                    for hour in hours:
                        if hour not in available_hours:
                            for venue in venues:
                                var_name = f"{subject_teacher}_{year}_{day}_{hour}_{venue}"
                                if var_name in variables:
                                    model.Add(variables[var_name] == 0)

        # Collect multiple solutions
        collector = TimetableCollector(list(variables.keys()), max_solutions=3)
        solver.parameters.enumerate_all_solutions = True
        status = solver.Solve(model, collector)

        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            with open(os.path.join(settings.BASE_DIR, 'timetable.log'), 'a') as f:
                f.write(f"No feasible solution found: {solver.StatusName(status)}\n")
            return []

        # Parse solutions into timetables
        timetables = []
        for solution in collector.solutions:
            timetable = []
            for var_name, value in solution.items():
                if value == 1:
                    parts = var_name.split('_')
                    subject_teacher = parts[0]
                    year = parts[1]
                    day = parts[2]
                    hour = int(parts[3])
                    venue = parts[4]
                    subject, teacher = subject_teacher.split(' - ')
                    timetable.append({
                        'year': year,
                        'subject': subject,
                        'teacher': teacher,
                        'day': day,
                        'start_hour': hour,
                        'end_hour': hour + 1,
                        'venue': venue
                    })
            timetables.append(timetable)

        return timetables

    except Exception as e:
        with open(os.path.join(settings.BASE_DIR, 'timetable.log'), 'a') as f:
            f.write(f"Error in generate_multiple_timetables: {str(e)}\n")
        return []