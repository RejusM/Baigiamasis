from .models import Stage


def stages_processor(request):
    stages = Stage.objects.all()
    return {'stages': stages}
