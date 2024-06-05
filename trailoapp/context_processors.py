from .models import Stage


def stages_processor(request):
    stagess = Stage.objects.all()
    return {'stagess': stagess}
