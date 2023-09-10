sql_date_trunc={
    'day':"date",
    'week':"date, 'weekday 0', '-6 days'",
    'month':"substr(date, 1, 7) || '-01'"
}