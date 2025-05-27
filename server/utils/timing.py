import datetime

def check_time(TZ):
    current_time = datetime.datetime.now(datetime.UTC).time()
    if current_time.hour >= 0 and current_time.hour <= 8:
        if TZ == "TOKYO":
            return True
        else:
            return False
    elif current_time.hour >= 7 and current_time.hour <= 15:
        if TZ == "LONDON":
            return True
        else:
            return False
    elif current_time.hour >= 13 and current_time.hour <= 19:
        if TZ == "NEW_YORK":
            return True
        else:
            return False
    elif current_time.hour >= 22 and current_time.hour <= 5:
        if TZ == "SYDNEY":
            return True
        else:
            return False
    else:
        return False
