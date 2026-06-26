# import math
# from collections import defaultdict

# # =======================================================================
# # =========================== Calculate AIAG ============================ 
# # =======================================================================

# def calculate_aiag_grr(study):

#     readings = study.readings.all()

#     if not readings.exists():
#         study.study_status = "PENDING"
#         study.save()
#         return

#     # ----------------------------------
#     # AIAG CONSTANTS
#     # ----------------------------------

#     K1 = {
#         2: 0.8862,
#         3: 0.5908,
#     }

#     K2 = {
#         2: 0.7071,
#         3: 0.5231,
#     }

#     K3 = {
#         2: 0.7071,
#         3: 0.5231,
#         10: 0.3146,
#     }

#     trial_count = study.trial_count
#     operator_count = study.operator_count
#     part_count = study.part_count

#     k1 = K1.get(trial_count, 0.5908)
#     k2 = K2.get(operator_count, 0.5231)
#     k3 = K3.get(part_count, 0.3146)

#     # ----------------------------------
#     # OPERATOR + PART DATA
#     # ----------------------------------

#     operator_part_data = defaultdict(list)

#     for reading in readings:

#         operator_part_data[
#             (
#                 reading.operator,
#                 reading.part_no
#             )
#         ].append(
#             float(reading.measured_value)
#         )

#     # ----------------------------------
#     # RANGE CALCULATION
#     # ----------------------------------

#     ranges = []

#     for values in operator_part_data.values():

#         if len(values) > 1:

#             ranges.append(
#                 max(values) - min(values)
#             )

#     if not ranges:

#         study.study_status = "PENDING"
#         study.save()
#         return

#     rbar = sum(ranges) / len(ranges)

#     # ----------------------------------
#     # EV
#     # ----------------------------------

#     ev = rbar * k1

#     # ----------------------------------
#     # OPERATOR AVERAGES
#     # ----------------------------------

#     operator_averages = {}

#     for operator in study.operator_names:

#         values = []

#         for reading in readings.filter(
#             operator=operator
#         ):

#             values.append(
#                 float(
#                     reading.measured_value
#                 )
#             )

#         if values:

#             operator_averages[operator] = (
#                 sum(values) / len(values)
#             )

#     if operator_averages:

#         xdiff = (
#             max(operator_averages.values())
#             -
#             min(operator_averages.values())
#         )

#     else:

#         xdiff = 0

#     # ----------------------------------
#     # AV
#     # ----------------------------------

#     av_term = (
#         (xdiff * k2) ** 2
#         -
#         (
#             ev ** 2
#             /
#             (
#                 part_count *
#                 trial_count
#             )
#         )
#     )

#     av = math.sqrt(
#         max(av_term, 0)
#     )

#     # ----------------------------------
#     # RR
#     # ----------------------------------

#     rr = math.sqrt(
#         (ev ** 2)
#         +
#         (av ** 2)
#     )

#     # ----------------------------------
#     # PART AVERAGES
#     # ----------------------------------

#     part_averages = []

#     unique_parts = (
#         readings.values_list(
#             "part_no",
#             flat=True
#         ).distinct()
#     )

#     for part_no in unique_parts:

#         values = [

#             float(
#                 reading.measured_value
#             )

#             for reading in readings.filter(
#                 part_no=part_no
#             )

#         ]

#         if values:

#             part_averages.append(
#                 sum(values) / len(values)
#             )
#     if part_averages:

#         rp = (
#             max(part_averages)
#             -
#             min(part_averages)
#         )

#     else:

#         rp = 0

#     # ----------------------------------
#     # PV
#     # ----------------------------------

#     pv = rp * k3

#     # ----------------------------------
#     # TV
#     # ----------------------------------

#     tv = math.sqrt(
#         (rr ** 2)
#         +
#         (pv ** 2)
#     )

#     # ----------------------------------
#     # PERCENTAGES
#     # ----------------------------------

#     if tv > 0:

#         percent_ev = (
#             ev / tv
#         ) * 100

#         percent_av = (
#             av / tv
#         ) * 100

#         percent_rr = (
#             rr / tv
#         ) * 100

#         percent_pv = (
#             pv / tv
#         ) * 100

#     else:

#         percent_ev = 0
#         percent_av = 0
#         percent_rr = 0
#         percent_pv = 0

#     # ----------------------------------
#     # NDC
#     # ----------------------------------

#     if rr > 0:

#         ndc = (
#             1.41 *
#             (
#                 pv / rr
#             )
#         )

#     else:

#         ndc = 0

#     # ----------------------------------
#     # STATUS
#     # ----------------------------------

#     if percent_rr < 10:

#         status = "ACCEPTED"

#     elif percent_rr <= 30:

#         status = "CONDITIONAL"

#     else:

#         status = "REJECTED"

#     # ----------------------------------
#     # SAVE RESULTS
#     # ----------------------------------

#     study.ev = round(ev, 6)
#     study.av = round(av, 6)
#     study.rr = round(rr, 6)
#     study.pv = round(pv, 6)
#     study.tv = round(tv, 6)

#     study.percent_ev = round(percent_ev, 2)
#     study.percent_av = round(percent_av, 2)
#     study.percent_rr = round(percent_rr, 2)
#     study.percent_pv = round(percent_pv, 2)

#     study.grr_percentage = round(
#         percent_rr,
#         2
#     )

#     study.ndc = round(
#         ndc,
#         2
#     )

#     study.study_status = status

#     study.save()





import math
from collections import defaultdict


def calculate_aiag_grr(study):

    readings = study.readings.all()

    if not readings.exists():

        study.ev = None
        study.av = None
        study.rr = None
        study.pv = None
        study.tv = None

        study.percent_ev = None
        study.percent_av = None
        study.percent_rr = None
        study.percent_pv = None

        study.ndc = None
        study.grr_percentage = None
        study.study_status = "PENDING"

        study.save()

        return

    # ==================================================
    # AIAG CONSTANTS
    # ==================================================

    K1_TABLE = {

        2: 0.8862,
        3: 0.5908,
        4: 0.4857,
        5: 0.4299,

    }

    K2_TABLE = {

        2: 0.7071,
        3: 0.5231,
        4: 0.4467,
        5: 0.4030,

    }

    K3_TABLE = {

        2: 0.7071,
        3: 0.5231,
        4: 0.4467,
        5: 0.4030,
        10: 0.3146,

    }

    trial_count = study.trial_count
    operator_count = study.operator_count
    part_count = study.part_count

    k1 = K1_TABLE.get(
        trial_count,
        0.5908
    )

    k2 = K2_TABLE.get(
        operator_count,
        0.5231
    )

    k3 = K3_TABLE.get(
        part_count,
        0.3146
    )

    # ==================================================
    # OPERATOR + PART DATA
    # ==================================================

    operator_part_data = defaultdict(list)

    for reading in readings:

        operator_part_data[
            (
                reading.operator,
                reading.part_no
            )
        ].append(
            float(
                reading.measured_value
            )
        )

    # ==================================================
    # RBAR
    # ==================================================

    ranges = []

    for values in operator_part_data.values():

        if len(values) > 1:

            ranges.append(

                max(values)
                -
                min(values)

            )

    if not ranges:

        study.study_status = "PENDING"
        study.save()

        return

    rbar = sum(ranges) / len(ranges)

    # ==================================================
    # EV
    # EV = Rbar × K1
    # ==================================================

    ev = rbar * k1

    # ==================================================
    # OPERATOR AVERAGES
    # ==================================================

    operator_averages = {}

    for operator in study.operator_names:

        values = [

            float(
                reading.measured_value
            )

            for reading in readings.filter(
                operator=operator
            )

        ]

        if values:

            operator_averages[
                operator
            ] = (

                sum(values)
                /
                len(values)

            )

    if operator_averages:

        xdiff = (

            max(
                operator_averages.values()
            )

            -

            min(
                operator_averages.values()
            )

        )

    else:

        xdiff = 0

    # ==================================================
    # AV
    # AV = √MAX(0,(Xdiff*K2)^2-(EV^2/(n*t)))
    # ==================================================

    av_term = (

        (
            xdiff * k2
        ) ** 2

        -

        (

            ev ** 2

            /

            (
                part_count *
                trial_count
            )

        )

    )

    av = math.sqrt(

        max(
            av_term,
            0
        )

    )

    # ==================================================
    # GRR
    # ==================================================

    grr = math.sqrt(

        (ev ** 2)

        +

        (av ** 2)

    )

    # ==================================================
    # PART AVERAGES
    # ==================================================

    unique_parts = (

        readings.values_list(
            "part_no",
            flat=True
        )

        .distinct()

    )

    part_averages = []

    for part_no in unique_parts:

        values = [

            float(
                x.measured_value
            )

            for x in readings.filter(
                part_no=part_no
            )

        ]

        if values:

            part_averages.append(

                sum(values)
                /
                len(values)

            )

    if part_averages:

        rp = (

            max(part_averages)

            -

            min(part_averages)

        )

    else:

        rp = 0

    # ==================================================
    # PV
    # ==================================================

    pv = rp * k3

    # ==================================================
    # TV
    # ==================================================

    tv = math.sqrt(

        (grr ** 2)

        +

        (pv ** 2)

    )

    # ==================================================
    # % VALUES
    # ==================================================

    if tv > 0:

        percent_ev = (

            ev / tv

        ) * 100

        percent_av = (

            av / tv

        ) * 100

        percent_grr = (

            grr / tv

        ) * 100

        percent_pv = (

            pv / tv

        ) * 100

    else:

        percent_ev = 0
        percent_av = 0
        percent_grr = 0
        percent_pv = 0

    # ==================================================
    # NDC
    # ==================================================

    if grr > 0:

        ndc = (

            1.41

            *

            (

                pv / grr

            )

        )

    else:

        ndc = 0

    # ==================================================
    # STATUS
    # ==================================================

    if percent_grr < 10:

        status = "ACCEPTED"

    elif percent_grr <= 30:

        status = "CONDITIONAL"

    else:

        status = "REJECTED"

    # ==================================================
    # SAVE
    # ==================================================

    study.ev = round(
        ev,
        6
    )

    study.av = round(
        av,
        6
    )

    study.rr = round(
        grr,
        6
    )

    study.pv = round(
        pv,
        6
    )

    study.tv = round(
        tv,
        6
    )

    study.percent_ev = round(
        percent_ev,
        2
    )

    study.percent_av = round(
        percent_av,
        2
    )

    study.percent_rr = round(
        percent_grr,
        2
    )

    study.percent_pv = round(
        percent_pv,
        2
    )

    study.grr_percentage = round(
        percent_grr,
        2
    )

    study.ndc = round(
        ndc,
        2
    )

    study.study_status = status

    study.save()


# # ==========================================================
# # OPERATOR SUMMARY TABLE
# # ==========================================================

# def get_operator_summary(study):

#     readings = study.readings.all()

#     summary = []

#     for operator in study.operator_names:

#         values = [

#             float(
#                 r.measured_value
#             )

#             for r in readings.filter(
#                 operator=operator
#             )

#         ]

#         if not values:

#             continue

#         avg = sum(values) / len(values)

#         minimum = min(values)

#         maximum = max(values)

#         value_range = (
#             maximum - minimum
#         )

#         if len(values) > 1:

#             mean = avg

#             variance = (

#                 sum(
#                     (
#                         x - mean
#                     ) ** 2

#                     for x in values
#                 )

#                 /

#                 (
#                     len(values) - 1
#                 )

#             )

#             std_dev = math.sqrt(
#                 variance
#             )

#         else:

#             std_dev = 0

#         summary.append({

#             "operator": operator,

#             "average": round(
#                 avg,
#                 4
#             ),

#             "min": round(
#                 minimum,
#                 4
#             ),

#             "max": round(
#                 maximum,
#                 4
#             ),

#             "range": round(
#                 value_range,
#                 4
#             ),

#             "std_dev": round(
#                 std_dev,
#                 4
#             )

#         })

#     return summary



# ======================================================================
# ========================= Get Operator Summary =======================
# ======================================================================
from statistics import mean, stdev

def get_operator_summary(study):

    readings = study.readings.all()

    summary = []

    for operator in study.operator_names:

        for part in study.parts.all():

            part_readings = [
                float(r.measured_value)
                for r in readings
                if (
                    r.operator == operator
                    and r.part_no == part.part_no
                )
            ]

            if not part_readings:
                continue

            summary.append({

                "operator": operator,

                "part": part.part_no,

                "trials": part_readings,

                "average": round(
                    mean(part_readings), 4
                ),

                "minimum": round(
                    min(part_readings), 4
                ),

                "maximum": round(
                    max(part_readings), 4
                ),

                "range": round(
                    max(part_readings) -
                    min(part_readings),
                    4
                ),

                "std_dev": round(
                    stdev(part_readings),
                    4
                ) if len(part_readings) > 1 else 0

            })

    return summary


from statistics import mean


def get_operator_charts(study):

    chart_data = {}

    readings = study.readings.all()

    for operator in study.operator_names:

        xbar_data = []
        range_data = []

        xbar_values = []
        range_values = []

        for part in study.parts.all():

            values = [

                float(r.measured_value)

                for r in readings.filter(
                    operator=operator,
                    part_no=part.part_no
                )

            ]

            if not values:
                continue

            avg = round(
                sum(values) / len(values),
                4
            )

            rng = round(
                max(values) - min(values),
                4
            )

            xbar_values.append(avg)
            range_values.append(rng)

            xbar_data.append({

                "part": part.part_no,
                "average": avg,

            })

            range_data.append({

                "part": part.part_no,
                "range": rng,

            })

        # ===================================
        # XBAR STATISTICS
        # ===================================

        if xbar_values:

            xbar_mean = round(
                mean(xbar_values),
                4
            )

            xbar_max = round(
                max(xbar_values),
                4
            )

            xbar_min = round(
                min(xbar_values),
                4
            )

        else:

            xbar_mean = 0
            xbar_max = 0
            xbar_min = 0

        # ===================================
        # RANGE STATISTICS
        # ===================================

        if range_values:

            range_mean = round(
                mean(range_values),
                4
            )

            range_max = round(
                max(range_values),
                4
            )

            range_min = round(
                min(range_values),
                4
            )

        else:

            range_mean = 0
            range_max = 0
            range_min = 0

        # ===================================
        # DATA FOR CHART LABELS
        # ===================================

        xbar_mean_line = [
            xbar_mean
        ] * len(xbar_data)

        xbar_max_line = [
            xbar_max
        ] * len(xbar_data)

        xbar_min_line = [
            xbar_min
        ] * len(xbar_data)

        range_mean_line = [
            range_mean
        ] * len(range_data)

        range_max_line = [
            range_max
        ] * len(range_data)

        range_min_line = [
            range_min
        ] * len(range_data)

        chart_data[operator] = {

            "xbar": xbar_data,

            "range": range_data,

            "xbar_mean": xbar_mean,
            "xbar_max": xbar_max,
            "xbar_min": xbar_min,

            "range_mean": range_mean,
            "range_max": range_max,
            "range_min": range_min,

            "xbar_mean_line": xbar_mean_line,
            "xbar_max_line": xbar_max_line,
            "xbar_min_line": xbar_min_line,

            "range_mean_line": range_mean_line,
            "range_max_line": range_max_line,
            "range_min_line": range_min_line,

        }

    return chart_data