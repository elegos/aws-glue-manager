def fromTimeToString(hours=0, minutes=0, seconds=0):
    totalSeconds = seconds + minutes * 60 + hours * 60 * 60

    hours = int(totalSeconds / 60 / 60)
    totalSeconds = totalSeconds - hours * 60 * 60
    minutes = int(totalSeconds / 60)
    seconds = totalSeconds - minutes * 60

    return f'{hours:02d}:{minutes:02d}:{seconds:02d}'
