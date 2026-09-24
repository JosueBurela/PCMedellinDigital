from portal.models import BitacoraSalidaVehiculo
print("Testing DB")
for b in BitacoraSalidaVehiculo.objects.all().order_by('-id')[:3]:
    print("ID:", b.id)
    print(b.descripcion_servicio)
    print("---")
