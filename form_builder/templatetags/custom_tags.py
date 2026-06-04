from django import template
import os
import json
import ast

register = template.Library()


# ================================
# ✅ GET DICT VALUE
# ================================
@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


# ================================
# ✅ LOOP RANGE
# ================================
@register.filter
def times(number):
    try:
        return range(int(number))
    except:
        return range(0)


# ================================
# ✅ CLEAN FILE NAME
# ================================
@register.filter
def clean_filename(value):
    if not value:
        return ""

    name = os.path.basename(str(value))

    if "_" in name:
        name = name.split("_", 1)[1]

    return name.replace("%20", " ")


# ================================
# ✅ CHECK IF LIST (🔥 REQUIRED)
# ================================
@register.filter
def is_list(val):
    return isinstance(val, list)


# ================================
# ✅ IMAGE CHECK (🔥 FIXED)
# ================================
@register.filter
def is_image(val):
    if not val:
        return False

    # 🔥 HANDLE MULTIPLE FILES (LIST)
    if isinstance(val, list):
        return any(
            str(v).lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
            for v in val
        )

    # SINGLE VALUE
    val = str(val).lower()
    return val.endswith(('.jpg', '.jpeg', '.png', '.webp'))


# ================================
# ✅ FILE CHECK (OPTIONAL BUT USEFUL)
# ================================
@register.filter
def is_file(val):
    if not val:
        return False

    if isinstance(val, list):
        return any(
            str(v).lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt'))
            for v in val
        )

    val = str(val).lower()
    return val.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt'))







@register.filter(name="parse_json")
def parse_json(value):

    if not value:
        return {}

    # already dict
    if isinstance(value, dict):
        return value

    # normal JSON
    try:
        return json.loads(value)
    except:
        pass

    # python dict string
    try:
        return ast.literal_eval(value)
    except:
        pass

    return {}

@register.simple_tag
def get_row_id_by_name(table, row_name):

    row = table.tablerow_set.filter(
        name=row_name
    ).first()

    if row:
        return row.id

    # fallback first row
    first = table.tablerow_set.first()

    return first.id if first else ""

@register.filter
def has_total_column(columns):

    if not columns:
        return False

    return any(
        getattr(col, "is_total", False)
        for col in columns
    )

@register.filter
def get_row_value(rows, row_name):

    if not rows:
        return {}

    for row in rows:

        if row.get("row_name") == row_name:
            return row

    return {}

@register.filter
def get_row_by_id(rows, row_id):

    if not rows:
        return {}

    row_id = str(row_id).strip()

    for row in rows:

        saved_id = str(
            row.get("_row_id", "")
        ).strip()

        # exact string match
        if saved_id == row_id:
            return row

        # int/string compatibility
        try:
            if int(saved_id) == int(row_id):
                return row
        except:
            pass

    return {}