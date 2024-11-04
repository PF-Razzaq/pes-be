import pytz
from .models import PesFullDump
from django.core.exceptions import FieldError
from django.db import DatabaseError
from datetime import datetime

class FullDumpManager:
    def search(self, **kwargs):
        try:
            # Start with all entries
            queryset = PesFullDump.objects.all()

            # Apply filters based on provided kwargs
            if 'd_sin' in kwargs and kwargs['d_sin']:
                queryset = queryset.filter(d_sin__startswith=kwargs['d_sin'])
            if 'd_last' in kwargs and kwargs['d_last']:
                queryset = queryset.filter(d_last__startswith=kwargs['d_last'])
            if 'd_first' in kwargs and kwargs['d_first']:
                queryset = queryset.filter(d_first__startswith=kwargs['d_first'])
            if 'e_last' in kwargs and kwargs['e_last']:
                queryset = queryset.filter(e_last__startswith=kwargs['e_last'])
            if 'billingcode' in kwargs and kwargs['billingcode']:
                queryset = queryset.filter(billingcode__startswith=kwargs['billingcode'])
            if 'contract' in kwargs and kwargs['contract']:
                queryset = queryset.filter(contract__startswith=kwargs['contract'])

            # Order by eventdate
            queryset = queryset.order_by('eventdate')

            # Convert to list of dictionaries with formatted dates
            results = []
            for instance in queryset:
                # Example: default timezone to 'America/Toronto'
                result = {
                    'eventID': instance.eventID,
                    'eventDate': self.format_date_with_timezone(instance.eventdate, 'Canada/Eastern') if instance.eventdate else None,
                    'd_SIN': instance.d_sin,
                    'd_First': instance.d_first,
                    'd_Last': instance.d_last,
                    'd_DOB': instance.d_dob,
                    'e_Last': instance.e_last,
                    'Contract': instance.contract,
                    'Status': instance.status,
                    'BillingCode': instance.billingcode,
                }
                results.append(result)

            if not results:
                return {"error": "No results found."}

            return results

        except FieldError as fe:
            return {"error": f"Field error: {str(fe)}"}
        except DatabaseError as db_err:
            return {"error": f"Database error: {str(db_err)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

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

    def format_date(self, date_value):
        if not date_value:
            return None
        if isinstance(date_value, datetime):
            return date_value.strftime('%d/%m/%Y')
        elif isinstance(date_value, str):
            for fmt in ('%Y-%m-%d', '%b %d %Y %I:%M%p'):
                try:
                    return datetime.strptime(date_value, fmt).strftime('%d/%m/%Y')
                except ValueError:
                    continue
            return date_value
