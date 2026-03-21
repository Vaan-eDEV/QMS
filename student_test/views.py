from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from qms_app.decorators import require_page_permission
from audit_log.models import AuditLog
from .models import Test, Question, StudentResult


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

    return render(request, "student_test/create_test.html")



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

            # MCQ
            option_a=request.POST.get("option_a"),
            option_b=request.POST.get("option_b"),
            option_c=request.POST.get("option_c"),
            option_d=request.POST.get("option_d"),
            correct_option=request.POST.get("correct_option"),

            # Fill
            correct_answer_text=request.POST.get("correct_answer_text"),

            # Yes / No
            correct_boolean=True if request.POST.get("correct_boolean") == "True" else
            False if request.POST.get("correct_boolean") == "False" else None
        )

        AuditLog.objects.create(
            user=request.user,
            module="Student Test",
            action="CREATE",
            object_id=f"Question: {request.POST.get('question_text')}",
            description="Question added to test"
        )

        return redirect("add_question", test.id)

    return render(request, "student_test/add_question.html", {
        "test": test
    })


# ===================================================================================================
# ==================================== TEST LIST (ADMIN + STUDENT) ==================================
# ===================================================================================================
@require_page_permission("can_tests")
@login_required
def test_list(request):

    if request.user.role not in ["student", "admin"] and not request.user.is_superuser:
        return redirect("dashboard")

    tests = Test.objects.all().order_by("-created_at")

    return render(request, "student_test/test_list.html", {
        "tests": tests
    })



# ====================================================================================================
# ========================================= Student Home =============================================
# ====================================================================================================
@require_page_permission("can_tests")
@login_required
def student_home(request):

    if request.user.role not in ["student", "admin"] and not request.user.is_superuser:
        return redirect("dashboard")

    tests = Test.objects.all()

    return render(request, "student_test/student_home.html", {
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

    is_student = request.user.role == "student"
    is_admin = request.user.role == "admin" or request.user.is_superuser

    if not (is_student or is_admin):
        return HttpResponseForbidden()

    #  Prevent student reattempt
    if is_student and StudentResult.objects.filter(
        student=request.user,
        test=test
    ).exists():
        return render(request, "student_test/already_attempted.html")

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
                    if submitted.strip().lower() == q.correct_answer_text.strip().lower():
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

        if is_student:
            StudentResult.objects.create(
                student=request.user,
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
                description=f"Student completed test with score {score}/{total}"
            )

        return render(request, "student_test/result.html", {
            "score": score,
            "total": total,
            "percentage": round(percentage, 2),
            "status": status,
            "pass_mark": test.pass_percentage,
            "is_admin_preview": is_admin
        })

    return render(request, "student_test/attempt_test.html", {
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

    return render(request, "student_test/result_list.html", {
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
                "is_correct": student_answer and
                              student_answer.strip().lower() ==
                              q.correct_answer_text.strip().lower(),
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

    return render(request, "student_test/result_detail.html", {
        "result": result,
        "detailed_results": detailed_results
    })
