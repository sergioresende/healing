from django.shortcuts import render, redirect
from medico.models import DadosMedico, Especialidades, DatasAbertas, is_medico
from datetime import datetime
from .models import Consulta, Documento
from django.contrib.messages import constants
from django.contrib import messages
from django.db import transaction

# Create your views here.
def home(request):
    if request.method == "GET":
        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')
        medicos = DadosMedico.objects.all()

        if medico_filtrar:
            medicos = medicos.filter(nome__icontains = medico_filtrar)
        especialidades = Especialidades.objects.all()

        if especialidades_filtrar:
            medicos = medicos.filter(especialidade_id__in = especialidades_filtrar)

        
        proxima_consulta = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now()).order_by("data_aberta__data").first()
        if proxima_consulta:
            dias = (proxima_consulta.data_aberta.data.date() - datetime.now().date()).days
        else:
            dias = 0
        return render(request, 'home.html', {'medicos': medicos, 'especialidades': especialidades, 'is_medico': is_medico(request.user), "proxima_consulta": proxima_consulta, "dias": dias})
    
def escolher_horario(request, id_dados_medicos):
    if request.method == "GET":
        medico = DadosMedico.objects.get(id = id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(user = medico.user).filter(data__gte = datetime.now()).filter(agendado = False)
    return render (request, 'escolher_horario.html', {'datas_abertas': datas_abertas, 'medico': medico, 'is_medico': is_medico(request.user)})

def agendar_horario(request, id_data_aberta):
    if request.method == "GET":
        with transaction.atomic():
            data_aberta = DatasAbertas.objects.get(id=id_data_aberta)

            horario_agendado = Consulta(
                paciente=request.user,
                data_aberta=data_aberta
            )

            horario_agendado.save()

            data_aberta.agendado = True
            data_aberta.save()

            messages.add_message(request, constants.SUCCESS, 'Horário agendado com sucesso.')

        return redirect('/pacientes/minhas_consultas/')

def minhas_consultas(request):
    
    if request.method =="GET":
        minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
        especialidades_filtrar = request.GET.get("especialidades")
        if especialidades_filtrar:
            minhas_consultas = minhas_consultas.filter(data_aberta__user__dadosmedico__especialidade__especialidade__icontains=especialidades_filtrar)
        data_filtrar = request.GET.get("data")
        if data_filtrar:
            minhas_consultas = minhas_consultas.filter(data_aberta__data__icontains = data_filtrar)
        
        return render(request, 'minhas_consultas.html', {'minhas_consultas': minhas_consultas, 'is_medico': is_medico(request.user)})

def consulta(request, id_consulta):
    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta = consulta)
        dado_medico = DadosMedico.objects.get(user=consulta.data_aberta.user)
        return render(request, 'consulta.html', {'consulta': consulta, 'dado_medico': dado_medico, 'is_medico': is_medico(request.user), "documentos": documentos})
    
def cancelar_consulta(request, id_consulta):
    
    consulta = Consulta.objects.get(id=id_consulta)
    if request.user != consulta.paciente: 
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!')
        return redirect('/pacientes/pacientes/minhas_consultas')
    
    consulta.status = "C"
    consulta.save()
    return redirect(f'/pacientes/consulta/{id_consulta}')

