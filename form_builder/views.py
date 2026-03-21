from django.shortcuts import render, redirect
from .models import Form, Stage, Field, Table, TableColumn, FormResponse
import json
from qms_app.decorators import require_page_permission
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
#
# ============================================== Form Builder ==============================================
#


@require_page_permission("can_form_build")
def form_builder(request):

    process_filter = request.GET.get("process")

    forms = Form.objects.all().order_by("id")

    # FILTER FORMS
    if process_filter:
        forms = forms.filter(process=process_filter)

    # 🔥 GET CURRENT BUILDING FORM (LATEST ONE)
    current_form = None
    if process_filter:
        current_form = Form.objects.filter(
            process=process_filter,
            is_active=False   # 👈 only building form
        ).order_by("-id").first()

    # ✅ FIXED STAGES FILTER (ONLY CURRENT FORM)
    if current_form:
        stages = Stage.objects.select_related("form").filter(
            form=current_form
        ).order_by("id")
    else:
        stages = []

    # OPTIONS SPLIT
    for stage in stages:
        for field in stage.field_set.all():
            field.option_list = field.options.split(",") if field.options else []

    if request.method == "POST":

        action = request.POST.get("action")

        # ================= CREATE FORM =================
        if action == "create_form":

            form_name = request.POST.get("form_name", "").strip()
            process = request.POST.get("process") or process_filter or "RFQ"

            if form_name:
                Form.objects.create(
                    name=form_name,
                    process=process,
                    is_active=False   # 🔥 builder mode
                )

            return redirect(f"/form-builder/builder/?process={process}")

        # ================= ADD STAGE =================
        elif action == "add_stage":

            form_id = request.POST.get("form_id")
            stage_name = request.POST.get("stage_name", "").strip()

            if form_id and stage_name:
                Stage.objects.create(form_id=form_id, name=stage_name)

            return redirect(request.get_full_path())

        # ================= ADD FIELD =================
        elif action == "add_field":

            stage_id = request.POST.get("stage_id")
            label = request.POST.get("label", "").strip()
            field_type = request.POST.get("field_type")
            formula = request.POST.get("formula", "").strip()
            options = request.POST.get("options", "").strip()

            if stage_id and label and field_type:

                field = Field.objects.create(
                    stage_id=stage_id,
                    label=label,
                    field_type=field_type,
                    formula=formula if formula else None,
                    options=options if options else None
                )

                if field_type == "table":

                    columns_json = request.POST.get("table_columns")

                    try:
                        columns = json.loads(columns_json) if columns_json else []
                    except:
                        columns = []

                    table = Table.objects.create(
                        stage_id=stage_id,
                        name=label
                    )

                    for col in columns:
                        if not col.get("name"):
                            continue

                        TableColumn.objects.create(
                            table=table,
                            name=col.get("name"),
                            column_type=col.get("type"),
                            formula=col.get("formula") or None,
                            is_total=col.get("is_total", False)
                        )

            return redirect(request.get_full_path())

        # ================= FINAL SUBMIT =================
        elif action == "final_submit":

            if current_form:
                current_form.is_active = True
                current_form.save()

            return redirect(f"/form-builder/builder/?process={process_filter}")

    return render(request, "form_builder/form_builder.html", {
        "forms": forms,
        "stages": stages,
        "selected_process": process_filter,
        "current_form": current_form   # 🔥 optional use
    })






# ============================================== Edit Form =====================================================
def edit_form(request, form_id):

    form = Form.objects.get(id=form_id)
    stages = Stage.objects.filter(form=form).order_by("id")

    # prepare options
    for stage in stages:
        for field in stage.field_set.all():
            field.option_list = field.options.split(",") if field.options else []

    if request.method == "POST":

        action = request.POST.get("action")

        # ================= EDIT FORM NAME =================
        if action == "update_form":

            form_name = request.POST.get("form_name", "").strip()

            if form_name:
                form.name = form_name
                form.save()

            return redirect(request.path)

        # ================= ADD STAGE =================
        elif action == "add_stage":

            stage_name = request.POST.get("stage_name")

            if stage_name:
                Stage.objects.create(form=form, name=stage_name)

            return redirect(request.path)

        # ================= ADD FIELD =================
        elif action == "add_field":

            stage_id = request.POST.get("stage_id")
            label = request.POST.get("label")
            field_type = request.POST.get("field_type")

            if stage_id and label and field_type:
                Field.objects.create(
                    stage_id=stage_id,
                    label=label,
                    field_type=field_type
                )

            return redirect(request.path)

        # ================= ADD TABLE ================= 
        elif action == "add_table":

            stage_id = request.POST.get("stage_id")
            table_name = request.POST.get("table_name")

            if stage_id and table_name:
                Table.objects.create(
                    stage_id=stage_id,
                    name=table_name
                )

            return redirect(request.path)

        # ================= ADD COLUMN ================= 
        elif action == "add_column":

            table_id = request.POST.get("table_id")
            col_name = request.POST.get("col_name")
            col_type = request.POST.get("col_type")

            if table_id and col_name:
                TableColumn.objects.create(
                    table_id=table_id,
                    name=col_name,
                    column_type=col_type
                )

            return redirect(request.path)
        # ================= UPDATE TABLE & COLUMN =================
        elif action == "update_table_column":

            for key, value in request.POST.items():

  
                if key.startswith("table_name_"):
                    table_id = key.split("_")[-1]
                    Table.objects.filter(id=table_id).update(name=value)

    
                elif key.startswith("col_name_"):
                    col_id = key.split("_")[-1]
                    TableColumn.objects.filter(id=col_id).update(name=value)

                elif key.startswith("col_type_"):
                    col_id = key.split("_")[-1]
                    TableColumn.objects.filter(id=col_id).update(column_type=value)

            return redirect(request.path)
    return render(request, "form_builder/edit_form.html", {
        "form": form,
        "stages": stages
    })
    
    
def delete_stage(request, stage_id):
    Stage.objects.filter(id=stage_id).delete()
    return JsonResponse({"status": "deleted"})
# ========================================== Delete Column ===================================================

def delete_column(request, col_id):
    TableColumn.objects.filter(id=col_id).delete()
    return JsonResponse({"status": "deleted"})



# ======================================
# FORM LIST
# ======================================
def form_list(request):

    forms = Form.objects.all().order_by("-id")

    return render(request, "form_builder/form_list.html", {
        "forms": forms
    })

from django.shortcuts import get_object_or_404, redirect

def delete_form(request, form_id):
    form = get_object_or_404(Form, id=form_id)

    if request.method == "POST":
        form.delete()
        return redirect("form_lists")

    return redirect("form_lists")
# ======================================
# FILL FORM
# ======================================
# def fill_form(request, form_id):

#     form = Form.objects.get(id=form_id)
#     stages = Stage.objects.filter(form=form)

#     ref_id = request.GET.get("rfq_id") or request.GET.get("ref_id")

#     # prepare options
#     for stage in stages:
#         for field in stage.field_set.all():
#             if field.options:
#                 field.option_list = field.options.split(",")
#             else:
#                 field.option_list = []

#     return render(request, "form_builder/fill_form.html", {
#         "form": form,
#         "stages": stages,
#         "ref_id": ref_id   
#     })
def fill_form(request, form_id):

    form = Form.objects.get(id=form_id)
    stages = Stage.objects.filter(form=form)

    ref_id = request.GET.get("rfq_id") or request.GET.get("ref_id")

    # ✅ AUTO GENERATE RFQ FOR DISPLAY
    if form.process == "RFQ":

        last = FormResponse.objects.filter(
            form__process="RFQ"
        ).order_by("-id").first()

        if last and last.ref_id:
            try:
                last_number = int(last.ref_id.split("-")[-1])
                new_number = last_number + 1
            except:
                new_number = 1
        else:
            new_number = 1

        ref_id = f"RFQ-{str(new_number).zfill(2)}"

    # prepare options
    for stage in stages:
        for field in stage.field_set.all():
            field.option_list = field.options.split(",") if field.options else []

    return render(request, "form_builder/fill_form.html", {
        "form": form,
        "stages": stages,
        "ref_id": ref_id
    })
# ======================================
# SAVE RESPONSE
# ======================================

# def save_response(request, form_id):

#     form = Form.objects.get(id=form_id)

#     if request.method == "POST":


#         if form.process == "RFQ":

#             last = FormResponse.objects.filter(form__process="RFQ").order_by("-id").first()

#             if last and last.ref_id:
#                 try:
#                     last_number = int(last.ref_id.split("-")[-1])
#                     new_number = last_number + 1
#                 except:
#                     new_number = 1
#             else:
#                 new_number = 1

#             rfq_id = f"RFQ-{str(new_number).zfill(2)}"

#         else:
#             rfq_id = request.POST.get("rfq_id")


#         if not rfq_id:
#             rfq_id = request.POST.get("Company Name")

#         cleaned_data = {}
#         table_data = {}

#         for key, value in request.POST.items():

#             if key in ["csrfmiddlewaretoken", "rfq_id"]:
#                 continue


#             if "__" in key:

#                 table_name, col_name, row_index = key.split("__")

#                 table_data.setdefault(table_name, {})
#                 table_data[table_name].setdefault(row_index, {})

#                 table_data[table_name][row_index][col_name] = value

#             else:
#                 cleaned_data[key] = value

#         for table_name, rows in table_data.items():
#             cleaned_data[table_name] = list(rows.values())

#         FormResponse.objects.create(
#             form=form,
#             ref_id=rfq_id,  
#             data=cleaned_data
#         )

#         return redirect(f"/form-builder/kanban/?process={form.process}")

def save_response(request, form_id):

    form = Form.objects.get(id=form_id)

    if request.method == "POST":

        # ================= RFQ AUTO GENERATE =================
        if form.process == "RFQ":

            last = FormResponse.objects.filter(
                form__process="RFQ"
            ).order_by("-id").first()

            if last and last.ref_id:
                try:
                    last_number = int(last.ref_id.split("-")[-1])
                    new_number = last_number + 1
                except:
                    new_number = 1
            else:
                new_number = 1

            rfq_id = f"RFQ-{str(new_number).zfill(2)}"

        # ================= OTHER STAGES =================
        else:
            rfq_id = request.POST.get("rfq_id")

        # 🚨 SAFETY CHECK
        if not rfq_id:
            return redirect(f"/form-builder/kanban/?process={form.process}")

        # ================= DATA PROCESS =================
        cleaned_data = {}
        table_data = {}

        for key, value in request.POST.items():

            if key in ["csrfmiddlewaretoken", "rfq_id"]:
                continue

            if "__" in key:
                table_name, col_name, row_index = key.split("__")

                table_data.setdefault(table_name, {})
                table_data[table_name].setdefault(row_index, {})

                try:
                    parsed_value = json.loads(value)
                except:
                    parsed_value = value

                table_data[table_name][row_index][col_name] = parsed_value

            else:
                cleaned_data[key] = value

        # ================= HELPER =================
        def normalize(name):
            return name.lower().replace(" ", "").replace("_", "")

        # ================= CALCULATE TABLE TOTAL =================
        for table_name, rows in table_data.items():

            row_list = list(rows.values())
            total = 0

            table_obj = None
            for stage in form.stage_set.all():
                for table in stage.table_set.all():
                    if table.name.strip() == table_name.strip():
                        table_obj = table
                        break

            if table_obj:
                total_columns = table_obj.tablecolumn_set.filter(is_total=True)

                for row in row_list:
                    for col in total_columns:
                        col_name = col.name.strip()

                        for key in row:
                            if key.strip() == col_name:
                                try:
                                    total += float(row.get(key) or 0)
                                except:
                                    pass

            table_name_clean = table_name.strip()

            cleaned_data[table_name_clean] = row_list
            cleaned_data[f"{table_name_clean}_total"] = round(total, 2)
        # ================= SAVE =================
        FormResponse.objects.create(
            form=form,
            ref_id=rfq_id,
            data=cleaned_data
        )

        return redirect(f"/form-builder/kanban/?process={form.process}")
# ============================================ Edit Response Column ==============================================
def edit_response(request, response_id):

    response = FormResponse.objects.get(id=response_id)
    form = response.form
    stages = Stage.objects.filter(form=form)

    data = response.data

    # ================= PREPARE OPTIONS =================
    for stage in stages:
        for field in stage.field_set.all():
            field.option_list = field.options.split(",") if field.options else []

    # ================= HELPER =================
    def normalize(name):
        return name.lower().replace(" ", "").replace("_", "")

    if request.method == "POST":

        updated_data = {}
        table_data = {}

        # ================= PARSE POST =================
        for key, value in request.POST.items():

            if key == "csrfmiddlewaretoken":
                continue

            if "__" in key:
                table, col, row = key.split("__")

                table_data.setdefault(table, {})
                table_data[table].setdefault(row, {})
                table_data[table][row][col] = value

            else:
                updated_data[key] = value

        # ================= PROCESS TABLES =================
        for table_name, rows in table_data.items():

            row_list = list(rows.values())
            total = 0

            # ✅ find correct table object
            table_obj = None
            for stage in stages:
                for table in stage.table_set.all():
                    if table.name.strip() == table_name.strip():
                        table_obj = table
                        break

            # ================= CALCULATE TOTAL =================
            if table_obj:
                total_columns = table_obj.tablecolumn_set.filter(is_total=True)

                total_col_names = [normalize(col.name) for col in total_columns]

                for row in row_list:
                    for key, val in row.items():
                        if normalize(key) in total_col_names:
                            try:
                                total += float(val or 0)
                            except:
                                pass

            # ================= SAVE TABLE =================
            table_name_clean = table_name.strip()

            updated_data[table_name_clean] = row_list
            updated_data[f"{table_name_clean}_total"] = round(total, 2)

        # ================= SAVE =================
        response.data = updated_data
        response.save()

        return redirect(
            f"/form-builder/kanban/?process={form.process}&ref_id={response.ref_id}"
        )

    return render(request, "form_builder/edit_response.html", {
        "form": form,
        "stages": stages,
        "data": data,
        "response": response
    })
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
    
    


# ======================================
# KANBAN VIEW
# ======================================

def kanban_view(request):

    processes = ["RFQ", "FEASABILITY", "COSTING"]

    selected_process = request.GET.get("process")
    selected_ref = request.GET.get("ref_id")

    forms = Form.objects.all()

    ref_list = None
    responses = None

    # ================= PROCESS CLICK =================
    if selected_process:

        ref_list = FormResponse.objects.filter(
            form__process=selected_process
        ).exclude(
            ref_id__isnull=True
        ).exclude(
            ref_id=""
        ).values_list("ref_id", flat=True).distinct()

    # ================= REF CLICK =================
    if selected_ref:

        responses = FormResponse.objects.filter(
            form__process=selected_process,
            ref_id=selected_ref
        ).prefetch_related(
            "form__stage_set__table_set__tablecolumn_set"
        )

        # 🔥 IMPORTANT: attach properties safely
        for response in responses:
            for stage in response.form.stage_set.all():

                tables = list(stage.table_set.all())  # ✅ force evaluation

                for table in tables:

                    total_cols = list(table.tablecolumn_set.filter(is_total=True))

                    table.has_total = len(total_cols) > 0
                    table.total_key = table.name.strip() + "_total"

    return render(request, "form_builder/kanban_builder.html", {
        "processes": processes,
        "forms": forms,
        "selected_process": selected_process,
        "selected_ref": selected_ref,
        "ref_list": ref_list,
        "responses": responses
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
        field_type=data.get("field_type", "text")
    )

    return JsonResponse({"status": "created"})



def delete_field(request, field_id):

    if request.method == "POST":
        Field.objects.filter(id=field_id).delete()
        return JsonResponse({"status": "deleted"})

    return JsonResponse({"status": "error"})



def edit_field(request, field_id):

    data = json.loads(request.body)

    field = Field.objects.get(id=field_id)
    field.label = data["label"]
    field.save()

    return JsonResponse({"status": "updated"})



import requests
from django.conf import settings
from django.core.cache import cache

@require_page_permission("can_costing_dashboard")
def dashboard_view(request):

    # ================= GET CURRENCY RATES =================
    API_KEY = settings.CURRENCY_API_KEY
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/INR"

    rates = cache.get("currency_rates")

    if not rates:
        try:
            res = requests.get(url)
            data = res.json()
            rates = data.get("conversion_rates", {})
            cache.set("currency_rates", rates, 3600)  # cache 1 hour
        except:
            rates = {}

    # ================= GET DATA =================
    responses = FormResponse.objects.filter(form__process="COSTING")

    company_data = {}

    for res in responses:

        company = res.ref_id

        if not company:
            continue

        data = res.data or {}

        tables = {}
        grand_total = 0

        # ✅ USE STORED TOTALS (IMPORTANT FIX)
        for key, value in data.items():

            if key.endswith("_total"):

                table_name = key.replace("_total", "")
                total = float(value or 0)

                tables[table_name] = total
                grand_total += total

        if tables:
            company_data[company] = {
                "tables": tables,
                "grand_total": round(grand_total, 2)
            }

    return render(request, "form_builder/dashboard.html", {
        "company_data": company_data,
        "rates": rates
    })
    
    
    
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json, random, string
from django.utils import timezone

@login_required
def verify_signature(request):

    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    password = data.get("password", "").strip()

    if not request.user.check_password(password):
        return JsonResponse({"ok": False, "error": "Invalid password"}, status=401)

    # ✅ generate unique code
    ref_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    return JsonResponse({
        "ok": True,
        "name": str(request.user),
        "time": timezone.now().strftime("%d %b %Y %H:%M"),
        "code": ref_code
    })