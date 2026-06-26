import math
from collections import defaultdict


def calculate_aiag_grr(study):

    readings = study.readings.all()

    if not readings.exists():
        study.study_status = "PENDING"
        study.save()
        return

    # ----------------------------------
    # AIAG CONSTANTS
    # ----------------------------------

    K1 = {
        2: 0.8862,
        3: 0.5908,
    }

    K2 = {
        2: 0.7071,
        3: 0.5231,
    }

    K3 = {
        2: 0.7071,
        3: 0.5231,
        10: 0.3146,
    }

    trial_count = study.trial_count
    operator_count = study.operator_count
    part_count = study.part_count

    k1 = K1.get(trial_count, 0.5908)
    k2 = K2.get(operator_count, 0.5231)
    k3 = K3.get(part_count, 0.3146)

    # ----------------------------------
    # OPERATOR + PART DATA
    # ----------------------------------

    operator_part_data = defaultdict(list)

    for reading in readings:

        operator_part_data[
            (
                reading.operator,
                int(reading.part_no)
            )
        ].append(
            float(reading.measured_value)
        )

    # ----------------------------------
    # RANGE CALCULATION
    # ----------------------------------

    ranges = []

    for values in operator_part_data.values():

        if len(values) > 1:

            ranges.append(
                max(values) - min(values)
            )

    if not ranges:

        study.study_status = "PENDING"
        study.save()
        return

    rbar = sum(ranges) / len(ranges)

    # ----------------------------------
    # EV
    # ----------------------------------

    ev = rbar * k1

    # ----------------------------------
    # OPERATOR AVERAGES
    # ----------------------------------

    operator_averages = {}

    for operator in study.operator_names:

        values = []

        for reading in readings.filter(
            operator=operator
        ):

            values.append(
                float(
                    reading.measured_value
                )
            )

        if values:

            operator_averages[operator] = (
                sum(values) / len(values)
            )

    if operator_averages:

        xdiff = (
            max(operator_averages.values())
            -
            min(operator_averages.values())
        )

    else:

        xdiff = 0

    # ----------------------------------
    # AV
    # ----------------------------------

    av_term = (
        (xdiff * k2) ** 2
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
        max(av_term, 0)
    )

    # ----------------------------------
    # RR
    # ----------------------------------

    rr = math.sqrt(
        (ev ** 2)
        +
        (av ** 2)
    )

    # ----------------------------------
    # PART AVERAGES
    # ----------------------------------

    part_averages = []

    for part in range(
        1,
        part_count + 1
    ):

        values = []

        for reading in readings.filter(
            part_no=str(part)
        ):

            values.append(
                float(
                    reading.measured_value
                )
            )

        if values:

            part_averages.append(
                sum(values) / len(values)
            )

    if part_averages:

        rp = (
            max(part_averages)
            -
            min(part_averages)
        )

    else:

        rp = 0

    # ----------------------------------
    # PV
    # ----------------------------------

    pv = rp * k3

    # ----------------------------------
    # TV
    # ----------------------------------

    tv = math.sqrt(
        (rr ** 2)
        +
        (pv ** 2)
    )

    # ----------------------------------
    # PERCENTAGES
    # ----------------------------------

    if tv > 0:

        percent_ev = (
            ev / tv
        ) * 100

        percent_av = (
            av / tv
        ) * 100

        percent_rr = (
            rr / tv
        ) * 100

        percent_pv = (
            pv / tv
        ) * 100

    else:

        percent_ev = 0
        percent_av = 0
        percent_rr = 0
        percent_pv = 0

    # ----------------------------------
    # NDC
    # ----------------------------------

    if rr > 0:

        ndc = (
            1.41 *
            (
                pv / rr
            )
        )

    else:

        ndc = 0

    # ----------------------------------
    # STATUS
    # ----------------------------------

    if percent_rr < 10:

        status = "ACCEPTED"

    elif percent_rr <= 30:

        status = "CONDITIONAL"

    else:

        status = "REJECTED"

    # ----------------------------------
    # SAVE RESULTS
    # ----------------------------------

    study.ev = round(ev, 6)
    study.av = round(av, 6)
    study.rr = round(rr, 6)
    study.pv = round(pv, 6)
    study.tv = round(tv, 6)

    study.percent_ev = round(percent_ev, 2)
    study.percent_av = round(percent_av, 2)
    study.percent_rr = round(percent_rr, 2)
    study.percent_pv = round(percent_pv, 2)

    study.grr_percentage = round(
        percent_rr,
        2
    )

    study.ndc = round(
        ndc,
        2
    )

    study.study_status = status

    study.save()