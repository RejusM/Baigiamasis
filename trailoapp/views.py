from django.shortcuts import render, get_object_or_404
from .models import Stage


def home(request):
    stages = Stage.objects.all().order_by('date')
    stages_count = stages.count()
    context = {
        'stages': stages,
        'stages_count': stages_count,
    }
    return render(request, 'home.html', context)


def all_stages(request):
    stages = Stage.objects.all().order_by('date')
    context = {
        'stages': stages
    }
    return render(request, 'all_stages.html', context)


def stage_detail(request, id):
    stage = get_object_or_404(Stage, id=id)
    context = {
        'stage': stage,
    }
    return render(request, 'stage_detail.html', context)
