from django.contrib import admin

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

# ======================================================
# INLINE: STAGE
# ======================================================

class StageInline(admin.TabularInline):

    model = Stage

    extra = 0

    ordering = ("order", "id")


# ======================================================
# INLINE: FIELD
# ======================================================

class FieldInline(admin.TabularInline):

    model = Field

    extra = 0

    ordering = ("order", "id")


# ======================================================
# INLINE: TABLE
# ======================================================

class TableInline(admin.TabularInline):

    model = Table

    extra = 0

    ordering = ("order", "id")


# ======================================================
# INLINE: TABLE COLUMN
# ======================================================

class TableColumnInline(admin.TabularInline):

    model = TableColumn

    extra = 0

    ordering = ("order", "id")


# ======================================================
# INLINE: TABLE ROW
# ======================================================

class TableRowInline(admin.TabularInline):

    model = TableRow

    extra = 0

    ordering = ("order", "id")


# ======================================================
# FORM
# ======================================================
@admin.register(Form)
class FormAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "process",
        "is_active",
        "created_at"
    )

    list_filter = (
        "process",
        "is_active"
    )

    search_fields = (
        "name",
    )

    ordering = (
        "-id",
    )

    inlines = [
        StageInline
    ]

    readonly_fields = (
        "form_structure_preview",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "process",
                    "created_by",
                    "is_active"
                )
            }
        ),
        (
            "FORM STRUCTURE PREVIEW",
            {
                "fields": (
                    "form_structure_preview",
                )
            }
        ),
    )

    # ==================================================
    # FORM PREVIEW
    # ==================================================

    def form_structure_preview(self, obj):

        if not obj:
            return "Save form first."

        html = ""

        stages = (
            obj.stage_set.all()
            .order_by("order", "id")
        )

        for stage in stages:

            html += f"""
            <div style="
                border:1px solid #ccc;
                padding:15px;
                margin-bottom:15px;
                border-radius:8px;
                background:#fafafa;
            ">
            """

            html += f"""
            <h2 style='color:#0d6efd;'>
                Stage: {stage.name}
            </h2>
            """

            # ==========================================
            # FIELDS
            # ==========================================

            fields = (
                stage.field_set.all()
                .order_by("order", "id")
            )

            if fields:

                html += """
                <h3>Fields</h3>
                <ul>
                """

                for field in fields:

                    html += f"""
                    <li>
                        <strong>{field.label}</strong>
                        ({field.field_type})
                    </li>
                    """

                html += "</ul>"

            # ==========================================
            # TABLES
            # ==========================================

            tables = (
                stage.table_set.all()
                .order_by("order", "id")
            )

            for table in tables:

                html += f"""
                <div style="
                    margin-top:15px;
                    padding:10px;
                    border:1px solid #ddd;
                    background:white;
                ">
                """

                html += f"""
                <h3>
                    Table: {table.name}
                </h3>
                """

                # ======================================
                # COLUMNS
                # ======================================

                columns = (
                    table.tablecolumn_set.all()
                    .order_by("order", "id")
                )

                html += """
                <strong>Columns:</strong>
                <ul>
                """

                for col in columns:

                    html += f"""
                    <li>
                        {col.name}
                        ({col.column_type})
                    </li>
                    """

                html += "</ul>"

                # ======================================
                # ROWS
                # ======================================

                rows = (
                    table.tablerow_set.all()
                    .order_by("order", "id")
                )

                html += """
                <strong>Rows:</strong>
                <ul>
                """

                for row in rows:

                    html += f"""
                    <li>
                        {row.name}
                    </li>
                    """

                html += "</ul>"

                html += "</div>"

            html += "</div>"

        from django.utils.safestring import mark_safe

        return mark_safe(html)

    form_structure_preview.short_description = (
        "Form Structure"
    )
# ======================================================
# STAGE
# ======================================================

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "form",
        "order"
    )

    list_editable = (
        "order",
    )

    ordering = (
        "form",
        "order",
        "id"
    )

    inlines = [
        FieldInline,
        TableInline
    ]


# ======================================================
# FIELD
# ======================================================

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "label",
        "field_type",
        "stage",
        "order"
    )

    list_editable = (
        "order",
    )

    ordering = (
        "stage",
        "order",
        "id"
    )

    list_filter = (
        "field_type",
    )

    search_fields = (
        "label",
    )


# ======================================================
# TABLE
# ======================================================

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "stage",
        "layout_type",
        "order"
    )

    list_editable = (
        "order",
    )

    ordering = (
        "stage",
        "order",
        "id"
    )

    inlines = [
        TableColumnInline,
        TableRowInline
    ]


# ======================================================
# TABLE COLUMN
# ======================================================

@admin.register(TableColumn)
class TableColumnAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "table",
        "column_type",
        "order",
        "is_total"
    )

    list_editable = (
        "order",
        "is_total"
    )

    ordering = (
        "table",
        "order",
        "id"
    )

    list_filter = (
        "column_type",
    )

    search_fields = (
        "name",
    )


# ======================================================
# TABLE ROW
# ======================================================

@admin.register(TableRow)
class TableRowAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "table",
        "order"
    )

    list_editable = (
        "order",
    )

    ordering = (
        "table",
        "order",
        "id"
    )

    search_fields = (
        "name",
    )


@admin.register(TableCellConfig)
class TableCellConfigAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "get_form_name",
        "table",
        "row",
        "column",
        "cell_type"
    )

    list_filter = (
        "cell_type",
    )

    search_fields = (
        "table__name",
        "row__name",
        "column__name",
        "table__stage__form__name",
    )

    ordering = (
        "table",
        "row",
        "column"
    )

    def get_form_name(self, obj):

        if obj.table and obj.table.stage:
            return obj.table.stage.form.name

        return "-"

    get_form_name.short_description = "Form"
# ======================================================
# FORM RESPONSE
# ======================================================

@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "ref_id",
        "company",
        "form",
        "status",
        "created_at"
    )

    search_fields = (
        "ref_id",
        "company"
    )

    list_filter = (
        "status",
        "form"
    )

    ordering = (
        "-id",
    )

    readonly_fields = (
        "created_at",
    )