import pandas as pd
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection


@authentication_classes([])  # Disable authentication
@permission_classes([])
class ReportAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    def has_permission(self, user):
        # Allow only users in a specific group or with a specific attribute
        allowed_group_name = 'LSM'
        if user.is_superuser:
            return True
        else:
            return True  # user.groups.filter(name=allowed_group_name).exists()

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        query1 = """
                SELECT 
                d.district_name, 
                count(CASE WHEN a.registration_for = 'Producer' THEN b.id else NULL END) as Producer,
                count(CASE WHEN a.registration_for = 'Consumer' THEN b.id else NULL END) as Consumer,
                count(CASE WHEN a.registration_for = 'Collector' THEN b.id else NULL END) as Collector,
                count(CASE WHEN a.registration_for = 'Recycler' THEN b.id else NULL END) as Recycler,
                count(b.id) as Total
                FROM 
                tbl_districts d
                LEFT JOIN pmc_api_businessprofile g on g.district_id = d.district_id
                LEFT JOIN public.pmc_api_applicantdetail a on a.id = g.applicant_id
                LEFT JOIN 
                    pmc_api_applicationsubmitted b ON a.id = b.applicant_id
                LEFT JOIN pmc_api_applicantfee f on a.id = f.applicant_id
                GROUP BY 1
                -- HAVING count(b.id) > 1
                ORDER BY 1;
        """
        # Second query
        query2 = """
                    SELECT DISTINCT ON (a.tracking_number) 
                    substring(a.tracking_number, 1, 3) AS district,
                    a.tracking_number,
                    (b.created_at)::timestamp AS received_on,
                    (c.created_at)::timestamp AS LSO_ASSIGNED_AT
                FROM public.pmc_api_applicantdetail a
                JOIN pmc_api_applicationsubmitted b ON a.id = b.applicant_id
                JOIN pmc_api_applicationassignment c ON a.id = c.applicant_id
                WHERE a.assigned_group = 'DO'
                  AND c.assigned_group = 'DO'
                ORDER BY a.tracking_number, b.created_at;
                """
        try:
            with connection.cursor() as cursor:
                # Execute first query
                cursor.execute(query1)
                columns1 = [col[0] for col in cursor.description]
                results1 = cursor.fetchall()

                # Execute second query
                cursor.execute(query2)
                columns2 = [col[0] for col in cursor.description]
                results2 = cursor.fetchall()
        except Exception as e:
            return Response({"error": str(e)}, status=500)
            # Convert the results to a DataFrame
            # Convert results to DataFrames
        df1 = pd.DataFrame(results1, columns=columns1)
        df2 = pd.DataFrame(results2, columns=columns2)
        # Create an HTTP response with an Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="report.xlsx"'
        # Write both DataFrames to separate sheets in the Excel file
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df1.to_excel(writer, index=False, sheet_name='Summary Report')
            df2.to_excel(writer, index=False, sheet_name='DO Report')
        return response
