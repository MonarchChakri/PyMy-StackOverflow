from django.shortcuts import redirect, render


def redirect_to_home(request):
    return redirect('questions:questions')


def handler404(request, exception, template_name='404.html'):
    response = render(request, template_name=template_name, context={}, status=404)
    return response
