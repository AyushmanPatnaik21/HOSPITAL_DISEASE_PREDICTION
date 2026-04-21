import sqlite3
import os

def get_db():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(BASE_DIR, "database", "hospital.db")
    return sqlite3.connect(db_path)


def add_appointment(patient_id, doctor_id, date, time):
    from datetime import datetime
    conn = get_db()
    cursor = conn.cursor()
    booked_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, date, time, status, booked_at)
        VALUES (?, ?, ?, ?, 'Booked', ?)
    """, (patient_id, doctor_id, date, time, booked_at))

    conn.commit()
    conn.close()


def get_all_appointments():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.appointment_id, p.name, d.name, a.date, a.time, a.status, a.booked_at
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def cancel_appointment(appointment_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE appointments
        SET status='Cancelled'
        WHERE appointment_id=?
    """, (appointment_id,))

    conn.commit()
    conn.close()


def delete_appointment(appointment_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM appointments
        WHERE appointment_id=?
    """, (appointment_id,))

    conn.commit()
    conn.close()


def get_appointments_by_user(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.appointment_id, p.name, d.name, a.date, a.time, a.status, a.booked_at
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE p.user_id = ?
    """, (user_id,))

    data = cursor.fetchall()
    conn.close()
    return data


def get_appointments_by_patient(patient_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.appointment_id, p.name, d.name, a.date, a.time, a.status, a.booked_at
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.patient_id = ?
        ORDER BY a.date DESC, a.time DESC
    """, (patient_id,))

    data = cursor.fetchall()
    conn.close()
    return data


def get_available_slots(doctor_id, date):
    """
    Get available time slots for a doctor on a specific date.
    Returns a list of available time slots in HH:MM format.
    """
    from backend.models.doctor_model import get_doctor
    from datetime import datetime
    
    try:
        doctor = get_doctor(doctor_id)
        if not doctor:
            print(f"DEBUG: Doctor not found for doctor_id {doctor_id}")
            return []
        
        availability = doctor[4]  # availability field is at index 4
        if not availability:
            print(f"DEBUG: No availability data for doctor {doctor_id}")
            return []
        
        print(f"DEBUG: Doctor availability string: '{availability}'")
        
        # Parse availability string to get start and end times
        parsed_availability = parse_doctor_availability(availability)
        if not parsed_availability:
            print(f"DEBUG: Failed to parse availability '{availability}'")
            return []
            
        if not parsed_availability.get('start_time') or not parsed_availability.get('end_time'):
            print(f"DEBUG: Missing start_time or end_time: {parsed_availability}")
            return []
        
        print(f"DEBUG: Parsed availability: {parsed_availability}")
        
        # Check if the requested date is a valid day for this doctor
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            day_name = date_obj.strftime('%A')  # Get day name (Monday, Tuesday, etc.)
            print(f"DEBUG: Requested date {date} is {day_name}")
            print(f"DEBUG: Available days: {parsed_availability['days']}")
            
            if day_name not in parsed_availability['days']:
                print(f"DEBUG: {day_name} not in available days")
                return []
        except Exception as e:
            print(f"DEBUG: Error parsing date {date}: {e}")
            return []
        
        # Parse start and end times
        try:
            start_time_str = parsed_availability['start_time']
            end_time_str = parsed_availability['end_time']
            
            start_hour, start_min = map(int, start_time_str.split(':'))
            end_hour, end_min = map(int, end_time_str.split(':'))
            print(f"DEBUG: Time range: {start_hour:02d}:{start_min:02d} to {end_hour:02d}:{end_min:02d}")
        except Exception as e:
            print(f"DEBUG: Error parsing times: {e}")
            return []
        
        # Get booked times for this doctor on this date
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT time FROM appointments 
            WHERE doctor_id = ? AND date = ? AND status != 'Cancelled'
        """, (doctor_id, date))
        booked_times = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"DEBUG: Booked times: {booked_times}")
        
        # Generate slots every 30 minutes
        slots = []
        current_hour = start_hour
        current_min = start_min
        
        while current_hour < end_hour or (current_hour == end_hour and current_min < end_min):
            time_str = f"{current_hour:02d}:{current_min:02d}"
            if time_str not in booked_times:
                slots.append(time_str)
            current_min += 30
            if current_min >= 60:
                current_min = 0
                current_hour += 1
        
        print(f"DEBUG: Generated {len(slots)} available slots")
        return slots
    except Exception as e:
        print(f"DEBUG: Unexpected error in get_available_slots: {e}")
        import traceback
        traceback.print_exc()
        return []


def parse_doctor_availability(availability_str):
    """
    Parse doctor availability string in multiple formats:
    - "Mon-Fri 09:00-17:00" (24-hour with colon)
    - "Sat-Sun 10.30-2.00" (12-hour with dot)
    - "Mon-Fri 9AM-5PM" (12-hour with AM/PM)
    - "9:00 - 17:00" (time only, any non-time preceded by day range)
    
    Returns dict with time and available days
    """
    if not availability_str:
        return None
    
    result = {
        'days': [],
        'start_time': '',
        'end_time': ''
    }
    
    try:
        # Clean up the string
        availability_str = availability_str.strip()
        print(f"DEBUG parse_availability: Input string: '{availability_str}'")
        
        # Split by space to separate days and times
        parts = availability_str.split()
        print(f"DEBUG parse_availability: parts = {parts}")
        
        # Find the day range (first part should be days)
        day_str = parts[0] if parts else ""
        result['days'] = expand_day_range(day_str)
        print(f"DEBUG parse_availability: Expanded days = {result['days']}")
        
        # Parse time range - look for any part that contains time info
        start_time = None
        end_time = None
        
        # Join the remaining parts and look for time pattern
        remaining_str = ' '.join(parts[1:]) if len(parts) > 1 else ""
        print(f"DEBUG parse_availability: Remaining string: '{remaining_str}'")
        
        # Try multiple time formats
        # Format 1: "09:00-17:00" or "09.00-17.00"
        import re
        # Pattern for HH:MM-HH:MM or H:MM-H:MM or HH.MM-HH.MM
        time_pattern_1 = r'(\d{1,2}[:.]\d{2})\s*-\s*(\d{1,2}[:.]\d{2})'
        match = re.search(time_pattern_1, remaining_str)
        if match:
            start_str = match.group(1).replace('.', ':')
            end_str = match.group(2).replace('.', ':')
            print(f"DEBUG parse_availability: Matched format 1: {start_str} - {end_str}")
        else:
            # Format 2: "9AM-5PM" or "9am-5pm" or "9 AM - 5 PM"
            time_pattern_2 = r'(\d{1,2})\s*(am|pm|AM|PM)\s*-\s*(\d{1,2})\s*(am|pm|AM|PM)'
            match = re.search(time_pattern_2, remaining_str)
            if match:
                start_hour = int(match.group(1))
                start_period = match.group(2).lower()
                end_hour = int(match.group(3))
                end_period = match.group(4).lower()
                
                # Convert to 24-hour format
                if start_period == 'pm' and start_hour != 12:
                    start_hour += 12
                elif start_period == 'am' and start_hour == 12:
                    start_hour = 0
                    
                if end_period == 'pm' and end_hour != 12:
                    end_hour += 12
                elif end_period == 'am' and end_hour == 12:
                    end_hour = 0
                
                start_str = f"{start_hour:02d}:00"
                end_str = f"{end_hour:02d}:00"
                print(f"DEBUG parse_availability: Matched format 2 (AM/PM): {start_str} - {end_str}")
            else:
                print(f"DEBUG parse_availability: No time pattern matched in '{remaining_str}'")
                # If no time format found, return what we have (days only)
                if result['days']:
                    result['start_time'] = "09:00"
                    result['end_time'] = "17:00"
                    print(f"DEBUG parse_availability: Using default times 09:00-17:00")
                return result if result['days'] else None
        
        result['start_time'] = start_str
        result['end_time'] = end_str
        
        return result if result['days'] else None
    except Exception as e:
        print(f"DEBUG parse_availability: Exception: {e}")
        import traceback
        traceback.print_exc()
        return None


def expand_day_range(day_str):
    """
    Expand day range like "Mon-Fri" or "Monday-Friday" to list of days
    """
    all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    short_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    if '-' not in day_str:
        # Single day
        if day_str in short_days:
            return [all_days[short_days.index(day_str)]]
        elif day_str in all_days:
            return [day_str]
        return []
    
    # Range like "Mon-Fri"
    parts = day_str.split('-')
    start_day = parts[0].strip()
    end_day = parts[1].strip()
    
    # Determine if we're using short or long format
    if start_day in short_days:
        start_idx = short_days.index(start_day)
        end_idx = short_days.index(end_day) if end_day in short_days else 0
        return [all_days[i] for i in range(start_idx, end_idx + 1)]
    elif start_day in all_days:
        start_idx = all_days.index(start_day)
        end_idx = all_days.index(end_day) if end_day in all_days else 0
        return [all_days[i] for i in range(start_idx, end_idx + 1)]
    
    return []


def format_time_to_12hour(time_24h):
    """
    Convert 24-hour format time (HH:MM) to 12-hour format (HH:MM AM/PM)
    """
    try:
        hours, minutes = map(int, time_24h.split(':'))
        period = 'AM' if hours < 12 else 'PM'
        hours_12 = hours % 12
        if hours_12 == 0:
            hours_12 = 12
        return f"{hours_12:02d}:{minutes:02d} {period}"
    except:
        return time_24h


def get_appointments_by_patient(patient_id):
    """Get appointments for a specific patient"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.appointment_id, p.name, d.name, a.date, a.time, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.patient_id = ?
    """, (patient_id,))

    data = cursor.fetchall()
    conn.close()
    return data


def get_appointments_by_user(user_id):
    """Get appointments for patients associated with a specific user"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.appointment_id, p.name, d.name, a.date, a.time, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE p.user_id = ?
    """, (user_id,))

    data = cursor.fetchall()
    conn.close()
    return data