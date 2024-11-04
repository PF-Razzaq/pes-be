# pdf_utils.py

import os
import requests
from django.http import HttpResponse,JsonResponse
from rest_framework import status
from rest_framework.response import Response
from django.db import connection
from django.shortcuts import get_object_or_404
from .models import PesEvents,PesFullDump




endpoint_to_filename = {
    'PDFDownload': 'ClientAgreement2024',
    'OASNotification': 'OASNotification',
    'OASNotificationEA': 'OASNotificationEA',
    'CRAForm': 'CRA',
    'CPPSource': 'cpp',
    'CPPSurvivor': 'Survivor',
    'CPPSurvivor2a': 'Survivor2',
    'CRArep': 'CRArep',
    'CPPStudent': 'CPP Student Benefit',
    'BCCIS': 'BC Client Information Sheet',
    'PODSource': 'POD',
    'PODmargins': 'PODmargins',
    'PrivacyPOD': 'POD',
    'FDSSsource': 'FDSS',
    'PrivacyFDSS': 'POD',
    'CommonLawUnion': 'CommonLawUnion',
    'DeclarationLegalMarriage': 'DeclarationLegalMarriage',
    'StatementofServices2022': 'SOS',
    'RSKANE': 'PODmargins',
    'AOAFORM': 'EAClientAgreement',
    'EABlankCA': 'EABlankCA',
    'fspStatementofServices': 'SOS',
    "ClientLetters":"ClientLetters",
    "AftercareTrackingSheet":"AftercareTrackingSheet",
    "EAWorkbook2024b":"EAWorkbook",
    "EAWebsiteLetter":"EAWebsiteLetter",
    "ClientAgreementFR":"ClientAgreementFR",
    "StatementofServiceFR":"StatementofServiceFR",
    "FDSDsource":"FDSDsource",
    "PrivacyFDSD":"PrivacyFDSD",
    "FDSDnoSIN":"FDSDnoSIN",
    "QPPfr":"QPPfr",
    "QPPSource":"QPPSource",
    "CPP_Source_FR":"CPP_Source_FR",
    "CRASource_FR":"CRASource_FR",
    "OASNotif_FR":"OASNotif_FR",
    "SurvivorSource_FR":"SurvivorSource_FR",
    "EAAftercareTrackingSheet":"EAAftercareTrackingSheet",
    "ASBForm":"ASBForm",
    "CPPSource2024":"CPP Death Benefit",
    "SecondNewCPPSurvivor":"AllowanceInfo",
    "NewCPPSurvivor":"AllowanceApp",
    "BCClientData":"BCClientData",
    "ClientData":"ClientData",

}

def handle_pdf_request(data, endpoint):
    base_url = os.getenv('DOTNET_PDF_BACKEND')
    if base_url is None:
        return JsonResponse({'error': "Environment variable 'DOTNET_PDF_BACKEND' is not set."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    asp_net_api_url = f"{base_url.rstrip('/')}/{endpoint}"
    try:
        response = requests.post(asp_net_api_url, json=data)
        response.raise_for_status()  # Raise an error if the response status code is not 2xx
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return JsonResponse({'error': f'URL not Found: {e}'}, status=status.HTTP_404_NOT_FOUND)
        else:
            error_message = e.response.text  # Get the error message from the response
            error_status = e.response.status_code  # Get the status code from the response
            return JsonResponse({'error': f"HTTP error: {error_message}", 'data': data}, status=error_status)
    except requests.exceptions.ConnectionError as e:
        return JsonResponse({'error': f"Cannot connect to Asp.net: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except requests.exceptions.Timeout as e:
        return JsonResponse({'error': f"Timeout error: {e}"}, status=status.HTTP_504_GATEWAY_TIMEOUT)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f"Request error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return JsonResponse({'error': f"Unexpected error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if response.status_code == 200:
        pdf = response.content
        # Set the filename based on the endpoint
        filename = endpoint_to_filename.get(endpoint, 'default') + '.pdf'
        django_response = HttpResponse(pdf, content_type='application/pdf')
        django_response['Content-Disposition'] = f'inline; filename="{filename}"'
        return django_response
    else:
        error_msg = f"Failed to generate PDF: {response.text}"
        return JsonResponse({'error': error_msg}, status=response.status_code)


def get_location_name(username):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                l.LocationName,
                l.City,
                l.Prov,
                l.Address,
                l.Phone,
                l.PostalCode,
                l.ServiceName,
                f.f_first,
                f.f_last
            FROM 
                FSPs f
            INNER JOIN 
                pes_user pu ON pu.username = f.Username AND pu.username = %s
            INNER JOIN 
                Locations l ON f.LocationID = l.LocationID
        """, [username])

        location_details = cursor.fetchone()
    if location_details:
        return location_details
    else:
        return None, None, None, None, None, None, None, None, None
    
from .models import FSPs
def get_fsp_data_report(request, username):
    try:
        # Fetch the record using username instead of fspid
        fsp = get_object_or_404(FSPs, username=username)
        
        # Get location name and other related data using username
        location_name, city, prov, address, phone, postalCode, ServiceName, f_First, f_Last = get_location_name(username)

        data = {
            'LocationName': location_name if location_name else '',
            'City': city if city else '',
            'Prov': prov if prov else '',
            'address': address if address else '',
            'phone': phone if phone else '',
            'postalCode': postalCode if postalCode else '',
            'ServiceName': ServiceName if ServiceName else '',
            'f_first': f_First,
            'f_last': f_Last
        }

        return data
    except Exception as e:
        return Response({'error': f'Data not found: {e}'}, status=status.HTTP_404_NOT_FOUND)



def get_event_data(request):
    try:
        event_id = request.data.get('eventID')
        if not event_id:
            return {'error': 'ID is required'}

        event = get_object_or_404(PesEvents, pk=event_id)

        data = {
            'd_First': str(event.d_First),
            'd_middle_a': str(event.d_middle_a),
            'd_middle_b': str(event.d_middle_b),
            'd_Last': str(event.d_Last),
            'd_Maiden': str(event.d_Maiden),
            'd_Address': str(event.d_Address),
            'd_Unit': str(event.d_Unit),
            'd_City': str(event.d_City),
            'd_Prov': str(event.d_Prov),
            'd_Postal': str(event.d_Postal),
            'd_AreaCode': str(event.d_AreaCode),
            'd_exchange': str(event.d_exchange),
            'd_phone': str(event.d_phone),
            'd_DOB': event.d_DOB,
            'd_birth_Country': str(event.d_birth_Country),
            'd_birth_City': str(event.d_birth_City),
            'd_birth_Prov': str(event.d_birth_Prov),
            'd_DOD': event.d_DOD,
            'd_death_Country': str(event.d_death_Country),
            'd_death_City': str(event.d_death_City),
            'd_death_Prov': str(event.d_death_Prov),
            'd_death_age': str(event.d_death_age),
            'd_dispdate': event.d_dispdate,
            'd_disp_Name': str(event.d_disp_Name),
            'd_SIN': str(event.d_SIN),
            'e_Salutation': str(event.e_Salutation),
            'e_First': str(event.e_First),
            'e_Initial': str(event.e_Initial),
            'e_Last': str(event.e_Last),
            'e_Address': str(event.e_Address),
            'e_Unit': str(event.e_Unit),
            'e_City': str(event.e_City),
            'e_Prov': str(event.e_Prov),
            'e_Postal': str(event.e_Postal),
            'e_AreaCode': str(event.e_AreaCode),
            'e_exchange': str(event.e_exchange),
            'e_phone_4': str(event.e_phone_4),
            'e_relationship': str(event.e_relationship)
        }
        return data
    except Exception as e:
        return {'error': f'Event Data Not found{e}'}


def get_event_data_report(request, eventID, username):
    try:
        event = get_object_or_404(PesEvents, pk=eventID)

        location_name, city, prov, address, phone, postalCode, ServiceName, f_First, f_Last = get_location_name(username)

        data = {
            'd_First': str(event.d_First),
            'd_middle_a': str(event.d_middle_a),
            'd_middle_b': str(event.d_middle_b),
            'd_Last': str(event.d_Last),
            'd_Maiden': str(event.d_Maiden) if event.d_Maiden else '',
            'd_Address': str(event.d_Address) if event.d_Address else '',
            'd_Unit': str(event.d_Unit) if event.d_Unit else '',
            'd_City': str(event.d_City) if event.d_City else '',
            'd_Prov': str(event.d_Prov) if event.d_Prov else '',
            'd_Postal': str(event.d_Postal) if event.d_Postal else '',
            'd_AreaCode': str(event.d_AreaCode) if event.d_AreaCode else '',
            'd_exchange': str(event.d_exchange) if event.d_exchange else '',
            'd_phone': str(event.d_phone) if event.d_phone else '',
            'd_DOB': str(event.d_DOB) if event.d_DOB else '1900-01-01',
            'd_birth_Country': str(event.d_birth_Country) if event.d_birth_Country else '',
            'd_birth_City': str(event.d_birth_City) if event.d_birth_City else '',
            'd_birth_Prov': str(event.d_birth_Prov) if event.d_birth_Prov else '',
            'd_DOD': str(event.d_DOD) if event.d_DOD else '1900-01-01',
            'd_death_Country': str(event.d_death_Country) if event.d_death_Country else '',
            'd_death_City': str(event.d_death_City) if event.d_death_City else '',
            'd_death_Prov': str(event.d_death_Prov) if event.d_death_Prov else '',
            'd_death_age': str(event.d_death_age) if event.d_death_age else '0',
            # Remove default value 1900
            'd_dispdate': str(event.d_dispdate) if event.d_dispdate else '',
            'd_disp_Name': str(event.d_disp_Name) if event.d_disp_Name else '',
            'd_SIN': str(event.d_SIN) if event.d_SIN else '',
            'e_Salutation': str(event.e_Salutation) if event.e_Salutation else '',
            'e_First': str(event.e_First) if event.e_First else '',
            'e_Initial': str(event.e_Initial) if event.e_Initial else '',
            'e_Last': str(event.e_Last) if event.e_Last else '',
            'e_Address': str(event.e_Address) if event.e_Address else '',
            'e_Unit': str(event.e_Unit) if event.e_Unit else '',
            'e_City': str(event.e_City) if event.e_City else '',
            'e_Prov': str(event.e_Prov) if event.e_Prov else '',
            'e_Postal': str(event.e_Postal) if event.e_Postal else '',
            'e_AreaCode': str(event.e_AreaCode) if event.e_AreaCode else '',
            'e_exchange': str(event.e_exchange) if event.e_exchange else '',
            'e_phone_4': str(event.e_phone_4) if event.e_phone_4 else '',
            'e_relationship': str(event.e_relationship) if event.e_relationship else '',
            'd_Country': str(event.d_Country) if event.d_Country else '',
            'e_Country': str(event.e_Country) if event.e_Country else '',
            'LocationName': location_name if location_name else '',
            'City': city if city else '',
            'Prov': prov if prov else '',
            'address': address if address else '',
            'phone': phone if phone else '',
            'postalCode': postalCode if postalCode else '',
            'username': username if username else '',
            'ServiceName': ServiceName if ServiceName else '',
            'f_first': f_First,
            'f_last': f_Last
        }

        return data
    except Exception as e:
        return Response({'error': f'Event data not found: {e}'}, status=status.HTTP_404_NOT_FOUND)

import datetime
from dateutil import parser
from datetime import datetime
def format_date(date_value):
    if date_value:
        try:
            if isinstance(date_value, datetime.datetime):
                return date_value.strftime('%Y-%m-%d')
            elif isinstance(date_value, str):
                # Assuming the string is in a known date format
                return datetime.datetime.strptime(date_value, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            pass
    return '2004-02-01'
def convert_to_yyyy_mm_dd(date_str):
    try:
        # Parse the date string to a datetime object
        parsed_date = parser.parse(date_str)
        # Format the datetime object to the desired format
        formatted_date = parsed_date.strftime('%Y-%m-%d')
        return formatted_date
    except (ValueError, OverflowError) as e:
        return '2004-02-02'  # Default date in case of error
def get_fulldump_data(request, eventID, ExecutorUsername):
    try:
        event = get_object_or_404(PesFullDump, eventID=eventID)

        data = {
    'd_First': str(event.d_first) if event.d_first else '',
    'd_middle_a': str(event.d_middle_a) if event.d_middle_a else '',
    'd_middle_b': str(event.d_middle_b) if event.d_middle_b else '',
    'd_Last': str(event.d_last) if event.d_last else '',
    'd_exchange': str(event.d_exchange) if event.d_exchange else '',
    'd_phone': str(event.d_phone) if event.d_phone else '',
    'd_death_age': str(event.d_death_age) if event.d_death_age else '',
    'd_dispdate': str(event.d_dispdate1) if event.d_dispdate1 else '',
    'e_first': str(event.e_first) if event.e_first else '',
    'e_Last': str(event.e_last) if event.e_last else '',
    'e_address': str(event.e_address) if event.e_address else '',
    'e_unit': str(event.e_unit) if event.e_unit else '',
    'e_City': str(event.e_city) if event.e_city else '',
    'e_Prov': str(event.e_prov) if event.e_prov else '',
    'e_Postal': str(event.e_postal) if event.e_postal else '',
    'e_exchange': str(event.e_exchange) if event.e_exchange else '',
    'e_phone_4': str(event.e_phone_4) if event.e_phone_4 else '',
    'e_relationship': str(event.e_relationship) if event.e_relationship else '',
    'ExecutorUsername': str(event.executorusername) if event.executorusername else '',
    'ExecutorPassword': str(event.executorpassword) if event.executorpassword else '',
    'LocationName': str(event.locationname) if event.locationname else '',
    'f_first': str(event.f_first) if event.f_first else '',
    'f_last': str(event.f_last) if event.f_last else '',
    'f_Company': str(event.locationname) if event.locationname else '',
    'contract': str(event.contract) if event.contract else '',
    'e_Initial': str(event.e_initial) if event.e_initial else '',
    'd_City': str(event.d_city) if event.d_city else '',
    'd_Prov': str(event.d_prov) if event.d_prov else '',
    'e_Salutation': str(event.e_salutation) if event.e_salutation else '',
    'd_maiden': str(event.d_maiden) if event.d_maiden else '',
    'd_birth_city': str(event.d_birth_city) if event.d_birth_city else '',
    'd_birth_prov': str(event.d_birth_prov) if event.d_birth_prov else '',
    'd_birth_country': str(event.d_birth_country) if event.d_birth_country else '',
    'd_death_city': str(event.d_death_city) if event.d_death_city else '',
    'd_death_prov': str(event.d_death_prov) if event.d_death_prov else '',
    'd_death_country': str(event.d_death_country) if event.d_death_country else '',
    'd_address': str(event.d_address) if event.d_address else '',
    'd_unit': str(event.d_unit) if event.d_unit else '',
    'd_postal': str(event.d_postal) if event.d_postal else '',
    'd_sin': str(event.d_sin) if event.d_sin else '',
    'e_AreaCode': str(event.e_areacode) if event.e_areacode else '',
    'postalcode': str(event.postalcode) if event.postalcode else '',
    'prov': str(event.prov) if event.prov else '',
    'city': str(event.city) if event.city else '',
    'address': str(event.address) if event.address else '',
    'phone': str(event.phone) if event.phone else '',
    'd_country': str(event.d_country) if event.d_country else '',
    'e_country': str(event.e_country) if event.e_country else '',

    # 'd_dob':'2004-02-02',
    # 'd_dod':'2004-02-02',
    # 'd_dob': format_date(event.d_dob),
    # 'd_dod': format_date(event.d_dod),
    'd_dob': convert_to_yyyy_mm_dd(str(event.d_dob)) if event.d_dob else '2004-02-02',
    'd_dod': convert_to_yyyy_mm_dd(str(event.d_dod)) if event.d_dod else '2004-02-02',
    'city': str(event.city) if event.city else '',
    'prov': str(event.prov) if event.prov else '',
}


        return data
    except Exception as e:
        return {'error': f'PesFullDump Data Not found{e}'}