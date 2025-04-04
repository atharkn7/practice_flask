from datetime import datetime

def format_date(users):
    if isinstance(users, list):
        for user in users:
            user.date_added = user.date_added.strftime("%Y.%m.%d")
    else:
        users.date_added = users.date_added.strftime("%Y.%m.%d")
