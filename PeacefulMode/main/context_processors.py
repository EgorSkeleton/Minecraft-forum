from .models import TagOfGanre, TagOfVersion

def common_data(request):
    return {
        'all_genres': TagOfGanre.objects.all(),
        'all_versions': TagOfVersion.objects.all(),
        'selected_genres': request.GET.getlist('genre'),
        'selected_version': request.GET.get('version'),
    }