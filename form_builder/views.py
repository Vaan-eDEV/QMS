from django.shortcuts import render, redirect
from .models import (
    Form,
    Stage,
    Field,
    Table,
    TableColumn,
    TableRow,
    TableCellConfig,
    FormResponse
)
from .services import build_traceability_data
import json
from qms_app.decorators import require_page_permission
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from po_qu.models import Quotation
import os
from django.db.models import Max
from django.conf import settings
#
# ============================================== Form Builder ==============================================
#


# from django.db.models import Max
# import json

# from django.db.models import Max
# import json

# @require_page_permission("can_form_build")
# def form_builder(request):

#     process_filter = request.GET.get("process")

#     forms = Form.objects.all().order_by("id")

#     if process_filter:
#         forms = forms.filter(process=process_filter)

#     current_form = None
#     if process_filter:
#         current_form = Form.objects.filter(
#             process=process_filter,
#             is_active=False,
#             created_by=request.user
#         ).order_by("-id").first()

#     if current_form:
#         stages = Stage.objects.select_related("form").filter(
#             form=current_form
#         ).order_by("order")
#     else:
#         stages = []

#     # ================= OPTIONS SPLIT =================
#     for stage in stages:
#         for field in stage.field_set.all():
#             field.option_list = field.options.split(",") if field.options else []

#         for table in stage.table_set.all():
#             for col in table.tablecolumn_set.all():
#                 col.option_list = col.options.split(",") if col.options else []
    
#     for stage in stages:
#         combined = []

#         # ✅ FIELDS
#         for field in stage.field_set.all():
#             field.option_list = field.options.split(",") if field.options else []

#             combined.append({
#                 "type": "field",
#                 "order": field.order,
#                 "data": field
#             })

#         # ✅ TABLES
#         for table in stage.table_set.all():
#             for col in table.tablecolumn_set.all():
#                 col.option_list = col.options.split(",") if col.options else []

#             combined.append({
#                 "type": "table",
#                 "order": table.order,
#                 "data": table
#             })

#         # ✅ FINAL SORT
#         stage.combined_items = sorted(combined, key=lambda x: x["order"])


#     if request.method == "POST":

#         action = request.POST.get("action")

#         # ================= CREATE FORM =================
#         if action == "create_form":

#             form_name = request.POST.get("form_name", "").strip()
#             process = request.POST.get("process") or process_filter or "RFQ"

#             if form_name:
#                 Form.objects.create(
#                     name=form_name,
#                     process=process,
#                     is_active=False,
#                     created_by=request.user
#                 )

#             return redirect(f"/form-builder/builder/?process={process}")

#         # ================= ADD STAGE =================
#         elif action == "add_stage":

#             form_id = request.POST.get("form_id")
#             stage_name = request.POST.get("stage_name", "").strip()

#             if form_id and stage_name:

#                 last = Stage.objects.filter(form_id=form_id)\
#                     .aggregate(Max("order"))["order__max"] or 0

#                 Stage.objects.create(
#                     form_id=form_id,
#                     name=stage_name,
#                     order=last + 1,
#                     created_by=request.user
#                 )

#             return redirect(request.get_full_path())

#         # ================= ADD FIELD =================
#         elif action == "add_field":

#             stage_id = request.POST.get("stage_id")
#             label = request.POST.get("label", "").strip()
#             field_type = request.POST.get("field_type")
#             formula = request.POST.get("formula", "").strip()
#             options = request.POST.get("options", "").strip()

#             if stage_id and label and field_type:

#                 # 🔥 FIX: COMMON ORDER (FIELD + TABLE)
#                 field_last = Field.objects.filter(stage_id=stage_id)\
#                     .aggregate(Max("order"))["order__max"] or 0

#                 table_last = Table.objects.filter(stage_id=stage_id)\
#                     .aggregate(Max("order"))["order__max"] or 0

#                 last = max(field_last, table_last)

#                 field = Field.objects.create(
#                     stage_id=stage_id,
#                     label=label,
#                     field_type=field_type,
#                     formula=formula or None,
#                     options=options or None,
#                     order=last + 1,
#                     created_by=request.user
#                 )

#                 # ================= TABLE CREATION =================
#                 if field_type == "table":

#                     columns_json = request.POST.get("table_columns")

#                     try:
#                         columns = json.loads(columns_json) if columns_json else []
#                     except:
#                         columns = []

#                     # 🔥 FIX: COMMON ORDER (FIELD + TABLE)
#                     field_last = Field.objects.filter(stage_id=stage_id)\
#                         .aggregate(Max("order"))["order__max"] or 0

#                     table_last = Table.objects.filter(stage_id=stage_id)\
#                         .aggregate(Max("order"))["order__max"] or 0

#                     last_table = max(field_last, table_last)

#                     table = Table.objects.create(
#                         stage_id=stage_id,
#                         name=label,
#                         order=last_table + 1,
#                         created_by=request.user
#                     )

#                     valid_columns = [col for col in columns if col.get("name")]

#                     for i, col in enumerate(valid_columns, start=1):
#                         TableColumn.objects.create(
#                             table=table,
#                             name=col.get("name"),
#                             column_type=col.get("type"),
#                             formula=col.get("formula") or None,
#                             options=col.get("options") or None,
#                             is_total=col.get("is_total", False),
#                             order=i,
#                             created_by=request.user
#                         )

#             return redirect(request.get_full_path())

#         # ================= FINAL SUBMIT =================
#         elif action == "final_submit":

#             if current_form:
#                 current_form.is_active = True
#                 current_form.save()

#             return redirect(f"/form-builder/builder/?process={process_filter}")

#     return render(request, "form_builder/form_builder.html", {
#         "forms": forms,
#         "stages": stages,
#         "selected_process": process_filter,
#         "current_form": current_form
#     })

from django.db.models import Max
import json

@require_page_permission("can_form_build")
def form_builder(request):

    process_filter = request.GET.get("process")

    forms = Form.objects.all().order_by("id")

    if process_filter:
        forms = forms.filter(process=process_filter)

    current_form = None

    if process_filter:
        current_form = Form.objects.filter(
            process=process_filter,
            is_active=False,
            created_by=request.user
        ).order_by("-id").first()

    if current_form:
        stages = Stage.objects.select_related("form").filter(
            form=current_form
        ).order_by("order")
    else:
        stages = []

    # =====================================================
    # OPTIONS SPLIT
    # =====================================================

    for stage in stages:

        for field in stage.field_set.all():

            field.option_list = (
                field.options.split(",")
                if field.options else []
            )

        for table in stage.table_set.all():

            for col in table.tablecolumn_set.all():

                col.option_list = (
                    col.options.split(",")
                    if col.options else []
                )

    # =====================================================
    # COMBINED ORDER
    # =====================================================

    for stage in stages:

        combined = []

        # =================================================
        # FIELDS
        # =================================================

        for field in stage.field_set.all():

            field.option_list = (
                field.options.split(",")
                if field.options else []
            )

            combined.append({
                "type": "field",
                "order": field.order,
                "data": field
            })

        # =================================================
        # TABLES
        # =================================================

        for table in stage.table_set.all():

            for col in table.tablecolumn_set.all():

                col.option_list = (
                    col.options.split(",")
                    if col.options else []
                )

            combined.append({
                "type": "table",
                "order": table.order,
                "data": table
            })

        # =================================================
        # FINAL SORT
        # =================================================

        stage.combined_items = sorted(
            combined,
            key=lambda x: x["order"]
        )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        action = request.POST.get("action")

        # =================================================
        # CREATE FORM
        # =================================================

        if action == "create_form":

            form_name = request.POST.get(
                "form_name",
                ""
            ).strip()

            process = (
                request.POST.get("process")
                or process_filter
                or "RFQ"
            )

            if form_name:

                Form.objects.create(
                    name=form_name,
                    process=process,
                    is_active=False,
                    created_by=request.user
                )

            return redirect(
                f"/form-builder/builder/?process={process}"
            )

        # =================================================
        # ADD STAGE
        # =================================================

        elif action == "add_stage":

            form_id = request.POST.get("form_id")

            stage_name = request.POST.get(
                "stage_name",
                ""
            ).strip()

            if form_id and stage_name:

                last = (
                    Stage.objects
                    .filter(form_id=form_id)
                    .aggregate(Max("order"))["order__max"]
                    or 0
                )

                Stage.objects.create(
                    form_id=form_id,
                    name=stage_name,
                    order=last + 1,
                    created_by=request.user
                )

            return redirect(request.get_full_path())

        # =================================================
        # ADD FIELD
        # =================================================

        elif action == "add_field":

            stage_id = request.POST.get("stage_id")

            label = request.POST.get(
                "label",
                ""
            ).strip()

            field_type = request.POST.get(
                "field_type"
            )

            formula = request.POST.get(
                "formula",
                ""
            ).strip()

            options = request.POST.get(
                "options",
                ""
            ).strip()

            if stage_id and label and field_type:

                # =========================================
                # COMMON ORDER
                # =========================================

                field_last = (
                    Field.objects
                    .filter(stage_id=stage_id)
                    .aggregate(Max("order"))["order__max"]
                    or 0
                )

                table_last = (
                    Table.objects
                    .filter(stage_id=stage_id)
                    .aggregate(Max("order"))["order__max"]
                    or 0
                )

                last = max(field_last, table_last)

                # =========================================
                # CREATE FIELD
                # =========================================

                if field_type != "table":
                    Field.objects.create(
                        stage_id=stage_id,
                        label=label,
                        field_type=field_type,
                        formula=formula or None,
                        options=options or None,
                        order=last + 1,
                        created_by=request.user
                    )

                # =========================================
                # TABLE CREATION
                # =========================================

                if field_type == "table":

                    columns_json = request.POST.get(
                        "table_columns"
                    )

                    rows_json = request.POST.get(
                        "table_rows"
                    )

                    cell_configs_json = request.POST.get(
                        "table_cell_configs"
                    )

                    layout_type = request.POST.get(
                        "layout_type",
                        "matrix"
                    )

                    # =====================================
                    # PARSE COLUMNS
                    # =====================================

                    try:
                        columns = (
                            json.loads(columns_json)
                            if columns_json else []
                        )
                    except:
                        columns = []

                    # =====================================
                    # PARSE ROWS
                    # =====================================

                    try:
                        rows = (
                            json.loads(rows_json)
                            if rows_json else []
                        )
                    except:
                        rows = []

                    # =====================================
                    # PARSE CELL CONFIGS
                    # =====================================

                    try:
                        cell_configs = (
                            json.loads(cell_configs_json)
                            if cell_configs_json else {}
                        )
                    except:
                        cell_configs = {}

                    # =====================================
                    # ORDER FIX
                    # =====================================

                    field_last = (
                        Field.objects
                        .filter(stage_id=stage_id)
                        .aggregate(Max("order"))["order__max"]
                        or 0
                    )

                    table_last = (
                        Table.objects
                        .filter(stage_id=stage_id)
                        .aggregate(Max("order"))["order__max"]
                        or 0
                    )

                    last_table = max(
                        field_last,
                        table_last
                    )

                    # =====================================
                    # CREATE TABLE
                    # =====================================
                    row_header_name = request.POST.get(
                        "row_header_name",
                        "Row Name"
                    ).strip()
                    table = Table.objects.create(
                        stage_id=stage_id,
                        name=label,
                        layout_type=layout_type,
                        row_header_name=row_header_name,
                        order=last_table + 1,
                        created_by=request.user
                    )

                    # =====================================
                    # CREATE COLUMNS
                    # =====================================

                    valid_columns = [
                        col for col in columns
                        if col.get("name")
                    ]

                    table_columns = []

                    for i, col in enumerate(
                        valid_columns,
                        start=1
                    ):

                        table_col = TableColumn.objects.create(

                            table=table,

                            name=col.get("name"),

                            # SAFE DEFAULT
                            column_type="text",

                            formula=None,

                            options=None,

                            
                            is_total=col.get(
                                "is_total",
                                False
                            ),


                            order=i,

                            created_by=request.user
                        )

                        table_columns.append(table_col)

                    # =====================================
                    # CREATE ROWS
                    # =====================================

                    created_rows = []

                    for i, row_name in enumerate(
                        rows,
                        start=1
                    ):

                        row_name = str(row_name).strip()

                        if not row_name:
                            continue

                        table_row = TableRow.objects.create(
                            table=table,
                            name=row_name,
                            order=i
                        )

                        created_rows.append(table_row)

                    # =====================================
                    # CREATE CELL CONFIGS
                    # =====================================

                    if layout_type == "matrix":

                        for row_index, row in enumerate(
                            created_rows
                        ):

                            for col_index, col in enumerate(
                                table_columns
                            ):

                                key = f"{row_index}_{col_index}"

                                config = (
                                    cell_configs.get(key, {})
                                )

                                TableCellConfig.objects.create(

                                    table=table,

                                    row=row,

                                    column=col,

                                    cell_type=config.get(
                                        "type",
                                        "text"
                                    ),

                                    options=config.get(
                                        "options",
                                        ""
                                    ),

                                    formula=config.get(
                                        "formula",
                                        ""
                                    ),
                                    is_total=config.get(
                                        "is_total",
                                        False
                                    )
                                )

            return redirect(request.get_full_path())

        # =================================================
        # FINAL SUBMIT
        # =================================================

        elif action == "final_submit":

            if current_form:

                current_form.is_active = True

                current_form.save()

            return redirect(
                f"/form-builder/builder/?process={process_filter}"
            )


    # =====================================================
    # CELL CONFIGS
    # =====================================================

    cell_configs = {}

    for config in TableCellConfig.objects.select_related(
        "row",
        "column"
    ):

        config.option_list = (
            config.options.split(",")
            if config.options else []
        )

        key = f"{config.row_id}_{config.column_id}"

        cell_configs[key] = config
    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "form_builder/form_builder.html",
        {
            "forms": forms,
            "stages": stages,
            "selected_process": process_filter,
            "current_form": current_form,
            "cell_configs": cell_configs
        }
    )



# ============================================== Edit Form =====================================================
# ============================================== EDIT FORM ==============================================
# ============================================== EDIT FORM ==============================================

from django.db.models import Max, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import json

from .models import (
    Form,
    Stage,
    Field,
    Table,
    TableColumn,
    TableRow,
    TableCellConfig
)


@login_required
def edit_form(request, form_id):

    # =====================================================
    # FORM
    # =====================================================

    form = get_object_or_404(
        Form,
        id=form_id
    )

    # =====================================================
    # STAGES
    # =====================================================

    stages = Stage.objects.filter(
        form=form
    ).prefetch_related(

        Prefetch(
            "field_set",
            queryset=Field.objects.order_by("order")
        ),

        Prefetch(
            "table_set",
            queryset=Table.objects.order_by("order").prefetch_related(

                Prefetch(
                    "tablecolumn_set",
                    queryset=TableColumn.objects.order_by("order")
                ),

                Prefetch(
                    "tablerow_set",
                    queryset=TableRow.objects.order_by("order")
                ),

                "tablecellconfig_set"
            )
        )

    ).order_by("order")

    # =====================================================
    # OPTIONS
    # =====================================================

    for stage in stages:

        for field in stage.field_set.all():

            field.option_list = (
                field.options.split(",")
                if field.options else []
            )

        for table in stage.table_set.all():

            for col in table.tablecolumn_set.all():

                col.option_list = (
                    col.options.split(",")
                    if col.options else []
                )

    # =====================================================
    # COMBINED ITEMS
    # =====================================================

    for stage in stages:

        combined = []

        # ================= FIELDS =================

        for field in stage.field_set.all():

            combined.append({
                "type": "field",
                "order": field.order,
                "data": field
            })

        # ================= TABLES =================

        for table in stage.table_set.all():

            combined.append({
                "type": "table",
                "order": table.order,
                "data": table
            })

        stage.combined_items = sorted(
            combined,
            key=lambda x: x["order"]
        )

    # =====================================================
    # CELL CONFIGS
    # =====================================================

    cell_configs = {}

    for config in TableCellConfig.objects.select_related(
        "row",
        "column"
    ):

        config.option_list = (
            config.options.split(",")
            if config.options else []
        )

        key = f"{config.row_id}_{config.column_id}"

        cell_configs[key] = config

    # =====================================================
    # VALID TYPES
    # =====================================================

    VALID_FIELD_TYPES = [
        i[0] for i in Field.FIELD_TYPES
    ]

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        action = request.POST.get("action")

        # =================================================
        # UPDATE FORM
        # =================================================

        if action == "update_form":

            form_name = request.POST.get(
                "form_name",
                ""
            ).strip()

            if form_name:

                form.name = form_name

                form.save()

            return redirect(request.path)

        # =================================================
        # ADD STAGE
        # =================================================

        elif action == "add_stage":

            stage_name = request.POST.get(
                "stage_name",
                ""
            ).strip()

            if stage_name:

                last = (
                    Stage.objects
                    .filter(form=form)
                    .aggregate(Max("order"))["order__max"]
                    or 0
                )

                Stage.objects.create(
                    form=form,
                    name=stage_name,
                    order=last + 1,
                    created_by=request.user
                )

            return redirect(request.path)

        # =================================================
        # ADD FIELD / TABLE
        # =================================================

        elif action == "add_field":

            stage_id = request.POST.get(
                "stage_id"
            )

            label = request.POST.get(
                "label",
                ""
            ).strip()

            field_type = request.POST.get(
                "field_type"
            )

            formula = request.POST.get(
                "formula",
                ""
            ).strip()

            options = request.POST.get(
                "options",
                ""
            ).strip()

            if field_type not in VALID_FIELD_TYPES:

                return HttpResponseForbidden(
                    f"Invalid field type: {field_type}"
                )

            if stage_id and label and field_type:

                # =========================================
                # COMMON ORDER
                # =========================================

                field_last = (
                    Field.objects
                    .filter(stage_id=stage_id)
                    .aggregate(Max("order"))["order__max"]
                    or 0
                )

                table_last = (
                    Table.objects
                    .filter(stage_id=stage_id)
                    .aggregate(Max("order"))["order__max"]
                    or 0
                )

                last = max(
                    field_last,
                    table_last
                )

                # =========================================
                # NORMAL FIELD
                # =========================================

                if field_type != "table":

                    Field.objects.create(

                        stage_id=stage_id,

                        label=label,

                        field_type=field_type,

                        formula=formula or None,

                        options=options or None,

                        order=last + 1,

                        created_by=request.user
                    )

                # =========================================
                # MATRIX TABLE
                # =========================================

                else:

                    columns_json = request.POST.get(
                        "table_columns"
                    )

                    rows_json = request.POST.get(
                        "table_rows"
                    )

                    cell_configs_json = request.POST.get(
                        "table_cell_configs"
                    )

                    layout_type = request.POST.get(
                        "layout_type",
                        "matrix"
                    )

                    # =====================================
                    # PARSE JSON
                    # =====================================

                    try:
                        columns = json.loads(
                            columns_json
                        ) if columns_json else []
                    except:
                        columns = []

                    try:
                        rows = json.loads(
                            rows_json
                        ) if rows_json else []
                    except:
                        rows = []

                    try:
                        cell_configs_data = json.loads(
                            cell_configs_json
                        ) if cell_configs_json else {}
                    except:
                        cell_configs_data = {}

                    # =====================================
                    # CREATE TABLE
                    # =====================================
                    
                    row_header_name = request.POST.get(
                        "row_header_name",
                        "Row Name"
                    )
                    table = Table.objects.create(

                        stage_id=stage_id,

                        name=label,

                        layout_type=layout_type,

                        row_header_name = row_header_name,

                        order=last + 1,

                        created_by=request.user

                    )

                    # =====================================
                    # CREATE COLUMNS
                    # =====================================

                    created_columns = []

                    for i, col in enumerate(
                        columns,
                        start=1
                    ):

                        if not col.get("name"):
                            continue

                        table_col = TableColumn.objects.create(

                            table=table,

                            name=col.get("name"),

                            column_type="text",

                            formula=None,

                            options=None,

                                is_total=col.get(
                                    "is_total",
                                    False
                                ),

                            order=i,

                            created_by=request.user
                        )

                        created_columns.append(
                            table_col
                        )

                    # =====================================
                    # CREATE ROWS
                    # =====================================

                    created_rows = []

                    for i, row_name in enumerate(
                        rows,
                        start=1
                    ):

                        row_name = str(
                            row_name
                        ).strip()

                        if not row_name:
                            continue

                        table_row = TableRow.objects.create(

                            table=table,

                            name=row_name,

                            order=i
                        )

                        created_rows.append(
                            table_row
                        )

                    # =====================================
                    # CREATE CELL CONFIGS
                    # =====================================

                    for row_index, row in enumerate(
                        created_rows
                    ):

                        for col_index, col in enumerate(
                            created_columns
                        ):

                            key = (
                                f"{row_index}_{col_index}"
                            )

                            config = (
                                cell_configs_data.get(
                                    key,
                                    {}
                                )
                            )

                            TableCellConfig.objects.create(

                                table=table,

                                row=row,

                                column=col,

                                cell_type=config.get(
                                    "type",
                                    "text"
                                ),

                                options=config.get(
                                    "options",
                                    ""
                                ),

                                formula=config.get(
                                    "formula",
                                    ""
                                ),
                                is_total=config.get(
                                    "is_total",
                                    False
                                )
                            )

            return redirect(request.path)

        # =================================================
        # UPDATE MATRIX TABLE
        # =================================================

        elif action == "update_matrix_table":

            table_id = request.POST.get(
                "table_id"
            )

            table = get_object_or_404(
                Table,
                id=table_id
            )

            table.name = request.POST.get(
                "table_name",
                table.name
            )

            table.row_header_name = request.POST.get(
                "row_header_name",
                "Row Name"
            )

            table.save()

            # =============================================
            # JSON
            # =============================================

            try:
                columns = json.loads(
                    request.POST.get(
                        "table_columns",
                        "[]"
                    )
                )
            except:
                columns = []

            try:
                rows = json.loads(
                    request.POST.get(
                        "table_rows",
                        "[]"
                    )
                )
            except:
                rows = []

            try:
                configs = json.loads(
                    request.POST.get(
                        "table_cell_configs",
                        "{}"
                    )
                )
            except:
                configs = {}

            # =============================================
            # DELETE OLD
            # =============================================

            TableCellConfig.objects.filter(
                table=table
            ).delete()

            TableColumn.objects.filter(
                table=table
            ).delete()

            TableRow.objects.filter(
                table=table
            ).delete()

            # =============================================
            # CREATE NEW COLUMNS
            # =============================================

            created_columns = []

            for i, col in enumerate(
                columns,
                start=1
            ):

                table_col = TableColumn.objects.create(

                    table=table,

                    name=col.get("name"),

                    column_type="text",

                    is_total=col.get(
                        "is_total",
                        False
                    ),

                    order=i,

                    created_by=request.user
                )

                created_columns.append(
                    table_col
                )

            # =============================================
            # CREATE NEW ROWS
            # =============================================

            created_rows = []

            for i, row_name in enumerate(
                rows,
                start=1
            ):

                table_row = TableRow.objects.create(

                    table=table,

                    name=row_name,

                    order=i
                )

                created_rows.append(
                    table_row
                )

            # =============================================
            # CREATE CELL CONFIGS
            # =============================================

            for row_index, row in enumerate(
                created_rows
            ):

                for col_index, col in enumerate(
                    created_columns
                ):

                    key = (
                        f"{row_index}_{col_index}"
                    )

                    config = configs.get(
                        key,
                        {}
                    )

                    TableCellConfig.objects.create(

                        table=table,

                        row=row,

                        column=col,

                        cell_type=config.get(
                            "type",
                            "text"
                        ),

                        options=config.get(
                            "options",
                            ""
                        ),

                        formula=config.get(
                            "formula",
                            ""
                        ),
                        is_total=config.get(
                            "is_total",
                            False
                        )
                    )

            return redirect(request.path)

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "form_builder/edit_form.html",
        {
            "form": form,
            "stages": stages,
            "FIELD_TYPES": Field.FIELD_TYPES,
            "COLUMN_TYPES": TableColumn.COLUMN_TYPES,
            "cell_configs": cell_configs
        }
    )


# =====================================================
# DELETE TABLE
# =====================================================

@login_required
def delete_table(request, table_id):

    if request.method == "POST":

        table = get_object_or_404(
            Table,
            id=table_id
        )

        AuditLog.objects.create(
            user=request.user,
            role=request.user.role,
            module="form_builder",
            action="DELETE",
            model_name="Table",
            object_id=str(table.id),
            object_repr=str(table),
            description="Table deleted"
        )

        table.delete()

        return JsonResponse({
            "status": "deleted"
        })

    return JsonResponse({
        "status":"error"
    })
# from django.shortcuts import get_object_or_404, redirect, render
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponseForbidden
# from .models import Form, Stage, Field, Table, TableColumn


# @login_required
# def edit_form(request, form_id):

#     form = get_object_or_404(Form, id=form_id)

#     stages = Stage.objects.filter(form=form).prefetch_related(

#         Prefetch("field_set", queryset=Field.objects.order_by("order")),

#         Prefetch(
#             "table_set",
#             queryset=Table.objects.order_by("order").prefetch_related(
#                 Prefetch(
#                     "tablecolumn_set",
#                     queryset=TableColumn.objects.order_by("order")
#                 )
#             )
#         )

#     ).order_by("order")

#     # ================= PREPARE OPTIONS =================
#     for stage in stages:
#         for field in stage.field_set.all():
#             field.option_list = field.options.split(",") if field.options else []

#         for table in stage.table_set.all():
#             for col in table.tablecolumn_set.all():
#                 col.option_list = col.options.split(",") if col.options else []

#     for stage in stages:
#         combined = []
#         for f in stage.field_set.all():
#             f.item_type = "field"
#             combined.append(f)

#         for t in stage.table_set.all():
#             t.item_type = "table"
#             combined.append(t)
#         stage.combined_items = sorted(combined, key=lambda x: x.order)


#     VALID_FIELD_TYPES = [i[0] for i in Field.FIELD_TYPES]
#     VALID_COLUMN_TYPES = [i[0] for i in TableColumn.COLUMN_TYPES]

#     if request.method == "POST":

#         action = request.POST.get("action")

#         # ================= UPDATE FORM =================
#         if action == "update_form":

#             form_name = request.POST.get("form_name", "").strip()

#             if form_name:
#                 form.name = form_name
#                 form.save()

#             return redirect(request.path)

#         # ================= ADD STAGE =================
#         elif action == "add_stage":

#             stage_name = request.POST.get("stage_name", "").strip()

#             if stage_name:
#                 last = Stage.objects.filter(form=form)\
#                     .aggregate(Max("order"))["order__max"] or 0

#                 Stage.objects.create(
#                     form=form,
#                     name=stage_name,
#                     order=last + 1,
#                     created_by=request.user
#                 )

#             return redirect(request.path)

#         # ================= ADD FIELD =================
#         elif action == "add_field":

#             stage_id = request.POST.get("stage_id")
#             label = request.POST.get("label", "").strip()
#             field_type = request.POST.get("field_type")

#             if field_type not in VALID_FIELD_TYPES:
#                 return HttpResponseForbidden(f"Invalid field type: {field_type}")

#             if stage_id and label:
#                 last = Field.objects.filter(stage_id=stage_id)\
#                     .aggregate(Max("order"))["order__max"] or 0

#                 Field.objects.create(
#                     stage_id=stage_id,
#                     label=label,
#                     field_type=field_type,
#                     order=last + 1,
#                     created_by=request.user
#                 )

#             return redirect(request.path)

#         # ================= ADD TABLE =================
#         elif action == "add_table":

#             stage_id = request.POST.get("stage_id")
#             table_name = request.POST.get("table_name", "").strip()

#             if stage_id and table_name:
#                 last = Table.objects.filter(stage_id=stage_id)\
#                     .aggregate(Max("order"))["order__max"] or 0

#                 Table.objects.create(
#                     stage_id=stage_id,
#                     name=table_name,
#                     order=last + 1,
#                     created_by=request.user
#                 )

#             return redirect(request.path)

#         # ================= ADD COLUMN =================
#         elif action == "add_column":

#             table_id = request.POST.get("table_id")
#             col_name = request.POST.get("col_name", "").strip()
#             col_type = request.POST.get("col_type")

#             if col_type not in VALID_COLUMN_TYPES:
#                 return HttpResponseForbidden(f"Invalid column type: {col_type}")

#             if table_id and col_name:
#                 last = TableColumn.objects.filter(table_id=table_id)\
#                     .aggregate(Max("order"))["order__max"] or 0

#                 TableColumn.objects.create(
#                     table_id=table_id,
#                     name=col_name,
#                     column_type=col_type,
#                     order=last + 1,
#                     created_by=request.user
#                 )

#             return redirect(request.path)

#         # ================= UPDATE TABLE & COLUMN =================
#         elif action == "update_table_column":

#             for key, value in request.POST.items():

#                 value = value.strip()

#                 if key.startswith("table_name_"):
#                     table_id = key.split("_")[-1]
#                     if value:
#                         Table.objects.filter(id=table_id).update(name=value)

#                 elif key.startswith("col_name_"):
#                     col_id = key.split("_")[-1]
#                     if value:
#                         TableColumn.objects.filter(id=col_id).update(name=value)

#                 elif key.startswith("col_type_"):
#                     col_id = key.split("_")[-1]

#                     if value in VALID_COLUMN_TYPES:
#                         TableColumn.objects.filter(id=col_id).update(column_type=value)
#                     else:
#                         return HttpResponseForbidden(f"Invalid column update: {value}")

#                 elif key.startswith("col_options_"):
#                     col_id = key.split("_")[-1]
#                     TableColumn.objects.filter(id=col_id).update(options=value)

#             return redirect(request.path)

#     return render(request, "form_builder/edit_form.html", {
#         "form": form,
#         "stages": stages,
#         "FIELD_TYPES": Field.FIELD_TYPES,
#         "COLUMN_TYPES": TableColumn.COLUMN_TYPES,
#     })




from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Form, FormResponse


@login_required
def open_next_form(request):

    process = request.GET.get("process")
    ref_id = request.GET.get("ref_id")
    company = request.GET.get("company")
    form_id = request.GET.get("form_id")

    # ================= FIX COMPANY =================
    #  DO NOT auto-fetch company using only ref_id
    #  If company is missing → redirect safely

    if ref_id and not company:
        return redirect("/form-builder/kanban/")  #  SAFE FAIL

    # ================= SELECT FORM =================
    if form_id:
        form = Form.objects.filter(id=form_id).first()
    else:
        form = Form.objects.filter(process=process).order_by("-id").first()

    if not form:
        return redirect("/form-builder/kanban/")

    # ================= BUILD URL =================
    url = f"/form-builder/fill/{form.id}/?"

    params = []

    if ref_id:
        params.append(f"ref_id={ref_id}")

    if company:
        params.append(f"company={company}")

    if params:
        url += "&".join(params)

    return redirect(url)


# @login_required
# def data_list(request):

#     companies = (
#         FormResponse.objects
#         .exclude(company__isnull=True)
#         .exclude(company="")
#         .values_list("company", flat=True)
#         .distinct()
#     )

#     return render(request, "form_builder/data_list.html", {
#         "companies": companies
#     })
@login_required
def data_list(request):

    responses = FormResponse.objects.select_related("form")

    company_data = {}
    register_data = []

    for res in responses:

        process = (res.form.process or "").strip().upper()

        # ================= RFQ =================
        if process == "RFQ":

            # 🚫 BLOCK DEFAULT COMPANY
            if not res.company or res.company.lower() == "default":
                continue

            if res.company not in company_data:
                company_data[res.company] = []

            company_data[res.company].append(res.ref_id)

        # ================= REGISTER =================
        elif process == "REGISTER":

            register_data.append({
                "ref_id": res.ref_id,
                "doc_name": res.doc_name
            })

    return render(request, "form_builder/data_list.html", {
        "company_data": company_data,
        "register_data": register_data
    })



@login_required
def company_rfq_list(request, company):

    rfqs = (
        FormResponse.objects
        .filter(company=company)
        .exclude(ref_id__isnull=True)
        .exclude(ref_id="")
        .values("ref_id")
        .distinct()
        .order_by("-ref_id")   #  latest first
    )

    rfq_list = [r["ref_id"] for r in rfqs]

    return render(request, "form_builder/rfq_list.html", {
        "company": company,
        "rfqs": rfq_list
    })




# import json
# @login_required
# def data_detail(request, ref_id):

#     company = request.GET.get("company")

#     if not company:
#         return HttpResponse(
#             "Company missing in URL",
#             status=400
#         )

#     responses = (
#         FormResponse.objects
#         .filter(
#             ref_id=ref_id,
#             company=company
#         )
#         .select_related("form")
#         .order_by("id")
#     )

#     # =========================================
#     # SIGNATURE CONVERTER
#     # =========================================

#     def convert_signature(val):

#         if (
#             isinstance(val, str)
#             and "signed_by" in val
#         ):

#             try:

#                 val = val.replace("'", '"')

#                 return json.loads(val)

#             except:

#                 return val

#         return val

#     # =========================================
#     # FINAL DATA
#     # =========================================

#     final_data = {}

#     # =========================================
#     # LOOP RESPONSES
#     # =========================================

#     for res in responses:

#         process = res.form.process

#         if process not in final_data:

#             final_data[process] = []

#         cleaned_data = {}

#         # =====================================
#         # SAME ORDER AS KANBAN
#         # =====================================

#         combined = []

#         # =====================================
#         # FIELDS
#         # =====================================

#         for field in Field.objects.filter(
#             stage__form=res.form
#         ):

#             combined.append({

#                 "type": "field",

#                 "order": field.order,

#                 "key": field.label,

#                 "value": res.data.get(field.label)

#             })

#         # =====================================
#         # TABLES
#         # =====================================

#         for table in Table.objects.filter(
#             stage__form=res.form
#         ):

#             combined.append({

#                 "type": "table",

#                 "order": table.order,

#                 "key": table.name,

#                 "value": res.data.get(table.name)

#             })

#         # =====================================
#         # FINAL SORT
#         # =====================================

#         combined = sorted(
#             combined,
#             key=lambda x: x["order"]
#         )

#         # =====================================
#         # LOOP ORDERED ITEMS
#         # =====================================

#         for item in combined:

#             key = item["key"]

#             val = item["value"]

#             if key not in res.data:
#                 continue

#             # =================================
#             # SKIP HEADER META
#             # =================================

#             if key.endswith("_row_header_name"):
#                 continue

#             # =================================
#             # TABLE DATA
#             # =================================

#             if (
#                 isinstance(val, list)
#                 and
#                 val
#                 and
#                 isinstance(val[0], dict)
#                 and
#                 "row_name" in val[0]
#             ):

#                 new_rows = []

#                 # =============================
#                 # FIND TABLE
#                 # =============================

#                 table_obj = Table.objects.filter(
#                     name=key
#                 ).first()

#                 # =============================
#                 # ORDERED COLUMNS
#                 # =============================

#                 ordered_columns = []

#                 if table_obj:

#                     ordered_columns = list(

#                         table_obj.tablecolumn_set.all()
#                         .order_by("order", "id")
#                         .values_list("name", flat=True)

#                     )

#                 # =============================
#                 # PROCESS ROWS
#                 # =============================

#                 for row in val:

#                     if not isinstance(row, dict):
#                         continue

#                     # =========================
#                     # FILTER EMPTY ROW
#                     # =========================

#                     # if not any(
#                     #     str(v).strip()
#                     #     not in ["", "None", "null"]
#                     #     for v in row.values()
#                     # ):
#                     #     continue

#                     ordered_row = {}

#                     # =========================
#                     # ROW NAME FIRST
#                     # =========================

#                     ordered_row["row_name"] = (
#                         row.get("row_name", "")
#                     )

#                     # =========================
#                     # KEEP COLUMN ORDER
#                     # =========================

#                     for col in ordered_columns:

#                         if col in row:

#                             ordered_row[col] = (
#                                 convert_signature(
#                                     row[col]
#                                 )
#                             )

#                     # =========================
#                     # EXTRA COLUMNS
#                     # =========================

#                     for k, v in row.items():

#                         if (
#                             k != "row_name"
#                             and
#                             k not in ordered_columns
#                         ):

#                             ordered_row[k] = (
#                                 convert_signature(v)
#                             )

#                     new_rows.append(ordered_row)

#                 # =============================
#                 # STORE TABLE
#                 # =============================

#                 # =============================
#                 # STORE TABLE
#                 # =============================

#                 if new_rows:

#                     # =====================================
#                     # TOTAL COLUMN SUPPORT
#                     # =====================================

#                     has_total = False

#                     total_column_name = ""

#                     if table_obj:

#                         total_col = (
#                             table_obj.tablecolumn_set
#                             .filter(is_total=True)
#                             .first()
#                         )

#                         if total_col:

#                             has_total = True

#                             total_column_name = (
#                                 total_col.name
#                             )

#                     # =====================================
#                     # FIND TOTAL VALUE
#                     # =====================================

#                     total_value = (

#                         res.data.get(f"{key}_total")

#                         or

#                         res.data.get(
#                             f"{key.lower()}_total"
#                         )

#                         or

#                         res.data.get(
#                             f"{key.upper()}_total"
#                         )

#                         or

#                         ""
#                     )

#                 # =====================================
#                 # STORE TABLE
#                 # =====================================

#                 cleaned_data[key] = {

#                     "type": "table",

#                     "header": res.data.get(

#                         f"{key}_row_header_name",

#                         (
#                             table_obj.row_header_name
#                             if table_obj
#                             else "Row Name"
#                         )
#                     ),

#                     "rows": new_rows,

#                     # =================================
#                     # TOTAL SUPPORT
#                     # =================================

#                     "show_total": has_total,

#                     "total_column": total_column_name,

#                     "total_value": total_value
#                 }
#             # =================================
#             # NORMAL FIELD
#             # =================================

#             else:

#                 cleaned_data[key] = (
#                     convert_signature(val)
#                 )

#         # =====================================
#         # FINAL APPEND
#         # =====================================

#         final_data[process].append({

#             "form_name": res.form.name,

#             "data": cleaned_data

#         })

#     # =========================================
#     # RENDER
#     # =========================================

#     return render(

#         request,

#         "form_builder/data_detail.html",

#         {
#             "data": final_data,
#             "ref_id": ref_id,
#             "company": company
#         }
#     )



@login_required
def data_detail(request, ref_id):

    company = request.GET.get("company")

    if not company:
        return HttpResponse(
            "Company missing in URL",
            status=400
        )

    final_data = build_traceability_data(
        ref_id=ref_id,
        company=company
    )

    return render(
        request,
        "form_builder/data_detail.html",
        {
            "data": final_data,
            "ref_id": ref_id,
            "company": company,
        }
    )






from audit_log.models import AuditLog

def delete_stage(request, stage_id):

    if request.method == "POST":

        stage = Stage.objects.get(id=stage_id)

        # 🔥 LOG BEFORE DELETE
        AuditLog.objects.create(
            user=request.user,
            role=request.user.role,
            module="form_builder",
            action="DELETE",
            model_name="Stage",
            object_id=str(stage.id),
            object_repr=str(stage),
            description="Stage deleted"
        )

        stage.delete()

        return JsonResponse({"status": "deleted"})

    return JsonResponse({"status": "error"})
# ========================================== Delete Column ===================================================

def delete_column(request, col_id):

    

        col = TableColumn.objects.get(id=col_id)

        AuditLog.objects.create(
            user=request.user,
            role=request.user.role,
            module="form_builder",
            action="DELETE",
            model_name="TableColumn",
            object_id=str(col.id),
            object_repr=str(col),
            description="Column deleted"
        )

        col.delete()

        return JsonResponse({"status": "deleted"})

 



# ======================================
# FORM LIST
# ======================================
@login_required
def form_list(request):

    queryset = Form.objects.select_related('created_by')

    # if not request.user.is_superuser:
    #     queryset = queryset.filter(created_by=request.user)

    forms = queryset.order_by("-created_at")

    return render(request, "form_builder/form_list.html", {
        "forms": forms,
        "total_forms": forms.count()
    })



from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
def delete_form(request, form_id):

    form = get_object_or_404(Form, id=form_id)

    if request.user != form.created_by and not request.user.is_superuser:
        return HttpResponse("Not allowed", status=403)

    if request.method == "POST":

        AuditLog.objects.create(
            user=request.user,
            role=request.user.role,
            module="form_builder",
            action="DELETE",
            model_name="Form",
            object_id=str(form.id),
            object_repr=str(form),
            description="Form deleted"
        )

        form.delete()

    return redirect("form_lists")



# ======================================
# FILL FORM
# ======================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Form, Stage, FormResponse
from qms_app.models import QMSDocument
import json


@login_required
def fill_form(request, form_id):

    import json
    import os

    from django.conf import settings
    from django.core.files.storage import FileSystemStorage

    from .models import (
        Form,
        Stage,
        FormResponse,
        TableCellConfig
    )

    form = get_object_or_404(Form, id=form_id)

    stages = Stage.objects.filter(form=form).prefetch_related(
        "field_set",
        "table_set__tablecolumn_set",
        "table_set__tablerow_set"
    )

    ref_id = request.GET.get("ref_id")

    company = request.GET.get("company") or "default"

    is_new = False

    # ==========================================================
    # STORE HEADER FROM MODAL
    # ==========================================================

    if request.method == "GET":

        if request.GET.get("doc_name"):
            request.session["doc_name"] = request.GET.get("doc_name")

        if request.GET.get("doc_number"):
            request.session["doc_number"] = request.GET.get("doc_number")

        if request.GET.get("revision"):
            request.session["revision"] = request.GET.get("revision")

    # ==========================================================
    # GENERATE REF
    # ==========================================================

    if not ref_id:

        if form.process in ["RFQ", "REGISTER"]:

            is_new = True

            last = FormResponse.objects.filter(
                form__process=form.process,
                company=company
            ).order_by("-id").first()

            if last and last.ref_id:

                try:
                    last_number = int(
                        last.ref_id.split("-")[-1]
                    )

                    new_number = last_number + 1

                except:
                    new_number = 1

            else:
                new_number = 1

            ref_id = (
                f"{form.process}-"
                f"{str(new_number).zfill(2)}"
            )

        else:
            return redirect("kanban_view")

    # ==========================================================
    # POST
    # ==========================================================

    if request.method == "POST":

        data = {}

        table_data = {}

        # ======================================================
        # FILE STORAGE
        # ======================================================

        fs = FileSystemStorage(
            location=os.path.join(
                settings.MEDIA_ROOT,
                "uploads"
            ),
            base_url=settings.MEDIA_URL + "uploads/"
        )

        # ======================================================
        # KEEP ORIGINAL FORM ORDER
        # ======================================================

        all_keys = []

        # ==========================================
        # ADD POST KEYS
        # ==========================================

        for key in request.POST.keys():

            if key not in all_keys:

                all_keys.append(key)

        # ==========================================
        # ADD FILE KEYS
        # ==========================================

        for file_key in request.FILES.keys():

            if file_key not in all_keys:

                all_keys.append(file_key)
                

        for key in all_keys:

            if key == "csrfmiddlewaretoken":
                continue

            # ==================================================
            # FILE HANDLING
            # ==================================================

            if key in request.FILES:

                uploaded_files = request.FILES.getlist(key)

                file_urls = []

                folder = ref_id if ref_id else "default"

                for f in uploaded_files:

                    filename = fs.save(
                        os.path.join(folder, f.name),
                        f
                    )

                    file_urls.append(
                        fs.url(filename)
                    )

                parsed_value = file_urls

            else:

                value = request.POST.get(key)

                if value is None:

                    parsed_value = False

                else:

                    if value == "on":

                        parsed_value = True

                    else:

                        try:
                            parsed_value = json.loads(value)

                        except:
                            parsed_value = value

            # ==================================================
            # TABLE VALUES
            # ==================================================

            if "__" in key:

                try:

                    # table_id__row_id__column_id

                    table_id, row_id, col_id = key.split("__")

                    # ==========================================
                    # GET ACTUAL OBJECTS
                    # ==========================================

                    table_obj = Table.objects.filter(
                        id=table_id
                    ).first()

                    col_obj = TableColumn.objects.filter(
                        id=col_id
                    ).first()

                    # ==========================================
                    # INVALID
                    # ==========================================

                    if not table_obj or not col_obj:

                        continue

                    # ==========================================
                    # REAL TABLE NAME
                    # ==========================================

                    table = table_obj.name

                    # ==========================================
                    # DYNAMIC ROW SUPPORT
                    # ==========================================

                    if str(row_id).isdigit():

                        row_obj = TableRow.objects.filter(
                            id=row_id
                        ).first()

                        row = (
                            row_obj.name
                            if row_obj
                            else row_id
                        )

                    else:

                        # dynamic row like Row4
                        row = row_id

                    # ==========================================
                    # COLUMN NAME
                    # ==========================================

                    col = col_obj.name


                except:
                    continue

                table_data.setdefault(table, {})

                table_data[table].setdefault(row, {})

                table_data[table][row][col] = parsed_value

            # ==================================================
            # NORMAL FIELD
            # ==================================================

            else:

                data[key] = parsed_value

        # ======================================================
        # CONVERT TABLE DATA
        # ======================================================

        for table_name, rows in table_data.items():

            sorted_rows = []

            # ==============================================
            # GET TABLE OBJECT
            # ==============================================

            table_obj = Table.objects.filter(
                id=table_id
            ).first()

            db_rows = []

            if table_obj:

                db_rows = list(
                    table_obj.tablerow_set.all().order_by("order")
                )

            # ==============================================
            # KEEP DATABASE ROW ORDER
            # ==============================================

            ordered_row_names = []

            if table_obj:

                ordered_row_names = list(

                    table_obj.tablerow_set.all()
                    .order_by("order","id")
                    .values_list("name", flat=True)
                )

            # ==============================================
            # ADD DYNAMIC ROWS
            # ==============================================

            for row_name in rows.keys():

                if row_name not in ordered_row_names:

                    ordered_row_names.append(row_name)

            # ==============================================
            # PROCESS ROWS
            # ==============================================

            for row_name in ordered_row_names:

                if row_name not in rows:
                    continue

                row = rows[row_name]

                # ==========================================
                # CHECK EMPTY ROW
                # ==========================================

                has_value = False

                for v in row.values():

                    # FILE LIST
                    if isinstance(v, list) and len(v) > 0:

                        has_value = True
                        break

                    # SIGNATURE OBJECT
                    elif isinstance(v, dict) and len(v.keys()) > 0:

                        has_value = True
                        break

                    # NORMAL VALUE
                    elif str(v).strip() not in [
                        "",
                        "None",
                        "null"
                    ]:

                        has_value = True
                        break

                if not has_value:
                    continue

                # ==========================================
                # PRESERVE ROW NAME
                # ==========================================

                row["row_name"] = row_name

                # ==========================================
                # APPEND
                # ==========================================

                sorted_rows.append(row)

                # ==============================================
                # SAVE TABLE
                # ==============================================

                if sorted_rows:

                    data[table_name] = sorted_rows

        # ======================================================
        # HEADER VALUES
        # ======================================================

        doc_name = (
            request.POST.get("doc_name")
            or request.session.get("doc_name")
            or form.name
        )

        doc_number = (
            request.POST.get("doc_number")
            or request.session.get("doc_number")
            or "N/A"
        )

        revision = (
            request.POST.get("revision")
            or request.session.get("revision")
            or "1.0"
        )

        # ======================================================
        # SAVE
        # ======================================================

        FormResponse.objects.update_or_create(

            form=form,

            ref_id=ref_id,

            company=company,

            defaults={

                "doc_name": doc_name,

                "doc_number": doc_number,

                "revision": revision,

                "data": data,

                "created_by": request.user
            }
        )

        # ======================================================
        # CLEAR SESSION
        # ======================================================

        request.session.pop("doc_name", None)

        request.session.pop("doc_number", None)

        request.session.pop("revision", None)

        # ======================================================
        # REDIRECT
        # ======================================================

        if form.process == "REGISTER":

            return redirect(
                f"/form-builder/register/?form_id={form.id}"
            )

        return redirect("kanban_view")

    # ==========================================================
    # LOAD EXISTING DATA
    # ==========================================================

    previous_data = {}

    existing = FormResponse.objects.filter(
        form=form,
        ref_id=ref_id,
        company=company
    ).first()

    if existing and existing.data:

        previous_data = existing.data

    # ==========================================================
    # OPTIONS
    # ==========================================================

    for stage in stages:

        for field in stage.field_set.all():

            field.option_list = (
                field.options.split(",")
                if field.options else []
            )

        for table in stage.table_set.all():

            for col in table.tablecolumn_set.all():

                col.option_list = (
                    col.options.split(",")
                    if col.options else []
                )

    # ==========================================================
    # COMBINED ELEMENTS
    # ==========================================================

    for stage in stages:

        elements = []

        # ======================================================
        # FIELDS
        # ======================================================

        for field in stage.field_set.all():

            elements.append({

                "type": "field",

                "order": getattr(field, "order", 0),

                "data": field
            })

        # ======================================================
        # TABLES
        # ======================================================

        for table in stage.table_set.all():

            elements.append({

                "type": "table",

                "order": getattr(table, "order", 0),

                "data": table
            })

        stage.elements = sorted(
            elements,
            key=lambda x: x["order"]
        )

    # ==========================================================
    # CELL CONFIGS
    # ==========================================================

    cell_configs = {}

    for stage in stages:

        for table in stage.table_set.all():

            rows = list(
                table.tablerow_set.all().order_by("order")
            )

            cols = list(
                table.tablecolumn_set.all().order_by("order")
            )
            for config in TableCellConfig.objects.select_related(
                "row",
                "column"
            ):

                config.option_list = (
                    config.options.split(",")
                    if config.options else []
                )

                key = f"{config.row_id}_{config.column_id}"

                cell_configs[key] = config
            # for row_index, row in enumerate(rows):

            #     for col_index, col in enumerate(cols):

            #         config = TableCellConfig.objects.filter(
            #             row=row,
            #             column=col
            #         ).first()

            #         if config:

            #             config.option_list = (
            #                 config.options.split(",")
            #                 if config.options else []
            #             )

            #             key = f"{row_index}_{col_index}"

            #             cell_configs[key] = config

    # ==========================================================
    # DOCUMENTS
    # ==========================================================

    documents = QMSDocument.objects.all().values(
        "id",
        "title"
    )

    # ==========================================================
    # RENDER
    # ==========================================================

    return render(
        request,
        "form_builder/fill_form.html",
        {
            "form": form,
            "stages": stages,
            "ref_id": ref_id,
            "company": company,
            "previous_data": previous_data,
            "documents": documents,
            "cell_configs": cell_configs,
            "is_new": is_new
        }
    )
# @login_required
# def fill_form(request, form_id):

#     from django.core.files.storage import FileSystemStorage
#     import json

#     form = get_object_or_404(Form, id=form_id)

#     stages = Stage.objects.filter(form=form).prefetch_related(
#         "field_set",
#         "table_set__tablecolumn_set"
#     )

#     ref_id = request.GET.get("ref_id")
#     company = request.GET.get("company") or "default"

#     is_new = False

#     # ==========================================================
#     # STORE HEADER FROM MODAL
#     # ==========================================================
#     if request.method == "GET":
#         if request.GET.get("doc_name"):
#             request.session["doc_name"] = request.GET.get("doc_name")
#         if request.GET.get("doc_number"):
#             request.session["doc_number"] = request.GET.get("doc_number")
#         if request.GET.get("revision"):
#             request.session["revision"] = request.GET.get("revision")

#     # ==========================================================
#     # GENERATE REF
#     # ==========================================================
#     if not ref_id:

#         if form.process in ["RFQ", "REGISTER"]:

#             is_new = True

#             last = FormResponse.objects.filter(
#                 form__process=form.process,
#                 company=company
#             ).order_by("-id").first()

#             if last and last.ref_id:
#                 try:
#                     last_number = int(last.ref_id.split("-")[-1])
#                     new_number = last_number + 1
#                 except:
#                     new_number = 1
#             else:
#                 new_number = 1

#             ref_id = f"{form.process}-{str(new_number).zfill(2)}"

#         else:
#             return redirect("kanban_view")

#     # ==========================================================
#     # 🔥 POST (UPDATED WITH FILE SUPPORT)
#     # ==========================================================
#     if request.method == "POST":

#         data = {}
#         table_data = {}

#         # 🔥 combine POST + FILES
#         all_keys = set(list(request.POST.keys()) + list(request.FILES.keys()))

#         fs = FileSystemStorage(location="media/uploads")

#         for key in all_keys:

#             if key == "csrfmiddlewaretoken":
#                 continue

#             # ================= FILE HANDLING =================
#             if key in request.FILES:

#                 file = request.FILES.getlist(key)

#                 fs = FileSystemStorage(
#                     location=os.path.join(settings.MEDIA_ROOT, "uploads"),
#                     base_url=settings.MEDIA_URL + "uploads/"
#                 )

   
#                 folder = ref_id if ref_id else "default"

#                 filename = fs.save(
#                     os.path.join(folder, file.name),
#                     file
#                 )

#                 file_url = fs.url(filename)

#                 data[key] = file_url

#                 continue

#             value = request.POST.get(key)

#             # ================= TABLE =================
#             if "__" in key:
#                 try:
#                     table, col, row = key.split("__")
#                 except:
#                     continue

#                 table_data.setdefault(table, {})
#                 table_data[table].setdefault(row, {})
#                 if value is None:
#                     parsed_value = False
#                 else:
#                     if value == "on":
#                         parsed_value = True
#                     else:
#                         try:
#                             parsed_value = json.loads(value)
#                         except:
#                             parsed_value = value

#                 table_data[table][row][col] = parsed_value

#             else:
#                 # data[key] = value
#                 try:
#                     parsed_value = json.loads(value)
#                 except:
#                     parsed_value = value

#                 data[key] = parsed_value

#         # ================= TABLE CONVERT =================
#         for table_name, rows in table_data.items():

#             sorted_rows = []

#             for k in sorted(rows.keys(), key=lambda x: int(x)):

#                 row = rows[k]   # 🔥 IMPORTANT FIX

#                 if any(str(v).strip() not in ["", "None", "null"] for v in row.values()):
#                     sorted_rows.append(row)

#             if sorted_rows:
#                 data[table_name] = sorted_rows
#         # ==========================================================
#         # HEADER VALUES
#         # ==========================================================
#         doc_name = (
#             request.POST.get("doc_name") or
#             request.session.get("doc_name") or
#             form.name
#         )

#         doc_number = (
#             request.POST.get("doc_number") or
#             request.session.get("doc_number") or
#             "N/A"
#         )

#         revision = (
#             request.POST.get("revision") or
#             request.session.get("revision") or
#             "1.0"
#         )

#         # ==========================================================
#         # SAVE
#         # ==========================================================
#         FormResponse.objects.update_or_create(
#             form=form,
#             ref_id=ref_id,
#             company=company,
#             defaults={
#                 "doc_name": doc_name,
#                 "doc_number": doc_number,
#                 "revision": revision,
#                 "data": data,
#                 "created_by": request.user
#             }
#         )

#         # ==========================================================
#         # CLEAR SESSION
#         # ==========================================================
#         request.session.pop("doc_name", None)
#         request.session.pop("doc_number", None)
#         request.session.pop("revision", None)

#         # ==========================================================
#         # REDIRECT
#         # ==========================================================
#         if form.process == "REGISTER":
#             return redirect(f"/form-builder/register/?form_id={form.id}")

#         return redirect("kanban_view")

#     # ==========================================================
#     # LOAD EXISTING DATA
#     # ==========================================================
#     previous_data = {}

#     existing = FormResponse.objects.filter(
#         form=form,
#         ref_id=ref_id,
#         company=company
#     ).first()

#     if existing and existing.data:
#         previous_data = existing.data

#     # ==========================================================
#     # OPTIONS
#     # ==========================================================
#     for stage in stages:
#         for field in stage.field_set.all():
#             field.option_list = field.options.split(",") if field.options else []
#         for table in stage.table_set.all():
#             for col in table.tablecolumn_set.all():
#                 col.option_list = col.options.split(",") if col.options else []
#     for stage in stages:
#         elements = []

#         # fields
#         for field in stage.field_set.all():
#             elements.append({
#                 "type": "field",
#                 "order": getattr(field, "order", 0),
#                 "data": field
#             })

#         # tables
#         for table in stage.table_set.all():
#             elements.append({
#                 "type": "table",
#                 "order": getattr(table, "order", 0),
#                 "data": table
#             })

#         # sort
#         stage.elements = sorted(elements, key=lambda x: x["order"])

#     documents = QMSDocument.objects.all().values("id", "title")

#     return render(request, "form_builder/fill_form.html", {
#         "form": form,
#         "stages": stages,
#         "ref_id": ref_id,
#         "company": company,
#         "previous_data": previous_data,
#         "documents": documents
#     })
    
    
    
from django.contrib.auth.decorators import login_required

@login_required
def process_summary(request, ref_id):

    company = request.GET.get("company")   # ✅ GET COMPANY

    responses = FormResponse.objects.filter(
        ref_id=ref_id,
        company=company   # ✅ FIX (CRITICAL)
    ).select_related("form")

    final_data = {}

    for res in responses:
        final_data[res.form.process] = res.data

    return render(request, "form_builder/process_summary.html", {
        "data": final_data,
        "ref_id": ref_id,
        "company": company   # ✅ PASS
    })
# ======================================
# SAVE RESPONSE
# ======================================

from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404, redirect, render
import uuid
import json

def edit_response(request, response_id):

    response = get_object_or_404(FormResponse, id=response_id)

    form = response.form

    stages = Stage.objects.filter(form=form)

    data = response.data or {}

    # =====================================================
    # NORMALIZE
    # =====================================================

    def normalize(name):
        return (
            name.lower()
            .replace(" ", "")
            .replace("_", "")
        )

    # =====================================================
    # FIX OLD DATA FORMAT
    # =====================================================

    for key, value in data.items():

        # =============================================
        # TABLE DATA (CURRENT FORMAT)
        # =============================================

        if isinstance(value, list):

            fixed_rows = []

            for row_data in value:

                if not isinstance(row_data, dict):
                    continue

                for k, v in row_data.items():

                    if isinstance(v, str) and "signed_by" in v:

                        try:

                            parsed = json.loads(
                                v.replace("'", '"')
                            )

                            row_data[k] = parsed

                        except:
                            pass

                fixed_rows.append(row_data)

            data[key] = fixed_rows

        # =============================================
        # OLD TABLE FORMAT
        # =============================================

        elif isinstance(value, dict):

            fixed_rows = []

            try:

                for row_index in sorted(
                    value.keys(),
                    key=lambda x: int(x)
                ):

                    row_data = value[row_index]

                    for k, v in row_data.items():

                        if isinstance(v, str) and "signed_by" in v:

                            try:

                                parsed = json.loads(
                                    v.replace("'", '"')
                                )

                                row_data[k] = parsed

                            except:
                                pass

                    fixed_rows.append(row_data)

                data[key] = fixed_rows

            except:
                pass

        # =============================================
        # NORMAL SIGNATURE FIELD
        # =============================================

        elif isinstance(value, str):

            if "signed_by" in value:

                try:

                    parsed = json.loads(
                        value.replace("'", '"')
                    )

                    data[key] = parsed

                except:
                    pass
    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        updated_data = {}

        table_data = {}
        deleted_rows = []

        for key in request.POST.keys():

            if key.startswith("delete_row__"):

                row_id = key.replace(
                    "delete_row__",
                    ""
                )

                deleted_rows.append(str(row_id))

        # ==========================================
        # DYNAMIC ROW NAME STORAGE
        # ==========================================

        dynamic_row_names = {}

        for k, v in request.POST.items():

            if k.startswith("row_name__"):

                parts = k.split("__")

                if len(parts) >= 3:

                    table_id = parts[1]
                    row_id = parts[2]

                    dynamic_row_names[
                        row_id
                    ] = v.strip()

        # =================================================
        # NORMAL FIELDS
        # =================================================

        for stage in stages:

            for field in stage.field_set.all():

                key = field.label

                values = request.POST.getlist(key)

                files = request.FILES.getlist(key)

                # =========================================
                # FILE / IMAGE
                # =========================================

                if field.field_type in ["file", "image"]:

                    if files:

                        file_urls = []

                        for f in files:

                            file_name = (
                                f"uploads/"
                                f"{uuid.uuid4()}_{f.name}"
                            )

                            path = default_storage.save(
                                file_name,
                                f
                            )

                            file_urls.append(
                                default_storage.url(path)
                            )

                        updated_data[key] = (
                            file_urls
                            if len(file_urls) > 1
                            else file_urls[0]
                        )

                    else:

                        updated_data[key] = data.get(key)

                # =========================================
                # SIGNATURE
                # =========================================

                elif field.field_type == "signature":

                    if values and str(values[0]).strip():

                        try:

                            updated_data[key] = json.loads(
                                values[0]
                            )

                        except:

                            updated_data[key] = values[0]

                    else:

                        updated_data[key] = data.get(key)

                # =========================================
                # NORMAL FIELD
                # =========================================

                else:

                    cleaned_values = []

                    for v in values:

                        if str(v).strip() not in [
                            "",
                            "None",
                            "null"
                        ]:

                            cleaned_values.append(v)

                    if cleaned_values:

                        updated_data[key] = (
                            cleaned_values[0]
                            if len(cleaned_values) == 1
                            else cleaned_values
                        )

                    else:

                        updated_data[key] = data.get(
                            key,
                            ""
                        )

        # =================================================
        # TABLE DATA
        # =================================================

        all_keys = list(request.POST.keys())

        # ==========================================
        # MERGE POST + FILE KEYS IN ORIGINAL ORDER
        # ==========================================

        all_keys = []

        for key in request.POST.keys():

            if key not in all_keys:

                all_keys.append(key)

        for key in request.FILES.keys():

            if key not in all_keys:

                insert_index = len(all_keys)

                # ==================================
                # FIND ORIGINAL ROW POSITION
                # ==================================

                if "__" in key:

                    try:

                        table_id, row_id, col_id = (
                            key.split("__")
                        )

                        table_obj = Table.objects.filter(
                            id=table_id
                        ).first()

                        row_obj = TableRow.objects.filter(
                            id=row_id
                        ).first()

                        if table_obj:

                            ordered_rows = list(

                                table_obj.tablerow_set.all()
                                .order_by("order", "id")
                                .values_list(
                                    "name",
                                    flat=True
                                )
                            )

                            if row_obj and row_obj.name in ordered_rows:

                                row_pos = (
                                    ordered_rows.index(row_obj.name)
                                )

                                for i, existing_key in enumerate(all_keys):

                                    if "__" not in existing_key:
                                        continue

                                    try:

                                        t, r, c = (
                                            existing_key.split("__")
                                        )

                                        existing_row_obj = TableRow.objects.filter(
                                            id=r
                                        ).first()

                                        if (
                                            t == str(table_id)
                                            and
                                            existing_row_obj
                                            and
                                            existing_row_obj.name in ordered_rows
                                            and
                                            ordered_rows.index(existing_row_obj.name) > row_pos
                                        ):

                                            insert_index = i
                                            break

                                    except:
                                        pass

                    except:
                        pass

                all_keys.insert(insert_index, key)

        for key in all_keys:

            if key == "csrfmiddlewaretoken":
                continue

            if key.startswith("_row_id__"):
                continue

            if key.startswith("row_name__"):
                continue

            if "__" not in key:
                continue

            parts = key.split("__")

            if len(parts) != 3:
                continue

            # table_id__row_id__column_id

            table_id, row_id, col_id = parts
            print("================================")
            print("POST KEY :", key)
            print("ROW ID   :", row_id)
            print("================================")
            # ==========================================
            # GET REAL OBJECTS
            # ==========================================

            table_obj = Table.objects.filter(
                id=table_id
            ).first()

            column_obj = TableColumn.objects.filter(
                id=col_id
            ).first()

            if not table_obj or not column_obj:
                continue

            table = table_obj.name

            # ==========================================
            # KEEP STABLE ROW ID
            # ==========================================

            row = str(row_id)

            col = column_obj.name


            table_data.setdefault(table, {})

            # ==========================================
            # SKIP DELETED ROWS
            # ==========================================

            if row in [
                str(x).strip()
                for x in deleted_rows
            ]:
                continue

            table_data[table].setdefault(row, {})
            

            # =============================================
            # CELL CONFIG TYPE
            # =============================================

            col_type = "text"


  

            # =============================================
            # FIND REAL ROW OBJECT
            # =============================================

            row_obj = None

            if str(row_id).isdigit():

                row_obj = TableRow.objects.filter(
                    id=row_id
                ).first()

            # =============================================
            # FIND CELL CONFIG
            # =============================================

            config = None

            if table_obj and row_obj and column_obj:

                config = (
                    TableCellConfig.objects
                    .filter(
                        table=table_obj,
                        row=row_obj,
                        column=column_obj
                    )
                    .first()
                )

                if config:

                    col_type = config.cell_type

            values = request.POST.getlist(key)

            files = request.FILES.getlist(key)

            # =============================================
            # SIGNATURE
            # =============================================
            if col_type == "signature":

                if values and str(values[0]).strip():

                    try:
                        # Store as dictionary
                        value = json.loads(values[0])

                    except Exception:
                        # Keep existing value if bad JSON comes
                        try:
                            old_rows = data.get(table, [])

                            value = ""

                            for r in old_rows:

                                if str(r.get("_row_id", "")) == str(row):
                                    value = r.get(col)
                                    break

                                # fallback by row name
                                if (
                                    r.get("row_name", "").strip().lower()
                                    ==
                                    (
                                        TableRow.objects.filter(id=row)
                                        .first().name.lower()
                                        if str(row).isdigit()
                                        and TableRow.objects.filter(id=row).exists()
                                        else ""
                                    )
                                ):
                                    value = r.get(col)
                                    break

                        except:
                            value = ""

                else:

                    try:
                        old_rows = data.get(table, [])

     
                        value = ""

                        for r in old_rows:

                            if str(r.get("_row_id", "")) == str(row):
                                value = r.get(col)
                                break

                            # fallback by row name
                            if (
                                r.get("row_name", "").strip().lower()
                                ==
                                (
                                    TableRow.objects.filter(id=row)
                                    .first().name.lower()
                                    if str(row).isdigit()
                                    and TableRow.objects.filter(id=row).exists()
                                    else ""
                                )
                            ):
                                value = r.get(col)
                                break


                    except:
                        value = ""
            # if col_type == "signature":

            #     if values and str(values[0]).strip():

            #         try:

            #             # =====================================
            #             # KEEP SIGNATURE AS JSON STRING
            #             # =====================================

            #             parsed_sign = json.loads(
            #                 values[0]
            #             )

            #             value = json.dumps(
            #                 parsed_sign
            #             )

            #         except:

            #             value = values[0]

            #     else:

            #         try:

            #             old_rows = data.get(table, [])

            #             value = (
            #                 next(
            #                     (
            #                         r.get(col)
            #                         for r in old_rows
            #                         if str(
            #                             r.get("_row_id", "")
                 
            #                         ) == str(row)
            #                     ),
            #                     ""
            #                 )
            #             )

            #         except:

            #             value = ""

            # =============================================
            # FILE / IMAGE
            # =============================================

            elif col_type in ["file", "image"]:

                if files:

                    file_urls = []

                    for f in files:

                        file_name = (
                            f"uploads/"
                            f"{uuid.uuid4()}_{f.name}"
                        )

                        path = default_storage.save(
                            file_name,
                            f
                        )

                        file_urls.append(
                            default_storage.url(path)
                        )

                    value = (
                        file_urls
                        if len(file_urls) > 1
                        else file_urls[0]
                    )

                else:

                    try:

                        old_rows = data.get(table, [])

                        value = (
                            next(
                                (
                                    r.get(col)
                                    for r in old_rows
                                    if str(
                                        r.get("_row_id", "")
     
                                    ) == str(row)
                                ),
                                ""
                            )
                        )

                    except:

                        value = ""

            # =============================================
            # NORMAL COLUMN
            # =============================================

            else:

                # =========================================
                # GET OLD VALUE
                # =========================================

                old_value = ""

                try:

                    old_rows = data.get(table, [])

                    old_value = (
                        next(
                            (
                                r.get(col)
                                for r in old_rows
                                if str(
                                    r.get("_row_id", "")

                                ) == str(row)
                            ),
                            ""
                        )
                    )

                except:

                    old_value = ""

                # =========================================
                # CLEAN NEW VALUES
                # =========================================

                cleaned_values = []

                for v in values:

                    if str(v).strip() not in [
                        "",
                        "None",
                        "null"
                    ]:

                        cleaned_values.append(v)

                # =========================================
                # UPDATE ONLY IF VALUE EXISTS
                # =========================================

                if cleaned_values:

                    value = (
                        cleaned_values[0]
                        if len(cleaned_values) == 1
                        else cleaned_values
                    )

                else:

                    value = old_value

            table_data[table][row][col] = value


        # =================================================
        # PROCESS TABLE
        # =================================================
        for table_name, rows in table_data.items():

            cleaned_rows = []
            # =============================================
            # MERGE OLD ROWS FIRST
            # =============================================

            old_rows = data.get(table_name, [])
            # =============================================
            # NORMALIZE OLD ROW IDS
            # =============================================

            # KEEP ORIGINAL ROW IDS
            normalized_old_rows = []

            for old_row in old_rows:
                
                row_id = str(
                    old_row.get("_row_id", "")
                ).strip()

                # FIX INVALID ROW IDS LIKE new_signature
                if (
                    not row_id
                    or not row_id.isdigit()
                ):

                    row_name = old_row.get(
                        "row_name",
                        ""
                    )

                    row_obj = TableRow.objects.filter(
                        table__name=table_name,
                        name=row_name
                    ).first()

                    if row_obj:

                        old_row["_row_id"] = str(
                            row_obj.id
                        )
                # if "_row_id" not in old_row:

                #     row_name = old_row.get("row_name", "")

                #     row_obj = TableRow.objects.filter(
                #         table__name=table_name,
                #         name=row_name
                #     ).first()

                #     if row_obj:

                #         old_row["_row_id"] = str(row_obj.id)

                normalized_old_rows.append(old_row)

            old_rows = normalized_old_rows

            for old_row in old_rows:

                old_row_id = str(
                    old_row.get("_row_id", "")
                ).strip()

                if not old_row_id:
                    continue

                # =====================================
                # SKIP DELETED ROWS
                # =====================================

                if old_row_id in [
                    str(x).strip()
                    for x in deleted_rows
                ]:
                    continue

                # =====================================
                # DO NOT RECREATE REMOVED ROWS
                # =====================================

                if old_row_id not in rows:
                    continue
            # =============================================
            # KEEP FRONTEND ORDER
            # =============================================

            ordered_row_names = []

            table_obj = Table.objects.filter(
                name=table_name
            ).first()

            if table_obj:

                ordered_row_names = [

                    str(r.id)

                    for r in table_obj.tablerow_set.all()
                    .order_by("order", "id")
                ]

            for row_key in rows.keys():

                if row_key not in ordered_row_names:

                    ordered_row_names.append(row_key)

            for row_name in ordered_row_names:

                if row_name not in rows:
                    continue
                if str(row_name).strip() in [
                    str(x).strip()
                    for x in deleted_rows
                ]:
                    continue
                # =========================================
                # FIND OLD SAVED ROW
                # =========================================

                existing_old_row = next(
                    (
                        r for r in old_rows
                        if str(
                            r.get("_row_id","")
                    
                           
                        ) == str(row_name)
                    ),
                    {}
                )

                # =========================================
                # START WITH OLD DATA
                # =========================================

                row = existing_old_row.copy()

                # =========================================
                # MERGE COLUMN BY COLUMN
                # =========================================

                for col_key, col_value in rows[row_name].items():

                    # KEEP OLD FILES IF EMPTY
                    if col_value in ["", None, [], {}]:

                        if col_key in row:
                            continue

                    row[col_key] = col_value

                # =========================================
                # REMOVE EMPTY ROW
                # =========================================

                has_value = False

                for k, v in row.items():

                    # SKIP META
                    if k in [
                        "_row_id",
                        "row_name"
                    ]:
                        continue

                    # KEEP FILE / IMAGE URL
                    if isinstance(v, str) and (
                        "/media/" in v or
                        "/uploads/" in v
                    ):

                        has_value = True
                        break

                    # NORMAL VALUE
                    if v not in ["", None, [], {}]:

                        has_value = True
                        break

                # =========================================
                # ALSO CHECK OLD SAVED ROW
                # =========================================

                old_rows = data.get(table_name, [])

                existing_old_row = next(
                    (
                        r for r in old_rows
                        if str(
                            r.get("_row_id", "")
                   
                        ) == str(row_name)
                    ),
                    None
                )

                # =========================================
                # FORCE SKIP DELETED ROW
                # =========================================

                if str(row_name).strip() in [
                    str(x).strip()
                    for x in deleted_rows
                ]:
                    continue

                # =========================================
                # REMOVE EMPTY ROWS
                # =========================================

                if not has_value:
                    continue

                # =========================================
                # PRESERVE ROW NAME
                # =========================================

                row_obj = None

                if str(row_name).isdigit():

                    row_obj = TableRow.objects.filter(
                        id=row_name
                    ).first()

                default_name = (
                    row_obj.name
                    if row_obj
                    else row_name
                )

                row["row_name"] = dynamic_row_names.get(
                    row_name,
                    default_name
                )

                row["_row_id"] = str(row_name)

                cleaned_rows.append(row)

            # =============================================
            # TOTAL
            # =============================================

            total = 0

            table_obj = None

            for stage in stages:

                for t in stage.table_set.all():

                    if (
                        t.name.strip() ==
                        table_name.strip()
                    ):

                        table_obj = t
                        break

                if table_obj:
                    break

            if table_obj:

                total_cols = (
                    table_obj
                    .tablecolumn_set
                    .filter(is_total=True)
                )

                total_names = [
                    normalize(col.name)
                    for col in total_cols
                ]

                for row in cleaned_rows:

                    for k, val in row.items():

                        if normalize(k) in total_names:

                            try:
                                total += float(val or 0)
                            except:
                                pass

            # =============================================
            # SAVE
            # =============================================

            updated_data[
                table_name.strip()
            ] = cleaned_rows

            updated_data[
                f"{table_name.strip()}_total"
            ] = round(total, 2)

        # =================================================
        # FINAL MERGE
        # =================================================

        for k, v in data.items():

            if k not in updated_data:

                updated_data[k] = v

        response.data = updated_data

        response.save()

        # =================================================
        # REDIRECT
        # =================================================

        if form.process == "REGISTER":

            return redirect(
                f"/form-builder/register/?form_id={form.id}"
            )

        else:

            return redirect(
                f"/form-builder/kanban/?process={form.process}"
            )

    # =====================================================
    # BUILD ORDER
    # =====================================================

    for stage in stages:

        elements = []

        for field in stage.field_set.all():

            elements.append({
                "type": "field",
                "data": field,
                "order": getattr(field, "order", 0)
            })

        for table in stage.table_set.all():

            elements.append({
                "type": "table",
                "data": table,
                "order": getattr(table, "order", 0)
            })

        stage.elements = sorted(
            elements,
            key=lambda x: x["order"]
        )

    # =====================================================
    # CELL CONFIGS
    # =====================================================

    cell_configs = {}

    for stage in stages:

        for table in stage.table_set.all():

            for config in table.tablecellconfig_set.all():

                key = f"{config.row.id}_{config.column.id}"

                # =====================================
                # FIX OPTION LIST
                # =====================================

                config.option_list = (
                    config.options.split(",")
                    if config.options else []
                )

                cell_configs[key] = config

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "form_builder/edit_response.html",
        {
            "form": form,
            "stages": stages,
            "data": data,
            "response": response,
            "cell_configs": cell_configs
        }
    )


# from django.core.files.storage import default_storage
# from django.shortcuts import get_object_or_404, redirect, render
# import uuid

# from django.core.files.storage import default_storage
# from django.shortcuts import get_object_or_404, redirect, render
# import uuid

# def edit_response(request, response_id):

#     response = get_object_or_404(FormResponse, id=response_id)
#     form = response.form
#     stages = Stage.objects.filter(form=form)

#     data = response.data or {}

#     def normalize(name):
#         return name.lower().replace(" ", "").replace("_", "")

#     if request.method == "POST":

#         updated_data = {}
#         table_data = {}

#         # ================= NORMAL FIELDS =================
#         for stage in stages:
#             for field in stage.field_set.all():

#                 key = field.label

#                 if field.field_type in ["file", "image"]:

#                     files = request.FILES.getlist(key)

#                     if files:
#                         file_urls = []
#                         for f in files:
#                             file_name = f"uploads/{uuid.uuid4()}_{f.name}"
#                             path = default_storage.save(file_name, f)
#                             file_urls.append(default_storage.url(path))

#                         updated_data[key] = file_urls if len(file_urls) > 1 else file_urls[0]

#                     else:
#                         # ✅ KEEP OLD FILE
#                         if key in data:
#                             updated_data[key] = data[key]

#                 else:
#                     values = request.POST.getlist(key)

#                     if values:
#                         updated_data[key] = values[0] if len(values) == 1 else values
#                     else:
#                         updated_data[key] = data.get(key, "")

#         # ================= TABLE DATA =================
#         all_keys = set(list(request.POST.keys()) + list(request.FILES.keys()))

#         for key in all_keys:

#             if key == "csrfmiddlewaretoken":
#                 continue

#             if "__" not in key:
#                 continue

#             parts = key.split("__")
#             if len(parts) != 3:
#                 continue

#             table, col, row = parts

#             table_data.setdefault(table, {})
#             table_data[table].setdefault(row, {})

#             # 🔥 Detect column type
#             col_type = None
#             for stage in stages:
#                 for t in stage.table_set.all():
#                     if t.name == table:
#                         for c in t.tablecolumn_set.all():
#                             if c.name == col:
#                                 col_type = c.column_type
#                                 break

#             files = request.FILES.getlist(key)

#             # ================= FILE / IMAGE =================
#             if col_type in ["file", "image"]:

#                 if files:
#                     file_urls = []
#                     for f in files:
#                         file_name = f"uploads/{uuid.uuid4()}_{f.name}"
#                         path = default_storage.save(file_name, f)
#                         file_urls.append(default_storage.url(path))

#                     value = file_urls if len(file_urls) > 1 else file_urls[0]

#                 else:
#                     # ✅ KEEP OLD FILE (CRITICAL FIX)
#                     try:
#                         old_rows = data.get(table, [])
#                         if int(row) < len(old_rows):
#                             value = old_rows[int(row)].get(col)
#                         else:
#                             value = ""
#                     except:
#                         value = ""

#             # ================= NORMAL COLUMN =================
#             else:
#                 values = request.POST.getlist(key)

#                 if values:
#                     value = values[0] if len(values) == 1 else values
#                 else:
#                     try:
#                         old_rows = data.get(table, [])
#                         if int(row) < len(old_rows):
#                             value = old_rows[int(row)].get(col)
#                         else:
#                             value = ""
#                     except:
#                         value = ""

#             table_data[table][row][col] = value

#         # ================= PROCESS TABLE =================
#         for table_name, rows in table_data.items():

#             row_list = [rows[k] for k in sorted(rows, key=int)]

#             total = 0

#             table_obj = None
#             for stage in stages:
#                 for t in stage.table_set.all():
#                     if t.name.strip() == table_name.strip():
#                         table_obj = t
#                         break
#                 if table_obj:
#                     break

#             if table_obj:
#                 total_cols = table_obj.tablecolumn_set.filter(is_total=True)
#                 total_names = [normalize(col.name) for col in total_cols]

#                 for row in row_list:
#                     for k, val in row.items():
#                         if normalize(k) in total_names:
#                             try:
#                                 total += float(val or 0)
#                             except:
#                                 pass

#             updated_data[table_name.strip()] = row_list
#             updated_data[f"{table_name.strip()}_total"] = round(total, 2)

#         # ================= KEEP OLD DATA =================
#         for k, v in data.items():
#             if k not in updated_data:
#                 updated_data[k] = v

#         response.data = updated_data
#         response.save()

#         if form.process == "REGISTER":
#             return redirect(f"/form-builder/register/?form_id={form.id}")
#         else:
#             return redirect(f"/form-builder/kanban/?process={form.process}")
#     # ================= BUILD ORDERED ELEMENTS =================
#     for stage in stages:

#         elements = []

#         # fields
#         for field in stage.field_set.all():
#             elements.append({
#                 "type": "field",
#                 "data": field,
#                 "order": getattr(field, "order", 0)
#             })

#         # tables
#         for table in stage.table_set.all():
#             elements.append({
#                 "type": "table",
#                 "data": table,
#                 "order": getattr(table, "order", 0)
#             })

#         # 🔥 FINAL ORDER FIX
#         stage.elements = sorted(elements, key=lambda x: x["order"])

#     return render(request, "form_builder/edit_response.html", {
#         "form": form,
#         "stages": stages,
#         "data": data,
#         "response": response
#     })
# ======================================
# VIEW RESPONSES
# ======================================

def responses(request, form_id):

    form = Form.objects.get(id=form_id)

    responses = FormResponse.objects.filter(form=form).order_by("-id")

    return render(request, "form_builder/responses.html", {
        "form": form,
        "responses": responses
    })
    
    
@login_required
def get_next_rfq(request):

    company = request.GET.get("company")

    if not company:
        return JsonResponse({"rfq_id": "RFQ-01"})

    last = FormResponse.objects.filter(
        form__process="RFQ",
        company=company
    ).order_by("-id").first()

    if last and last.ref_id:
        try:
            last_number = int(last.ref_id.split("-")[-1])
            new_number = last_number + 1
        except:
            new_number = 1
    else:
        new_number = 1

    return JsonResponse({
        "rfq_id": f"RFQ-{str(new_number).zfill(2)}"
    })

# ======================================
# KANBAN VIEW
# ======================================

# def kanban_view(request):

#     processes = ["RFQ", "FEASIBILITY", "COSTING","REGISTER"]

#     selected_process = request.GET.get("process")
#     selected_ref = request.GET.get("ref_id")

#     forms = Form.objects.all()

#     ref_list = None
#     responses = None

#     # ================= PROCESS CLICK =================
#     if selected_process:

#         ref_list = FormResponse.objects.filter(
#             form__process=selected_process
#         ).exclude(
#             ref_id__isnull=True
#         ).exclude(
#             ref_id=""
#         ).values_list("ref_id", flat=True).distinct()

#     # ================= REF CLICK =================
#     if selected_ref:

#         responses = FormResponse.objects.filter(
#             form__process=selected_process,
#             ref_id=selected_ref
#         ).prefetch_related(
#             "form__stage_set__table_set__tablecolumn_set"
#         )

#         # 🔥 IMPORTANT: attach properties safely
#         for response in responses:
#             for stage in response.form.stage_set.all():

#                 tables = list(stage.table_set.all())  # ✅ force evaluation

#                 for table in tables:

#                     total_cols = list(table.tablecolumn_set.filter(is_total=True))

#                     table.has_total = len(total_cols) > 0
#                     table.total_key = table.name.strip() + "_total"

#     return render(request, "form_builder/kanban_builder.html", {
#         "processes": processes,
#         "forms": forms,
#         "selected_process": selected_process,
#         "selected_ref": selected_ref,
#         "ref_list": ref_list,
#         "responses": responses
#     })
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required

from po_qu.models import Quotation
from .models import FormResponse, Form


ALLOWED_FLOW = {
    "RFQ": "FEASIBILITY",
    "FEASIBILITY": "COSTING",
    "COSTING": "PROPOSAL",
    "PROPOSAL": "WON",
}


@login_required
@transaction.atomic
def move_stage(request):

    # =============================
    # 📥 INPUT (NORMALIZED)
    # =============================
    ref_id = (request.POST.get("ref_id") or "").strip()
    company = (request.POST.get("company") or "").strip()

    next_stage = (request.POST.get("next_stage") or "").strip().upper()

    if not ref_id or not company or not next_stage:
        return JsonResponse({
            "status": "error",
            "msg": "Missing data"
        })

    # Normalize for safe comparison
    ref_id_clean = ref_id.strip()
    company_clean = company.strip()

    # =============================
    # 🔒 LOCK RECORDS (SAFE)
    # =============================
    responses = (
        FormResponse.objects
        .select_for_update()
        .filter(
            ref_id__iexact=ref_id_clean,
            company__iexact=company_clean
        )
        .select_related("form")
        .order_by("-id")
    )

    # 🔍 DEBUG (REMOVE LATER)
    if not responses.exists():
        print("❌ DEBUG:")
        print("REF:", ref_id_clean)
        print("COMPANY:", company_clean)

        all_ref = FormResponse.objects.filter(ref_id__iexact=ref_id_clean)
        print("RFQ MATCH COUNT:", all_ref.count())

        all_company = all_ref.filter(company__iexact=company_clean)
        print("COMPANY MATCH COUNT:", all_company.count())

        return JsonResponse({
            "status": "error",
            "msg": "Record not found"
        })

    last = responses.first()
    current_stage = (last.form.process or "").strip().upper()

    # =============================
    # 🚫 FLOW VALIDATION
    # =============================
    if ALLOWED_FLOW.get(current_stage) != next_stage:
        return JsonResponse({
            "status": "error",
            "msg": f"Invalid transition: {current_stage} → {next_stage}"
        })

    # =============================
    # 🚫 QUOTATION CHECK
    # =============================
    if next_stage == "PROPOSAL":

        quotation = (
            Quotation.objects
            .filter(
                rfq_id__iexact=ref_id_clean,
                company__iexact=company_clean
            )
            .order_by("-id")
            .first()
        )

        if not quotation:
            return JsonResponse({
                "status": "error",
                "msg": "Quotation required before moving to Proposal"
            })

    # =============================
    # 🚫 PREVENT WRONG WON FLOW
    # =============================
    if next_stage == "WON" and current_stage != "PROPOSAL":
        return JsonResponse({
            "status": "error",
            "msg": "Only Proposal can move to Won"
        })

    # =============================
    # ✅ HANDLE WON (NO FORM)
    # =============================
    if next_stage == "WON":
        last.status = "WON"
        last.save()

        return JsonResponse({
            "status": "success",
            "msg": "Moved to WON"
        })

    # =============================
    # ✅ CREATE NEXT STAGE ENTRY
    # =============================
    next_form = Form.objects.filter(
        process__iexact=next_stage
    ).order_by("-id").first()

    if not next_form:
        return JsonResponse({
            "status": "error",
            "msg": f"No form found for stage {next_stage}"
        })

    new_response = FormResponse.objects.create(
        form=next_form,
        ref_id=ref_id_clean,
        company=company_clean,
        data=last.data,
        created_by=request.user
    )

    # =============================
    # 🧾 AUDIT LOG (OPTIONAL)
    # =============================
    try:
        from audit_log.models import AuditLog

        AuditLog.objects.create(
            user=request.user,
            role=getattr(request.user, "role", ""),
            module="kanban",
            action="MOVE",
            model_name="FormResponse",
            object_id=str(new_response.id),
            object_repr=f"{ref_id_clean} moved {current_stage} → {next_stage}",
            description=f"{ref_id_clean} moved from {current_stage} to {next_stage}"
        )
    except:
        pass

    # =============================
    # ✅ SUCCESS
    # =============================
    return JsonResponse({
        "status": "success",
        "msg": f"{current_stage} → {next_stage} moved successfully"
    })




from django.db.models import Max, Prefetch
from django.shortcuts import render
from .models import FormResponse, Form, Stage
import json

from qms_app.models import QMSDocument
from po_qu.models import Quotation   # 🔥 IMPORTANT


# @login_required
# def kanban_view(request):

#     import json

#     selected_ref = request.GET.get("ref_id")
#     selected_company = request.GET.get("company")

#     # ================= HELPER (PRODUCTION FIX) =================
#     def process_cell_value(value, col_type=None):

#         # ===== SIGNATURE =====
#         if isinstance(value, str):
#             try:
#                 parsed = json.loads(value)
#                 if isinstance(parsed, dict) and "signed_by" in parsed:
#                     return parsed
#             except:
#                 pass

#         # ===== LINK =====
#         if col_type == "link" and value:
#             try:
#                 doc = QMSDocument.objects.get(id=value)
#                 return {
#                     "type": "link",
#                     "id": doc.id,
#                     "name": doc.title
#                 }
#             except:
#                 return {
#                     "type": "link",
#                     "id": value,
#                     "name": f"Document {value}"
#                 }

#         return value

#     # ================= LATEST CARDS =================
#     latest = (
#         FormResponse.objects
#         .exclude(ref_id__isnull=True)
#         .exclude(ref_id="")
#         .values("ref_id", "company")
#         .annotate(latest_id=Max("id"))
#     )

#     latest_ids = [item["latest_id"] for item in latest]

#     latest_responses = (
#         FormResponse.objects
#         .filter(id__in=latest_ids)
#         .select_related("form")
#     )

#     rfq_cards, feas_cards, cost_cards, proposal_cards = [], [], [], []

#     # ================= BUILD CARDS =================
#     for res in latest_responses:

#         card = {
#             "ref": res.ref_id,
#             "company": res.company,
#             "id": res.id,
#             "approved": getattr(res, "is_costing_approved", False),
#             "approved_by": res.approved_by,
#             "approved_at": res.approved_at
#         }

#         if res.form.process == "RFQ":
#             rfq_cards.append(card)

#         elif res.form.process == "FEASIBILITY":
#             feas_cards.append(card)

#         elif res.form.process == "COSTING":
#             cost_cards.append(card)

#     # ================= PROPOSAL =================
#     for res in latest_responses:
#         if res.form.process == "PROPOSAL":

#             quotation = Quotation.objects.filter(
#                 rfq_id=res.ref_id,
#                 company__iexact=(res.company or "").strip()
#             ).order_by("-id").first()
            
#             proposal_cards.append({
#                 "ref": res.ref_id,
#                 "company": res.company,
#                 "quotation": quotation
#             })

#     # ================= DATA VIEW =================
#     previous_data = {}
#     responses = None
#     last_response = None
#     processed_responses = []

#     if selected_ref and selected_company:

#         responses = (
#             FormResponse.objects
#             .filter(ref_id=selected_ref, company=selected_company)
#             .select_related("form")
#             .prefetch_related(
#                 Prefetch(
#                     "form__stage_set",
#                     queryset=Stage.objects.prefetch_related(
#                         "field_set",
#                         "table_set__tablecolumn_set"
#                     )
#                 )
#             )
#             .order_by("id")
#         )

#         last_response = responses.last()

#         # ===== MERGE DATA =====
#         for r in responses:
#             if r.data:
#                 previous_data.update(r.data)

#         # ================= PROCESS =================
#         for res in responses:

#             processed = {
#                 "form": res.form,
#                 "stages": [],
#                 "response_id": res.id,
#                 "ref_id": res.ref_id,
#                 "company": res.company,
#                 "approved": getattr(res, "is_costing_approved", False),
#                 "approved_by": getattr(res, "approved_by", None),
#                 "approved_at": getattr(res, "approved_at", None),
#             }

#             for stage in res.form.stage_set.all():

#                 stage_data = {
#                     "name": stage.name,
#                     "fields": [],
#                     "tables": []
#                 }

#                 # ========= FIELDS =========
#                 for field in stage.field_set.all():

#                     val = res.data.get(field.label)

#                     val = process_cell_value(val, field.field_type)

#                     if val is not None and not isinstance(val, list):
#                         stage_data["fields"].append({
#                             "label": field.label,
#                             "value": val,
#                             "type": field.field_type
#                         })

#                 # ========= TABLE =========
#                 for table in stage.table_set.all():

#                     rows = res.data.get(table.name)

#                     if isinstance(rows, list):

#                         clean_rows = []

#                         for row in rows:
#                             clean_row = {}

#                             for key, value in row.items():

#                                 col_obj = table.tablecolumn_set.filter(name=key).first()
#                                 col_type = col_obj.column_type if col_obj else None

#                                 clean_row[key] = process_cell_value(value, col_type)

#                             clean_rows.append(clean_row)

#                         stage_data["tables"].append({
#                             "name": table.name,
#                             "rows": clean_rows,
#                             "columns": list(table.tablecolumn_set.all().order_by("order")),
#                             "total": res.data.get(f"{table.name}_total")
#                         })

#                 processed["stages"].append(stage_data)

#             processed_responses.append(processed)

#     # ================= FORM FETCH =================
#     def get_forms(process):
#         return list(
#             Form.objects
#             .filter(process=process)
#             .order_by("-is_active", "-id")
#             .values("id", "name")
#         )

#     rfq_forms = get_forms("RFQ")

#     stage_forms = {
#         "RFQ": get_forms("RFQ"),
#         "FEASIBILITY": get_forms("FEASIBILITY"),
#         "COSTING": get_forms("COSTING"),
#         "PROPOSAL": get_forms("PROPOSAL"),
#     }

#     return render(request, "form_builder/kanban_builder.html", {
#         "rfq_cards": rfq_cards,
#         "feas_cards": feas_cards,
#         "cost_cards": cost_cards,
#         "proposal_cards": proposal_cards,
#         "selected_ref": selected_ref,
#         "responses": responses,
#         "previous_data": previous_data,
#         "rfq_forms": rfq_forms,
#         "last_response": last_response,
#         "processed_responses": processed_responses,
#         "stage_forms": stage_forms,
#     })

from django.db.models import Max, Prefetch
from django.shortcuts import render
from .models import FormResponse, Form, Stage
import json

from qms_app.models import QMSDocument
from po_qu.models import Quotation   # 🔥 IMPORTANT


@login_required
def kanban_view(request):

    import json

    selected_ref = request.GET.get("ref_id")
    selected_company = request.GET.get("company")

    # ================= HELPER (PRODUCTION FIX) =================
    def process_cell_value(value, col_type=None):

        import json

        # ================= SIGNATURE =================
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict) and "signed_by" in parsed:
                    return parsed
            except:
                pass

        # ================= MULTI FILE / IMAGE SUPPORT 🔥 =================
        if isinstance(value, list):
            return value   # IMPORTANT: keep list as-is

        # ================= CHECKBOX =================
        if col_type == "checkbox":
            if not value:
                return []
            if isinstance(value, list):
                return value
            return [value]

        # ================= LINK =================
        if col_type == "link" and value:
            try:
                doc = QMSDocument.objects.get(id=value)
                return {
                    "type": "link",
                    "id": doc.id,
                    "name": doc.title
                }
            except:
                return {
                    "type": "link",
                    "id": value,
                    "name": f"Document {value}"
                }

        return value

    # ================= LATEST CARDS =================
    latest = (
        FormResponse.objects
        .exclude(ref_id__isnull=True)
        .exclude(ref_id="")
        .values("ref_id", "company")
        .annotate(latest_id=Max("id"))
    )

    latest_ids = [item["latest_id"] for item in latest]

    latest_responses = (
        FormResponse.objects
        .filter(id__in=latest_ids)
        .select_related("form")
    )

    rfq_cards, feas_cards, cost_cards, proposal_cards, won_cards = [], [], [], [], []

    # ================= BUILD CARDS =================

    for res in latest_responses:
        quotation = Quotation.objects.filter(
            rfq_id__iexact=(res.ref_id or "").strip(),
            company__iexact=(res.company or "").strip()
        ).order_by("-id").first()
    
        card = {
            "ref": res.ref_id,
            "company": res.company,
            "id": res.id,
            "approved": getattr(res, "is_costing_approved", False),
            "approved_by": res.approved_by,
            "approved_at": res.approved_at,
            "quotation": quotation
        }

        if res.form.process == "RFQ":
            rfq_cards.append(card)

        elif res.form.process == "FEASIBILITY":
            feas_cards.append(card)

        elif res.form.process == "COSTING":
            cost_cards.append(card)
            


    # ================= PROPOSAL =================
    proposal_cards = []
    won_cards = []

    for res in latest_responses:

   
        quotation = Quotation.objects.filter(
            rfq_id__iexact=(res.ref_id or "").strip(),
            company__iexact=(res.company or "").strip()
        ).order_by("-id").first()
            

        # ================= PROPOSAL =================
        if res.form.process == "PROPOSAL":

            # 🚫 NOT WON → stay in proposal
            if res.status != "WON":
                proposal_cards.append({
                    "ref": res.ref_id,
                    "company": res.company,
                    "quotation": quotation
                })

            # ✅ WON → move to won
            else:
                won_cards.append({
                    "ref": res.ref_id,
                    "company": res.company,
                    "quotation": quotation,
                    "reviewed": res.is_reviewed,
                    "reviewed_by": res.reviewed_by,
                    "reviewed_at": res.reviewed_at
                })
    # ================= DATA VIEW =================
    previous_data = {}
    responses = None
    last_response = None
    processed_responses = []

    if selected_ref and selected_company:

        responses = (
            FormResponse.objects
            .filter(ref_id=selected_ref, company=selected_company)
            .select_related("form")
            .prefetch_related(
                Prefetch(
                    "form__stage_set",
                    queryset=Stage.objects.prefetch_related(
                        "field_set",
                        "table_set__tablecolumn_set"
                    )
                )
            )
            .order_by("id")
        )

        last_response = responses.last()

        # ===== MERGE DATA =====
        for r in responses:
            if r.data:
                previous_data.update(r.data)

        # ================= PROCESS =================
        for res in responses:

            quotation = Quotation.objects.filter(
                rfq_id__iexact=(res.ref_id or "").strip(),
                company__iexact=(res.company or "").strip(),
                is_signed=True
            ).order_by("-id").first()

            processed = {
                "form": res.form,
                "stages": [],
                "response_id": res.id,
                "ref_id": res.ref_id,
                "company": res.company,
                "approved": getattr(res, "is_costing_approved", False),
                "approved_by": getattr(res, "approved_by", None),
                "approved_at": getattr(res, "approved_at", None),
                "quotation": quotation   # ✅ NOW CORRECT
            }

            for stage in res.form.stage_set.all():

                combined = []

                # ================= FIELDS =================
                for field in stage.field_set.all():
                    combined.append({
                        "type": "field",
                        "order": field.order,
                        "data": field
                    })

                # ================= TABLES =================
                for table in stage.table_set.all():
                    combined.append({
                        "type": "table",
                        "order": table.order,
                        "data": table
                    })

                # 🔥 SORT (VERY IMPORTANT)
                combined_items = sorted(combined, key=lambda x: x["order"])

                stage_data = {
                    "name": stage.name,
                    "items": []
                }

                # ================= PROCESS IN ORDER =================
                for item in combined_items:

                    # ---------- FIELD ----------
                    if item["type"] == "field":

                        field = item["data"]
                        val = res.data.get(field.label)
                        val = process_cell_value(val, field.field_type)

                        if val is not None:
                            stage_data["items"].append({
                                "type": "field",
                                "label": field.label,
                                "value": val,
                                "field_type": field.field_type
                            })

                    # ---------- TABLE ----------
                    elif item["type"] == "table":

                        table = item["data"]
                        rows = res.data.get(table.name)

                        if isinstance(rows, list):

                            clean_rows = []

                            for row in rows:

                                clean_row = {}

                                # ================= ROW NAME =================
                                row_name = row.get("row_name") or row.get("Row") or ""

                                clean_row["row_name"] = row_name

                                # ================= KEEP COLUMN ORDER =================

                                ordered_columns = list(
                                    table.tablecolumn_set.all().order_by("order", "id")
                                )

                                for col_obj in ordered_columns:

                                    key = col_obj.name

                                    value = row.get(key)

                                    col_type = None

                                    # ================= MATRIX CELL CONFIG =================

                                    if row_name:

                                        row_obj = table.tablerow_set.filter(
                                            name=row_name
                                        ).first()

                                        if row_obj:

                                            config = TableCellConfig.objects.filter(
                                                row=row_obj,
                                                column=col_obj
                                            ).first()

                                            if config:
                                                col_type = config.cell_type

                                    # ================= PROCESS VALUE =================

                                    clean_row[key] = process_cell_value(
                                        value,
                                        col_type
                                    )

                                clean_rows.append(clean_row)

                            stage_data["items"].append({
                                "type": "table",
                                "name": table.name,
                                "row_header_name": res.data.get(
                                    f"{table.name}_row_header_name",
                                    table.row_header_name
                                ),
                                "rows": clean_rows,
                                "columns": list(
                                    table.tablecolumn_set.all().order_by("order")
                                )
                            })
                processed["stages"].append(stage_data)

            processed_responses.append(processed)

    # ================= FORM FETCH =================
    def get_forms(process):
        return list(
            Form.objects
            .filter(process=process)
            .order_by("-is_active", "-id")
            .values("id", "name")
        )

    rfq_forms = get_forms("RFQ")

    stage_forms = {
        "RFQ": get_forms("RFQ"),
        "FEASIBILITY": get_forms("FEASIBILITY"),
        "COSTING": get_forms("COSTING"),
        "PROPOSAL": get_forms("PROPOSAL"),
        "WON": get_forms("WON"), 
    }

    return render(request, "form_builder/kanban_builder.html", {
        "rfq_cards": rfq_cards,
        "feas_cards": feas_cards,
        "cost_cards": cost_cards,
        "proposal_cards": proposal_cards,
        "won_cards": won_cards,
        "selected_ref": selected_ref,
        "responses": responses,
        "previous_data": previous_data,
        "rfq_forms": rfq_forms,
        "last_response": last_response,
        "processed_responses": processed_responses,
        "stage_forms": stage_forms,
    })





@login_required
def move_to_won(request):

    ref_id = request.POST.get("ref_id")

    last = FormResponse.objects.filter(
        ref_id=ref_id
    ).order_by("-id").first()

    if not last:
        return JsonResponse({"status": "error"})

    # ✅ NEW LOGIC
    last.status = "WON"
    last.save()

    return JsonResponse({"status": "success"})


@login_required
def review_won(request):

    ref_id = request.POST.get("ref_id")
    password = request.POST.get("password")

    if not request.user.check_password(password):
        return JsonResponse({"status": "error", "msg": "Wrong password"})

    last = FormResponse.objects.filter(
        ref_id=ref_id,
        status="WON"
    ).order_by("-id").first()

    if not last:
        return JsonResponse({"status": "error"})

    last.is_reviewed = True
    last.reviewed_by = request.user
    last.reviewed_at = timezone.now()
    last.save()

    return JsonResponse({"status": "success"})
    
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@require_POST
@login_required
def delete_card(request):

    id = request.POST.get("id")
    action_type = request.POST.get("type")  # 🔥 full / rollback

    if not id:
        return JsonResponse({"status": "error", "msg": "ID missing"})

    try:
        response = FormResponse.objects.get(id=id)

        ref = response.ref_id
        process = response.form.process

        process_flow = ["RFQ", "FEASIBILITY", "COSTING", "PROPOSAL", "WON"]

        # ================= FULL DELETE =================
        if action_type == "full":

            FormResponse.objects.filter(
                ref_id=ref,
                company=response.company
            ).delete()

            return JsonResponse({"status": "success"})

        # ================= ROLLBACK =================
        elif action_type == "rollback":

            idx = process_flow.index(process)

            if idx == 0:
                return JsonResponse({"status": "error", "msg": "Already first stage"})

            # delete ONLY current stage
            response.delete()

            previous_stage = process_flow[idx - 1]

            return JsonResponse({
                "status": "success",
                "move_to": previous_stage
            })

        else:
            return JsonResponse({"status": "error", "msg": "Invalid type"})

    except FormResponse.DoesNotExist:
        return JsonResponse({"status": "error", "msg": "Not found"})

def update_field_position(request):

    data = json.loads(request.body)

    field = Field.objects.get(id=data["field_id"])

    field.stage_id = data["stage_id"]
    field.order = data["order"]
    field.save()

    return JsonResponse({"status": "ok"})


def add_field_ajax(request):

    data = json.loads(request.body)

    Field.objects.create(
        stage_id=data["stage_id"],
        label=data["label"],
        field_type=data.get("field_type", "text"),
        created_by=request.user
    )

    return JsonResponse({"status": "created"})



def delete_field(request, field_id):

   

        field = Field.objects.get(id=field_id)

        AuditLog.objects.create(
            user=request.user,
            role=request.user.role,
            module="form_builder",
            action="DELETE",
            model_name="Field",
            object_id=str(field.id),
            object_repr=str(field),
            description="Field deleted"
        )

        field.delete()

        return JsonResponse({"status": "deleted"})

  



def edit_field(request, field_id):

    data = json.loads(request.body)

    field = Field.objects.get(id=field_id)
    field.label = data["label"]
    field.save()

    return JsonResponse({"status": "updated"})



# import requests

# from django.conf import settings
# from django.core.cache import cache
# from django.shortcuts import render

# @require_page_permission("can_costing_dashboard")
# def dashboard_view(request):

#     # ================= GET CURRENCY RATES =================

#     API_KEY = settings.CURRENCY_API_KEY

#     url = (
#         f"https://v6.exchangerate-api.com/"
#         f"v6/{API_KEY}/latest/INR"
#     )

#     rates = cache.get("currency_rates")

#     if not rates:

#         try:

#             response = requests.get(url)

#             currency_data = response.json()

#             rates = currency_data.get(
#                 "conversion_rates",
#                 {}
#             )

#             cache.set(
#                 "currency_rates",
#                 rates,
#                 3600
#             )

#         except Exception:

#             rates = {}

#     # ================= GET COSTING RESPONSES =================

#     responses = FormResponse.objects.filter(
#         form__process__iexact="COSTING"
#     )

#     company_data = {}

#     for res in responses:

#         # ================= COMPANY NAME =================

#         company_name = (
#             getattr(res, "company", None)
#             or (res.data or {}).get("company")
#             or (res.data or {}).get("Company")
#             or "Unknown Company"
#         )

#         # ================= RFQ =================

#         rfq = res.ref_id or "NO-RFQ"

#         # ================= FINAL DISPLAY =================

#         company = f"{rfq} - {company_name}"

#         data = res.data or {}

#         tables = {}

#         grand_total = 0

#         # ================= GET TABLE TOTALS =================

#         for key, value in data.items():

#             if key.endswith("_total"):

#                 table_name = key.replace(
#                     "_total",
#                     ""
#                 )

#                 try:

#                     total = float(value or 0)

#                 except Exception:

#                     total = 0

#                 tables[table_name] = total

#                 grand_total += total

#         # ================= SAVE COMPANY DATA =================

#         if tables:

#             company_data[company] = {

#                 "tables": tables,

#                 "grand_total": round(
#                     grand_total,
#                     2
#                 )
#             }

#     # ================= RENDER =================

#     return render(
#         request,
#         "form_builder/cost_dash.html",
#         {
#             "company_data": company_data,
#             "rates": rates
#         }
#     )
    
import requests

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
@require_page_permission("can_costing_dashboard")
def dashboard_view(request):

    # =========================================
    # GET CURRENCY RATES
    # =========================================

    API_KEY = settings.CURRENCY_API_KEY

    url = (
        f"https://v6.exchangerate-api.com/"
        f"v6/{API_KEY}/latest/INR"
    )

    rates = cache.get("currency_rates")

    if not rates:

        try:

            response = requests.get(url)

            currency_data = response.json()

            rates = currency_data.get(
                "conversion_rates",
                {}
            )

            cache.set(
                "currency_rates",
                rates,
                3600
            )

        except Exception:

            rates = {}

    # =========================================
    # GET COSTING RESPONSES
    # =========================================

    responses = FormResponse.objects.filter(
        form__process__iexact="COSTING"
    )

    company_data = {}

    # =========================================
    # LOOP RESPONSES
    # =========================================

    for res in responses:

        data = res.data or {}

        # =====================================
        # COMPANY NAME
        # =====================================

        company_name = (

            getattr(res, "company", None)

            or

            data.get("company")

            or

            data.get("Company")

            or

            "Unknown Company"
        )

        # =====================================
        # RFQ
        # =====================================

        rfq = res.ref_id or "NO-RFQ"

        # =====================================
        # DISPLAY NAME
        # =====================================

        company = f"{rfq} - {company_name}"

        # =====================================
        # TABLE TOTALS
        # =====================================

        tables = {}

        grand_total = 0

        for key, value in data.items():

            if key.endswith("_total"):

                table_name = key.replace(
                    "_total",
                    ""
                )

                try:

                    total = float(value or 0)

                except Exception:

                    total = 0

                tables[table_name] = total

                grand_total += total

        # =====================================
        # DEFAULT DETAILS
        # =====================================

        details = {

            "part_number": "-",

            "drawing_revision": "-",

            "description": "-",

            "customer_name": "-",

            "vendor_code": "-",

            "customer_country": "-",

            "currency": "INR",

            "issue_date": "-",

            "issue_number": "-",

            "date_completed": "-",

            "production_part": "-"
        }

        # =====================================
        # SCAN TABLE ROWS
        # =====================================

        for table_name, rows in data.items():

            # ONLY TABLE DATA
            if not isinstance(rows, list):
                continue

            # LOOP ROWS
            for row in rows:

                if not isinstance(row, dict):
                    continue

                row_name = str(

                    row.get("row_name", "")

                ).strip().lower()

                # =================================
                # FIND FIRST REAL VALUE
                # =================================

                value = "-"

                for k, v in row.items():

                    if k in [
                        "row_name",
                        "_row_id"
                    ]:
                        continue

                    if v not in [
                        None,
                        "",
                        "None",
                        "null"
                    ]:

                        value = str(v)

                        break

                # =================================
                # MAP VALUES
                # =================================

                if row_name == "part number":

                    details["part_number"] = value

                elif row_name == "drawing revision":

                    details["drawing_revision"] = value

                elif row_name == "description":

                    details["description"] = value

                elif row_name == "customer name":

                    details["customer_name"] = value

                elif row_name == "vendor code":

                    details["vendor_code"] = value

                elif row_name == "customer country":

                    details["customer_country"] = value

                elif row_name == "cost base currency":

                    details["currency"] = value

                elif row_name == "issue date":

                    details["issue_date"] = value

                elif row_name == "issue number":

                    details["issue_number"] = value

                elif row_name == "date completed":

                    details["date_completed"] = value

                elif row_name == "production part":

                    details["production_part"] = value

        # =====================================
        # SAVE COMPANY DATA
        # =====================================

        if tables:

            company_data[company] = {

                "tables": tables,

                "grand_total": round(
                    grand_total,
                    2
                ),

                "details": details
            }

    # =========================================
    # RENDER
    # =========================================

    return render(

        request,

        "form_builder/cost_dash.html",

        {
            "company_data": company_data,

            "rates": rates
        }
    )









from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.utils import timezone


import json
import random
import string    
@login_required
def verify_signature(request):

    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    password = data.get("password", "").strip()

    if not request.user.check_password(password):
        return JsonResponse({"ok": False, "error": "Invalid password"}, status=401)

    # ✅ SAFE NAME HANDLING
    first = request.user.first_name or ""
    last = request.user.last_name or ""

    full_name = (first + " " + last).strip()

    if not full_name:
        full_name = getattr(request.user, "username", None) or request.user.email

    # ✅ generate unique code
    ref_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    local_time = timezone.localtime(timezone.now())
    return JsonResponse({
        "ok": True,
        "name": full_name,
        "time": local_time.strftime("%d %b %Y %I:%M %p"),
        "code": ref_code
    })
    
    
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Form, FormResponse


@login_required
def register_list(request):

    forms = Form.objects.filter(process="REGISTER").order_by("name")

    responses = FormResponse.objects.filter(
        form__process="REGISTER"
    ).select_related("form").order_by("-id")

    return render(request, "form_builder/register_list.html", {
        "forms": forms,
        "responses": responses
    })


# ======================================
# SAVE RESPONSE
# ======================================

@login_required
def save_response(request, form_id):

    import json
    import os
    import uuid

    from django.conf import settings
    from django.core.files.storage import FileSystemStorage

    form = Form.objects.get(id=form_id)

    if request.method != "POST":
        return redirect("kanban_view")

    # ==========================================================
    # COMPANY
    # ==========================================================

    company = request.POST.get("company", "")

    # ==========================================================
    # HEADER
    # ==========================================================

    doc_name = request.POST.get("doc_name") or form.name

    doc_number = request.POST.get("doc_number") or "N/A"

    revision = request.POST.get("revision") or "1.0"

    # ==========================================================
    # REF GENERATION
    # ==========================================================

    if form.process in ["RFQ", "REGISTER"]:

        last = FormResponse.objects.filter(
            form__process=form.process,
            company=company
        ).order_by("-id").first()

        if last and last.ref_id:

            try:

                last_number = int(
                    last.ref_id.split("-")[-1]
                )

                new_number = last_number + 1

            except:

                new_number = 1

        else:

            new_number = 1

        rfq_id = (
            f"{form.process}-"
            f"{str(new_number).zfill(2)}"
        )

    else:

        rfq_id = request.POST.get("rfq_id")

    if not rfq_id:
        return redirect("kanban_view")

    # ==========================================================
    # EXISTING DATA
    # ==========================================================

    existing = FormResponse.objects.filter(
        form=form,
        ref_id=rfq_id,
        company=company
    ).first()

    existing_data = (
        existing.data
        if existing and existing.data
        else {}
    )

    # ==========================================================
    # STORAGE
    # ==========================================================

    fs = FileSystemStorage(
        location=os.path.join(
            settings.MEDIA_ROOT,
            "uploads"
        ),
        base_url=settings.MEDIA_URL + "uploads/"
    )

    cleaned_data = {}

    table_data = {}
    table_objects = {}
    # ==========================================
    # DYNAMIC ROW NAME STORAGE
    # ==========================================

    dynamic_row_names = {}

    for k, v in request.POST.items():

        if k.startswith("row_name__"):

            parts = k.split("__")

            if len(parts) >= 2:

                dynamic_key = parts[1]

                dynamic_row_names[
                    dynamic_key
                ] = v.strip()



    all_keys = list(request.POST.keys())
    for key in request.FILES.keys():
        if key not in all_keys:
            all_keys.append(key)
    for key in all_keys:

        if key in [
            "csrfmiddlewaretoken",
            "rfq_id",
            "company",
            "doc_name",
            "doc_number",
            "revision"
        ]:
            continue

        file_urls = []

        # ======================================================
        # FILE HANDLING
        # ======================================================

        if key in request.FILES:

            files = request.FILES.getlist(key)

            folder = rfq_id if rfq_id else "default"

            for f in files:

                unique_name = (
                    f"{uuid.uuid4().hex}_{f.name}"
                )

                filename = fs.save(
                    os.path.join(folder, unique_name),
                    f
                )

                file_urls.append(
                    fs.url(filename)
                )

        # ======================================================
        # NORMAL VALUES
        # ======================================================

        values = request.POST.getlist(key)

        if len(values) > 1:

            parsed_value = values

        else:

            value = values[0] if values else None

            try:

                parsed_value = json.loads(value)

            except:

                parsed_value = value

        # ======================================================
        # TABLE VALUES
        # ======================================================

        if "__" in key:

            try:

                table_id, row_id, col_id = key.split("__")

                # ==========================================
                # GET ACTUAL OBJECTS
                # ==========================================

                table_obj = Table.objects.filter(
                    id=table_id
                ).first()

                col_obj = TableColumn.objects.filter(
                    id=col_id
                ).first()

                # ==========================================
                # INVALID
                # ==========================================

                if not table_obj or not col_obj:

                    continue

                # ==========================================
                # REAL TABLE NAME
                # ==========================================

                table_name = table_obj.name
                table_objects[table_name] = table_obj
                # ==========================================
                # DYNAMIC ROW SUPPORT
                # ==========================================

                if str(row_id).isdigit():

                    row_obj = TableRow.objects.filter(
                        id=row_id
                    ).first()

                    row_name = (
                        row_obj.name
                        if row_obj
                        else row_id
                    )

                else:

                 
                    row_name = dynamic_row_names.get(
                        row_id,
                        row_id
                    )

                # ==========================================
                # COLUMN NAME
                # ==========================================

                col_name = col_obj.name

            except:

                continue

            table_data.setdefault(table_name, {})

            if row_name not in table_data[table_name]:
                table_data[table_name][row_name] = {}

            # ==================================================
            # FILE CASE
            # ==================================================

            if file_urls:

                table_data[
                    table_name
                ][
                    row_name
                ][
                    col_name
                ] = file_urls

            # ==================================================
            # NORMAL VALUE
            # ==================================================

            elif parsed_value not in [
                "",
                None,
                "None",
                "null",
                []
            ]:

                table_data[
                    table_name
                ][
                    row_name
                ][
                    col_name
                ] = parsed_value

        # ======================================================
        # NORMAL FIELD
        # ======================================================

        else:

            if file_urls:

                cleaned_data[key] = file_urls

            elif existing_data.get(key):

                cleaned_data[key] = existing_data.get(key)

            else:

                cleaned_data[key] = parsed_value

    # ==========================================================
    # CLEAN Tif table_obj:ABLE DATA
    # ==========================================================

    for table_name, rows in table_data.items():

        row_list = []

        # ======================================================
        # KEEP ORIGINAL ROW ORDER
        # ======================================================

        table_obj = table_objects.get(table_name)

        # ======================================================
        # USE ACTUAL TABLE ROW ORDER
        # ======================================================

        ordered_row_names = []

        if table_obj:

            ordered_row_names = list(

                table_obj.tablerow_set.all()
                .order_by("order", "id")
                .values_list("name", flat=True)
            )

        # ======================================================
        # ADD MISSING ROWS
        # ======================================================

        for row_name in rows.keys():

            if row_name not in ordered_row_names:

                ordered_row_names.append(row_name)
        # ======================================================
        # PROCESS ROWS IN TABLE ORDER
        # ======================================================

        for row_name in ordered_row_names:

            if row_name not in rows:
                continue

            original_row = rows[row_name]

            if not original_row:
                continue

            ordered_row = {}

            # ==================================================
            # KEEP DATABASE COLUMN ORDER
            # ==================================================

            ordered_columns = []

            if table_obj:

                ordered_columns = list(

                    table_obj.tablecolumn_set.all()
                    .order_by("order", "id")
                    .values_list("name", flat=True)
                )

            # ==================================================
            # ADD MISSING COLUMNS
            # ==================================================

            for col_name in original_row.keys():

                if col_name not in ordered_columns:

                    ordered_columns.append(col_name)

            # ==================================================
            # BUILD ROW IN COLUMN ORDER 
            # ==================================================

            for col_name in ordered_columns:

                if col_name in original_row:

                    ordered_row[col_name] = (
                        original_row[col_name]
                    )   

            # ==================================================
            # CHECK EMPTY
            # ==================================================

            # valid_values = [

            #     v for v in ordered_row.values()

            #     if v not in [
            #         "",
            #         None,
            #         "None",
            #         "null",
            #         {},
            #         []
            #     ]
            # ]

            # if not valid_values:
            #     continue

            # ==================================================
            # PRESERVE ROW NAME
            # ==================================================

            ordered_row["row_name"] = row_name

            print("===================================")
            print("TABLE ID :", table_obj.id if table_obj else None)
            print("TABLE    :", table_obj.name if table_obj else None)
            print("ROW NAME :", repr(row_name))
            print(
                "DB ROWS  :",
                list(
                    table_obj.tablerow_set.values_list(
                        "id",
                        "name"
                    )
                ) if table_obj else []
            )

            row_obj = TableRow.objects.filter(
                table=table_obj,
                name=row_name
            ).first()

            print("FOUND :", row_obj)
            print("===================================")

            if row_obj:

                ordered_row["_row_id"] = str(
                    row_obj.id
                )

            else:

                ordered_row["_row_id"] = (
                    f"new_{row_name}"
                )

            # ==================================================
            # APPEND
            # ==================================================

            row_list.append(ordered_row)

        
        # ======================================================
        # SKIP EMPTY TABLE
        # ======================================================

        if not row_list:
            continue

        # ======================================================
        # TOTAL CALCULATION
        # ======================================================

        total = 0

        if table_obj:

            total_columns = (
                table_obj.tablecolumn_set.filter(
                    is_total=True
                )
            )

            for row in row_list:

                for col in total_columns:

                    col_name = col.name.strip()

                    for key in row:

                        if key.strip() == col_name:

                            try:

                                total += float(
                                    row.get(key) or 0
                                )

                            except:
                                pass

        # ======================================================
        # SAVE TABLE DATA
        # ======================================================

        table_name_clean = table_name.strip()

        cleaned_data[
            table_name_clean
        ] = row_list

        # =================================================
        # Save Row header Name
        # =================================================
        if table_obj:
            cleaned_data[
                f"{table_name_clean}_row_header_name"
            ] = table_obj.row_header_name

        # ======================================================
        # SAVE TOTAL
        # ======================================================

        if (
            table_obj
            and
            table_obj.tablecolumn_set.filter(
                is_total=True
            ).exists()
        ):

            cleaned_data[
                f"{table_name_clean}_total"
            ] = round(total, 2)

    # ==========================================================
    # SAVE RESPONSE
    # ==========================================================

    FormResponse.objects.update_or_create(

        form=form,

        ref_id=rfq_id,

        company=company,

        defaults={

            "data": cleaned_data,

            "doc_name": doc_name,

            "doc_number": doc_number,

            "revision": revision,

            "created_by": request.user
        }
    )

    # ==========================================================
    # REDIRECT
    # ==========================================================

    process = (
        form.process or ""
    ).strip().upper()

    if process == "REGISTER":

        return redirect(
            f"/form-builder/register/?form_id={form.id}"
        )

    return redirect("kanban_view")









import os
import mimetypes
from django.http import FileResponse, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required
def open_uploaded_file(request, path):

    import os
    from django.conf import settings

    file_path = os.path.join(settings.MEDIA_ROOT, path)

    print("DEBUG PATH:", file_path)  # 🔥 ADD THIS

    if not os.path.exists(file_path):
        raise Http404("File not found")

    return FileResponse(open(file_path, 'rb'))
# ============================================ Edit Response Column ==============================================


# ======================================
# VIEW RESPONSES
# ======================================

def responses(request, form_id):

    form = Form.objects.get(id=form_id)

    responses = FormResponse.objects.filter(form=form).order_by("-id")

    return render(request, "form_builder/responses.html", {
        "form": form,
        "responses": responses
    })
    
    
@login_required
def get_next_rfq(request):

    company = request.GET.get("company")

    if not company:
        return JsonResponse({"rfq_id": "RFQ-01"})

    last = FormResponse.objects.filter(
        form__process="RFQ",
        company=company
    ).order_by("-id").first()

    if last and last.ref_id:
        try:
            last_number = int(last.ref_id.split("-")[-1])
            new_number = last_number + 1
        except:
            new_number = 1
    else:
        new_number = 1

    return JsonResponse({
        "rfq_id": f"RFQ-{str(new_number).zfill(2)}"
    })

def update_field_position(request):

    data = json.loads(request.body)

    field = Field.objects.get(id=data["field_id"])

    field.stage_id = data["stage_id"]
    field.order = data["order"]
    field.save()

    return JsonResponse({"status": "ok"})


def add_field_ajax(request):

    data = json.loads(request.body)

    Field.objects.create(
        stage_id=data["stage_id"],
        label=data["label"],
        field_type=data.get("field_type", "text"),
        created_by=request.user
    )

    return JsonResponse({"status": "created"})



def delete_field(request, field_id):

   

        field = Field.objects.get(id=field_id)

        AuditLog.objects.create(
            user=request.user,
            role=request.user.role,
            module="form_builder",
            action="DELETE",
            model_name="Field",
            object_id=str(field.id),
            object_repr=str(field),
            description="Field deleted"
        )

        field.delete()

        return JsonResponse({"status": "deleted"})

 



def edit_field(request, field_id):

    data = json.loads(request.body)

    field = Field.objects.get(id=field_id)
    field.label = data["label"]
    field.save()

    return JsonResponse({"status": "updated"})




    

# from django.http import JsonResponse

# @login_required
# def response_detail(request, response_id):

#     response = FormResponse.objects.get(id=response_id)

#     responses = FormResponse.objects.filter(
#         ref_id=response.ref_id,
#         company=response.company
#     ).select_related("form").prefetch_related(
#         "form__stage_set__table_set__tablecolumn_set"
#     ).order_by("id")

#     data_list = []

#     for res in responses:

#         tables_meta = {}

#         # ✅ GET COLUMN ORDER FROM DB
#         for stage in res.form.stage_set.all():
#             for table in stage.table_set.all():

#                 columns = list(
#                     table.tablecolumn_set
#                     .order_by("id")   # 🔥 later change to "order"
#                     .values_list("name", flat=True)
#                 )

#                 tables_meta[table.name] = columns

#         data_list.append({
#             "id": res.id,
#             "form_id": res.form.id,
#             "form_name": res.form.name,
#             "ref_id": res.ref_id,
#             "company": res.company,
#             "doc_name": res.doc_name or res.form.name,
#             "doc_number": res.doc_number or "N/A",
#             "revision": res.revision or "1.0",
#             "data": res.data,
#             "tables_meta": tables_meta   # ✅ ADD THIS
#         })

#     return JsonResponse(data_list, safe=False)
from django.http import JsonResponse

@login_required
def response_detail(request, response_id):

    # =====================================
    # GET MAIN RESPONSE
    # =====================================

    response = FormResponse.objects.get(
        id=response_id
    )

    # =====================================
    # GET ALL RELATED RESPONSES
    # =====================================

    responses = (

        FormResponse.objects.filter(

            ref_id=response.ref_id,

            company=response.company

        )

        .select_related("form")

        .prefetch_related(
            "form__stage_set__table_set__tablecolumn_set"
        )

        .order_by("id")
    )

    data_list = []

    # =====================================
    # LOOP RESPONSES
    # =====================================

    for res in responses:

        tables_meta = {}

        row_headers = {}

        table_titles = {}

        # =================================
        # GET TABLE METADATA
        # =================================

        for stage in res.form.stage_set.all():

            for table in stage.table_set.all():

                # ==========================
                # COLUMN ORDER
                # ==========================

                columns = list(

                    table.tablecolumn_set

                    .order_by("order", "id")

                    .values_list(
                        "name",
                        flat=True
                    )
                )

                # ==========================
                # ENSURE row_name FIRST
                # ==========================

                if "row_name" not in columns:

                    columns.insert(
                        0,
                        "row_name"
                    )

                # ==========================
                # SAVE META
                # ==========================

                tables_meta[
                    table.name
                ] = columns

                # ==========================
                # ROW HEADER NAME
                # ==========================

                row_headers[
                    table.name
                ] = (

                    table.row_header_name
                    or
                    "Row Name"
                )

                # ==========================
                # TABLE TITLE
                # ==========================

                table_titles[
                    table.name
                ] = table.name

        # =================================
        # RESPONSE DATA
        # =================================

        response_data = res.data or {}

        # =================================
        # APPEND
        # =================================

        data_list.append({

            "id": res.id,

            "form_id": res.form.id,

            "form_name": res.form.name,

            "ref_id": res.ref_id,

            "company": res.company,

            "doc_name": (
                res.doc_name
                or
                res.form.name
            ),

            "doc_number": (
                res.doc_number
                or
                "N/A"
            ),

            "revision": (
                res.revision
                or
                "1.0"
            ),

            "data": response_data,

            # =============================
            # TABLE SUPPORT
            # =============================

            "tables_meta": tables_meta,

            "row_headers": row_headers,

            "table_titles": table_titles
        })

    # =====================================
    # RETURN
    # =====================================

    return JsonResponse(
        data_list,
        safe=False
    )


    

from django.utils import timezone

@login_required
def costing_action(request):

    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=400)

    response_id = request.POST.get("id")
    action = request.POST.get("action")

    if not response_id:
        return JsonResponse({"status": "error", "msg": "Missing ID"})

    try:
        obj = FormResponse.objects.get(id=response_id)
    except FormResponse.DoesNotExist:
        return JsonResponse({"status": "error", "msg": "Invalid ID"})

    # ✅ ONLY COSTING
    if obj.form.process != "COSTING":
        return JsonResponse({"status": "error", "msg": "Invalid stage"})

    # ✅ APPROVE LOGIC
    if action == "approve":

        # prevent double approval
        if obj.is_costing_approved:
            return JsonResponse({"status": "error", "msg": "Already approved"})

        obj.is_costing_approved = True
        obj.approved_by = request.user              # 🔥 WHO
        obj.approved_at = timezone.localtime(timezone.now())  # 🔥 WHEN

        obj.save()

    return JsonResponse({"status": "success"})

@login_required
def register_data_api(request):

    form_id = request.GET.get("form_id")

    responses = FormResponse.objects.filter(
        form__process="REGISTER"
    )

    # ✅ OPTIONAL FILTER
    if form_id:
        responses = responses.filter(form_id=form_id)

    responses = responses.select_related("form").order_by("-id")

    data = []

    for r in responses:
        data.append({
            "id": r.id,
            "ref_id": r.ref_id or "No Ref",
            "form_name": r.form.name,
            "doc_name": r.doc_name,
            "doc_number": r.doc_number,
            "revision": r.revision,
            "company": r.company,
        })

    return JsonResponse(data, safe=False)



@login_required
def register_detail_api(request, response_id):

    response = FormResponse.objects.get(id=response_id)

    responses = FormResponse.objects.filter(
        ref_id=response.ref_id,
        company=response.company
    ).select_related("form").prefetch_related(
        "form__stage_set__field_set",
        "form__stage_set__table_set__tablecolumn_set"
    ).order_by("id")

    result = []

    for res in responses:

        processed = {
            "form_name": res.form.name,
            "doc_name": res.doc_name or res.form.name,
            "doc_number": res.doc_number or "N/A",
            "revision": res.revision or "1.0",
            "stages": []
        }

        for stage in res.form.stage_set.all():

            stage_data = {
                "name": stage.name,
                "fields": [],
                "tables": []
            }

            # ================= FIELDS =================
            for field in stage.field_set.all():

                val = res.data.get(field.label)

                # signature fix
                if isinstance(val, str):
                    try:
                        parsed = json.loads(val)
                        if isinstance(parsed, dict) and "signed_by" in parsed:
                            val = parsed
                    except:
                        pass

                stage_data["fields"].append({
                    "label": field.label,
                    "value": val
                })

            # ================= TABLE =================
            for table in stage.table_set.all():

                rows = res.data.get(table.name)

                if isinstance(rows, list):

                    clean_rows = []

                    for row in rows:
                        clean_row = {}

                        for k, v in row.items():

                            if isinstance(v, str):
                                try:
                                    parsed = json.loads(v)
                                    if isinstance(parsed, dict) and "signed_by" in parsed:
                                        v = parsed
                                except:
                                    pass

                            clean_row[k] = v

                        clean_rows.append(clean_row)

                    stage_data["tables"].append({
                        "name": table.name,
                        "columns": [col.name for col in table.tablecolumn_set.all().order_by("id")],
                        "rows": clean_rows
                    })

            processed["stages"].append(stage_data)

        result.append(processed)

    return JsonResponse(result, safe=False)