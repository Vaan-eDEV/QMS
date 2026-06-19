import json

from .models import (
    FormResponse,
    Field,
    Table,
)


def build_traceability_data(ref_id, company):

    responses = (
        FormResponse.objects
        .filter(
            ref_id=ref_id,
            company=company
        )
        .select_related("form")
        .order_by("id")
    )

    # =========================================
    # SIGNATURE CONVERTER
    # =========================================

    def convert_signature(val):

        if (
            isinstance(val, str)
            and "signed_by" in val
        ):
            try:
                val = val.replace("'", '"')
                return json.loads(val)
            except Exception:
                return val

        return val

    # =========================================
    # FINAL DATA
    # =========================================

    final_data = {}

    # =========================================
    # LOOP RESPONSES
    # =========================================

    for res in responses:

        process = res.form.process

        if process not in final_data:
            final_data[process] = []

        cleaned_data = {}

        combined = []

        # =====================================
        # FIELDS
        # =====================================

        for field in Field.objects.filter(
            stage__form=res.form
        ):

            combined.append({
                "type": "field",
                "order": field.order,
                "key": field.label,
                "value": res.data.get(field.label),
            })

        # =====================================
        # TABLES
        # =====================================

        for table in Table.objects.filter(
            stage__form=res.form
        ):

            combined.append({
                "type": "table",
                "order": table.order,
                "key": table.name,
                "value": res.data.get(table.name),
            })

        # =====================================
        # SORT
        # =====================================

        combined = sorted(
            combined,
            key=lambda x: x["order"]
        )

        # =====================================
        # PROCESS ITEMS
        # =====================================

        for item in combined:

            key = item["key"]
            val = item["value"]

            if key not in res.data:
                continue

            if key.endswith("_row_header_name"):
                continue

            # =================================
            # TABLE
            # =================================

            if (
                isinstance(val, list)
                and val
                and isinstance(val[0], dict)
                and "row_name" in val[0]
            ):

                new_rows = []

                table_obj = Table.objects.filter(
                    name=key
                ).first()

                ordered_columns = []

                if table_obj:

                    ordered_columns = list(
                        table_obj.tablecolumn_set
                        .all()
                        .order_by("order", "id")
                        .values_list("name", flat=True)
                    )

                for row in val:

                    if not isinstance(row, dict):
                        continue

                    ordered_row = {}

                    ordered_row["row_name"] = (
                        str(row.get("row_name", "")).strip()
                    )

                    # =====================================
                    # ADD ORDERED COLUMNS
                    # =====================================

                    for col in ordered_columns:

                        clean_col = str(col).strip()

                        for row_key, row_value in row.items():

                            if str(row_key).strip() == clean_col:

                                ordered_row[clean_col] = (
                                    convert_signature(row_value)
                                )

                                break

                    # =====================================
                    # ADD REMAINING KEYS
                    # =====================================

                    for k, v in row.items():

                        clean_key = str(k).strip()

                        if (
                            clean_key != "row_name"
                            and clean_key not in ordered_row
                        ):

                            ordered_row[clean_key] = (
                                convert_signature(v)
                            )

                    new_rows.append(
                        ordered_row
                    )

                if new_rows:

                    has_total = False
                    total_column_name = ""

                    if table_obj:

                        total_col = (
                            table_obj.tablecolumn_set
                            .filter(is_total=True)
                            .first()
                        )

                        if total_col:

                            has_total = True
                            total_column_name = (
                                total_col.name
                            )

                    total_value = (
                        res.data.get(f"{key}_total")
                        or res.data.get(
                            f"{key.lower()}_total"
                        )
                        or res.data.get(
                            f"{key.upper()}_total"
                        )
                        or ""
                    )

                    # =====================================
                    # BUILD COLUMN LIST
                    # =====================================

                    all_columns = []

                    for row in new_rows:

                        for col in row.keys():

                            clean_col = str(col).strip()

                            if clean_col not in ["row_name", "_row_id"]:

                                if clean_col not in all_columns:

                                    all_columns.append(clean_col)
                    # =====================================
                    # STORE TABLE
                    # =====================================

                    cleaned_data[key] = {

                        "type": "table",

                        "header": res.data.get(
                            f"{key}_row_header_name",
                            (
                                table_obj.row_header_name
                                if table_obj
                                else "Row Name"
                            )
                        ),

                        "rows": new_rows,

                        # NEW
                        "columns": all_columns,

                        "show_total": has_total,

                        "total_column": total_column_name,

                        "total_value": total_value,
                    }

            # =================================
            # NORMAL FIELD
            # =================================

            else:

                cleaned_data[key] = (
                    convert_signature(val)
                )

        final_data[process].append({

            "form_name": res.form.name,

            "data": cleaned_data

        })

    return final_data