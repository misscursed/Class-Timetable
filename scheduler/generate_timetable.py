import json
import random
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    filename='timetable.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def generate_timetable(subjects_list, excel_file):
    logging.debug("Starting timetable generation")
    # Parse subjects_list (from frontend)
    try:
        subjects_list = json.loads(subjects_list) if subjects_list else []
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse subjects_list: {str(e)}")
        return []
    
    if not subjects_list:
        logging.error("Subjects list is empty")
        return []

    # Read Excel file data if provided
    subjects_data = None
    venues = None
    fixed_lectures = None
    teacher_availability = {}

    if excel_file:
        try:
            xl = pd.ExcelFile(excel_file)
            logging.debug(f"Excel file sheets: {xl.sheet_names}")

            # Read sheets
            subjects_df = pd.read_excel(xl, sheet_name='Subjects') if 'Subjects' in xl.sheet_names else pd.DataFrame()
            venues_df = pd.read_excel(xl, sheet_name='Venues') if 'Venues' in xl.sheet_names else pd.DataFrame()
            fixed_lectures_df = pd.read_excel(xl, sheet_name='Fixed Lectures') if 'Fixed Lectures' in xl.sheet_names else pd.DataFrame()
            teacher_availability_df = pd.read_excel(xl, sheet_name='Teacher Availability') if 'Teacher Availability' in xl.sheet_names else pd.DataFrame()

            # Process subjects
            subjects_data = subjects_df.to_dict('records') if subjects_df is not None and not subjects_df.empty else None
            logging.debug(f"Subjects data from Excel: {subjects_data}")

            # Process venues
            venues = venues_df['Venue'].tolist() if venues_df is not None and 'Venue' in venues_df.columns else None
            logging.debug(f"Venues from Excel: {venues}")

            # Process fixed lectures
            fixed_lectures = []
            if fixed_lectures_df is not None and not fixed_lectures_df.empty:
                for _, row in fixed_lectures_df.iterrows():
                    fixed_lectures.append({
                        'subject': row['Subject'],
                        'teacher': row['Teacher'],
                        'year': row['Year'],
                        'day': row['Day'],
                        'start_hour': int(row['Start Hour']),
                        'end_hour': int(row['End Hour']),
                        'venue': row['Venue']
                    })
                logging.debug(f"Fixed lectures from Excel: {fixed_lectures}")

            # Process teacher availability
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            if teacher_availability_df is not None and not teacher_availability_df.empty:
                for _, row in teacher_availability_df.iterrows():
                    teacher = row['Teacher']
                    teacher_availability[teacher] = {}
                    for day in days:
                        avail = row.get(day, '')
                        if avail:
                            slots = []
                            for slot in avail.split(','):
                                try:
                                    start, end = map(int, slot.split('-'))
                                    slots.extend(list(range(start, end)))
                                except ValueError:
                                    logging.warning(f"Invalid availability format for {teacher} on {day}: {avail}")
                                    slots.extend(list(range(8, 18)))
                            teacher_availability[teacher][day] = slots
                        else:
                            teacher_availability[teacher][day] = list(range(8, 18))
                logging.debug(f"Teacher availability from Excel: {teacher_availability}")

        except Exception as e:
            logging.error(f"Error reading Excel file: {str(e)}")
            # Fallback to default data

    # Default data if Excel file is missing or fails
    if subjects_data is None:
        subjects_data = [
            {'Subject': 'MATH', 'Teacher': 'BOB'},
            {'Subject': 'PHYSICS', 'Teacher': 'ALICE'},
            {'Subject': 'CHEMISTRY', 'Teacher': 'CAROL'},
            {'Subject': 'BIOLOGY', 'Teacher': 'DAVE'},
            {'Subject': 'HL', 'Teacher': 'CAROL'},
            {'Subject': 'OE', 'Teacher': 'BOB'}
        ]
        logging.debug("Using default subjects data")

    if venues is None:
        venues = ['LT-1.11', 'LT-2']
        logging.debug("Using default venues")

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    if not teacher_availability:
        for subject_entry in subjects_data:
            teacher = subject_entry['Teacher']
            teacher_availability[teacher] = {
                day: list(range(8, 18)) for day in days
            }
        logging.debug("Using default teacher availability")

    if fixed_lectures is None:
        fixed_lectures = [
            {'subject': 'HL', 'teacher': 'CAROL', 'year': '1st Year', 'day': 'Monday', 'start_hour': 9, 'end_hour': 11, 'venue': 'LT-1.11'},
            {'subject': 'OE', 'teacher': 'BOB', 'year': '1st Year', 'day': 'Tuesday', 'start_hour': 13, 'end_hour': 15, 'venue': 'LT-2'}
        ]
        logging.debug("Using default fixed lectures")

    # Generate timetable
    timetables = []
    for _ in range(2):  # Generate 2 possible timetables
        timetable = []
        # Add fixed lectures
        timetable.extend(fixed_lectures)

        # Track used slots and subject schedules
        used_slots = {(slot['day'], slot['start_hour'], slot['end_hour'], slot['venue']) for slot in timetable}
        subject_schedules = {}  # Track schedules per subject to check for back-to-back slots

        for subject_entry in subjects_list:
            subject_teacher = subject_entry.get('subject_teacher', '')
            hours = int(subject_entry.get('hours', 0))
            year = subject_entry.get('year', '1st Year')
            schedule_type = subject_entry.get('schedule_type', 'distributed')
            if not subject_teacher or hours <= 0:
                logging.warning(f"Invalid subject entry: {subject_entry}")
                continue

            try:
                subject, teacher = subject_teacher.split(' - ')
            except ValueError:
                logging.error(f"Invalid subject_teacher format: {subject_teacher}")
                continue

            # Initialize tracking for this subject
            subject_key = f"{subject}-{teacher}-{year}"
            if subject_key not in subject_schedules:
                subject_schedules[subject_key] = []

            # Skip if already scheduled as a fixed lecture
            fixed_hours = sum(
                (slot['end_hour'] - slot['start_hour'])
                for slot in fixed_lectures
                if slot['subject'] == subject and slot['teacher'] == teacher and slot['year'] == year
            )
            remaining_hours = hours - fixed_hours
            if remaining_hours <= 0:
                continue

            if schedule_type == 'all_together':
                # Schedule all hours consecutively on one day
                scheduled = False
                attempts = 0
                while not scheduled and attempts < 100:
                    attempts += 1
                    day = random.choice(days)
                    venue = random.choice(venues)
                    available_hours = sorted(teacher_availability.get(teacher, {}).get(day, list(range(8, 18))))
                    if len(available_hours) < remaining_hours:
                        logging.debug(f"Not enough available hours for {subject} on {day}: {available_hours}")
                        continue

                    # Find a consecutive block of remaining_hours
                    start_hour = None
                    for i in range(len(available_hours) - remaining_hours + 1):
                        consecutive = True
                        for j in range(remaining_hours):
                            current_hour = available_hours[i + j]
                            if j > 0 and current_hour != available_hours[i + j - 1] + 1:
                                consecutive = False
                                break
                            for h in range(current_hour, current_hour + 1):
                                if (day, h, h + 1, venue) in used_slots:
                                    consecutive = False
                                    break
                        if consecutive:
                            start_hour = available_hours[i]
                            break

                    if start_hour is not None:
                        end_hour = start_hour + remaining_hours
                        for h in range(start_hour, end_hour):
                            used_slots.add((day, h, h + 1, venue))
                        timetable.append({
                            'subject': subject,
                            'teacher': teacher,
                            'year': year,
                            'day': day,
                            'start_hour': start_hour,
                            'end_hour': end_hour,
                            'venue': venue
                        })
                        subject_schedules[subject_key].append((day, start_hour, end_hour))
                        scheduled = True
                        logging.debug(f"Scheduled {subject} - {teacher} on {day} from {start_hour} to {end_hour} in {venue} (all together)")
                    else:
                        logging.debug(f"Failed to find consecutive slot for {subject} - {teacher} on {day}")

            else:
                # Distributed scheduling: spread across different days with random durations, no back-to-back
                scheduled_days = set()  # Track days already used for this subject
                hours_to_schedule = remaining_hours
                while hours_to_schedule > 0:
                    # Randomly choose duration: 1 or 2 hours, ensuring we don't overshoot remaining hours
                    duration = random.choice([1, 2]) if hours_to_schedule >= 2 else 1
                    hours_to_schedule -= duration

                    scheduled = False
                    attempts = 0
                    while not scheduled and attempts < 100:
                        attempts += 1
                        # Pick a day that hasn't been used yet for this subject
                        available_days = [d for d in days if d not in scheduled_days]
                        if not available_days:
                            # If all days are used, allow reuse
                            available_days = days
                        day = random.choice(available_days)
                        venue = random.choice(venues)
                        available_hours = sorted(teacher_availability.get(teacher, {}).get(day, list(range(8, 18))))
                        if not available_hours:
                            logging.debug(f"No available hours for {teacher} on {day}")
                            continue

                        # Find a random start hour that can fit the duration
                        possible_starts = [
                            h for h in available_hours
                            if all((day, h + i, h + i + 1, venue) not in used_slots for i in range(duration))
                            and (h + duration - 1) in available_hours
                        ]
                        if not possible_starts:
                            logging.debug(f"No possible start hours for {subject} on {day} for duration {duration}")
                            continue
                        start_hour = random.choice(possible_starts)
                        end_hour = start_hour + duration

                        # Check for back-to-back slots on the same day
                        back_to_back = False
                        for scheduled_slot in subject_schedules[subject_key]:
                            scheduled_day, scheduled_start, scheduled_end = scheduled_slot
                            if scheduled_day == day:
                                if start_hour == scheduled_end or end_hour == scheduled_start:
                                    back_to_back = True
                                    break

                        if not back_to_back:
                            for h in range(start_hour, end_hour):
                                used_slots.add((day, h, h + 1, venue))
                            timetable.append({
                                'subject': subject,
                                'teacher': teacher,
                                'year': year,
                                'day': day,
                                'start_hour': start_hour,
                                'end_hour': end_hour,
                                'venue': venue
                            })
                            subject_schedules[subject_key].append((day, start_hour, end_hour))
                            scheduled = True
                            scheduled_days.add(day)  # Mark this day as used
                            logging.debug(f"Scheduled {subject} - {teacher} on {day} from {start_hour} to {end_hour} in {venue} (distributed)")
                        else:
                            logging.debug(f"Avoided back-to-back scheduling for {subject} - {teacher} on {day} from {start_hour} to {end_hour}")

        timetables.append(timetable)

    logging.debug(f"Generated timetables: {timetables}")
    return timetables