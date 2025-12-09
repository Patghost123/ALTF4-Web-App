from django.db import models

class Lab(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    capacity = models.PositiveIntegerField()
    description = models.TextField()
    map_svg_id = models.CharField(max_length=50, unique=True, help_text="Matches ID in Figma SVG")
    is_active = models.BooleanField(default=True)
    safety_guidelines = models.TextField()

    def __str__(self):
        return self.name

class Equipment(models.Model):
    lab = models.ForeignKey(Lab, related_name='equipment', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    serial_number = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True)
    is_operational = models.BooleanField(default=True)
    last_maintenance = models.DateField()
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name} ({self.lab.name if self.lab else 'Storage'})"
