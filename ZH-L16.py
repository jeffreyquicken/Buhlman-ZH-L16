import math
import json

# Half-time values for Nitrogen with associated 'b' value and 'a' value for ZH-L16A, ZH-L16B and ZH-L16C
# ZH-L16A: original without conservatism
# ZH-L16B: more conservative 'a' values (for dive table construction)
# ZH-L16C: faster 'a' values
ZHL16N = {
    "1": {"t": 4.0, "b": 0.505, "a": {"A": 1.2599, "B": 1.2599, "C": 1.2599}},
    "1b": {"t": 5.0, "b": 0.5578, "a": {"A": 1.1696, "B": 1.1696, "C": 1.1696}},
    "2": {"t": 8.0, "b": 0.6514, "a": {"A": 1.0, "B": 1.0, "C": 1.0}},
    "3": {"t": 12.5, "b": 0.7222, "a": {"A": 0.8618, "B": 0.8618, "C": 0.8618}},
    "4": {"t": 18.5, "b": 0.7825, "a": {"A": 0.7562, "B": 0.7562, "C": 0.7562}},
    "5": {"t": 27.0, "b": 0.8126, "a": {"A": 0.6667, "B": 0.6667, "C": 0.62}},
    "6": {"t": 38.3, "b": 0.8434, "a": {"A": 0.5933, "B": 0.56, "C": 0.5043}},
    "7": {"t": 54.3, "b": 0.8693, "a": {"A": 0.5282, "B": 0.4947, "C": 0.441}},
    "8": {"t": 77.0, "b": 0.891, "a": {"A": 0.4701, "B": 0.45, "C": 0.4}},
    "9": {"t": 109.0, "b": 0.9092, "a": {"A": 0.4187, "B": 0.4187, "C": 0.375}},
    "10": {"t": 146.0, "b": 0.9222, "a": {"A": 0.3798, "B": 0.3798, "C": 0.35}},
    "11": {"t": 187.0, "b": 0.9319, "a": {"A": 0.3497, "B": 0.3497, "C": 0.3295}},
    "12": {"t": 239.0, "b": 0.9403, "a": {"A": 0.3223, "B": 0.3223, "C": 0.3065}},
    "13": {"t": 305.0, "b": 0.9477, "a": {"A": 0.2971, "B": 0.285, "C": 0.2835}},
    "14": {"t": 390.0, "b": 0.9544, "a": {"A": 0.2737, "B": 0.2737, "C": 0.261}},
    "15": {"t": 498.0, "b": 0.9602, "a": {"A": 0.2523, "B": 0.2523, "C": 0.248}},
    "16": {"t": 635.0, "b": 0.9653, "a": {"A": 0.2327, "B": 0.2327, "C": 0.2327}}
}

# Partial pressure of water vapour
PP_WATERVAPOUR = 0.0567

# factionof N2 in air
fN = 0.79

def depth_to_atm(depth):
    """
    Converts dive depth (m) to hydrostatic pressure (atm)

    :param depth: dive depth in meters
    :return: pressure in atm (1 atmosphere = 1 bar)
    """
    return depth / 10 + 1


def calculate_inert_gas_pressure_compartment(p_begin, pp_gasmix, t_exposure, halftime, depth):
    """
    Calculates pressure of inert gas in compartment

    WARNING -- This formula assumes the descent is instant. Averaging is necessary for more realistic values
    :param p_begin: Inert gas pressure in the compartment before the exposure (atm)
    :param pp_gasmix: Partial pressure of the inert gas breathed by the diver
    :param t_exposure:
    :param halftime:
    :return: pressure of inert gas in compartment (atm)
    """
    p_depth = depth_to_atm(depth)
    p_gasmix = pp_gasmix * p_depth  # P of inert gas at depth is partial P of inert gas multiplied by total P at depth
    return p_begin + (p_gasmix - p_begin) * (1 - 2 ** (- t_exposure / halftime))


def calculate_tolerated_ambient_pressure_compartment(a, b, p_comp):
    """
    Calculates the maximum tolerated ambient pressure we can safely ascend to for a given compartment (a and b)
    without bubble formation in compartment
    :param a: a modifier as given by the ZH-L16 variant
    :param b: b modifier as given by the ZH-L16 variant
    :param p_comp: Inert gas pressure in the compartment
    :return: Maximum tolerated pressure for compartment (atm)
    """
    return ((p_comp - a) * b)


def initialise_compartments():
    p_N = round(fN * (1 - PP_WATERVAPOUR), 4)  # Initial value of nitrogen loading in all compartments
    compartments = {
        "1": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "1b": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "2": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "3": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "4": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "5": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "6": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "7": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "8": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "9": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "10": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "11": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "12": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "13": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "14": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "15": {"p_N": p_N, "p_He": 0, "p_total": p_N},
        "16": {"p_N": p_N, "p_He": 0, "p_total": p_N}
    }

    with open('compartments.json', 'w') as f:
        json.dump(compartments, f)


def calculate_schreiner(p_comp, time, rate, halftime_decay, p_ambient=0.7452):
    """
    Calculates Schreiner equation; inert pressure in compartment after time at depth

    :param p_comp: initial compartment inert gas pressure
    :param time: time interval
    :param rate: rate of descent times fraction of inert gas
    :param halftime_decay: halftime decay value of compartment (ln(2)/halftime)
    :param p_ambient: ambient pressure minus water vapor pressure (=0.7452)
    :return: pressure in tissue compartment
    """
    x1 = rate * (time - 1 / halftime_decay)
    x2 = p_ambient - p_comp - (rate / halftime_decay)
    x3 = math.e ** - halftime_decay * time
    result = round(p_ambient + x1 - x2 * x3, 4)
    return result

def evaluate_descent(depth, descent_rate = 30):
    time = depth / descent_rate
    print("time: " + str(time))
    p_comp_init = (depth - PP_WATERVAPOUR) * fN
    rate = descent_rate * fN
    print("rate: " + str(rate))
    with open('compartments.json') as f:
        data = json.load(f)
    for compartment in data:
        p_comp = data[compartment]["p_N"]
        print("pcomp: " + str(p_comp))
        halftime = ZHL16N[compartment]["t"]
        print("halftime: " + str(halftime))
        haltime_decay = math.log(2) / halftime
        print("decay: " + str(haltime_decay))
        result = calculate_schreiner(p_comp, time, rate, haltime_decay, p_comp_init)
        print(result)
        data[compartment]["p_N"] = result

    with open('compartments.json', 'w') as f:
        json.dump(data, f)
initialise_compartments()

evaluate_descent(10)