from datetime import datetime, timedelta

now = datetime.now()
then = datetime(2022, 3, 14, 15, 9, 26)
print((now - then).days)

(datetime.now() - then).days
