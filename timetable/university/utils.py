def collapse_weeks(week_list, academic_term):
    def format_weeks(start, end):
        if start == end:
            return '%d' % start
        else:
            return '%d-%d' % (
                start,
                end,
            )
    result_list = []
    tmp_start = None
    tmp_end = None
    for week in sorted(week_list):
        if tmp_start is None:
            tmp_start = week
            tmp_end = week
        elif tmp_end + 1 == week:
            tmp_end = week
        elif tmp_end + 1 == academic_term.tcp_week == week - 1:
            tmp_end = week
        else:
            result_list.append(format_weeks(tmp_start, tmp_end))
            tmp_start = week
            tmp_end = week
    result_list.append(format_weeks(tmp_start, tmp_end))
    return ','.join(result_list)
