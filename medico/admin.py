from django.contrib import admin

# Register your models here.
from .models import Especialidades, DadosMedico, DatasAbertas

# Register your models here.
admin.site.register(Especialidades)
admin.site.register(DadosMedico)
admin.site.register(DatasAbertas)