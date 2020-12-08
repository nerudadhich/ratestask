from django.db import models


class Region(models.Model):
    slug = models.CharField(primary_key=True, max_length=256)
    name = models.TextField()
    parent_slug = models.ForeignKey(
        "Region", db_column="parent_slug", null=True, blank=True, on_delete=models.PROTECT
    )

    class Meta:
        db_table = "regions"


class Port(models.Model):
    code = models.CharField(max_length=5, primary_key=True)
    name = models.TextField()
    parent_slug = models.ForeignKey(
        Region, db_column="parent_slug", on_delete=models.PROTECT)

    class Meta:
        db_table = "ports"


class Price(models.Model):
    orig_code = models.ForeignKey(
        Port, db_column="orig_code", related_name="origin_codes", on_delete=models.PROTECT
    )
    dest_code = models.ForeignKey(
        Port, db_column="dest_code", related_name="dest_codes", on_delete=models.PROTECT
    )
    day = models.DateField()
    price = models.IntegerField()

    class Meta:
        db_table = "prices"
