import datetime


def year(request):
    current_datetime = datetime.datetime.now()
    return {'year': current_datetime.year}
