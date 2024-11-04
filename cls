warning: in the working copy of 'pes/models.py', LF will be replaced by CRLF the next time Git touches it
[1mdiff --git a/pes/models.py b/pes/models.py[m
[1mindex 4da2e32..b38598d 100644[m
[1m--- a/pes/models.py[m
[1m+++ b/pes/models.py[m
[36m@@ -35,11 +35,11 @@[m [mclass PesEvents(models.Model):[m
     d_AreaCode = models.IntegerField(null=True)[m
     d_exchange = models.IntegerField(null=True)[m
     d_phone = models.CharField(max_length=4, null=True)[m
[31m-    d_DOB = models.DateTimeField()[m
[32m+[m[32m    d_DOB = models.DateField()[m
     d_birth_Country = models.CharField(max_length=125)[m
     d_birth_City = models.CharField(max_length=125, null=True)[m
     d_birth_Prov = models.CharField(max_length=3, null=True)[m
[31m-    d_DOD = models.DateTimeField()[m
[32m+[m[32m    d_DOD = models.DateField()[m
     d_death_Country = models.CharField(max_length=125)[m
     d_death_City = models.CharField(max_length=125, null=True)[m
     d_death_Prov = models.CharField(max_length=3, null=True)[m
[36m@@ -49,8 +49,8 @@[m [mclass PesEvents(models.Model):[m
     d_BCN = models.CharField(max_length=255, null=True)[m
     d_death_age = models.IntegerField()[m
     d_disp_Name = models.CharField(max_length=275)[m
[31m-    d_disp_Postal = models.CharField(max_length=12)[m
[31m-    d_dispdate = models.DateTimeField()[m
[32m+[m[32m    d_disp_Postal = models.CharField(max_length=12,null=True)[m
[32m+[m[32m    d_dispdate = models.DateField()[m
     e_Salutation = models.CharField(max_length=12, null=True)[m
     e_First = models.CharField(max_length=75)[m
     e_Initial = models.CharField(max_length=75, null=True)[m
[36m@@ -65,8 +65,8 @@[m [mclass PesEvents(models.Model):[m
     e_phone_4 = models.CharField(max_length=4)[m
     e_relationship = models.CharField(max_length=50)[m
     ExecutorID = models.IntegerField(null=True)[m
[31m-    FaxDate = models.DateTimeField(null=True)[m
[31m-    ReportDate = models.DateTimeField(null=True)[m
[32m+[m[32m    FaxDate = models.DateField(null=True)[m
[32m+[m[32m    ReportDate = models.DateField(null=True)[m
     Status = models.CharField(max_length=50, null=True)[m
     notes = models.CharField(max_length=600, null=True)[m
     DignityPlan = models.SmallIntegerField(null=True)[m
