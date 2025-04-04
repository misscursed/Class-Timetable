# from django import forms

# class TimetableForm(forms.Form):
#     def clean(self):
#         cleaned_data = super().clean()
#         subjects = {}
#         teachers = set()
#         venues = set()
#         for key, value in self.data.items():
#             if key.startswith('subject_'):
#                 idx = key.split('_')[1]
#                 subject = value
#                 teacher = self.data.get(f'teacher_{idx}')
#                 year = self.data.get(f'year_{idx}')
#                 hours = self.data.get(f'hours_{idx}')
#                 if not all([subject, teacher, year, hours]):
#                     raise forms.ValidationError(f"Missing data for subject entry {idx}")
#                 try:
#                     hours = int(hours)
#                     if hours <= 0:
#                         raise ValueError
#                 except ValueError:
#                     raise forms.ValidationError(f"Hours for {subject} must be a positive integer")
#                 subjects.setdefault(subject, []).append((teacher, year, hours))
#                 teachers.add(teacher)
#             elif key.startswith('venue_'):
#                 venues.add(value)
#             elif key.startswith('teacher_availability_') or key.startswith('venue_availability_'):
#                 try:
#                     for slot in value.split(','):
#                         start, end = map(int, slot.split('-'))
#                         if not (8 <= start < end <= 18):
#                             raise ValueError
#                 except ValueError:
#                     raise forms.ValidationError(f"Invalid availability format for {key}: use e.g., '8-12,13-18' within 8-18")
#         cleaned_data['subjects'] = subjects
#         cleaned_data['teachers'] = teachers
#         cleaned_data['venues'] = venues
#         return cleaned_data





from django import forms

class TimetableUploadForm(forms.Form):
    file = forms.FileField(label="Upload Timetable Data File")