import time
import calendar
from datetime import datetime
from .models import CompanyInfo

def company_data(request):
    info = CompanyInfo.objects.first()
    
    # Получием таймзону
    tz_name = time.tzname[0]
    offset = int(-time.timezone / 3600)
    sign = "+" if offset >= 0 else ""
    local_tz = f"{tz_name} (UTC{sign}{offset})"
    
    now_local = datetime.now()
    now_utc = datetime.utcnow()
    
    # Текстовый календарь
    cal = calendar.TextCalendar(calendar.MONDAY)
    text_calendar = cal.formatmonth(now_local.year, now_local.month)

    return {
        'company_global': info,
        'date_local': now_local.strftime("(%d/%m/%Y)"),
        'time_local': now_local.strftime("%H:%M:%S"),
        'date_utc': now_utc.strftime("(%d/%m/%Y)"),
        'time_utc': now_utc.strftime("%H:%M:%S"),
        'tz_user': local_tz,
        'text_calendar_global': text_calendar,
    }