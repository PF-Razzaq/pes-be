
import jwt
import datetime
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer,EventsSerializer,PdfDataSerializer,LocationsSerializer,CountrySerializer,FSPsSerializerData
from .models import User,PesEvents,PesExecutor,Locations,Country,Admins
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
import random
import string
from django.contrib.auth.hashers import make_password
from .serializers import ChangePasswordSerializer
from django.db import connection
from rest_framework.decorators import permission_classes,api_view,authentication_classes
from rest_framework import generics, permissions
import logging
import json
import requests
from datetime import date
from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from rest_framework.authentication import BasicAuthentication,SessionAuthentication,TokenAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser,DjangoModelPermissions
import os
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404


logger = logging.getLogger(__name__)

base_url = os.getenv('DOTNET_PDF_BACKEND')

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

logger = logging.getLogger('custom_logger')
from rest_framework import status as http_status  # Renamed import to avoid conflict

class LoginView(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            logger.info(f"Username: {username}, Password: {password}")

            if not username or not password:
                raise AuthenticationFailed('Username and password are required.', code='missing_credentials')

            user = User.objects.filter(username=username).first()

            if user is None:
                raise AuthenticationFailed('User not found.', code='user_not_found')

            if not user.check_password(password):
                raise AuthenticationFailed('Incorrect password.', code='incorrect_password')

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        f.FSPID, 
                        f.RoutingID, 
                        l.LocationName, 
                        l.city, 
                        l.prov, 
                        l.postalcode,
                        l.Phone,
                        l.Address,
                        l.LocationID,
                        f.Status,
                        f.LoginCount
                    FROM 
                        FSPs f
                    INNER JOIN 
                        pes_user pu ON pu.username = f.Username AND pu.username = %s
                    INNER JOIN 
                        Locations l ON f.LocationID = l.LocationID
                """, [username])

                results = cursor.fetchone()

            if not results:
                raise AuthenticationFailed('FSPID or RoutingID not found for the user.', code='fspid_routingid_not_found')

            fsp_id, routing_id, location_name, city, prov, postalcode, phone, address, LocationID, fsp_status, login_count = results

            # Check if status is 0 (inactive), and return an error response if so
            if fsp_status == 0:
                return Response({'error': 'Your account is inactive. Please contact Administrator.', 'status': '0'}, status=http_status.HTTP_403_FORBIDDEN)

            # Update lastAccessed field to the current time and increment LoginCount
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE FSPs 
                    SET lastAccessed = %s, 
                        LoginCount = LoginCount + 1
                    WHERE Username = %s
                """, [timezone.now(), username])

            token, created = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(instance=user)

            response_data = {
                'jwt': token.key,
                'username': username,
                'FSPID': fsp_id,
                'RoutingID': routing_id,
                'LocationName': location_name,
                'city': city,
                'prov': prov,
                'postalcode': postalcode,
                'Phone': phone,
                'Address': address,
                'LocationID': LocationID,
                'status': 1,
                'user': serializer.data
            }

            return Response(response_data)

        except AuthenticationFailed as e:
            logger.error(f"Authentication error: {str(e)}, code: {e.get_codes()}")
            return Response({'error': 'Incorrect username or password. Please try again.'}, status=http_status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}")
            return Response({'error': f'Cannot connect: {e}', 'status': 0}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

           
def convert_string_to_yyyy_mm_dd(date_str):
    if not date_str:
        return None
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%b %d %Y %I:%M%p'):
        try:
            return datetime.strptime(date_str, fmt).date().strftime('%Y-%m-%d')
            #.strftime('%d/%m/%Y')
        except ValueError:
            continue
    return date_str

class AdminLoginView(APIView):
    def post(self, request):
        password = request.data.get('password')

        user = get_object_or_404(User, username=request.data['password'])
        if not user.check_password(request.data['password']):
            return Response({"detail": "Admin Not found."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            admin = Admins.objects.get(adminpassword=password)
        except Admins.DoesNotExist:
            return Response({"detail": "Wrong password"}, status=status.HTTP_400_BAD_REQUEST)
        # try:
        #     user = User.objects.get(username=admin.adminname)
        # except User.DoesNotExist:
        #     return Response({"detail": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        # if not user.check_password(password):
        #     return Response({"detail": "Wrong Password"}, status=status.HTTP_400_BAD_REQUEST)

        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(instance=user)

        return Response({"token": token.key, "user": serializer.data})



class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)

class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response
class AddRandomCode(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            random_code_int = None
            while not (random_code_int and len(str(random_code_int)) == 4):
                random_code = ''.join(random.choices(string.digits, k=4))
                random_code_int = int(random_code)
            send_mail(
                'Password Reset Code',
                f'Your password reset code is: {random_code_int}',
                'abdulrazzaqchohan1@gmail.com',
                [email],
                fail_silently=False,
                html_message=f'<p>Your OTP is {random_code_int}</p>'
            )
            user.otpCode = random_code_int
            user.save()
            return JsonResponse({'message': 'Random code added successfully'}, status=200)
        else:
            return JsonResponse({'Error': 'Email does not exist in the database'}, status=409)


class CheckCodeExist(APIView):
    def post(self, request):
        code = request.data.get('otpCode')
        try:
            user = User.objects.get(otpCode=code)
            return JsonResponse({'Successfly code match': code}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'Error':'Code mismatched'}, status=409)
        
class ChangePassword(APIView):
    def post(self, request):
        code = request.data.get('otpCode')
        password = request.data.get('password')
        try:
            user = User.objects.get(otpCode=code)
            user.set_password(password)
            user.otpCode = None
            user.save()
            return JsonResponse({'Successfly change Password': code}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'Error':'Code mismatched'}, status=409)
    

# Data insert api



# class CreateRecordAPIView(APIView):
#     def post(self, request):
#         data = request.data

#         with connection.cursor() as cursor:
#             cursor.execute(
#     "INSERT INTO Events (FSPID, eventdate, d_First, d_middle_a, d_middle_b, d_Last, d_Maiden, d_Address, d_Unit, d_City, d_Prov, d_Postal, d_AreaCode, d_exchange, d_phone, d_DOB, d_birth_Country, d_birth_City, d_birth_Prov, d_DOD, d_death_Country, d_death_City, d_death_Prov, d_death_age, d_dispdate, d_disp_Name, d_SIN, e_Salutation, e_First, e_Initial, e_Last, e_Address, e_Unit, e_City, e_Prov, e_Postal, e_AreaCode, e_exchange, e_phone_4, e_relationship) VALUES (%s,GETDATE(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
#     [
#         data.get('FSPID'), data.get('d_First'), data.get('d_middle_a'), data.get('d_middle_b'), data.get('d_Last'), data.get('d_Maiden'),
#         data.get('d_Address'), data.get('d_Unit'), data.get('d_City'), data.get('d_Prov'), data.get('d_Postal'),
#         data.get('d_AreaCode'), data.get('d_exchange'), data.get('d_phone'), data.get('d_DOB'), data.get('d_birth_Country'),
#         data.get('d_birth_City'), data.get('d_birth_Prov'), data.get('d_DOD'), data.get('d_death_Country'), data.get('d_death_City'),
#         data.get('d_death_Prov'), data.get('d_death_age'), data.get('d_dispdate'), data.get('d_disp_Name'), data.get('d_SIN'),
#         data.get('e_Salutation'), data.get('e_First'), data.get('e_Initial'), data.get('e_Last'), data.get('e_Address'),
#         data.get('e_Unit'), data.get('e_City'), data.get('e_Prov'), data.get('e_Postal'), data.get('e_AreaCode'),
#         data.get('e_exchange'), data.get('e_phone_4'), data.get('e_relationship')
#     ]
# )


#         return Response({'Record created successfully'}, status=status.HTTP_201_CREATED)

# from .utils import read_data_from_database
# For Database
# def my_view(request):
#     data = read_data_from_database()
#     # Process the data as needed
#     return HttpResponse("Data read from database successfully")

# End DataBase


# class EventsListCreateView(generics.ListCreateAPIView):
#     queryset = PesEvents.objects.all()
#     serializer_class = EventsSerializer

#     def get_pes_events_data(self):
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT eventID, e_Last FROM PesEvents")
#             rows = cursor.fetchall()
#             print('rows',rows)
#             return rows

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def events_list(request):
    try:
        if request.method == 'GET':
            events = PesEvents.objects.all()
            paginator = PageNumberPagination()
            paginator.page_size = 20
            result_page = paginator.paginate_queryset(events, request)
            serializer = EventsSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        logger.error(f"Error retrieving events: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def events_create(request):
    if request.method == 'POST':
        if request.data.get("FaxDate") is not None:
            request.data["FaxDate"] = datetime.strptime(request.data.get("FaxDate"), "%d/%m/%Y")

        if request.data.get("ReportDate") is not None:
            request.data["ReportDate"] = datetime.strptime(request.data.get("ReportDate"), "%d/%m/%Y")

        request.data["d_DOB"] = convert_string_to_yyyy_mm_dd(request.data.get("d_DOB"))
        request.data["d_DOD"] = convert_string_to_yyyy_mm_dd(request.data.get("d_DOD"))

        if request.data.get("d_dispdate") == "/00/00":
            request.data["d_dispdate"] = None
        else:
            request.data["d_dispdate"] = convert_string_to_yyyy_mm_dd(request.data.get("d_dispdate"))

        if request.data.get("Status") == "":
            request.data["Status"] = None

        request.data["eventdate"] = timezone.now()

        serializer = EventsSerializer(data=request.data)
        if serializer.is_valid():
            # Save the PesEvents object
            pes_event = serializer.save()

            eventID = serializer.data.get('eventID')
            e_Last = serializer.data.get('e_Last')

            random_number = random.randint(1000, 9999)

            # Remove apostrophes from the last name
            modified_l_name = e_Last.replace("'", "")

            username = modified_l_name + str(random_number)

            password = str(random.randint(100000, 999999))

            # Connect to the database and save username, password, and Status=1 in PesExecutor table
            executor = PesExecutor.objects.create(Username=username, Password=password, Status=1)
            executor_id = executor.ExecutorID

            # Update the PesEvents object with the executor_id
            pes_event.ExecutorID = executor_id
            pes_event.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# @api_view(['POST'])
# def events_create(request):
#     if request.method == 'POST':
#         serializer = EventsSerializer(data=request.data)
#         if serializer.is_valid():
#             # Save the PesEvents object
#             pes_event = serializer.save()

#             eventID = serializer.data.get('eventID')
#             e_Last = serializer.data.get('e_Last')

#             random_number = random.randint(1000, 9999)
            
#             # Remove apostrophes from the last name
#             modified_l_name = e_Last.replace("'", "")

#             username = modified_l_name + str(random_number)

#             password = str(random.randint(100000, 999999))

#             # Connect to the database and save username, password, and Status=1 in PesExecutor table
#             executor = PesExecutor.objects.create(Username=username, Password=password, Status=1)
#             executor_id = executor.ExecutorID

#             # Update the PesEvents object with the executor_id
#             pes_event.ExecutorID = executor_id
#             pes_event.save()

#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventsRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = PesEvents.objects.all()
    serializer_class = EventsSerializer

@api_view(['PUT'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def event_modify(request):
    if request.method == 'PUT':
        pes_event = PesEvents.objects.get(eventID=request.data.get('eventID'))
        if request.data.get("FaxDate") is not None:
                request.data["FaxDate"] = datetime.strptime(request.data.get("FaxDate"), "%d/%m/%Y")
                
        if request.data.get("ReportDate") is not None:
            request.data["ReportDate"] = datetime.strptime(request.data.get("ReportDate"), "%d/%m/%Y")

        request.data["d_DOB"] = convert_string_to_yyyy_mm_dd(request.data.get("d_DOB"))
        request.data["d_DOD"] = convert_string_to_yyyy_mm_dd(request.data.get("d_DOD"))
        
        if request.data.get("d_dispdate") == "/00/00":
            request.data["d_dispdate"] = None
        else:
            request.data["d_dispdate"] = convert_string_to_yyyy_mm_dd(request.data.get("d_dispdate"))
        
        if request.data["Status"] == "":
            request.data["Status"] = None
        
        request.data["eventdate"] = timezone.now()
        pes_event.eventdate = request.data.get("eventdate")
        pes_event.save()
        
        serializer = EventsSerializer(pes_event, data=request.data)
        if serializer.is_valid():
            # Save the PesEvents object
            pes_event = serializer.save()
            return Response({'Record updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({f'Record updated successfully {request.data["d_DOB"]} {serializer.errors}'}, status=status.HTTP_400_BAD_REQUEST)
            

@api_view(['PUT'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def event_admin(request):
    if request.method == 'PUT':
        pes_event = PesEvents.objects.get(eventID=request.data.get('eventID'))
        if request.data.get("FaxDate") is not None:
            if len(request.data.get("FaxDate")) > 0:
                request.data["FaxDate"] = datetime.strptime(request.data.get("FaxDate"), "%d/%m/%Y")
            else:
                request.data["FaxDate"] = None
                
        if request.data.get("ReportDate") is not None:
            if len(request.data.get("ReportDate")) > 0:
                request.data["ReportDate"] = datetime.strptime(request.data.get("ReportDate"), "%d/%m/%Y")
            else:
                request.data["ReportDate"] = None
        
        request.data["d_DOB"] = convert_string_to_yyyy_mm_dd(request.data.get("d_DOB"))
        request.data["d_DOD"] = convert_string_to_yyyy_mm_dd(request.data.get("d_DOD"))
        
        if request.data.get("d_dispdate") == "/00/00":
            request.data["d_dispdate"] = None
        else:
            request.data["d_dispdate"] = convert_string_to_yyyy_mm_dd(request.data.get("d_dispdate"))
        

        serializer = EventsSerializer(pes_event, data=request.data)        

        if serializer.is_valid():
            # Save the PesEvents object
            pes_event = serializer.save()

            eventID = serializer.data.get('eventID')
            pesstatus = serializer.data.get('Status')
            UpdateID = request.data.get('UpdateID')
            if pesstatus == "":
                pes_event.Status = None
            else:
                if UpdateID is not None:
                    if len(UpdateID)>0 :
                        try:
                            query = """
                            SELECT
                                UpdateDesc
                            FROM
                                dbo.Updates
                            WHERE
                                UpdateID = %s
                            """
                            with connection.cursor() as cursor:
                                cursor.execute(query, [UpdateID])
                                rows = cursor.fetchall()
                                columns = [col[0] for col in cursor.description]
                                for row in rows:
                                    pes_event.Status = row[0]
                        except Exception as e:
                            return Response({'message': f'Db Connection Error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        pes_event.UpdateID = None

                else:
                    pes_event.UpdateID = None

                        
                #pes_event.FaxDate = datetime.date(
                pes_event.save()

                AdminName = 'Not currently available'

                with connection.cursor() as cursor:
                    cursor.execute(
                        "Insert InTo EventUpdates (EventID, UpdateID, Date, Notes, EventUpdateFaxDate, EventUpdateReportDate, AdminName,Status) values (%s, %s, GetDate(), %s, %s, %s, %s, %s)",
                        [
                            pes_event.eventID, pes_event.UpdateID, pes_event.notes, pes_event.FaxDate, pes_event.ReportDate, AdminName, pes_event.Status
                        ]
                    )
            
                return Response({'Record updated successfully'}, status=status.HTTP_201_CREATED)

        else:
            print(serializer.errors)
            return Response({'message': f'dddaaa{serializer.errors}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
	return Response("passed for {}".format(request.user.email))


@api_view(['GET'])
def get_data_from_location(request,locationname):
    try:
        locationname_record = Locations.objects.filter(locationname=locationname)
        serializer = LocationsSerializer(locationname_record, many=True)
        return Response(serializer.data)
    except FSPs.DoesNotExist:
        return Response({"message": "No records found for the specified LocationName"}, status=401)



        
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_update_by_event_id(request, event_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.EventID, e.UpdateID, e.Date, e.Notes, e.EventUpdateFaxDate, e.EventUpdateReportDate, u.UpdateDesc as Status
            From EventUpdates e left join Updates u on u.UpdateID = e.UpdateID 
            WHERE e.EventID = %s
            Order By e.Date 
        """, [event_id])
        
        rows = cursor.fetchall()
        
        if rows:
            results = []
            for row in rows:
                result = {
                    "EventID": int(row[0]),  # Convert Decimal to int
                    "UpdateID": row[1] if row[1] is not None else None,
                    "Date": row[2].isoformat() if row[2] is not None else None,
                    "Notes": row[3],
                    "EventUpdateFaxDate": row[4].isoformat() if row[4] is not None else None,
                    "EventUpdateReportDate": row[5].isoformat() if row[5] is not None else None,
                    "Status": row[6]
                }
                results.append(result)
        else:
            results = []

    return JsonResponse(results, safe=False)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def countries(request):
    try:
        country_data_records = Country.objects.filter(isactive=1).order_by('orderby')
        serializer = CountrySerializer(country_data_records, many=True)
        return Response(serializer.data)
    except Country.DoesNotExist:
        return Response({'message': 'No records found'}, status=status.HTTP_404_NOT_FOUND)
    

# @api_view(['GET'])
# # @permission_classes([IsAdminUser])
# # @authentication_classes([SessionAuthentication])
# def filter_pes_events_by_fspid(request, fspid):
#     try:
#         pes_events = PesEvents.objects.filter(FSPID=fspid)
#         serializer = EventsSerializer(pes_events, many=True)
#         return Response(serializer.data)
#     except PesEvents.DoesNotExist:
#         return Response({'message': 'No records found for the specified FSPID'}, status=status.HTTP_404_NOT_FOUND)

# Replace by below this code

# @api_view(['GET'])
# def after_care_page(request, location_id):
#     def format_date_with_timezone(date_value, timezone_str):
#         if not date_value:
#             return None
#         try:
#             timezone = pytz.timezone(timezone_str)
#             date_value = date_value.astimezone(timezone)
#             formatted_date = date_value.strftime('%Y-%m-%dT%H:%M:%S%z')
#             # Insert the colon in the timezone offset
#             formatted_date = formatted_date[:-2] + ':' + formatted_date[-2:]
#             return formatted_date
#         except Exception as e:
#             return str(e)

#     try:
#         query = """
#         SELECT
#             PesEvents.EventID,
#             PesEvents.d_First,
#             PesEvents.d_Last,
#             PesEvents.e_Last,
#             PesEvents.Status,
#             PesEvents.eventdate
#         FROM
#             dbo.PesEvents
#         INNER JOIN dbo.FSPs ON
#             dbo.PesEvents.FSPID = dbo.FSPs.FSPID
#         WHERE
#             (PesEvents.eventdate >= GETDATE() - 61)
#             AND (PesEvents.Status = 'HOLD - Unsigned CA'
#                 OR PesEvents.Status = 'HOLD - Missing PO'
#                 OR PesEvents.Status = 'COMPLETE'
#                 OR PesEvents.Status = 'HOLD - Missing CA'
#                 OR PesEvents.Status = 'HOLD - Missing POD'
#                 OR PesEvents.Status = 'HOLD - Other'
#                 OR PesEvents.Status IS NULL)
#             AND FSPs.LocationID = %s
#         ORDER BY
#             PesEvents.EventID DESC
#         """

#         with connection.cursor() as cursor:
#             cursor.execute(query, [location_id])
#             rows = cursor.fetchall()
#             columns = [col[0] for col in cursor.description]

#         if not rows:
#             return Response({'message': 'No records found for the specified LocationID'}, status=status.HTTP_404_NOT_FOUND)

#         results = [
#             {
#                 **dict(zip(columns, row)),
#                 'eventdate': format_date_with_timezone(row[columns.index('eventdate')], 'Canada/Eastern') if row[columns.index('eventdate')] else None
#             }
#             for row in rows
#         ]

#         return Response(results, status=status.HTTP_200_OK)

#     except Exception as e:
#         return Response({'message': f'Db Connection Error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # aftercare 360 days records
# @api_view(['GET'])
# def after_care_page360(request, location_id):
#     try:
#         query = """
#         SELECT
#             PesEvents.EventID,
#             PesEvents.d_First,
#             PesEvents.d_Last,
#             PesEvents.e_Last,
#             PesEvents.Status,
#             PesEvents.eventdate
#         FROM
#             dbo.PesEvents
#         INNER JOIN dbo.FSPs ON
#             dbo.PesEvents.FSPID = dbo.FSPs.FSPID
#         WHERE
#             (PesEvents.eventdate >= GETDATE() - 360)
#             AND (PesEvents.Status = 'HOLD - Unsigned CA'
#                 OR PesEvents.Status = 'HOLD - Missing PO'
#                 OR PesEvents.Status = 'COMPLETE'
#                 OR PesEvents.Status = 'HOLD - Missing CA'
#                 OR PesEvents.Status = 'HOLD - Missing POD'
#                 OR PesEvents.Status = 'HOLD - Other'
#                 OR PesEvents.Status IS NULL)
#             AND FSPs.LocationID = %s
#         ORDER BY
#             PesEvents.eventdate DESC
#         """

#         with connection.cursor() as cursor:
#             cursor.execute(query, [location_id])
#             rows = cursor.fetchall()
#             columns = [col[0] for col in cursor.description]

#         if not rows:
#             return Response({'message': 'No records found for the specified LocationID'}, status=status.HTTP_404_NOT_FOUND)

#         results = [
#             dict(zip(columns, row))
#             for row in rows
#         ]

#         return Response(results, status=status.HTTP_200_OK)

#     except Exception as e:
#         return Response({'message': f'Db Connection Error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
from datetime import timedelta
from django.utils import timezone
from django.db.models import F, Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import pytz
from .models import PesEvents, FSPs, Modifier,Aftercare,Aftercare360
from .serializers import ModifierSerializer,AftercareSerializer,Aftercare360Serializer

@api_view(['GET'])
def modifier_page(request, location_id):
    def format_date_with_timezone(self, date_value, timezone_str):
        if not date_value:
            return None
        try:
            timezone = pytz.timezone(timezone_str)
            date_value = date_value.astimezone(timezone)
            formatted_date = date_value.strftime('%Y-%m-%dT%H:%M:%S%z')
            # Insert the colon in the timezone offset
            formatted_date = formatted_date[:-2] + ':' + formatted_date[-2:]
            return formatted_date
        except Exception as e:
            return str(e)
    try:

        modifier_page = Modifier.objects.filter(locationid = location_id).order_by('-EventID')
        serializer = ModifierSerializer(modifier_page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': f'Db Connection Error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
@api_view(['GET'])
def after_care_page(request, location_id):
    def format_date_with_timezone(date_value, timezone_str):
        if not date_value:
            return None
        try:
            timezone = pytz.timezone(timezone_str)
            date_value = date_value.astimezone(timezone)
            formatted_date = date_value.strftime('%Y-%m-%dT%H:%M:%S%z')
            # Insert the colon in the timezone offset
            formatted_date = formatted_date[:-2] + ':' + formatted_date[-2:]
            return formatted_date
        except Exception as e:
            return str(e)

    try:

        after_care_page = Aftercare.objects.filter(locationid = location_id).order_by('-EventID')
        serializer = AftercareSerializer(after_care_page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': f'Db Connection Error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def after_care_page360(request, location_id):
    try:
        after_care_page = Aftercare360.objects.filter(locationid = location_id).order_by('-EventID')
        serializer = Aftercare360Serializer(after_care_page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': f'Db Connection Error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# @api_view(['GET'])
# def modifier_page(request, location_id):
#     def format_date_with_timezone(self, date_value, timezone_str):
#         if not date_value:
#             return None
#         try:
#             timezone = pytz.timezone(timezone_str)
#             date_value = date_value.astimezone(timezone)
#             formatted_date = date_value.strftime('%Y-%m-%dT%H:%M:%S%z')
#             # Insert the colon in the timezone offset
#             formatted_date = formatted_date[:-2] + ':' + formatted_date[-2:]
#             return formatted_date
#         except Exception as e:
#             return str(e)

#     try:
#         # Fetch data using Django ORM
#         events = PesEvents.objects.select_related('FSPID').all()
#         print(events)

#         # Check if no records found
#         if not events.exists():
#             return Response({'message': 'No records found for the specified LocationID'}, status=status.HTTP_404_NOT_FOUND)

#         # Format the results
#         results = [
#             {
#                 'EventID': event.eventID,
#                 'd_First': event.d_First,
#                 'd_Last': event.d_Last,
#                 'e_Last': event.e_Last,
#                 'Status': event.Status,
#                 'eventdate': format_date_with_timezone(event.eventdate, 'Canada/Eastern') if event.eventdate else None
#             }
#             for event in events
#         ]

#         return Response(results, status=status.HTTP_200_OK)

#     except Exception as e:
#         return Response({'message': f'Db Connection Error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from .serializers import PesEventsSerializer
# @api_view(['GET'])
# def event_list_specific_fields(request):
#     try:
#         if request.method == 'GET':
#             events = PesEvents.objects.all()
#             paginator = PageNumberPagination()
#             paginator.page_size = 20
#             result_page = paginator.paginate_queryset(events, request)
#             serializer = PesEventsSerializer(result_page, many=True)
#             return paginator.get_paginated_response(serializer.data)
#     except Exception as e:
#         logger.error(f"Error retrieving events: {str(e)}")
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.db import connection
# from rest_framework.decorators import api_view
# from rest_framework.response import Response

# @api_view(['GET'])
# def event_list_specific_fields(request):
#     try:
#         if request.method == 'GET':
#             with connection.cursor() as cursor:
#                 # Define the SQL query
#                 sql_query = """
#                     SELECT 
#                         p.d_First, p.d_middle_a, p.d_middle_b, p.d_Last, p.d_Address, p.d_Unit, p.d_City,
#                         p.d_Prov, p.d_Postal, p.d_DOB, p.d_BCN, p.d_DOD, p.d_SIN, p.FaxDate, p.Contract,
#                         p.Status, p.notes, p.eventdate, p.ReportDate,
#                         f.f_first, f.f_last,
#                         l.LocationName, l.BillingCode, l.OldLocation, l.AdminEmail, l.Phone 
#                     FROM 
#                         FSPs f
#                     INNER JOIN 
#                         PesEvents p ON f.FSPID = p.fspid 
#                     INNER JOIN 
#                         Locations l ON f.LocationID = l.LocationID
#                 """

#                 # Execute the SQL query
#                 cursor.execute(sql_query)

#                 # Fetch all rows from the executed query
#                 rows = cursor.fetchall()
#                 print("rows", rows)  # Print the fetched rows to check if data is retrieved properly

#                 # Pagination
#                 paginator = Paginator(rows, 20)
#                 page_number = request.GET.get('page')
#                 try:
#                     rows = paginator.page(page_number)
#                 except PageNotAnInteger:
#                     rows = paginator.page(1)
#                 except EmptyPage:
#                     rows = paginator.page(paginator.num_pages)

#                 # Serialize the data
#                 serialized_data = []
#                 for row in rows:
#                     data = {
#                         'd_First': row[0],
#                         'd_middle_a': row[1],
#                         'd_middle_b': row[2],
#                         'd_Last': row[3],
#                         'd_Address': row[4],
#                         'd_Unit': row[5],
#                         'd_City': row[6],
#                         'd_Prov': row[7],
#                         'd_Postal': row[8],
#                         'd_DOB': row[9],
#                         'd_BCN': row[10],
#                         'd_DOD': row[11],
#                         'd_SIN': row[12],
#                         'FaxDate': row[13],
#                         'Contract': row[14],
#                         'Status': row[15],
#                         'notes': row[16],
#                         'eventdate': row[17],
#                         'ReportDate': row[18],
#                         'f_first': row[19],
#                         'f_last': row[20],
#                         'LocationName': row[21],
#                         'BillingCode': row[22],
#                         'OldLocation': row[23],
#                         'AdminEmail': row[24],
#                         'Phone': row[25]
#                     }
#                     serialized_data.append(data)
#                     print("data", data)  # Print each data entry to check if serialization works properly

#                 return Response(serialized_data)

#     except Exception as e:
#         print("Error:", str(e))  # Print any errors that occur during execution for debugging
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_fsp(request):
    try:
        if request.method == 'GET':
            with connection.cursor() as cursor:
                # Define the SQL query
                sql_query = """
                    select FSPID, LocationID, Status, f_first, f_last, RoutingID from FSPs where FSPID=%s;
                """
                # Execute the SQL query
                cursor.execute(sql_query, [request.data['FSPID']])

                # Fetch all rows from the executed query
                results = cursor.fetchall()
                if not results:
                    return Response('No Record Found')

                # Serialize the data
                serialized_data = []
                for row in results:
                    data = {
                        'FSPID': row[0],
                        'LocationID': row[1],
                        'Status': row[2],
                        'f_first': row[3],
                        'f_last': row[4],
                        'RoutingID': row[5]
                    }
                    serialized_data.append(data)

                return Response(serialized_data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def getlocations(request):
    try:
        if request.method == 'GET':
            with connection.cursor() as cursor:
                # Define the SQL query
                sql_query = """
                    SELECT LocationID, LocationName, City, CONCAT(LocationName, ' (', City, ')') Description FROM Locations ORDER BY LocationName, City
                """
                # Execute the SQL query
                cursor.execute(sql_query, [])

                # Fetch all rows from the executed query
                results = cursor.fetchall()
                if not results:
                    return Response('No Record Found')

                # Serialize the data
                serialized_data = []
                for row in results:
                    data = {
                        'LocationID': row[0],
                        'LocationName': row[1],
                        'City': row[2],
                        'Description': row[3]
                    }
                    serialized_data.append(data)

                return Response(serialized_data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PesEventsSerializer

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def event_list_today(request):
    try:
        if request.method == 'GET':
            with connection.cursor() as cursor:
                # Define the SQL query
                sql_query = """
                        SELECT
                            d_First,
                            d_middle_a,
                            d_middle_b,
                            d_Last,
                            d_Address,
                            d_Unit,
                            d_City,
                            d_Prov,
                            d_Postal,
                            CONVERT(nvarchar(10), CONVERT(date, d_DOB, 103), 103) AS d_DOB,
                            d_BCN,
                            CONVERT(nvarchar(10), CONVERT(date, d_DOD, 103), 103) AS d_DOD,
                            d_SIN,
                            CONVERT(varchar, FaxDate, 103) AS FaxDate,
                            BillingCode,
                            OldLocation,
                            Contract,
                            AdminEmail,
                            Status,
                            notes,
                            CONVERT(varchar, eventdate, 103) + ' ' + LEFT(CONVERT(varchar, eventdate, 108), 5) AS eventdate,  -- Format DD/MM/YYYY HH:MM for eventdate
                            CONVERT(varchar, ReportDate, 103) + ' ' + LEFT(CONVERT(varchar, ReportDate, 108), 5) AS ReportDate,
                            f_first,
                            f_last,
                            LocationName,
                            Phone
                        FROM
                            AdminReport
                        WHERE
                            Status = 'Complete'
                            AND CAST(ReportDate AS DATE) = CAST(GETDATE() AS DATE)
                        ORDER BY
                            Status DESC,
                            EventID;
                """
                # Execute the SQL query
                cursor.execute(sql_query)

                # Fetch all rows from the executed query
                results = cursor.fetchall()
                if not results:
                    return Response('No Record Found')

                # Serialize the data
                serialized_data = []
                for row in results:
                    data = {
                        'd_First': row[0],
                        'd_middle_a': row[1],
                        'd_middle_b': row[2],
                        'd_Last': row[3],
                        'd_Address': row[4],
                        'd_Unit': row[5],
                        'd_City': row[6],
                        'd_Prov': row[7],
                        'd_Postal': row[8],
                        'd_DOB': row[9],
                        'd_BCN': row[10],
                        'd_DOD': row[11],
                        'd_SIN': row[12],
                        'FaxDate': row[13],
                        'BillingCode': row[14],
                        'OldLocation': row[15],
                        'Contract': row[16],
                        'AdminEmail': row[17],
                        'Status': row[18],
                        'notes': row[19],
                        'eventdate': row[20],
                        'ReportDate': row[21],
                        'f_first': row[22],
                        'f_last': row[23],
                        'LocationName': row[24],
                        'Phone': row[25]
                    }
                    serialized_data.append(data)

                return Response(serialized_data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def event_list_yesterday(request):
    try:
        if request.method == 'GET':
            with connection.cursor() as cursor:
                # Define the SQL query
                sql_query = """
                            SELECT
                        	d_First,
                        	d_middle_a,
                        	d_middle_b,
                        	d_Last,
                        	d_Address,
                        	d_Unit,
                        	d_City,
                        	d_Prov,
                        	d_Postal,
                        	CONVERT(nvarchar(10), CONVERT(date, d_DOB, 103), 103) AS d_DOB,
                        	d_BCN,
                        	CONVERT(nvarchar(10),	CONVERT(date,	d_DOD,	103),	103) as d_DOD,
                        	d_SIN,
                        	convert(varchar,	FaxDate,	103) as FaxDate,
                        	BillingCode,
                        	OldLocation,
                        	Contract,
                        	AdminEmail,
                        	Status,
                        	notes,
                        	CONVERT(varchar, eventdate, 103) + ' ' + LEFT(CONVERT(varchar, eventdate, 108), 5) AS eventdate,  -- Format DD/MM/YYYY HH:MM for eventdate
                            CONVERT(varchar, ReportDate, 103) + ' ' + LEFT(CONVERT(varchar, ReportDate, 108), 5) AS ReportDate,  --
                        	f_first,
                        	f_last,
                        	LocationName,
                        	Phone
                        FROM
                        	AdminReport
                        WHERE
                        	Status = 'Complete'
                        	AND CAst(ReportDate as DAte) = cast( GETDATE()-1 as DAte)
                        ORDER BY
                        	Status DESC,
                        	EventID;    
                """
                # Execute the SQL query
                cursor.execute(sql_query)

                # Fetch all rows from the executed query
                results = cursor.fetchall()
                if not results:
                    return Response('No Record Found')

                # Serialize the data
                serialized_data = []
                for row in results:
                    data = {
                        'd_First': row[0],
                        'd_middle_a': row[1],
                        'd_middle_b': row[2],
                        'd_Last': row[3],
                        'd_Address': row[4],
                        'd_Unit': row[5],
                        'd_City': row[6],
                        'd_Prov': row[7],
                        'd_Postal': row[8],
                        'd_DOB': row[9],
                        'd_BCN': row[10],
                        'd_DOD': row[11],
                        'd_SIN': row[12],
                        'FaxDate': row[13],
                        'BillingCode': row[14],
                        'OldLocation': row[15],
                        'Contract': row[16],
                        'AdminEmail': row[17],
                        'Status': row[18],
                        'notes': row[19],
                        'eventdate': row[20],
                        'ReportDate': row[21],
                        'f_first': row[22],
                        'f_last': row[23],
                        'LocationName': row[24],
                        'Phone': row[25]
                    }
                    serialized_data.append(data)

                return Response(serialized_data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def event_list_tomorrow(request):
    try:
        if request.method == 'GET':
            with connection.cursor() as cursor:
                # Define the SQL query
                sql_query = """
                            SELECT
                        	d_First,
                        	d_middle_a,
                        	d_middle_b,
                        	d_Last,
                        	d_Address,
                        	d_Unit,
                        	d_City,
                        	d_Prov,
                        	d_Postal,
                        	CONVERT(nvarchar(10), CONVERT(date, d_DOB, 103), 103) AS d_DOB,
                        	d_BCN,
                        	CONVERT(nvarchar(10),	CONVERT(date,	d_DOD,	103),	103) as d_DOD,
                        	d_SIN,
                        	convert(varchar,	FaxDate,	103) as FaxDate,
                        	BillingCode,
                        	OldLocation,
                        	Contract,
                        	AdminEmail,
                        	Status,
                        	notes,
                        	CONVERT(varchar, eventdate, 103) + ' ' + LEFT(CONVERT(varchar, eventdate, 108), 5) AS eventdate,  -- Format DD/MM/YYYY HH:MM for eventdate
                            CONVERT(varchar, ReportDate, 103) + ' ' + LEFT(CONVERT(varchar, ReportDate, 108), 5) AS ReportDate,  --
                        	f_first,
                        	f_last,
                        	LocationName,
                        	Phone
                        FROM
                        	PesFullDump pfd
                        WHERE
                        	Status = 'Complete'
                        	AND ReportDate = CONVERT(DATETIME, 
                            CAST(DATEADD(DAY, 1, GETDATE()) AS DATE), 101) 
                        ORDER BY
                        	Status DESC,
                        	EventID;  
                """
                # Execute the SQL query
                cursor.execute(sql_query)

                # Fetch all rows from the executed query
                results = cursor.fetchall()
                if not results:
                    return Response('No Record Found')

                # Serialize the data
                serialized_data = []
                for row in results:
                    data = {
                        'd_First': row[0],
                        'd_middle_a': row[1],
                        'd_middle_b': row[2],
                        'd_Last': row[3],
                        'd_Address': row[4],
                        'd_Unit': row[5],
                        'd_City': row[6],
                        'd_Prov': row[7],
                        'd_Postal': row[8],
                        'd_DOB': row[9],
                        'd_BCN': row[10],
                        'd_DOD': row[11],
                        'd_SIN': row[12],
                        'FaxDate': row[13],
                        'BillingCode': row[14],
                        'OldLocation': row[15],
                        'Contract': row[16],
                        'AdminEmail': row[17],
                        'Status': row[18],
                        'notes': row[19],
                        'eventdate': row[20],
                        'ReportDate': row[21],
                        'f_first': row[22],
                        'f_last': row[23],
                        'LocationName': row[24],
                        'Phone': row[25]
                    }
                    serialized_data.append(data)

                return Response(serialized_data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def three_days_ago_report(request):
    try:
        if request.method == 'GET':
            with connection.cursor() as cursor:
                # Define the SQL query
                sql_query = """
                            SELECT
                        	d_First,
                        	d_middle_a,
                        	d_middle_b,
                        	d_Last,
                        	d_Address,
                        	d_Unit,
                        	d_City,
                        	d_Prov,
                        	d_Postal,
                        	CONVERT(nvarchar(10), CONVERT(date, d_DOB, 103), 103) AS d_DOB,
                        	d_BCN,
                        	CONVERT(nvarchar(10),	CONVERT(date,	d_DOD,	103),	103) as d_DOD,
                        	d_SIN,
                        	convert(varchar,	FaxDate,	103) as FaxDate,
                        	BillingCode,
                        	OldLocation,
                        	Contract,
                        	AdminEmail,
                        	Status,
                        	notes,
                        	CONVERT(varchar, eventdate, 103) + ' ' + LEFT(CONVERT(varchar, eventdate, 108), 5) AS eventdate,  -- Format DD/MM/YYYY HH:MM for eventdate
                            CONVERT(varchar, ReportDate, 103) + ' ' + LEFT(CONVERT(varchar, ReportDate, 108), 5) AS ReportDate,  --
                        	f_first,
                        	f_last,
                        	LocationName,
                        	Phone
                        FROM
                        	AdminReport
                        WHERE
                        	Status = 'Complete'
                        	AND CAst(ReportDate as DAte) = cast( GETDATE()-3 as DAte)
                        ORDER BY
                        	Status DESC,
                        	EventID;  
                """
                # Execute the SQL query
                cursor.execute(sql_query)

                # Fetch all rows from the executed query
                results = cursor.fetchall()
                if not results:
                    return Response('No Record Found')

                # Serialize the data
                serialized_data = []
                for row in results:
                    data = {
                        'd_First': row[0],
                        'd_middle_a': row[1],
                        'd_middle_b': row[2],
                        'd_Last': row[3],
                        'd_Address': row[4],
                        'd_Unit': row[5],
                        'd_City': row[6],
                        'd_Prov': row[7],
                        'd_Postal': row[8],
                        'd_DOB': row[9],
                        'd_BCN': row[10],
                        'd_DOD': row[11],
                        'd_SIN': row[12],
                        'FaxDate': row[13],
                        'BillingCode': row[14],
                        'OldLocation': row[15],
                        'Contract': row[16],
                        'AdminEmail': row[17],
                        'Status': row[18],
                        'notes': row[19],
                        'eventdate': row[20],
                        'ReportDate': row[21],
                        'f_first': row[22],
                        'f_last': row[23],
                        'LocationName': row[24],
                        'Phone': row[25]
                    }
                    serialized_data.append(data)

                return Response(serialized_data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def event_list_reports(request, days_ago):
    try:
        # Convert the passed parameter to an integer for safety
        days_ago = int(days_ago)

        if request.method == 'GET':
            with connection.cursor() as cursor:
                status_condition = ""
                if days_ago == 180:
                    status_condition = " AND Status = 'Complete'"

                if days_ago == 365:
                    status_condition = " AND Status = 'Complete'"

                if days_ago == 90:
                    status_condition = " AND (Status = 'Complete' OR Status IS NULL)"
                # Define the SQL query with dynamic days
                sql_query = f"""
                            SELECT
                            EventID,
                            CONVERT(varchar, eventdate, 103) + ' ' + LEFT(CONVERT(varchar, eventdate, 108), 5) AS eventdate,  -- Format DD/MM/YYYY HH:MM for eventdate
                        	d_First,
                        	d_middle_a,
                        	d_middle_b,
                        	d_Last,
                        	d_Address,
                        	d_Unit,
                        	d_City,
                        	d_Prov,
                        	d_Postal,
                        	CONVERT(nvarchar(10), CONVERT(date, d_DOB, 103), 103) AS d_DOB,
                        	d_BCN,
                        	CONVERT(nvarchar(10),	CONVERT(date,	d_DOD,	103),	103) as d_DOD,
                        	d_SIN,
                        	convert(varchar,	FaxDate,	103) as FaxDate,
                        	BillingCode,
                        	OldLocation,
                        	Contract,
                        	AdminEmail,
                        	Status,
                        	notes,
                            CONVERT(varchar, ReportDate, 103) + ' ' + LEFT(CONVERT(varchar, ReportDate, 108), 5) AS ReportDate,  --
                        	f_first,
                        	f_last,
                        	LocationName,
                        	Phone
                        FROM
                        	AdminReport
                        WHERE Cast(eventdate as DAte) >= cast( GETDATE() - %s as DAte)  {status_condition}
                        ORDER BY
                        	Status DESC,
                        	EventID;   
                """

                # Execute the SQL query
                cursor.execute(sql_query, [days_ago])

                # Fetch all rows from the executed query
                results = cursor.fetchall()
                if not results:
                    return Response('No Record Found')

                # Serialize the data
                serialized_data = []
                for row in results:
                    data = {
                            'EventID': row[0],
                            'eventdate': row[1],
                            'd_First': row[2],
                            'd_middle_a': row[3],
                            'd_middle_b': row[4],
                            'd_Last': row[5],
                            'd_Address': row[6],
                            'd_Unit': row[7],
                            'd_City': row[8],
                            'd_Prov': row[9],
                            'd_Postal': row[10],
                            'd_DOB': row[11],
                            'd_BCN': row[12],
                            'd_DOD': row[13],
                            'd_SIN': row[14],
                            'FaxDate': row[15],
                            'BillingCode': row[16],
                            'OldLocation': row[17],
                            'Contract': row[18],
                            'AdminEmail': row[19],
                            'Status': row[20],
                            'notes': row[21],
                            'ReportDate': row[22],
                            'f_first': row[23],
                            'f_last': row[24],
                            'LocationName': row[25],
                            'Phone': row[26]
                    }
                    serialized_data.append(data)

                return Response(serialized_data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def event_list_30(request):
    try:
        if request.method == 'GET':
            with connection.cursor() as cursor:
                # Define the SQL query
                sql_query = """
                    Select
                    	eventID,
                    	CONVERT(varchar, eventdate, 103) + ' ' + LEFT(CONVERT(varchar, eventdate, 108), 5) AS eventdate,
                    	d_First,
                    	d_middle_a,
                    	d_Last,
                    	CONVERT(nvarchar(10),	CONVERT(date,	d_DOD,	103),	103) as d_DOD,
                    	contract,
                    	convert(varchar,
                    	FaxDate,
                    	103) as FaxDate,
                    	notes,
                    	BillingCode,
                    	OldLocation,
                    	LocationName,
                    	f_first,
                    	f_last,
                    	CONVERT(varchar, ReportDate, 103) + ' ' + LEFT(CONVERT(varchar, ReportDate, 108), 5) AS ReportDate,
                    	Status,
                    	e_First,
                    	e_Middle,
                    	e_Last
                    From
                    	AdminReport
                    Where Cast(eventdate as DAte) >= cast( GETDATE()-30 as DAte)
                    ORDER BY EventID
                """
                # Execute the SQL query
                cursor.execute(sql_query)

                # Fetch all rows from the executed query
                results = cursor.fetchall()
                if not results:
                    return Response('No Record Found')

                # Serialize the data
                serialized_data = []
                for row in results:
                    data = {
                        'eventID': row[0],
                        'eventdate': row[1],
                        'd_First': row[2],
                        'd_middle_a': row[3],
                        'd_Last': row[4],
                        'd_DOD': row[5],
                        'contract': row[6],
                        'FaxDate': row[7],
                        'notes': row[8],
                        'BillingCode': row[9],
                        'OldLocation': row[10],
                        'LocationName': row[11],
                        'f_first': row[12],
                        'f_last': row[13],
                        'ReportDate': row[14],
                        'Status': row[15],
                        'e_First': row[16],
                        'e_Middle': row[17],
                        'e_Last': row[18]
                    }
                    serialized_data.append(data)

                return Response(serialized_data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def event_list_hold(request):
    try:
        if request.method == 'GET':
            with connection.cursor() as cursor:
                # Define the SQL query
                sql_query = """
                        	SELECT
                        	d_Unit,
                        	d_City,
                        	eventID,
                        	CONVERT(varchar, eventdate, 103) + ' ' + LEFT(CONVERT(varchar, eventdate, 108), 5) AS eventdate, 
                        	d_First,
                        	d_middle_a,
                        	d_middle_b,
                        	d_Last,
                        	CONVERT(nvarchar(10),
                        	CONVERT(date,
                        	d_DOB,
                        	103),
                        	103) as d_DOB,
                        
                        	d_SIN,
                        	Status,
                        	convert(varchar,
                        	FaxDate,
                        	103) as FaxDate,
                        	CONVERT(varchar, ReportDate, 103) + ' ' + LEFT(CONVERT(varchar, ReportDate, 108), 5) AS ReportDate,  
                        	notes,
                        	LocationName,
                        	Phone,
                        	BillingCode
                        FROM
                        	AdminReport
                        WHERE
                        	(Status = 'HOLD - Unsigned CA'
                        		AND (Cast(eventdate as DAte) >= cast( GETDATE()-270 as DAte)))
                        	OR 
                                                                (Status = 'HOLD - Missing CA'
                        		AND (Cast(eventdate as DAte) >= cast( GETDATE()-270 as DAte)))
                        	OR 
                                                                (Status = 'HOLD - Missing PO'
                        		AND (Cast(eventdate as DAte) >= cast( GETDATE()-270 as DAte)))
                        	OR 
                                                                (Status = 'HOLD - Missing POD'
                        		AND (Cast(eventdate as DAte) >= cast( GETDATE()-270 as DAte)))
                        	OR 
                                                                (Status = 'HOLD - Other'
                        		AND (Cast(eventdate as DAte) >= cast( GETDATE()-270 as DAte)))
                        ORDER BY
                        	Status DESC,
                        	EventID;
                """
                # Execute the SQL query
                cursor.execute(sql_query)

                # Fetch all rows from the executed query
                results = cursor.fetchall()
                if not results:
                    return Response('No Record Found')

                # Serialize the data
                serialized_data = []
                for row in results:
                    data = {
                        'd_Unit': row[0],
                        'd_City': row[1],
                        'eventID': row[2],
                        'eventdate': row[3],
                        'd_First': row[4],
                        'd_middle_a': row[5],
                        'd_middle_b': row[6],
                        'd_Last': row[7],
                        'd_DOB': row[8],
                        'd_SIN': row[9],
                        'Status': row[10],
                        'FaxDate': row[11],
                        'ReportDate': row[12],
                        'notes': row[13],
                        'LocationName': row[14],
                        'Phone': row[15],
                        'BillingCode': row[16]
                    }
                    serialized_data.append(data)

                return Response(serialized_data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



# class EventsListCreateView(generics.ListCreateAPIView):
#     queryset = PesEvents.objects.all()
#     serializer_class = EventsSerializer

#     def get(self, request, *args, **kwargs):
#         # Check for JWT in request cookies
#         token = request.COOKIES.get('jwt')

#         if not token:
#             return Response({'error': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

#         try:
#             payload = jwt.decode(token, 'secret', algorithms=['HS256'])
#         except jwt.ExpiredSignatureError:
#             return Response({'error': 'Authentication credentials were expired.'}, status=status.HTTP_401_UNAUTHORIZED)

#         return super().get(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         # Check for JWT in request cookies
#         token = request.COOKIES.get('jwt')
#         if not token:
#             return Response({'error': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

#         try:
#             payload = jwt.decode(token, 'secret', algorithms=['HS256'])
#         except jwt.ExpiredSignatureError:
#             return Response({'error': 'Authentication credentials were expired.'}, status=status.HTTP_401_UNAUTHORIZED)

#         return super().post(request, *args, **kwargs)

# class EventsRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = PesEvents.objects.all()
#     serializer_class = EventsSerializer

#     def put(self, request, *args, **kwargs):
#         # Check for JWT in request cookies
#         token = request.COOKIES.get('jwt')

#         if not token:
#             return Response({'error': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

#         try:
#             payload = jwt.decode(token, 'secret', algorithms=['HS256'])
#         except jwt.ExpiredSignatureError:
#             return Response({'error': 'Authentication credentials were expired.'}, status=status.HTTP_401_UNAUTHORIZED)

#         return super().put(request, *args, **kwargs)

#     def delete(self, request, *args, **kwargs):
#         # Check for JWT in request cookies
#         token = request.COOKIES.get('jwt')

#         if not token:
#             return Response({'error': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

#         try:
#             payload = jwt.decode(token, 'secret', algorithms=['HS256'])
#         except jwt.ExpiredSignatureError:
#             return Response({'error': 'Authentication credentials were expired.'}, status=status.HTTP_401_UNAUTHORIZED)

#         return super().delete(request, *args, **kwargs)

# class CustomJSONEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, date):
#             return obj.isoformat()
#         return super().default(obj)


# class PdfDownload(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = PdfDataSerializer(data=request.data)
        
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         data = serializer.validated_data
#         asp_net_api_url = "http://192.168.0.120:5001/api/pdf/PDFDownload"

#         try:
#             response = requests.post(asp_net_api_url, json=data)
#             response.raise_for_status()  # Raise an error if the response status code is not 2xx
#         except requests.HTTPError as e:
#             if e.response.status_code == 404:
#                 return Response({'error': 'Resource not found on ASP.NET API'}, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 error_msg = f"Internet Connection Error: {e}"
#                 return Response({'error': error_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#         if response.status_code == 200:
#             pdf = response.content
#             django_response = HttpResponse(pdf, content_type='application/pdf')
#             django_response['Content-Disposition'] = 'attachment; filename="download.pdf"'
#             return django_response
#         else:
#             error_msg = f"Failed to generate PDF: {response.text}"
#             return Response({'error': error_msg}, status=response.status_code)

# class ISPSource(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = PdfDataSerializer(data=request.data)
        
#         if not serializer.is_valid():
#             return Response({'error': 'Validation Error'}, status=status.HTTP_400_BAD_REQUEST)
        
#         data = serializer.validated_data

#         asp_net_api_url = "http://192.168.0.120:5001/api/pdf/ISPSource"

#         try:
#             response = requests.post(asp_net_api_url, json=data)

#             response.raise_for_status()  # Raise an error if the response status code is not 2xx
#         except requests.HTTPError as e:
#             if e.response.status_code == 404:
#                 return Response({'error': 'Resource not found on ASP.NET API'}, status=status.HTTP_404_NOT_FOUND)
#             else:
#                 error_msg = f"Internet Connection Error: {e}"
#                 return Response({'error': error_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#         if response.status_code == 200:
#             pdf = response.content
#             django_response = HttpResponse(pdf, content_type='application/pdf')
#             django_response['Content-Disposition'] = 'attachment; filename="download.pdf"'
#             return django_response
#         else:
#             error_msg = f"Failed to generate PDF: {response.text}"
#             return Response({'error': error_msg}, status=response.status_code)

from .pdf_utils import handle_pdf_request

# class PdfDownload(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = PdfDataSerializer(data=request.data)
        
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         data = serializer.validated_data
#         return handle_pdf_request(data, 'PDFDownload')

# class ISPSource(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = PdfDataSerializer(data=request.data)
        
#         if not serializer.is_valid():
#             return Response({'error': 'Validation Error'}, status=status.HTTP_400_BAD_REQUEST)
        
#         data = serializer.validated_data
#         return handle_pdf_request(data, 'ISPSource')

# views.py

from .pdf_utils import get_event_data
from .pdf_utils import get_event_data_report,get_fulldump_data

class CPPSource2024(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'CPPSource2024')


class CPPSurvivor(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'CPPSurvivor')

    

class NewCPPSurvivor(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'NewCPPSurvivor')

class CPPSource(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'CPPSource')

class CPPSurvivor2a(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'CPPSurvivor2a')

class CRAForm(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'CRAForm')

class SecondNewCPPSurvivor(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'SecondNewCPPSurvivor')    

class CRArep(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'CRArep')

class PODmargins(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'PODmargins')

class CPPStudent(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'CPPStudent')

class PODSource(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'PODSource')

class PrivacyPOD(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'PrivacyPOD')

class FDSSsource(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
     
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
     
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data
        return handle_pdf_request(data, 'FDSSsource')
class FDSDsource(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'FDSDsource')

class PrivacyFDSS(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'PrivacyFDSS')
class PrivacyFDSD(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'PrivacyFDSD')
class FDSDnoSIN(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'FDSDnoSIN')

class StatementofServices2022(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'StatementofServices2022')

class BCCIS(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'BCCIS')

class PdfDownload(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'PDFDownload')

class OASNotification(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'OASNotification')

class OASNotificationEA(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'OASNotificationEA')

class DeclarationLegalMarriage(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'DeclarationLegalMarriage')

class CommonLawUnion(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'CommonLawUnion')

class RSKANE(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'RSKANE')
class fspStatementofServices(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'fspStatementofServices')
class AOAFORM(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'AOAFORM')
from .pdf_utils import get_fsp_data_report    
class EABlankCA(APIView):
    def get(self, request, *args, **kwargs):
        username = request.query_params.get('username')  # Get 'username' from frontend request
        
        if not username:
            return JsonResponse({'error': 'Username is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_fsp_data_report(request, username)  # Fetch data using 'username'
        
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'EABlankCA')  # Send the data to your PDF handler


class AftercareTrackingSheet(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'AftercareTrackingSheet')
    
class EAAftercareTrackingSheet(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'EAAftercareTrackingSheet')
class ClientLetters(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'ClientLetters')
    
class EAWorkbook2024b(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'EAWorkbook2024b')
class ClientData(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'ClientData')
class BCClientData(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        username = request.query_params.get('User')
        
        if not eventID or not username:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_event_data_report(request, eventID, username)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'BCClientData')
class StatementofServiceFR(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        ExecutorUsername = request.query_params.get('User')
        
        if not eventID or not ExecutorUsername:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        data = get_fulldump_data(request, eventID, ExecutorUsername)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'StatementofServiceFR')
class ClientAgreementFR(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        ExecutorUsername = request.query_params.get('User')
        
        if not eventID or not ExecutorUsername:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        data = get_fulldump_data(request, eventID, ExecutorUsername)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'ClientAgreementFR')
class QPPfr(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        ExecutorUsername = request.query_params.get('User')
        
        if not eventID or not ExecutorUsername:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        data = get_fulldump_data(request, eventID, ExecutorUsername)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'QPPfr')
class QPPSource(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        ExecutorUsername = request.query_params.get('User')
        
        if not eventID or not ExecutorUsername:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        data = get_fulldump_data(request, eventID, ExecutorUsername)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'QPPSource')
class CPP_Source_FR(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        ExecutorUsername = request.query_params.get('User')
        
        if not eventID or not ExecutorUsername:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        data = get_fulldump_data(request, eventID, ExecutorUsername)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'CPP_Source_FR')
class CRASource_FR(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        ExecutorUsername = request.query_params.get('User')
        
        if not eventID or not ExecutorUsername:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        data = get_fulldump_data(request, eventID, ExecutorUsername)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'CRASource_FR')
class SurvivorSource_FR(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        ExecutorUsername = request.query_params.get('User')
        
        if not eventID or not ExecutorUsername:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        data = get_fulldump_data(request, eventID, ExecutorUsername)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'SurvivorSource_FR')
class OASNotif_FR(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        ExecutorUsername = request.query_params.get('User')
        
        if not eventID or not ExecutorUsername:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        data = get_fulldump_data(request, eventID, ExecutorUsername)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'OASNotif_FR')
class ASBForm(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        ExecutorUsername = request.query_params.get('User')
        
        if not eventID or not ExecutorUsername:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        data = get_fulldump_data(request, eventID, ExecutorUsername)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'ASBForm')
# class FDSDsource(APIView):
#     def get(self, request, *args, **kwargs):
#         eventID = request.query_params.get('EventID')
#         username = request.query_params.get('User')
        
#         if not eventID or not username:
#             return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
#         data = get_fulldump_data(request, eventID, username)
#         if isinstance(data, Response):
#             return data

#         return handle_pdf_request(data, 'FDSDsource')
# class PrivacyFDSD(APIView):
#     def get(self, request, *args, **kwargs):
#         eventID = request.query_params.get('EventID')
#         username = request.query_params.get('User')
        
#         if not eventID or not username:
#             return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
#         data = get_fulldump_data(request, eventID, username)
#         if isinstance(data, Response):
#             return data

#         return handle_pdf_request(data, 'PrivacyFDSD')
    
class EAWebsiteLetter(APIView):
    def get(self, request, *args, **kwargs):
        eventID = request.query_params.get('EventID')
        ExecutorUsername = request.query_params.get('User')
        
        if not eventID or not ExecutorUsername:
            return JsonResponse({'error': 'EventID and User parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        data = get_fulldump_data(request, eventID, ExecutorUsername)
        if isinstance(data, Response):
            return data

        return handle_pdf_request(data, 'EAWebsiteLetter')
    
from .serializers import PesEventsSearchSerializer
from django.db.models import Q
from .managers import FullDumpManager
from django.db import DatabaseError

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def search_pes_events(request):
    try:
        manager = FullDumpManager()

        d_sin = request.query_params.get('d_SIN', None)
        d_last = request.query_params.get('d_Last', None)
        d_first = request.query_params.get('d_First', None)
        e_last = request.query_params.get('e_Last', None)
        billingcode = request.query_params.get('BillingCode', None)
        contract = request.query_params.get('contract', None)

        filters = {}
        if d_sin:
            filters['d_sin'] = d_sin
        if d_last:
            filters['d_last'] = d_last
        if d_first:
            filters['d_first'] = d_first
        if e_last:
            filters['e_last'] = e_last
        if billingcode:
            filters['billingcode'] = billingcode
        if contract:
            filters['contract'] = contract

        queryset = manager.search(**filters)
        if "error" in queryset:
            return Response(queryset)

        # Pagination
        #paginator = PageNumberPagination()
        #paginator.page_size = None
        #result_page = paginator.paginate_queryset(queryset, request)

        #serializer = PesEventsSearchSerializer(result_page, many=True)
        #return paginator.get_paginated_response(serializer.data)
        return Response(queryset)

    except DatabaseError as db_err:
        return Response({"error": f"Database error: {str(db_err)}"}, status=500)
    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


from .serializers import UpdatesSerializer

@api_view(['GET'])
def get_all_updates(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Updates ORDER BY UpdateID")
            rows = cursor.fetchall()

            # Get column names
            columns = [col[0] for col in cursor.description]

            # Convert rows to list of dictionaries
            updates = [dict(zip(columns, row)) for row in rows]

        # Serialize the data
        serializer = UpdatesSerializer(updates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from datetime import datetime, timedelta
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_full_dump(request,event_id):
    #return Response({"sss": 4}, status=status.HTTP_200_OK)

    # Define your SQL query
    sql_query = "SELECT * FROM PesFullDump WHERE EventID = %s"
    with connection.cursor() as cursor:
        cursor.execute(sql_query, [event_id])
        row = cursor.fetchone()
        if row is None:
            return Response({"error": "eventid not found pesfulldump" }, status=status.HTTP_404_NOT_FOUND)
        
        result = {
            'EventID': row[0],
        }
        print(result)

        sql_query2 = "SELECT TOP 1 EventUpdateFaxDate AS MaxOfFax, EventUpdateReportDate AS MaxOfReport FROM EventUpdates ORDER BY EventUpdateID DESC"
        cursor.execute(sql_query2)
        row2 = cursor.fetchone()

        if row2 is None:
            dtmLastFax = datetime.today() - timedelta(days=1)
            dtmLastReport = datetime.today()
        else:
            if row2[0] is None:
                dtmLastFax = datetime.today() - timedelta(days=1)
            else:
                dtmLastFax = row2[0]

            if row2[1] is None:
                dtmLastReport = datetime.today() - timedelta(days=1)
            else:
                dtmLastReport = row2[1]

        # Add the additional data to the result dictionary
        result['MaxOfFax'] = dtmLastFax.strftime("%d/%m/%Y")
        result['MaxOfReport'] = dtmLastReport.strftime("%d/%m/%Y")
        #result['MaxOfFax'] = dtmLastFax
        #result['MaxOfReport'] = dtmLastReport

        return Response(result, status=status.HTTP_200_OK)

class AuthMixin(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

class LocationListCreate(AuthMixin,generics.ListCreateAPIView):
    queryset = Locations.objects.all()
    serializer_class = LocationsSerializer


class AdminReportLocations(AuthMixin,generics.ListCreateAPIView):
    queryset = Locations.objects.all().order_by('locationid')
    serializer_class = LocationsSerializer
    pagination_class = None  

class LocationDetailAPIView(AuthMixin,generics.RetrieveUpdateDestroyAPIView):
    queryset = Locations.objects.all()
    serializer_class = LocationsSerializer

from .serializers import FSPsSerializer
from rest_framework.exceptions import ValidationError
from .models import FSPs

class FSPsListCreate(AuthMixin,generics.ListCreateAPIView):
    queryset = FSPs.objects.all()
    serializer_class = FSPsSerializer

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def perform_create(request):
    if request.method == 'POST':
        try:
            username = request.data.get('username')
            password = request.data.get('password')

            if not username or not password:
                return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

            request.data["email"] = username  # Set email as username

            # Encrypt the password
            encrypted_password = make_password(password)

            # Save FSPs object with the encrypted password
            serializer = FSPsSerializer(data=request.data)
            if serializer.is_valid():
                fsp_instance = serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user already exists in the User table
            if not User.objects.filter(username=username).exists():
                try:
                    user = User.objects.create_user(username=username, password=password)
                    user.is_superuser = False
                    user.is_staff = True
                    user.save()
                except Exception as e:
                    # If the user creation fails, delete the FSPs record that was just created
                    fsp_instance.delete()
                    return Response({"error": f"User creation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"error": "User with this username already exists."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Record created successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Request Fail: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FSPsDetailAPIView(AuthMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = FSPs.objects.all()
    serializer_class = FSPsSerializer

    def update(self, request, *args, **kwargs):
        # Perform the default update operation
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Retrieve the current username associated with this FSPs instance
        current_username = instance.username  # Assuming FSPs has a username field

        # Check if the username or password needs to be updated
        new_username = request.data.get('username')
        new_password = request.data.get('password')

        # Proceed only if new username or password is provided
        if new_username or new_password:
            try:
                # Retrieve the User object where username matches the FSPs username
                user, created = User.objects.get_or_create(username=current_username)

                # If a new User was created, it means it didn't exist before
                if created:
                    # Optionally, set other fields for the new User object here
                    user.username = new_username or current_username
                    if new_password:
                        user.set_password(new_password)  # Hash the password using set_password
                        user.is_superuser=False
                        user.is_staff=True
                    user.save()
                else:
                    # Update username and/or password in the User table
                    if new_username:
                        user.username = new_username
                    if new_password:
                        user.set_password(new_password)  # Hash the password using set_password
                    user.save()

                # After updating the User table, update the FSPs table
                instance.username = new_username or instance.username  # Update the FSPs table with the new username
                serializer.save()

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        else:
            # If no username or password change, just perform the default update
            serializer.save()

        return Response(serializer.data)






class FSPsByLocationIDView(AuthMixin):
    def get(self, request, locationid, format=None):
        try:
            fsps_record = FSPs.objects.filter(locationid=locationid).order_by('fspid')
            if not fsps_record.exists():
                return Response({"message": "No User Found"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = FSPsSerializer(fsps_record, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class LocationCreate(APIView):
#     def post(self, request):
#         serializer = Locations(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class LocationDetailAPIView(APIView):
#     def get_object(self, pk):
#         try:
#             return Locations.objects.get(pk=pk)
#         except Locations.DoesNotExist:
#             return Response("Record Does not exist")

#     def get(self, request, pk):
#         location = self.get_object(pk)
#         serializer = Locations(location)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         location = self.get_object(pk)
#         serializer = Locations(location, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         location = self.get_object(pk)
#         location.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class AdminReportFSPs(generics.ListAPIView):
    queryset = FSPs.objects.all().order_by('fspid')  # Order by FSPID
    serializer_class = FSPsSerializer
    pagination_class = None  # Disable pagination

    def get_queryset(self):
        """
        Optionally restricts the returned results by filtering against a `status` query parameter.
        """
        queryset = FSPs.objects.all().order_by('fspid')
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset
