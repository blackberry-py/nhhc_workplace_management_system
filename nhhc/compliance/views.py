from django.shortcuts import render

# Create your views here.


def create_contract(request):
    pass


def employee_report_export(request):
    employees = Employee.objects.all().values()
    employee_json = json.dumps(list(employees), cls=DjangoJSONEncoder)
    return HttpResponse(content=employee_json, status=200)


def generate_report(requst):
    sessionDataCSV = f"TTPUpload{now.to_date_string()}.csv"
    sessions = employee_report_export()
    with open(sessionDataCSV, "w+") as csv_output_file_pointer:
        csv_writer = csv.writer(csv_output_file_pointer)
        # Writing headers of CSV file
        header = (
            "SSN",
            "FirstName",
            "LastName",
            "MiddleName",
            "DateOfBirth",
            "Gender",
            "EmailAddress",
            "Ethnicity",
            "Race",
            "Qualifications",
            "LanguageCode",
            "ContractNumber",
            "EmployeeTitle",
            "TitleStartDate",
            "CaseLoad",
            "Prior to 10/01/2021",
            "TrainingDate",
            "InitialCBC",
            "MostCurrentCBC",
        )
        csv_writer.writerow(header)
        for employee in employees:
            row_data = (
                employee["social_security"],
                employee["first_name"],
                employee["last_name"],
                employee["middle_name"],
                employee["date_of_birth"],
                employee["gender"],
                employee["ethnicity"],
                employee["race"],
                employee["qualifications"],
                employee["language"],
                employee["contract"],
                employee["title"],
                employee["hire_date"],
                "Find Out What Caseload Is" "False",
                " ",
                employee["initial_idph_background_check_completion_date"],
                employee["current_idph_background_check_completion_date"],
            )
            csv_writer.writerow(row_data)
            os.open(sessionDataCSV, os.O_NONBLOCK)
