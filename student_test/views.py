from importlib.resources import files
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from urllib3 import request
from qms_app.decorators import require_page_permission
from audit_log.models import AuditLog
from .models import StudyMaterialProgress, Test, Question, StudentResult, Employee, EmployeeCertificate,StudyMaterial
import re
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime

@login_required
@require_page_permission("can_tests")
def upload_material(request, test_id):

    if request.user.role != "admin" and not request.user.is_superuser:
        return HttpResponseForbidden()

    test = get_object_or_404(Test, id=test_id)

    if request.method == "POST":
        title = request.POST.get("title")
        files = request.FILES.getlist("file")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        # 🔒 Validation
        if not title or not files:
            materials = test.materials.all().order_by("-id")
            for m in materials:
                m.full_url = request.build_absolute_uri(m.file.url)
            return render(request, "student_test/test/upload_material.html", {
                "test": test,
                "materials": materials,
                "error": "Title and file are required"
            })

        # 🔥 Convert datetime strings properly
        start_dt = parse_datetime(start_date) if start_date else None
        end_dt = parse_datetime(end_date) if end_date else None

        for f in files:
            StudyMaterial.objects.create(
                test=test,
                title=title,
                file=f,
                start_date=start_dt,
                end_date=end_dt,
                uploaded_by=request.user
            )

        return redirect("upload_material", test.id)

    # 🔥 GET REQUEST
    materials = test.materials.all().order_by("-id")

    # ✅ Add full URL for Google preview
    for m in materials:
        m.full_url = request.build_absolute_uri(m.file.url)

    return render(request, "student_test/test/upload_material.html", {
        "test": test,
        "materials": materials
    })




    
    

# =====================================================
# ADMIN SECTION
# =====================================================
@require_page_permission("can_tests")
@login_required
def create_test(request):

    if request.user.role != "admin" and not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == "POST":
        test = Test.objects.create(
            category=request.POST.get("category"),
            training_type = request.POST.get("training_type"),
            title=request.POST.get("title"),
            duration_minutes=request.POST.get("duration"),
            pass_percentage=request.POST.get("pass_percentage"),
            created_by=request.user
        )
        AuditLog.objects.create(
            user=request.user,
            module="Student Test",
            action="CREATE",
            object_id=f"Test: {test.title}",
            description="Test created"
        )
        return redirect("add_question", test.id)

    return render(request, "student_test/test/create_test.html")



#===========================================================================================================
#================================================= Delete Test =============================================
#===========================================================================================================
@require_page_permission("can_tests")
@login_required
def delete_test(request, test_id):

    if request.user.role != "admin" and not request.user.is_superuser:
        return HttpResponseForbidden()

    test = get_object_or_404(Test, id=test_id)

    if request.method == "POST":
        AuditLog.objects.create(
            user=request.user,
            module="Student Test",
            action="DELETE",
            object_id=f"Test: {test.title}",
            description="Test deleted"
        )
        test.delete()

    return redirect("test_list")



#==========================================================================================================
#================================================ Add question ============================================
#==========================================================================================================

@require_page_permission("can_tests")
@login_required
def add_question(request, test_id):

    if request.user.role != "admin" and not request.user.is_superuser:
        return HttpResponseForbidden()

    test = get_object_or_404(Test, id=test_id)

    if request.method == "POST":

        question_type = request.POST.get("question_type")

        Question.objects.create(
            test=test,
            question_text=request.POST.get("question_text"),
            question_type=question_type,

            # -------- MCQ TEXT --------
            option_a=request.POST.get("option_a"),
            option_b=request.POST.get("option_b"),
            option_c=request.POST.get("option_c"),
            option_d=request.POST.get("option_d"),

            # 🔥 -------- MCQ IMAGES --------
            option_a_image=request.FILES.get("option_a_image"),
            option_b_image=request.FILES.get("option_b_image"),
            option_c_image=request.FILES.get("option_c_image"),
            option_d_image=request.FILES.get("option_d_image"),

            correct_option=request.POST.get("correct_option"),

            # -------- FILL --------
            correct_answer_text=request.POST.get("correct_answer_text"),

            # -------- YES / NO --------
            correct_boolean=(
                True if request.POST.get("correct_boolean") == "True"
                else False if request.POST.get("correct_boolean") == "False"
                else None
            )
        )

        AuditLog.objects.create(
            user=request.user,
            module="Student Test",
            action="CREATE",
            model_name ="Question",
            object_id=f"Question: {request.POST.get('question_text')}",
            description="Question added to test"
        )

        return redirect("add_question", test.id)

    return render(request, "student_test/test/add_question.html", {
        "test": test
    })
# ===================================================================================================
# ==================================== TEST LIST (ADMIN + STUDENT) ==================================
# ===================================================================================================
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from qms_app.decorators import require_page_permission

from .models import (
    Test,
    StudentResult,
    StudyMaterialProgress
)


@require_page_permission("can_tests")
@login_required
def test_list(request):

    # =========================================
    # ACCESS CHECK
    # =========================================

    if (
        request.user.role not in ["student", "admin"]
        and not request.user.is_superuser
    ):
        return redirect("dashboard")

    # =========================================
    # ALL TESTS
    # =========================================

    tests = (
        Test.objects
        .all()
        .prefetch_related(
            "questions",
            "materials"
        )
        .order_by("-created_at")
    )

    # =========================================
    # ATTEMPTED TESTS
    # =========================================

    attempted_tests = []

    if request.user.role == "student":

        attempted_tests = (
            StudentResult.objects
            .filter(student=request.user)
            .values_list(
                "test_id",
                flat=True
            )
        )

    # =========================================
    # ADMIN → SHOW ALL TESTS
    # =========================================

    if (
        request.user.role == "admin"
        or request.user.is_superuser
    ):

        visible_tests = tests
        locked_tests = []

    # =========================================
    # STUDENT LMS LOGIC
    # =========================================

    else:

        visible_tests = []
        locked_tests = []

        for test in tests:

            materials = test.materials.all()

            # =================================
            # NO MATERIALS
            # =================================

            if not materials.exists():

                visible_tests.append(test)
                continue

            # =================================
            # CHECK COMPLETION
            # =================================

            all_completed = True

            for material in materials:

                completed = (
                    StudyMaterialProgress.objects
                    .filter(
                        user=request.user,
                        material=material,
                        completed=True
                    )
                    .exists()
                )

                if not completed:

                    all_completed = False
                    break

            # =================================
            # ADD TO LIST
            # =================================

            if all_completed:

                visible_tests.append(test)

            else:

                locked_tests.append(test)

    # =========================================
    # RENDER
    # =========================================

    return render(
        request,
        "student_test/test/test_list.html",
        {
            "tests": visible_tests,
            "locked_tests": locked_tests,
            "attempted_tests": attempted_tests,
            "now": timezone.now(),
        }
    )


@login_required
def edit_test(request, test_id):

    test = Test.objects.get(id=test_id)

    questions = test.questions.all()

    return render(
        request,
        "student_test/test/edit_test.html",
        {
            "test": test,
            "questions": questions
        }
    )

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Question


# =========================================
# EDIT QUESTION
# =========================================

@login_required
def edit_question(request, question_id):

    question = get_object_or_404(
        Question,
        id=question_id
    )

    if request.method == "POST":

        question.question_text = request.POST.get(
            "question_text"
        )

        question.option_a = request.POST.get(
            "option_a"
        )

        question.option_b = request.POST.get(
            "option_b"
        )

        question.option_c = request.POST.get(
            "option_c"
        )

        question.option_d = request.POST.get(
            "option_d"
        )

        question.correct_option = request.POST.get(
            "correct_option"
        )

        question.save()

        return redirect(
            "edit_test",
            question.test.id
        )

    return render(
        request,
        "student_test/test/edit_question.html",
        {
            "question": question
        }
    )


# =========================================
# DELETE QUESTION
# =========================================

@login_required
def delete_question(request, question_id):

    question = get_object_or_404(
        Question,
        id=question_id
    )

    test_id = question.test.id

    question.delete()

    return redirect(
        "edit_test",
        test_id
    )
@login_required
def study_material_view(request, test_id):

    test = get_object_or_404(Test, id=test_id)

    # 🔥 optimize query
    materials = test.materials.all().order_by("id")

    progress_map = {}
    all_completed = True

    for m in materials:

        # 🔥 create or get progress
        progress, _ = StudyMaterialProgress.objects.get_or_create(
            user=request.user,
            material=m
        )

        progress_map[m.id] = progress

        # 🔥 check completion
        if not progress.completed:
            all_completed = False

        # 🔥 VERY IMPORTANT (for preview)
        m.full_url = request.build_absolute_uri(m.file.url)

        # 🔥 OPTIONAL: deadline check
        if m.end_date and m.end_date < timezone.now():
            m.is_expired = True
        else:
            m.is_expired = False

    return render(request, "student_test/test/study_material.html", {
        "test": test,
        "materials": materials,
        "progress_map": progress_map,
        "all_completed": all_completed
    })



from django.shortcuts import get_object_or_404

@login_required
def delete_material(request, material_id):

    material = get_object_or_404(
        StudyMaterial,
        id=material_id
    )

    test_id = material.test.id

    # DELETE FILE FROM STORAGE
    if material.file:
        material.file.delete(save=False)

    material.delete()

    return redirect(
        "upload_material",
        test_id
    )
@login_required
def mark_material_complete(request, material_id):

    material = get_object_or_404(StudyMaterial, id=material_id)

    progress, _ = StudyMaterialProgress.objects.get_or_create(
        user=request.user,
        material=material
    )

    progress.completed = True
    progress.save()

    return redirect("study_material_view", material.test.id)
# ====================================================================================================
# ========================================= Student Home =============================================
# ====================================================================================================
@require_page_permission("can_tests")
@login_required
def student_home(request):

    if request.user.role not in ["student", "admin"] and not request.user.is_superuser:
        return redirect("dashboard")

    tests = Test.objects.all()

    return render(request, "student_test/test/student_home.html", {
        "tests": tests
    })


# =====================================================
# ATTEMPT TEST (MCQ + FILL + BOOL SUPPORTED)
# =====================================================
@require_page_permission("can_tests")
@login_required
def attempt_test(request, test_id):

    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()

    is_student = request.user.role in ["student", "user"]
    is_admin = request.user.role == "admin" or request.user.is_superuser

    # 🔒 Access control
    if not (is_student or is_admin):
        return HttpResponseForbidden()

    # 🚫 Prevent reattempt (students only)
    if is_student and StudentResult.objects.filter(
        student=request.user,
        test=test
    ).exists():
        return render(request, "student_test/test/already_attempted.html")

    if request.method == "POST":

        score = 0
        answers = {}

        for q in questions:
            submitted = request.POST.get(f"question_{q.id}")
            answers[str(q.id)] = submitted

            # ---------- MCQ ----------
            if q.question_type == "MCQ":
                if submitted == q.correct_option:
                    score += 1

            # ---------- FILL ----------

            elif q.question_type == "FILL":

                if submitted and q.correct_answer_text:



                    # =========================
                    # CLEAN STUDENT ANSWER
                    # =========================

                    student_answer = re.sub(
                        r'[^a-z0-9]',
                        '',
                        str(submitted)
                        .strip()
                        .lower()
                    )

                    # =========================
                    # CLEAN CORRECT ANSWER
                    # =========================

                    correct_answer = re.sub(
                        r'[^a-z0-9]',
                        '',
                        str(q.correct_answer_text)
                        .strip()
                        .lower()
                    )

                    # =========================
                    # COMPARE
                    # =========================

                    if student_answer == correct_answer:

                        score += 1

            # ---------- YES / NO ----------
            elif q.question_type == "BOOL":
                if submitted is not None:
                    if (submitted == "True" and q.correct_boolean) or \
                       (submitted == "False" and not q.correct_boolean):
                        score += 1

        total = questions.count()
        percentage = (score / total) * 100 if total else 0
        status = "PASS" if percentage >= test.pass_percentage else "FAIL"

        # 🔥 Proper employee mapping (NO try/except)
        employee = getattr(request.user, "employee_profile", None)

        # ✅ Save result only for students
        if is_student:
            StudentResult.objects.create(
                student=request.user,
                employee=employee,
                test=test,
                score=score,
                total=total,
                percentage=round(percentage, 2),
                status=status,
                answers=answers
            )

            AuditLog.objects.create(
                user=request.user,
                module="Student Test",
                action="COMPLETE",
                object_id=f"Result: {request.user.email} - {test.title}",
                description=f"Score: {score}/{total} ({round(percentage, 2)}%)"
            )

        return render(request, "student_test/test/result.html", {
            "score": score,
            "total": total,
            "percentage": round(percentage, 2),
            "status": status,
            "pass_mark": test.pass_percentage,
            "is_admin_preview": is_admin
        })

    return render(request, "student_test/test/attempt_test.html", {
        "test": test,
        "questions": questions,
        "duration": test.duration_minutes,
        "is_admin_preview": is_admin
    })

# =====================================================
# RESULT LIST (ADMIN ONLY)
# =====================================================

@require_page_permission("can_tests")
@login_required
def result_list(request):

    if request.user.role != "admin" and not request.user.is_superuser:
        return redirect("dashboard")

    results = StudentResult.objects.select_related(
        "student", "test"
    ).order_by("-completed_at")

    return render(request, "student_test/test/result_list.html", {
        "results": results
    })

#=======================================================================================================
#============================================ Delete Result ============================================
#=======================================================================================================

@login_required
def delete_result(request, result_id):

    if request.user.role != "admin" and not request.user.is_superuser:
        return HttpResponseForbidden()

    result = get_object_or_404(StudentResult, id=result_id)

    if request.method == "POST":
        AuditLog.objects.create(
            user=request.user,
            module="Student Test",
            action="DELETE",
            object_id=f"Result: {result.student.email} - {result.test.title}",
            description="Student result deleted"
        )
        result.delete()

    return redirect("result_list")

# =====================================================
# RESULT DETAIL (MCQ + FILL + BOOL DISPLAY)
# =====================================================

@login_required
def result_detail(request, result_id):

    if request.user.role != "admin" and not request.user.is_superuser:
        return redirect("dashboard")

    result = get_object_or_404(StudentResult, id=result_id)
    questions = result.test.questions.all()

    detailed_results = []

    for q in questions:

        student_answer = result.answers.get(str(q.id))

        # -------- MCQ --------
        if q.question_type == "MCQ":

            option_map = {
                "A": q.option_a,
                "B": q.option_b,
                "C": q.option_c,
                "D": q.option_d,
            }

            detailed_results.append({
                "question_obj": q,
                "student_answer": option_map.get(student_answer, "Not Answered"),
                "correct_answer": option_map.get(q.correct_option),
                "is_correct": student_answer == q.correct_option,
                "type": "MCQ"
            })

        # -------- FILL --------
        elif q.question_type == "FILL":

            detailed_results.append({
                "question_obj": q,
                "student_answer": student_answer or "Not Answered",
                "correct_answer": q.correct_answer_text,
                "is_correct": (

                    re.sub(
                        r'[^a-z0-9]',
                        '',
                        str(student_answer)
                        .strip()
                        .lower()
                    )

                    ==

                    re.sub(
                        r'[^a-z0-9]',
                        '',
                        str(q.correct_answer_text)
                        .strip()
                        .lower()
                    )
                ),
                "type": "FILL"
            })

        # -------- YES / NO --------
        elif q.question_type == "BOOL":

            correct_text = "Yes" if q.correct_boolean else "No"

            detailed_results.append({
                "question_obj": q,
                "student_answer": "Yes" if student_answer == "True"
                                   else "No" if student_answer == "False"
                                   else "Not Answered",
                "correct_answer": correct_text,
                "is_correct": (
                    (student_answer == "True" and q.correct_boolean) or
                    (student_answer == "False" and not q.correct_boolean)
                ),
                "type": "BOOL"
            })

    return render(request, "student_test/test/result_detail.html", {
        "result": result,
        "detailed_results": detailed_results
    })
# ==================================================== employee certificate list (ADMIN ONLY) ============================================

# ================================
# CREATE EMPLOYEE
# ================================
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Employee, EmployeeCertificate


@login_required
def create_employee(request):

    User = get_user_model()
    users = User.objects.all()

    if request.method == "POST":

        user_id = request.POST.get("user_id")
        user = User.objects.filter(id=user_id).first()

        emp = Employee.objects.create(

            # ================= BASIC =================
            emp_id=request.POST.get("emp_id"),
            name=request.POST.get("name"),
            email=user.email if user else request.POST.get("email"),
            user=user,
            profile_image=request.FILES.get("profile_image"),

            # ================= PERSONAL =================
            dob=request.POST.get("dob") or None,
            gender=request.POST.get("gender"),
            marital_status=request.POST.get("marital_status"),
            nationality=request.POST.get("nationality"),
            blood_group=request.POST.get("blood_group"),

            # ================= GOVT IDS =================
            pan_number=request.POST.get("pan_number"),
            aadhar_number=request.POST.get("aadhar_number"),
            uan_number=request.POST.get("uan_number"),
            pf_number=request.POST.get("pf_number"),
            esi_number=request.POST.get("esi_number"),

            # ================= CONTACT =================
            mobile_number=request.POST.get("mobile_number"),
            alternate_number=request.POST.get("alternate_number"),

            # ================= ADDRESS =================
            current_address=request.POST.get("current_address"),
            permanent_address=request.POST.get("permanent_address"),

            # ================= EMPLOYMENT =================
            department=request.POST.get("department"),
            role=request.POST.get("role"),
            date_of_joining=request.POST.get("doj") or None,
            employment_type=request.POST.get("employment_type"),
            work_location=request.POST.get("work_location"),
            shift=request.POST.get("shift"),
            cost_center=request.POST.get("cost_center"),
            reporting_manager=request.POST.get("reporting_manager"),

            # ================= BANK =================
            bank_name=request.POST.get("bank_name"),
            branch_name=request.POST.get("branch_name"),
            account_number=request.POST.get("account_number"),
            account_type=request.POST.get("account_type"),
            ifsc_code=request.POST.get("ifsc_code"),

            # ================= SALARY =================
            pay_grade=request.POST.get("pay_grade"),
            basic_salary=request.POST.get("basic_salary") or None,
            effective_date=request.POST.get("effective_date") or None,
            payment_cycle=request.POST.get("payment_cycle"),

            # ================= EMERGENCY =================
            emergency_contact_name=request.POST.get("emergency_contact_name"),
            emergency_relationship=request.POST.get("emergency_relationship"),
            emergency_mobile=request.POST.get("emergency_mobile"),
            emergency_alternate=request.POST.get("emergency_alternate"),
            emergency_address=request.POST.get("emergency_address"),

            # ================= EXTRA =================
            qualification=request.POST.get("qualification"),
            skills=request.POST.get("skills"),
            experience=request.POST.get("experience"),
            notes=request.POST.get("notes"),
            

            status="PENDING"
        )

        # ================= CERTIFICATES =================
        import os
        from docx2pdf import convert

        files = request.FILES.getlist("certificates")

        for f in files:
            cert = EmployeeCertificate.objects.create(
                employee=emp,
                certificate_name=f.name,
                file=f
            )

            if f.name.lower().endswith(".docx"):
                try:
                    input_path = cert.file.path
                    output_path = input_path.replace(".docx", ".pdf")

                    convert(input_path, output_path)

            
                    cert.pdf_file.name = cert.file.name.replace(".docx", ".pdf")
                    cert.save()

                except Exception as e:
                    print("PDF conversion error:", e)
        return redirect("employee_approval_list")

    return render(request, "student_test/employee/create.html", {
        "users": users
    })





from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from .models import Employee, EmployeeCertificate


@login_required
def edit_employee(request, emp_id):

    emp = get_object_or_404(Employee, id=emp_id)
    User = get_user_model()
    users = User.objects.all()

    if request.method == "POST":

        user_id = request.POST.get("user_id")
        user = User.objects.filter(id=user_id).first() if user_id else None

        # ================= BASIC =================
        emp.name = request.POST.get("name")
        emp.email = user.email if user else request.POST.get("email")
        emp.user = user

        # ================= PERSONAL =================
        emp.dob = request.POST.get("dob") or None
        emp.gender = request.POST.get("gender")
        emp.marital_status = request.POST.get("marital_status")
        emp.nationality = request.POST.get("nationality")
        emp.blood_group = request.POST.get("blood_group")

        # ================= GOVT IDS =================
        emp.pan_number = request.POST.get("pan_number")
        emp.aadhar_number = request.POST.get("aadhar_number")
        emp.uan_number = request.POST.get("uan_number")
        emp.pf_number = request.POST.get("pf_number")
        emp.esi_number = request.POST.get("esi_number")

        # ================= CONTACT =================
        emp.mobile_number = request.POST.get("mobile_number")
        emp.alternate_number = request.POST.get("alternate_number")

        # ================= ADDRESS =================
        emp.current_address = request.POST.get("current_address")
        emp.permanent_address = request.POST.get("permanent_address")

        # ================= EMPLOYMENT =================
        emp.department = request.POST.get("department")
        emp.role = request.POST.get("role")
        emp.date_of_joining = request.POST.get("doj") or None
        emp.employment_type = request.POST.get("employment_type")
        emp.work_location = request.POST.get("work_location")
        emp.shift = request.POST.get("shift")
        emp.cost_center = request.POST.get("cost_center")
        emp.reporting_manager = request.POST.get("reporting_manager")

        # ================= BANK =================
        emp.bank_name = request.POST.get("bank_name")
        emp.branch_name = request.POST.get("branch_name")
        emp.account_number = request.POST.get("account_number")
        emp.account_type = request.POST.get("account_type")
        emp.ifsc_code = request.POST.get("ifsc_code")

        # ================= SALARY =================
        emp.pay_grade = request.POST.get("pay_grade")
        emp.basic_salary = request.POST.get("basic_salary") or None
        emp.effective_date = request.POST.get("effective_date") or None
        emp.payment_cycle = request.POST.get("payment_cycle")

        # ================= EMERGENCY =================
        emp.emergency_contact_name = request.POST.get("emergency_contact_name")
        emp.emergency_relationship = request.POST.get("emergency_relationship")
        emp.emergency_mobile = request.POST.get("emergency_mobile")
        emp.emergency_alternate = request.POST.get("emergency_alternate")
        emp.emergency_address = request.POST.get("emergency_address")

        # ================= EXTRA =================
        emp.qualification = request.POST.get("qualification")
        emp.skills = request.POST.get("skills")
        emp.experience = request.POST.get("experience")
        emp.notes = request.POST.get("notes")
        if request.FILES.get("profile_image"):
            emp.profile_image = request.FILES.get("profile_image")

        emp.save()

        # ================= ADD NEW CERTIFICATES =================
        from docx2pdf import convert

        files = request.FILES.getlist("certificates")

        for f in files:
            cert = EmployeeCertificate.objects.create(
                employee=emp,
                certificate_name=f.name,
                file=f
            )

            if f.name.lower().endswith(".docx"):
                try:
                    input_path = cert.file.path
                    output_path = input_path.replace(".docx", ".pdf")

                    convert(input_path, output_path)

                    cert.pdf_file.name = cert.file.name.replace(".docx", ".pdf")
                    cert.save()

                except Exception as e:
                    print("PDF conversion error:", e)

        return redirect("employee_detail", emp.id)

    return render(request, "student_test/employee/edit.html", {
        "emp": emp,
        "users": users
    })
    
    
@login_required
def delete_certificate(request, cert_id):

    cert = get_object_or_404(EmployeeCertificate, id=cert_id)
    emp_id = cert.employee.id

    if request.method == "POST":
        cert.delete()
        return redirect("edit_employee", emp_id=emp_id)

    # ❌ If someone hits URL directly
    return redirect("edit_employee", emp_id=emp_id)

  
@login_required
def employee_approval_list(request):
    employees = Employee.objects.filter(status="PENDING")
    return render(request, "student_test/employee/approval_list.html", {
        "employees": employees
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from datetime import datetime
from django.core.files import File
from .models import Employee, EmployeeCertificate


# =========================================================
# 🔧 HELPER: UPDATE EMPLOYEE
# =========================================================
def update_employee_from_request(emp, request):

    User = get_user_model()

    user_id = request.POST.get("user_id")
    user = User.objects.filter(id=user_id).first() if user_id else None

    # ================= BASIC =================
    emp.name = request.POST.get("name") or emp.name
    emp.email = user.email if user and user.email else request.POST.get("email") or emp.email
    emp.user = user if user else emp.user

    # ================= PERSONAL =================
    dob = request.POST.get("dob")
    emp.dob = datetime.strptime(dob, "%Y-%m-%d") if dob else emp.dob

    emp.gender = request.POST.get("gender") or emp.gender
    emp.marital_status = request.POST.get("marital_status") or emp.marital_status
    emp.nationality = request.POST.get("nationality") or emp.nationality
    emp.blood_group = request.POST.get("blood_group") or emp.blood_group

    # ================= GOVT IDS =================
    emp.pan_number = request.POST.get("pan_number") or emp.pan_number
    emp.aadhar_number = request.POST.get("aadhar_number") or emp.aadhar_number
    emp.uan_number = request.POST.get("uan_number") or emp.uan_number
    emp.pf_number = request.POST.get("pf_number") or emp.pf_number
    emp.esi_number = request.POST.get("esi_number") or emp.esi_number

    # ================= CONTACT =================
    emp.mobile_number = request.POST.get("mobile_number") or emp.mobile_number
    emp.alternate_number = request.POST.get("alternate_number") or emp.alternate_number

    # ================= ADDRESS =================
    emp.current_address = request.POST.get("current_address") or emp.current_address
    emp.permanent_address = request.POST.get("permanent_address") or emp.permanent_address

    # ================= EMPLOYMENT =================
    emp.department = request.POST.get("department") or emp.department
    emp.role = request.POST.get("role") or emp.role

    doj = request.POST.get("doj")
    emp.date_of_joining = datetime.strptime(doj, "%Y-%m-%d") if doj else emp.date_of_joining

    emp.employment_type = request.POST.get("employment_type") or emp.employment_type
    emp.work_location = request.POST.get("work_location") or emp.work_location
    emp.shift = request.POST.get("shift") or emp.shift
    emp.cost_center = request.POST.get("cost_center") or emp.cost_center
    emp.reporting_manager = request.POST.get("reporting_manager") or emp.reporting_manager

    # ================= BANK =================
    emp.bank_name = request.POST.get("bank_name") or emp.bank_name
    emp.branch_name = request.POST.get("branch_name") or emp.branch_name
    emp.account_number = request.POST.get("account_number") or emp.account_number
    emp.account_type = request.POST.get("account_type") or emp.account_type
    emp.ifsc_code = request.POST.get("ifsc_code") or emp.ifsc_code

    # ================= SALARY =================
    emp.pay_grade = request.POST.get("pay_grade") or emp.pay_grade
    emp.basic_salary = request.POST.get("basic_salary") or emp.basic_salary

    eff = request.POST.get("effective_date")
    emp.effective_date = datetime.strptime(eff, "%Y-%m-%d") if eff else emp.effective_date

    emp.payment_cycle = request.POST.get("payment_cycle") or emp.payment_cycle

    # ================= EMERGENCY =================
    emp.emergency_contact_name = request.POST.get("emergency_contact_name") or emp.emergency_contact_name
    emp.emergency_relationship = request.POST.get("emergency_relationship") or emp.emergency_relationship
    emp.emergency_mobile = request.POST.get("emergency_mobile") or emp.emergency_mobile
    emp.emergency_alternate = request.POST.get("emergency_alternate") or emp.emergency_alternate
    emp.emergency_address = request.POST.get("emergency_address") or emp.emergency_address

    # ================= EXTRA =================
    emp.qualification = request.POST.get("qualification") or emp.qualification
    emp.skills = request.POST.get("skills") or emp.skills
    emp.experience = request.POST.get("experience") or emp.experience
    emp.notes = request.POST.get("notes") or emp.notes
    if request.FILES.get("profile_image"):
        emp.profile_image = request.FILES.get("profile_image")

    emp.save()
    return emp


# =========================================================
# 📄 HELPER: HANDLE CERTIFICATES
# =========================================================
def handle_certificates(emp, request):

    from docx2pdf import convert

    files = request.FILES.getlist("certificates")

    for f in files:

        cert = EmployeeCertificate.objects.create(
            employee=emp,
            certificate_name=f.name,
            file=f
        )

        # ===== DOCX → PDF =====
        if f.name.lower().endswith(".docx"):
            try:
                input_path = cert.file.path
                output_path = input_path.replace(".docx", ".pdf")

                convert(input_path, output_path)

                with open(output_path, "rb") as pdf:
                    cert.pdf_file.save(
                        f.name.replace(".docx", ".pdf"),
                        File(pdf),
                        save=True
                    )

            except Exception as e:
                print("PDF conversion error:", e)

        # ===== IMAGE / PDF =====
        # No processing needed (stored directly)


# =========================================================
# 👁️ EMPLOYEE APPROVAL + EDIT PAGE
# =========================================================
@login_required
def employee_detail_approval(request, emp_id):

    emp = get_object_or_404(Employee, id=emp_id)

    if request.method == "POST":

        update_employee_from_request(emp, request)
        handle_certificates(emp, request)

        messages.success(request, "Employee updated successfully")

        return redirect("employee_detail_approval", emp.id)

    return render(request, "student_test/employee/employee_detail_approval.html", {
        "emp": emp
    })


# =========================================================
# 🗑 DELETE CERTIFICATE
# =========================================================
@login_required
def delete_certificates(request, cert_id):

    cert = get_object_or_404(EmployeeCertificate, id=cert_id)
    emp_id = cert.employee.id

    if request.method == "POST":
        cert.delete()
        messages.success(request, "Certificate deleted successfully")

    return redirect("employee_detail_approval", emp_id)
    
    
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Employee


@login_required
def approve_employee(request, emp_id):

    emp = get_object_or_404(Employee, id=emp_id)
    User = get_user_model()

    # ✅ Match by email (CORRECT LOGIC)
    user = User.objects.filter(email=emp.email).first()

    if user:
        emp.user = user
        message = "Employee approved and linked to user."
    else:
        message = "Employee approved, but no matching user found."

    emp.status = "APPROVED"
    emp.save()

    messages.success(request, message)

    return redirect("employee_approval_list")
# ================================
# EMPLOYEE LIST
# ================================
@login_required
def employee_list(request):

    employees = Employee.objects.filter(status="APPROVED").order_by("-created_at")

    return render(request, "student_test/employee/list.html", {
        "employees": employees
    })
    
    
# ================================
# EMPLOYEE DETAIL
# ================================
@login_required
def employee_detail(request, emp_id):

    emp = get_object_or_404(Employee, id=emp_id)

    return render(request, "student_test/employee/detail.html", {
        "emp": emp
    })
    
# ================================
# ADD CERTIFICATE
# ================================
@login_required
def add_certificate(request, emp_id):

    emp = get_object_or_404(Employee, id=emp_id)

    if request.method == "POST":

        files = request.FILES.getlist("certificates")

        for f in files:
            EmployeeCertificate.objects.create(
                employee=emp,
                certificate_name=f.name,
                file=f
            )

        return redirect("employee_detail", emp.id)

    return redirect("employee_detail", emp.id)




@login_required
def employee_dashboard(request):

    # 🔥 Always take logged-in user's employee
    emp = getattr(request.user, "employee_profile", None)

    # 🚫 If no employee linked
    if not emp:
        return render(request, "student_test/employee/no_profile.html")

    # 📊 Data
    tests = Test.objects.all()
    results = StudentResult.objects.filter(employee=emp)

    completed_tests = results.values_list("test_id", flat=True)

    total = tests.count()
    completed = results.count()
    pending = total - completed

    progress = int((completed / total) * 100) if total else 0

    return render(request, "student_test/employee_detail.html", {
        "emp": emp,
        "tests": tests,
        "results": results,
        "completed_tests": completed_tests,
        "total": total,
        "completed": completed,
        "pending": pending,
        "progress": progress
    })
    
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Prefetch
from .models import (
    Employee,
    Test,
    StudentResult,
    StudyMaterial,
    StudyMaterialProgress
)


@login_required
def my_profile(request):

    # ======================================================
    # 🔥 SAFE EMPLOYEE FETCH (PRODUCTION)
    # ======================================================
    emp = Employee.objects.filter(user=request.user).first()

    # fallback (important if linking missed)
    if not emp:
        emp = Employee.objects.filter(email=request.user.email).first()

        if emp:
            emp.user = request.user
            emp.save()

    # 🚫 No employee at all
    if not emp:
        return render(request, "student_test/employee/no_profile.html")

    # 🚫 Not approved
    if emp.status != "APPROVED":
        return render(request, "student_test/employee/pending_approval.html", {
            "emp": emp
        })

    # ======================================================
    # 📊 TEST DATA
    # ======================================================
    tests = Test.objects.all()

    results = StudentResult.objects.filter(
        employee=emp
    ).select_related("test")

    total = tests.count()
    completed = results.count()
    pending = max(total - completed, 0)
    progress = int((completed / total) * 100) if total else 0

    # ======================================================
    # 📄 CERTIFICATES
    # ======================================================
    certificates = emp.certificates.all().order_by("-uploaded_at")

    # ======================================================
    # 📚 STUDY MATERIALS (OPTIMIZED)
    # ======================================================
    materials = StudyMaterial.objects.select_related("test").order_by("-id")

    # fetch all progress in one query
    progress_qs = StudyMaterialProgress.objects.filter(user=request.user)
    progress_map = {p.material_id: p for p in progress_qs}

    completed_materials = sum(1 for p in progress_map.values() if p.completed)

    total_materials = materials.count()
    material_progress = int(
        (completed_materials / total_materials) * 100
    ) if total_materials else 0

    # ======================================================
    # 🎯 FINAL RESPONSE
    # ======================================================
    return render(request, "student_test/employee/my_profile.html", {

        "emp": emp,

        # test stats
        "results": results,
        "total": total,
        "completed": completed,
        "pending": pending,
        "progress": progress,

        # certificates
        "certificates": certificates,

        # materials
        "materials": materials,
        "progress_map": progress_map,
        "material_progress": material_progress,
    })