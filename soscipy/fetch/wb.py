import world_bank_data as wb


def world_bank(url):
    data = wb.get_series('SP.POP.TOTL', mrv=1).to_frame().reset_index()
    return data