from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def intranet_hub(request):
    """
    Panel maestro (Hub) para administradores y personal de la intranet.
    """
    # En el futuro aquí podemos validar que el usuario tenga rol de ADMIN
    # if not request.user.is_staff and not request.user.rol_vehicular in ['ADMIN', 'JEFE_GUARDIA']:
    #     messages.error(request, "No tienes permisos para acceder a la Intranet.")
    #     return redirect('index')
        
    return render(request, 'portal/intranet_hub.html')
