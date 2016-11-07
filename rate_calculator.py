def tennesse_pennysylvania(weight, percentage=None):
    rates = {100: 1.65, 300: 1.60}  # USD
    rates_keys = rates.keys()
    min_val, max_val = min(rates_keys), max(rates_keys)

    if weight < min_val:
        rate = rates.get(min_val)
    else:
        rate = rates.get(max(i for i in rates_keys if i <= weight))

    fsc = weight * 0.85
    sec = weight * 0.17

    pick_up = max(35, weight * 0.35)
    transfer = max(20, weight * 0.12)
    export_formalities = 75

    if percentage:
        final_rate = rate + rate * (percentage / 100)
    else:
        final_rate = rate

    total = weight * final_rate + fsc + sec + pick_up + transfer + export_formalities

    return total, rate, final_rate


def hong_kong(weight, percentage=None):
    rates = {300: 1.79}  # USD
    rates_keys = rates.keys()
    min_val, max_val = min(rates_keys), max(rates_keys)

    if weight < min_val:
        rate = rates.get(min_val)
    else:
        rate = rates.get(max(i for i in rates_keys if i <= weight))

    airline_handling = 35
    terminal_handling = weight * 0.23
    cartage = weight * 0.10
    pick_up = max(45, weight * 0.10)

    if percentage:
        final_rate = rate + rate * (percentage / 100)
    else:
        final_rate = rate

    total = weight * final_rate + airline_handling + terminal_handling + cartage + pick_up

    return total, rate, final_rate


def london(weight, percentage=None):
    rates = {300: 1.30}  # USD
    rates_keys = rates.keys()
    min_val, max_val = min(rates_keys), max(rates_keys)

    if weight < min_val:
        rate = rates.get(min_val)
    else:
        rate = rates.get(max(i for i in rates_keys if i <= weight))

    pick_up = (25 + weight * 0.15) * 1.23  # converting GBP to USD

    if percentage:
        final_rate = rate + rate * (percentage / 100)
    else:
        final_rate = rate

    total = weight * final_rate + pick_up

    return total, rate, final_rate


def uk(weight, area, percentage=None):
    rates = {45: 1.65, 100: 1.40, 300: 1.30, 500: 1.15, 1000: 1.10}  # GBP
    rates_keys = rates.keys()
    min_val, max_val = min(rates_keys), max(rates_keys)

    if weight < min_val:
        rate = rates.get(min_val)
    else:
        rate = rates.get(max(i for i in rates_keys if i <= weight))

    if area == '1':
        pick_up = 25 + weight * 0.10
    if area == '2':
        pick_up = 25 + weight * 0.15
    if area == '3':
        pick_up = 25 + weight * 0.20
    if area == '4':
        pick_up = 30 + weight * 0.30
    if area == '5':
        pick_up = 30 + weight * 0.35

    if percentage:
        final_rate = rate + rate * (percentage / 100)
    else:
        final_rate = rate

    pre_total = max(60, weight * final_rate)
    total = (pre_total + pick_up) * 1.23  # converting GBP to USD

    return total, rate, final_rate


def new_york(weight, percentage=None):
    rates = {300: 2.75}  # AED
    rates_keys = rates.keys()
    min_val, max_val = min(rates_keys), max(rates_keys)

    if weight < min_val:
        rate = rates.get(min_val)
    else:
        rate = rates.get(max(i for i in rates_keys if i <= weight))

    if percentage:
        final_rate = rate + rate * (percentage / 100)
    else:
        final_rate = rate

    total = weight * final_rate

    return total, rate, final_rate


# all values in AED
def dubai(weight):
    custom_clearance = 200
    delivery_order = 300
    transportation = max(150, weight * 0.30 if weight <= 3000 else weight * 0.20)
    airline_handling = max(90, weight * 0.30)
    custom_bill = 110
    cargo_transfer = 120
    total = custom_clearance + delivery_order + transportation + airline_handling + custom_bill + cargo_transfer

    return total  # AED