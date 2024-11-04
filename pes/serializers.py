from rest_framework import serializers
from .models import User,PesEvents,Locations,FSPs
from datetime import datetime
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password','otpCode']
        # extra_kwargs = {
        #     'password': {'write_only': True}
        # }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    otpCode = serializers.CharField(required=True)

    def validate_password(self, value):
        # Implement any password validation logic here
        return value
    


from datetime import datetime,date


class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PesEvents
        fields = '__all__'
     
    def to_representation(self, instance):
        getdate = super().to_representation(instance)
        
        getdate['FaxDate'] = instance.FaxDate.strftime('%d/%m/%Y') if instance.FaxDate else None
        getdate['ReportDate'] = instance.ReportDate.strftime('%d/%m/%Y') if instance.ReportDate else None

        def format_date(date_value):
            if not date_value:
                return None
            if isinstance(date_value, (datetime, date)):
                return date_value.strftime('%d/%m/%Y')
            elif isinstance(date_value, str):
                for fmt in ('%Y-%m-%d', '%b %d %Y %I:%M%p'):
                    try:
                        return datetime.strptime(date_value, fmt).strftime('%d/%m/%Y')
                    except ValueError:
                        continue
                return date_value
            return date_value

        getdate['d_DOB'] = format_date(instance.d_DOB)
        getdate['d_DOD'] = format_date(instance.d_DOD)
        getdate['d_dispdate'] = format_date(instance.d_dispdate)

        return getdate



class PdfDataSerializer(serializers.Serializer):
    LocationName = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    city = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    prov = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    postalcode = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    Phone = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    Address = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_First = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_middle_a = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_middle_b = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_Last = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_Maiden = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_Address = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_Unit = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_City = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_Prov = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_Postal = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_AreaCode = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_exchange = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_phone = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_DOB = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_birth_Country = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_birth_City = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_birth_Prov = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_DOD = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_death_Country = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_death_City = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_death_Prov = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_death_age = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_dispdate = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_disp_Name = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    d_SIN = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_Salutation = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_First = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_Initial = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_Last = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_Address = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_Unit = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_City = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_Prov = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_Postal = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_AreaCode = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_exchange = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_phone_4 = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_relationship = serializers.CharField(allow_null=True, allow_blank=True, required=False)



class PesEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PesEvents
        fields = [
            'd_First', 'd_middle_a', 'd_middle_b', 'd_Last', 'd_Address', 'd_Unit', 'd_City',
            'd_Prov', 'd_Postal', 'd_DOB', 'd_BCN', 'd_DOD', 'd_SIN', 'FaxDate', 'BillingCode',
            'OldLocation', 'Contract', 'AdminEmail', 'Status', 'notes', 'eventdate', 'ReportDate',
            'f_first', 'f_last', 'LocationName', 'Phone'
        ]

# class PesEventsSearchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PesEvents
#         fields = ['Status', 'eventdate', 'FaxDate', 'notes', 'ReportDate']

class PesEventsSearchSerializer(serializers.Serializer):
    eventID = serializers.IntegerField()
    d_SIN = serializers.CharField()
    Status = serializers.CharField()
    d_First = serializers.CharField()
    d_Last = serializers.CharField()
    e_Last = serializers.CharField()
    eventDate = serializers.DateTimeField()
    d_DOB = serializers.CharField()
    Contract = serializers.CharField()
    BillingCode= serializers.CharField()


class UpdatesSerializer(serializers.Serializer):
    UpdateID = serializers.IntegerField()
    UpdateDesc = serializers.CharField()

class LocationsSerializer(serializers.ModelSerializer):
    dateadded = serializers.DateTimeField(format='%d/%m/%Y %H:%M', required=False, allow_null=True)
    class Meta:
        model = Locations
        fields = '__all__'

class FSPsSerializer(serializers.ModelSerializer):
    lastaccessed = serializers.DateTimeField(
        format='%d/%m/%Y %H:%M',
        input_formats=['%d/%m/%Y %H:%M', 'iso-8601'],
        required=False,
        allow_null=True
    )
    fspdateadded = serializers.DateTimeField(
        format='%d/%m/%Y %H:%M',
        input_formats=['%d/%m/%Y %H:%M', 'iso-8601'],
        required=False,
        allow_null=True
    )

    class Meta:
        model = FSPs
        fields = (
            'fspid', 'status', 'f_first', 'f_last', 'fspphone', 'fspemail', 'username',
            'password', 'jobtitle', 'oldid', 'fspdateadded', 'lastaccessed', 'logincount',
            'languageid', 'routingid', 'locationid'
        )

from .models import Modifier,Aftercare,Aftercare360,Country

class ModifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modifier

        fields = '__all__'
class AftercareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aftercare
        fields = '__all__'
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['name', 'name_value']

class Aftercare360Serializer(serializers.ModelSerializer):
    class Meta:
        model = Aftercare360
        fields = '__all__'

class FSPsSerializerData(serializers.ModelSerializer):
    class Meta:
        model = FSPs
        fields = [
            'fspid', 'locationid', 'status', 'f_first', 'f_last',
            'fspphone', 'fspemail', 'username', 'password', 'jobtitle',
            'oldid', 'fspdateadded', 'lastaccessed', 'logincount', 'languageid', 'routingid'
        ]