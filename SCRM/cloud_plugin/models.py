from django.db import models
import json

# Create your models here.


class Region(models.Model):
        #RegionId = models.AutoField(primary_key=True)
        EndPoint = models.CharField(max_length=256)
        RegionName = models.CharField(max_length=256, primary_key=True)
        LastUpdated = models.DateTimeField(auto_now=True)
        CloudId = models.ForeignKey('RunningCloudTable', on_delete=models.CASCADE, blank=True)
	
        class Meta:
                db_table = "region"


class Vpc(models.Model):
        VpcId = models.CharField(primary_key=True, max_length=256)
        RegionName = models.ForeignKey('Region', on_delete=models.CASCADE)
        apiDump = models.CharField(max_length=256)
        IsDefault = models.BooleanField(default=True)
        State = models.CharField(max_length=256)
        LastUpdated = models.DateTimeField(auto_now=True)
        CloudId = models.ForeignKey('RunningCloudTable', on_delete=models.CASCADE, blank=True)

        class Meta:
                db_table = "vpc"

        @property
        def get_apidump(self):
            return json.loads(self.apiDump)


class SecurityGroup(models.Model):
        GroupId = models.CharField(primary_key=True, max_length=256)
        GroupName = models.CharField(max_length=256, blank=True)           
        Description = models.TextField(blank=True)
        VpcId = models.ForeignKey('Vpc', on_delete=models.CASCADE, blank=True)
        OwnerId = models.CharField(max_length=256, blank=True)
        ingress = models.TextField(blank=True)
        egress = models.TextField(blank=True)
        LastUpdated = models.DateTimeField(auto_now=True)
        CloudId = models.ForeignKey('RunningCloudTable', on_delete=models.CASCADE, blank=True)
   
        class Meta:
                db_table = "securityGroup"
        @property
        def get_ingress(self):
            return json.loads(self.ingress)

        @property
        def get_egress(self):
            return json.loads(self.egress)


class SmIssues(models.Model):
    Component = models.CharField(max_length=256)
    Resource = models.CharField(max_length=256)
    Name = models.CharField(max_length=256)
    Region = models.CharField(max_length=256)
    Action = models.CharField(max_length=256)
    Issue = models.TextField(blank=True)
    LastUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "issues"


class RunningCloudTable(models.Model):
    CloudName = models.CharField(max_length=256)
    CloudId = models.PositiveSmallIntegerField(primary_key=True)
    CloudType = models.CharField(max_length=64)
    CloudCat = models.CharField(max_length=64)
    LastUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "RunningCloudTable"
