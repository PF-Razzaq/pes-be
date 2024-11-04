from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True, default='admin')
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    otpCode = models.CharField(max_length=4 ,blank=True,null=True)


    REQUIRED_FIELDS = [ 'email']

    def __str__(self):
        return self.username


class PesEvents(models.Model):
    eventID = models.BigAutoField(primary_key=True)
    OLDdID = models.IntegerField(null=True, blank=True)
    FSPID = models.IntegerField(null=True, blank=True)
    eventdate = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    Created_date = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    Modify_date = models.DateTimeField(null=True, blank=True, auto_now=True)
    d_First = models.CharField(max_length=75, null=True, blank=True)
    d_middle_a = models.CharField(max_length=75, null=True, blank=True)
    d_middle_b = models.CharField(max_length=75, null=True, blank=True)
    d_Last = models.CharField(max_length=125, null=True, blank=True)
    d_Maiden = models.CharField(max_length=125, null=True, blank=True)
    d_Address = models.CharField(max_length=255, null=True, blank=True)
    d_Unit = models.CharField(max_length=50, null=True, blank=True)
    d_City = models.CharField(max_length=125, null=True, blank=True)
    d_Prov = models.CharField(max_length=3, null=True, blank=True)
    d_Postal = models.CharField(max_length=20,null=True, blank=True)
    d_AreaCode = models.CharField(max_length=10, null=True, blank=True)
    d_exchange = models.CharField(max_length=10, null=True, blank=True)
    d_phone = models.CharField(max_length=4, null=True, blank=True)
    d_DOB = models.DateField(null=True, blank=True)
    d_birth_Country = models.CharField(max_length=125, null=True, blank=True)
    d_birth_City = models.CharField(max_length=125, null=True, blank=True)
    d_birth_Prov = models.CharField(max_length=3, null=True, blank=True)
    d_DOD = models.DateField(null=True, blank=True)
    d_death_Country = models.CharField(max_length=125, null=True, blank=True)
    d_Country = models.CharField(max_length=125, null=True, blank=True)
    e_Country = models.CharField(max_length=125, null=True, blank=True)
    d_death_City = models.CharField(max_length=125, null=True, blank=True)
    d_death_Prov = models.CharField(max_length=3, null=True, blank=True)
    d_SIN = models.CharField(max_length=11, null=True, blank=True)
    d_PHC = models.CharField(max_length=50, null=True, blank=True)
    d_Prov_PHC = models.CharField(max_length=3, null=True, blank=True)
    d_BCN = models.CharField(max_length=255, null=True, blank=True)
    d_death_age = models.IntegerField(null=True, blank=True)
    d_disp_Name = models.CharField(max_length=275, null=True, blank=True)
    d_disp_Postal = models.CharField(max_length=12, null=True, blank=True)
    d_dispdate = models.DateField(null=True, blank=True)
    e_Salutation = models.CharField(max_length=12, null=True, blank=True)
    e_First = models.CharField(max_length=75, null=True, blank=True)
    e_Initial = models.CharField(max_length=75, null=True, blank=True)
    e_Last = models.CharField(max_length=125, null=True, blank=True)
    e_Address = models.CharField(max_length=255, null=True, blank=True)
    e_Unit = models.CharField(max_length=50, null=True, blank=True)
    e_City = models.CharField(max_length=125, null=True, blank=True)
    e_Prov = models.CharField(max_length=3, null=True, blank=True)
    e_Postal = models.CharField(max_length=20,null=True, blank=True)
    e_AreaCode = models.CharField(max_length=10, null=True, blank=True)
    e_exchange = models.CharField(max_length=10, null=True, blank=True)
    e_phone_4 = models.CharField(max_length=10, null=True, blank=True)
    e_relationship = models.CharField(max_length=50, null=True, blank=True)
    ExecutorID = models.IntegerField(null=True, blank=True)
    FaxDate = models.DateTimeField(null=True, blank=True, auto_now=False)
    ReportDate = models.DateTimeField(null=True, blank=True, auto_now=False)
    Status = models.CharField(max_length=50, null=True, blank=True)
    notes = models.CharField(max_length=600, null=True, blank=True)
    DignityPlan = models.SmallIntegerField(null=True, blank=True)
    Contract = models.CharField(max_length=125, null=True, blank=True)
    e_email = models.CharField(max_length=255, null=True, blank=True)
    UpdateID = models.CharField(max_length=255, null=True, blank=True)


    class Meta:
        db_table = 'PesEvents'

class PesExecutor(models.Model):
    ExecutorID = models.BigAutoField(primary_key=True)
    Username = models.CharField(max_length=50, null=True, blank=True)
    Password = models.CharField(max_length=50, null=True, blank=True)
    Status = models.IntegerField(null=True, blank=True)
    ExecutorOverrideID = models.IntegerField(null=True, blank=True)
    LastAccessed = models.DateTimeField(null=True, blank=True)
    LoginCount = models.DecimalField(max_digits=18, decimal_places=0, null=True, blank=True)
    LanguageID = models.CharField(max_length=2, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'PesExecutor'

class Locations(models.Model):
    locationid = models.AutoField(db_column='LocationID', primary_key=True)  # Field name made lowercase.
    status = models.BooleanField(db_column='Status', blank=True, null=True)  # Field name made lowercase.
    locationname = models.CharField(db_column='LocationName', max_length=125)  # Field name made lowercase.
    parentcompany = models.CharField(db_column='ParentCompany', max_length=125, blank=True, null=True)  # Field name made lowercase.
    address = models.CharField(db_column='Address', max_length=255, blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=50, blank=True, null=True)  # Field name made lowercase.
    prov = models.CharField(db_column='Prov', max_length=50, blank=True, null=True)  # Field name made lowercase.
    postalcode = models.CharField(db_column='PostalCode', max_length=12, blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=125, blank=True, null=True)  # Field name made lowercase.
    phone = models.CharField(db_column='Phone', max_length=50, blank=True, null=True)  # Field name made lowercase.
    fax = models.CharField(db_column='Fax', max_length=50, blank=True, null=True)  # Field name made lowercase.
    adminemail = models.CharField(db_column='AdminEmail', max_length=128, blank=True, null=True)  # Field name made lowercase.
    customurl = models.CharField(db_column='CustomURL', max_length=255, blank=True, null=True)  # Field name made lowercase.
    managementemail = models.CharField(db_column='ManagementEmail', max_length=125, blank=True, null=True)  # Field name made lowercase.
    billingcode = models.CharField(db_column='BillingCode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    oldlocation = models.CharField(db_column='OldLocation', max_length=50, blank=True, null=True)  # Field name made lowercase.
    servicename = models.CharField(db_column='ServiceName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    billingnotes = models.CharField(db_column='BillingNotes', max_length=255, blank=True, null=True)  # Field name made lowercase.
    billingemail = models.CharField(db_column='BillingEmail', max_length=125, blank=True, null=True)  # Field name made lowercase.
    miscnotes = models.CharField(db_column='MiscNotes', max_length=255, blank=True, null=True)  # Field name made lowercase.
    website = models.CharField(db_column='Website', max_length=125, blank=True, null=True)  # Field name made lowercase.
    logosmall = models.BinaryField(db_column='LogoSmall', blank=True, null=True)  # Field name made lowercase.
    logolarge = models.BinaryField(db_column='LogoLarge', blank=True, null=True)  # Field name made lowercase.
    dateadded = models.DateTimeField(db_column='DateAdded', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Locations'


class FSPs(models.Model):
    fspid = models.AutoField(db_column='FSPID', primary_key=True)  # Field name made lowercase.
    locationid = models.ForeignKey('Locations', models.DO_NOTHING, db_column='LocationID')  # Field name made lowercase.
    status = models.IntegerField(db_column='Status')  # Field name made lowercase.
    f_first = models.CharField(max_length=75, blank=True, null=True)
    f_last = models.CharField(max_length=125, blank=True, null=True)
    fspphone = models.CharField(db_column='FSPPhone', max_length=32, blank=True, null=True)  # Field name made lowercase.
    fspemail = models.CharField(db_column='FSPEmail', max_length=128, blank=True, null=True)  # Field name made lowercase.
    username = models.CharField(db_column='Username', unique=True, max_length=50)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=50)  # Field name made lowercase.
    jobtitle = models.CharField(db_column='JobTitle', max_length=50, blank=True, null=True)  # Field name made lowercase.
    oldid = models.IntegerField(db_column='OldID', blank=True, null=True)  # Field name made lowercase.
    fspdateadded = models.DateTimeField(db_column='FSPDateAdded', blank=True, null=True)  # Field name made lowercase.
    lastaccessed = models.DateTimeField(db_column='LastAccessed', blank=True, null=True)  # Field name made lowercase.
    logincount = models.DecimalField(db_column='LoginCount', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    languageid = models.CharField(db_column='LanguageID', max_length=2, blank=True, null=True)  # Field name made lowercase.
    routingid = models.CharField(db_column='RoutingID', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'FSPs'

class PesFullDump(models.Model):
    eventID = models.BigIntegerField(db_column='eventID', primary_key=True)  # Field name made lowercase.
    fspid = models.IntegerField(db_column='FSPID', blank=True, null=True)  # Field name made lowercase.
    eventdate = models.DateTimeField(blank=True, null=True)
    d_first = models.CharField(db_column='d_First', max_length=75, blank=True, null=True)  # Field name made lowercase.
    d_middle_a = models.CharField(max_length=75, blank=True, null=True)
    d_middle_b = models.CharField(max_length=75, blank=True, null=True)
    d_last = models.CharField(db_column='d_Last', max_length=125, blank=True, null=True)  # Field name made lowercase.
    d_maiden = models.CharField(db_column='d_Maiden', max_length=125, blank=True, null=True)  # Field name made lowercase.
    d_address = models.CharField(db_column='d_Address', max_length=255, blank=True, null=True)  # Field name made lowercase.
    d_unit = models.CharField(db_column='d_Unit', max_length=50, blank=True, null=True)  # Field name made lowercase.
    d_city = models.CharField(db_column='d_City', max_length=125, blank=True, null=True)  # Field name made lowercase.
    d_prov = models.CharField(db_column='d_Prov', max_length=3, blank=True, null=True)  # Field name made lowercase.
    d_postal = models.CharField(db_column='d_Postal', max_length=20, blank=True, null=True)  # Field name made lowercase.
    d_areacode = models.CharField(db_column='d_AreaCode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    d_exchange = models.CharField(max_length=10, blank=True, null=True)
    d_phone = models.CharField(max_length=4, blank=True, null=True)
    d_bcn = models.CharField(db_column='d_BCN', max_length=255, blank=True, null=True)  # Field name made lowercase.
    d_dob = models.CharField(db_column='d_DOB', max_length=12, blank=True, null=True)  # Field name made lowercase.
    d_dob1 = models.DateField(db_column='d_DOB1', blank=True, null=True)  # Field name made lowercase.
    d_dod = models.CharField(db_column='d_DOD', max_length=12, blank=True, null=True)  # Field name made lowercase.
    d_dod1 = models.DateField(db_column='d_DOD1', blank=True, null=True)  # Field name made lowercase.
    d_death_country = models.CharField(db_column='d_death_Country', max_length=125, blank=True, null=True)  # Field name made lowercase.
    d_death_city = models.CharField(db_column='d_death_City', max_length=125, blank=True, null=True)  # Field name made lowercase.
    d_death_prov = models.CharField(db_column='d_death_Prov', max_length=3, blank=True, null=True)  # Field name made lowercase.
    d_sin = models.CharField(db_column='d_SIN', max_length=11, blank=True, null=True)  # Field name made lowercase.
    d_phc = models.CharField(db_column='d_PHC', max_length=50, blank=True, null=True)  # Field name made lowercase.
    d_prov_phc = models.CharField(db_column='d_Prov_PHC', max_length=3, blank=True, null=True)  # Field name made lowercase.
    d_dispdate = models.CharField(max_length=12, blank=True, null=True)
    d_dispdate1 = models.DateField(blank=True, null=True)
    faxdate = models.DateTimeField(db_column='FaxDate', blank=True, null=True)  # Field name made lowercase.
    reportdate = models.DateTimeField(db_column='ReportDate', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    notes = models.CharField(max_length=600, blank=True, null=True)
    executorusername = models.CharField(db_column='ExecutorUsername', max_length=50, blank=True, null=True)  # Field name made lowercase.
    executorpassword = models.CharField(db_column='ExecutorPassword', max_length=50, blank=True, null=True)  # Field name made lowercase.
    f_first = models.CharField(max_length=75, blank=True, null=True)
    f_last = models.CharField(max_length=125, blank=True, null=True)
    eventupdateid = models.DecimalField(db_column='EventUpdateID', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    updateid = models.DecimalField(db_column='UpdateID', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    updatedesc = models.CharField(db_column='UpdateDesc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    eventupdatenotes = models.CharField(db_column='EventUpdateNotes', max_length=512, blank=True, null=True)  # Field name made lowercase.
    billingcode = models.CharField(db_column='BillingCode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    oldlocation = models.CharField(db_column='OldLocation', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dignityplan = models.SmallIntegerField(db_column='DignityPlan', blank=True, null=True)  # Field name made lowercase.
    adminemail = models.CharField(db_column='AdminEmail', max_length=128, blank=True, null=True)  # Field name made lowercase.
    locationname = models.CharField(db_column='LocationName', max_length=125, blank=True, null=True)  # Field name made lowercase.
    phone = models.CharField(db_column='Phone', max_length=50, blank=True, null=True)  # Field name made lowercase.
    parentcompany = models.CharField(db_column='ParentCompany', max_length=125, blank=True, null=True)  # Field name made lowercase.
    address = models.CharField(db_column='Address', max_length=255, blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=50, blank=True, null=True)  # Field name made lowercase.
    prov = models.CharField(db_column='Prov', max_length=50, blank=True, null=True)  # Field name made lowercase.
    postalcode = models.CharField(db_column='PostalCode', max_length=12, blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=125, blank=True, null=True)  # Field name made lowercase.
    fax = models.CharField(db_column='Fax', max_length=50, blank=True, null=True)  # Field name made lowercase.
    customurl = models.CharField(db_column='CustomURL', max_length=255, blank=True, null=True)  # Field name made lowercase.
    managementemail = models.CharField(db_column='ManagementEmail', max_length=125, blank=True, null=True)  # Field name made lowercase.
    servicename = models.CharField(db_column='ServiceName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    billingnotes = models.CharField(db_column='BillingNotes', max_length=255, blank=True, null=True)  # Field name made lowercase.
    billingemail = models.CharField(db_column='BillingEmail', max_length=125, blank=True, null=True)  # Field name made lowercase.
    locationid = models.IntegerField(db_column='LocationID', blank=True, null=True)  # Field name made lowercase.
    jobtitle = models.CharField(db_column='JobTitle', max_length=50, blank=True, null=True)  # Field name made lowercase.
    d_birth_country = models.CharField(db_column='d_birth_Country', max_length=125, blank=True, null=True)  # Field name made lowercase.
    d_birth_city = models.CharField(db_column='d_birth_City', max_length=125, blank=True, null=True)  # Field name made lowercase.
    d_birth_prov = models.CharField(db_column='d_birth_Prov', max_length=3, blank=True, null=True)  # Field name made lowercase.
    d_death_age = models.IntegerField(blank=True, null=True)
    d_disp_name = models.CharField(db_column='d_disp_Name', max_length=275, blank=True, null=True)  # Field name made lowercase.
    d_disp_postal = models.CharField(db_column='d_disp_Postal', max_length=12, blank=True, null=True)  # Field name made lowercase.
    e_salutation = models.CharField(db_column='e_Salutation', max_length=12, blank=True, null=True)  # Field name made lowercase.
    e_first = models.CharField(db_column='e_First', max_length=75, blank=True, null=True)  # Field name made lowercase.
    e_initial = models.CharField(db_column='e_Initial', max_length=75, blank=True, null=True)  # Field name made lowercase.
    e_last = models.CharField(db_column='e_Last', max_length=125, blank=True, null=True)  # Field name made lowercase.
    e_address = models.CharField(db_column='e_Address', max_length=255, blank=True, null=True)  # Field name made lowercase.
    e_unit = models.CharField(db_column='e_Unit', max_length=50, blank=True, null=True)  # Field name made lowercase.
    e_city = models.CharField(db_column='e_City', max_length=125, blank=True, null=True)  # Field name made lowercase.
    e_prov = models.CharField(db_column='e_Prov', max_length=3, blank=True, null=True)  # Field name made lowercase.
    e_postal = models.CharField(db_column='e_Postal', max_length=20, blank=True, null=True)  # Field name made lowercase.
    e_areacode = models.IntegerField(db_column='e_AreaCode', blank=True, null=True)  # Field name made lowercase.
    e_exchange = models.IntegerField(blank=True, null=True)
    e_phone_4 = models.CharField(max_length=4, blank=True, null=True)
    e_relationship = models.CharField(max_length=50, blank=True, null=True)
    contract = models.CharField(db_column='Contract', max_length=125, blank=True, null=True)  # Field name made lowercase.
    website = models.CharField(db_column='Website', max_length=125, blank=True, null=True)  # Field name made lowercase.
    olddid = models.IntegerField(db_column='OLDdID', blank=True, null=True)  # Field name made lowercase.
    fspphone = models.CharField(db_column='FSPPhone', max_length=32, blank=True, null=True)  # Field name made lowercase.
    routingid = models.CharField(db_column='RoutingID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    executorstatus = models.IntegerField(db_column='ExecutorStatus', blank=True, null=True)  # Field name made lowercase.
    lastaccessed = models.DateTimeField(db_column='LastAccessed', blank=True, null=True)  # Field name made lowercase.
    logincount = models.DecimalField(db_column='LoginCount', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    languageid = models.CharField(db_column='LanguageID', max_length=2, blank=True, null=True)  # Field name made lowercase.
    executorid = models.BigIntegerField(db_column='ExecutorID', blank=True, null=True)  # Field name made lowercase.
    expr1 = models.IntegerField(db_column='Expr1', blank=True, null=True)  # Field name made lowercase.
    d_country = models.CharField(db_column='d_Country', max_length=125, blank=True, null=True)  # Field name made lowercase.
    e_country = models.CharField(db_column='e_Country', max_length=125, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PesFullDump'

class Modifier(models.Model):
    EventID = models.BigIntegerField(db_column='EventID' ,primary_key=True)  # Field name made lowercase.
    d_First = models.CharField(db_column='d_First', max_length=75, blank=True, null=True)  # Field name made lowercase.
    d_Last = models.CharField(db_column='d_Last', max_length=125, blank=True, null=True)  # Field name made lowercase.
    e_Last = models.CharField(db_column='e_Last', max_length=125, blank=True, null=True)  # Field name made lowercase.
    Status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    eventdate = models.DateTimeField(blank=True, null=True)
    locationid = models.IntegerField(db_column='LocationID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Modifier'

class Aftercare(models.Model):
    EventID = models.BigIntegerField(db_column='EventID' ,primary_key=True)  # Field name made lowercase.
    d_First = models.CharField(db_column='d_First', max_length=75, blank=True, null=True)  # Field name made lowercase.
    d_Last = models.CharField(db_column='d_Last', max_length=125, blank=True, null=True)  # Field name made lowercase.
    e_Last = models.CharField(db_column='e_Last', max_length=125, blank=True, null=True)  # Field name made lowercase.
    Status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    eventdate = models.DateTimeField(blank=True, null=True)
    locationid = models.IntegerField(db_column='LocationID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Aftercare'

class Aftercare360(models.Model):
    EventID = models.BigIntegerField(db_column='EventID' ,primary_key=True)  # Field name made lowercase.
    d_First = models.CharField(db_column='d_First', max_length=75, blank=True, null=True)  # Field name made lowercase.
    d_Last = models.CharField(db_column='d_Last', max_length=125, blank=True, null=True)  # Field name made lowercase.
    e_Last = models.CharField(db_column='e_Last', max_length=125, blank=True, null=True)  # Field name made lowercase.
    Status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    eventdate = models.DateTimeField(blank=True, null=True)
    locationid = models.IntegerField(db_column='LocationID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Aftercare360'


class Country(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    alpha2 = models.CharField(max_length=50, blank=True, null=True)
    alpha3 = models.CharField(max_length=50, blank=True, null=True)
    countrycode = models.IntegerField(blank=True, null=True)
    iso = models.CharField(max_length=50, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    subregion = models.CharField(max_length=100, blank=True, null=True)
    intermediateregion = models.CharField(max_length=100, blank=True, null=True)
    regioncode = models.IntegerField(blank=True, null=True)
    subregioncode = models.IntegerField(blank=True, null=True)
    intermediateregioncode = models.IntegerField(blank=True, null=True)
    isactive = models.IntegerField()
    orderby = models.IntegerField(blank=True, null=True)
    name_value = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'country'


class Admins(models.Model):
    adminid = models.AutoField(db_column='AdminID', primary_key=True)  # Field name made lowercase.
    adminpassword = models.CharField(db_column='AdminPassword', max_length=50)  # Field name made lowercase.
    adminname = models.CharField(db_column='AdminName', max_length=50)  # Field name made lowercase.
    adminlevel = models.IntegerField(db_column='AdminLevel')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Admins'