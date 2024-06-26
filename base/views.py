from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Bodega, Proveedor, Referencia, Producto, TipoProducto, EstadoProducto
from .forms import ReferenciaForm, ProductoForm, ProductoForm2, ProductoForm2_disabled, BodegaForm, TransferenciaForm
# from django.core.cache import cache

import pandas as pd
from io import BytesIO

items_p = [
    {'id': 1, 'name': 'Prótesis 1', 'lote': 'LOTE1', 'type': 'Prótesis', 'stock': 5, 'fecha_rec': '20-11-2023'},
    {'id': 2, 'name': 'Prótesis 2', 'lote': 'LOTE2', 'type': 'Prótesis', 'stock': 11, 'fecha_rec': '19-11-2023'},
    {'id': 3, 'name': 'Prótesis 3', 'lote': 'LOTE3', 'type': 'Prótesis', 'stock': 7, 'fecha_rec': '21-11-2023'},
    {'id': 4, 'name': 'Cinta 1', 'lote': 'LOTE4', 'type': 'Cinta', 'stock': 20, 'fecha_rec': '01-11-2023'},
    {'id': 5, 'name': 'Cinta 2', 'lote': 'LOTE5', 'type': 'Cinta', 'stock': 15, 'fecha_rec': '03-11-2023'}
]

products = [
    {'id': 1, 'type': 'Prótesis', 'SKU': 'SKU1', 'lote': 'LOTE1'},
    {'id': 2, 'type': 'Prótesis', 'SKU': 'SKU2', 'lote': 'LOTE1'},
    {'id': 3, 'type': 'Prótesis', 'SKU': 'SKU3', 'lote': 'LOTE2'},
    {'id': 4, 'type': 'Cinta', 'SKU': 'SKU4', 'lote': 'LOTE4'}
]

def home(request):
    return render(request, 'base/login.html')

def dashboard(request):
    current_user = request.user if request.user.is_authenticated else None
    # la_bodega = Bodega.objects.all().filter(nombre='Bogotá')
    print(current_user)
    los_productos = Producto.objects.all()
    las_referencias = Referencia.objects.all()
    tipos_prod = {}
    conteo_prod = {}
    # conteo_prod[""][""] = 0
    for prod in los_productos:
        #tipos de producto
        for ref in las_referencias:
            if prod.IdReferencia == ref:
                el_tipo = str(ref.tipo)
                print('Tipo producto: ' + el_tipo)
                print('Tipo producto: ' + str(ref.tipo_id))
                if ref.tipo_id in tipos_prod.keys():
                    tipos_prod[ref.tipo_id] += 1
                else:
                    tipos_prod[ref.tipo_id] = 1
                break

        # Conteo productos
        str_bodega = el_tipo#str(prod.IdBodega)
        str_referencia = str(prod.IdReferencia)
        if str_bodega in conteo_prod.keys():
            if str_referencia in conteo_prod[str_bodega].keys():
                conteo_prod[str_bodega][str_referencia] += 1
            else:
                conteo_prod[str_bodega][str_referencia] = 1
        else:
            conteo_prod[str_bodega] = {}
            conteo_prod[str_bodega][str_referencia] = 1
        # print(conteo_prod)
        # print(conteo_prod[str_bodega][str_referencia])
        # print(str_bodega)
        # print(prod.IdBodega_id)

    tipos_ordenados = dict(sorted(tipos_prod.items()))
    print('tipos de producto:')
    print(tipos_ordenados)
    prod_id = str(los_productos[1])
    print(prod_id)

    producto_get = Producto.objects.get(id=prod_id)
    print(producto_get)
    producto_form = ProductoForm2(instance=producto_get)
    
    conteo_zipped = zip(conteo_prod.keys(), conteo_prod.values())
    context = {'los_productos': los_productos, 'conteo_zipped': conteo_zipped, 'form': producto_form, 'tipos_ordenados': tipos_ordenados}
    return render(request, 'base/dashboard.html', context)

def dashboards(request, pk):
    
    if int(pk)<=5 and int(pk)>=1:
        ref_bool = True
        tipo_prod = TipoProducto.objects.all().filter(id=pk)
        las_referencias = Referencia.objects.all()
        # Así se busca la referencia de un modelo dentro de otro
        los_productos = Producto.objects.all().filter(IdReferencia__tipo=pk)
        print(los_productos)
        if not los_productos:
            # No hay productos
            return render(request, 'base/productos.html')

        conteo_prod = {}
        conteo_prod_enTransito = {}
        str_referencia=""
        for prod in los_productos:
            str_bodega = str(prod.IdBodega)
            str_estado = str(prod.IdEstado_producto)
            for refe in las_referencias:
                if refe == prod.IdReferencia:
                    str_referencia = str(refe.id)
            
            if str_estado == 'En bodega':
                if str_bodega in conteo_prod.keys():
                    if str_referencia in conteo_prod[str_bodega].keys():
                        conteo_prod[str_bodega][str_referencia] += 1
                    else:
                        conteo_prod[str_bodega][str_referencia] = 1
                else:
                    conteo_prod[str_bodega] = {}
                    conteo_prod[str_bodega][str_referencia] = 1
            elif str_estado == 'En tránsito':
                if str_bodega in conteo_prod_enTransito.keys():
                    if str_referencia in conteo_prod_enTransito[str_bodega].keys():
                        conteo_prod_enTransito[str_bodega][str_referencia] += 1
                    else:
                        conteo_prod_enTransito[str_bodega][str_referencia] = 1
                else:
                    conteo_prod_enTransito[str_bodega] = {}
                    conteo_prod_enTransito[str_bodega][str_referencia] = 1

        prod_id = str(los_productos[0])

        producto_get = Producto.objects.get(id=prod_id)
        producto_form = ProductoForm2(instance=producto_get)
        
        conteo_zipped = zip(conteo_prod.keys(), conteo_prod.values())
        conteo__enTransito_zipped = zip(conteo_prod_enTransito.keys(), conteo_prod_enTransito.values())
        context = {'los_productos': los_productos, 'conteo_zipped': conteo_zipped, 'conteo__enTransito_zipped': conteo__enTransito_zipped,
                   'form': producto_form, 'el_tipo_producto': tipo_prod[0]}
        return render(request, 'base/dashboards.html', context)
    else:
        return render(request, 'base/productos.html')



def dashboard_producto(request, pk):
    
    if int(pk)<=5 and int(pk)>=1:
        tipo_prod = TipoProducto.objects.all().filter(id=pk)
        las_referencias = Referencia.objects.all()
        # Así se busca la referencia de un modelo dentro de otro
        los_productos = Producto.objects.all().filter(IdReferencia__tipo=pk)
        print(los_productos)
        if not los_productos:
            # No hay productos
            return render(request, 'base/productos.html')

        conteo_total = {}
        conteo_prod = {}
        conteo_prod_enTransito = {}
        str_referencia=""
        for prod in los_productos:
            str_bodega = str(prod.IdBodega)
            str_estado = str(prod.IdEstado_producto)
            print(prod.IdEstado_producto)
            for refe in las_referencias:
                if refe == prod.IdReferencia:
                    str_referencia = str(refe.id)
            
            if str_estado == 'En bodega':
                if str_referencia in conteo_prod.keys():
                    conteo_prod[str_referencia] += 1
                else:
                    conteo_prod[str_referencia] = 1


            elif str_estado == 'En tránsito':
                if str_referencia in conteo_prod_enTransito.keys():
                    conteo_prod_enTransito[str_referencia] += 1
                else:
                    conteo_prod_enTransito[str_referencia] = 1

            if str_estado == 'En bodega' or str_estado == 'En tránsito':
                if str_referencia in conteo_total.keys():
                    conteo_total[str_referencia] += 1
                else:
                    conteo_total[str_referencia] = 1

        # Formulario bodegas:
        todas_bodegas = Bodega.objects.all()
        listado_bodegas = {}
        for bode in todas_bodegas:
            listado_bodegas[bode.id] = bode.nombre

        context = {'los_productos': los_productos, 'conteo_prod': conteo_prod, 'conteo_prod_enTransito': conteo_prod_enTransito,
                   'conteo_total': conteo_total, 'el_tipo_producto': tipo_prod[0], 'listado_bodegas': listado_bodegas, 'el_pk': pk}
        return render(request, 'base/dashboard_producto.html', context)
    else:
        return render(request, 'base/productos.html')



def bodega_producto(request):

    pk = int(request.GET.get('tipoProducto'))
    nom_bodega = request.GET.get('nom_bodega')

    bodega = Bodega.objects.all().filter(id=nom_bodega) #La bodega sería bodega[0]
    
    if int(pk)<=5 and int(pk)>=1:
        tipo_prod = TipoProducto.objects.all().filter(id=pk)
        las_referencias = Referencia.objects.all()
        # Así se busca la referencia de un modelo dentro de otro
        los_productos = Producto.objects.all().filter(IdReferencia__tipo=pk, IdBodega__id=nom_bodega)
        print(los_productos)
        if not los_productos:
            # No hay productos
            return render(request, 'base/productos.html')

        conteo_prod = {}
        conteo_prod_enTransito = {}
        str_referencia=""
        for prod in los_productos:
            str_estado = str(prod.IdEstado_producto)
            for refe in las_referencias:
                if refe == prod.IdReferencia:
                    str_referencia = str(refe.id)
            
            if str_estado == 'En bodega':
                if str_referencia in conteo_prod.keys():
                    conteo_prod[str_referencia] += 1
                else:
                    conteo_prod[str_referencia] = 1
            elif str_estado == 'En tránsito':
                if str_referencia in conteo_prod_enTransito.keys():
                    conteo_prod_enTransito[str_referencia] += 1
                else:
                    conteo_prod_enTransito[str_referencia] = 1
        
        context = {'los_productos': los_productos, 'conteo_prod': conteo_prod, 'conteo_prod_enTransito': conteo_prod_enTransito,
                   'el_tipo_producto': tipo_prod[0], 'bodega': bodega[0], 'id_bodega': nom_bodega}
        return render(request, 'base/bodega_producto.html', context)
    else:
        return render(request, 'base/productos.html')


def la_referencia(request):

    flag_post = False
    # Si se hizo transferencia:
    if request.method == 'POST':
        flag_post = True
        ids_a_transferir = Producto.objects.all().filter(IdReferencia=request.POST.get('IdReferencia'),
                                                         IdEstado_producto=request.POST.get('IdEstado_producto'),
                                                         IdBodega=request.POST.get('IdBodega'),
                                                         codigoQR=request.POST.get('codigoQR'),
                                                         lote=request.POST.get('lote'))
        
        print(ids_a_transferir)
        print(request.POST.get('IdReferencia'))
        ids = []
        cantidad_ids = int(request.POST.get('cantidad_manual'))
        instancia_IdBodega = Bodega.objects.get(id=int(request.POST.get('id_bodega')))
        instancia_Estado = EstadoProducto.objects.get(id=2)
        for id_s in ids_a_transferir:
            if cantidad_ids > 0:
                ids.append(str(id_s))
                cantidad_ids -= 1
                cambio_producto = Producto.objects.get(id=str(id_s))
                print('antes')
                print(cambio_producto.IdEstado_producto)
                print(cambio_producto.IdBodega)
                cambio_producto.IdBodega = instancia_IdBodega
                cambio_producto.IdEstado_producto = instancia_Estado
                cambio_producto.save()
                print('después')
                print(cambio_producto.IdEstado_producto)
                print(cambio_producto.IdBodega)
            else: break
            
    referencia = request.GET.get('refer')
    id_bodega = request.GET.get('idBodega')
    el_estado = request.GET.get('elEstado')

    bodega = Bodega.objects.all().filter(id=id_bodega) #La bodega sería bodega[0]
    referencias_detalles = Referencia.objects.all().filter(id=referencia)
    estado = EstadoProducto.objects.all().filter(id=el_estado)
    los_productos = Producto.objects.all().filter(IdReferencia=referencia, IdBodega__id=id_bodega)
    if not los_productos:
        # No hay productos
        return render(request, 'base/productos.html')
    
    conteo_prod = {}
    cantidad_total = 0
    
    for prod in los_productos:
        cantidad_total += 1
        if not prod.lote in conteo_prod.keys():
            conteo_prod[prod.lote] = [prod.codigoQR, prod.fecha_vencimiento, 1]
        else:
            conteo_prod[prod.lote][2] += 1

    
    refID = referencias_detalles[0].id
    refNombre = referencias_detalles[0].nombre
    refProveedor = referencias_detalles[0].IdProveedor
    refTipo = referencias_detalles[0].tipo

    # Formulario Transferencia:

    current_user = request.user if request.user.is_authenticated else None
    form = TransferenciaForm(initial={'usuario': current_user, 'IdReferencia': refID, 'IdEstado_producto': el_estado, 'IdBodega': id_bodega})

    todas_bodegas = Bodega.objects.all()
    listado_bodegas = {}
    for bode in todas_bodegas:
        listado_bodegas[bode.id] = bode.nombre

        
    
    context = {'refID': refID, 'estado': estado[0], 'conteo_prod': conteo_prod, 'cantidad_total': cantidad_total, 'form': form,
                'bodega': bodega[0], 'refNombre': refNombre, 'refProveedor': refProveedor, 'refTipo': refTipo, 'el_estado': el_estado,
                'listado_bodegas': listado_bodegas, 'flag_post': flag_post, 'canti_t': request.POST.get('cantidad_manual')}
    return render(request, 'base/la_referencia.html', context)


def items_pk(request, pk):
    it_bool = False
    items_id = None
    for ite in items_p:
        if ite['id'] == int(pk):
            it_bool = True
            items_id = ite
    if it_bool:
        context = {'items_id': items_id}
        return render(request, 'base/items_det.html', context)
    else:
        context = {'items_p': items_p}
        return render(request, 'base/items.html', context)

def items(request):
    context = {'items_p': items_p}
    return render(request, 'base/items.html', context)

def bodegas(request):
    las_bodegas = Bodega.objects.all().order_by('id')
    context = {'las_bodegas': las_bodegas}
    return render(request, 'base/bodegas.html', context)

def proveedores(request):
    los_proveedores = Proveedor.objects.all().order_by('id')
    context = {'los_proveedores': los_proveedores}
    return render(request, 'base/proveedores.html', context)

def ingreso_productos(request, pk):
    exito=False
    if '_' in pk:
        mk = pk.split('_')
        pk = mk[0]
        exito=True
    las_referencias = Referencia.objects.all().filter(tipo=pk)
    ref_bool = False
    if int(pk)<=5 and int(pk)>=1:
        ref_bool = True
    if ref_bool:
        context = {'las_referencias': las_referencias, 'el_tipo_producto': las_referencias[0], 'obteniendo_id': pk, 'exito': exito}
        return render(request, 'base/ingreso_productos.html', context)
    else:
        return render(request, 'base/productos.html')

def ingreso_manual(request, pk):
    mk=pk.split('_')
    pk=mk[1]
    current_user = request.user if request.user.is_authenticated else None
    form = ProductoForm(initial={'usuario': current_user, 'IdReferencia': pk, 'IdEstado_producto': 4, 'IdBodega': 1})
    
    if request.method == 'POST':
        la_cantidad_manual = int(request.POST.get('cantidad_manual', ''))
            # la_cantidad_manual_nro = int(la_cantidad_manual)
            # cache.set('cantidad_cached', la_cantidad_manual_nro, 40)
            # print(cache.get('cantidad_cached'))
        new_request = request.POST.copy()
        new_request.pop('cantidad_manual')
        form = ProductoForm(new_request)    
        if form.is_valid():
            # cada instancia de formulario sólo puede guardar una vez
            instance = form.save(commit=False)
            for i in range(la_cantidad_manual):
                instance.id = None
                instance.save()
            # form.save()
            return redirect('/ingreso_productos/'+str(mk[0])+'_/')
    else:
        la_cantidad_manual = 0
    context = {'form': form, 'cantidad_ingresos': la_cantidad_manual, 'ref': pk}
    return render(request, 'base/ingreso_productos/ingreso_manual.html', context)

def ingreso_qr(request, pk):
    mk=pk.split('_')
    pk=mk[1]
    # obteniendo_record = TipoProducto.objects.get(tipo=mk[0])
    # obteniendo_id = obteniendo_record.id
    current_user = request.user if request.user.is_authenticated else None
    form = ProductoForm(initial={'usuario': current_user, 'IdReferencia': pk, 'IdEstado_producto': 4, 'IdBodega': 1})
    if request.method == 'POST':
        la_cantidad_manual = int(request.POST.get('cantidad_manual', ''))
        new_request = request.POST.copy()
        new_request.pop('cantidad_manual')
        form = ProductoForm(new_request)
        if form.is_valid():
            instance = form.save(commit=False)
            for i in range(la_cantidad_manual):
                instance.id = None
                instance.save()
            return redirect('/ingreso_productos/'+str(mk[0])+'_/')
    else:
        la_cantidad_manual = 0
    context = {'form': form, 'cantidad_ingresos': la_cantidad_manual}
    return render(request, 'base/ingreso_productos/ingreso_qr.html', context)

def ingreso_referencias(request):
    current_user = request.user if request.user.is_authenticated else None
    form = ReferenciaForm(initial={'usuario': current_user})
    if request.method == 'POST':
        # print(request.POST)
        form = ReferenciaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ingreso_referencias')
    context = {'form': form}
    return render(request, 'base/ingreso_referencias.html', context)

# De aquí para abajo son ejemplos


def transferencias_stock(request):
    current_user = request.user if request.user.is_authenticated else None
    
    if request.method == 'POST':
        los_productos = {}
        los_productos['IdReferencia'] = request.POST.get('IdReferencia')
        los_productos['IdEstado_producto'] = request.POST.get('IdEstado_producto')
        los_productos['IdBodega'] = request.POST.get('IdBodega')
        los_productos['qr'] = request.POST.get('codigoQR')
        print(los_productos)

        if request.POST.get('codigoQR') != '':
            consulta = Producto.objects.all().filter(IdReferencia=request.POST.get('IdReferencia'), IdEstado_producto=request.POST.get('IdEstado_producto'), IdBodega=request.POST.get('IdBodega'), 
                                                 codigoQR=request.POST.get('codigoQR'), lote=request.POST.get('lote'))
        else:
            consulta = Producto.objects.all().filter(IdReferencia=request.POST.get('IdReferencia'), IdEstado_producto=request.POST.get('IdEstado_producto'), IdBodega=request.POST.get('IdBodega'), 
                                                 lote=request.POST.get('lote'))
        # los_productos_form = ProductoForm(initial={'usuario': current_user}, instance=los_productos)
        form = ProductoForm2(request.POST)
        form_disabled = ProductoForm2_disabled(request.POST)
        context = {'form': form, 'form_disabled': form_disabled, 'cantidad_de_queries': len(consulta), 'ids_queryset': list(consulta)}
        return render(request, 'base/transferencias/transferencias_stock.html', context)
    elif request.method == 'GET':
        # Si no es POST, es recepción de producto
        if not request.GET.get('nom_bodega') is None:
            nom_bodega = request.GET.get('nom_bodega')
        else:
            nom_bodega = 1
        bodega = Bodega.objects.all().filter(id=nom_bodega)
        todas_bodegas = Bodega.objects.all()
        listado_bodegas = {}
        for bode in todas_bodegas:
            listado_bodegas[bode.id] = bode.nombre

        bodegas_zipped = zip(listado_bodegas.keys(), listado_bodegas.values())
        form = BodegaForm(initial={'usuario': current_user, 'nombre': bodega[0]})

        # Productos que están llegando a esta bodega
        en_transito = Producto.objects.all().filter(IdEstado_producto='2', IdBodega=bodega[0])
        listado_en_transito = {}
        for bode in en_transito:
            if bode.IdReferencia in listado_en_transito.keys():
                listado_en_transito[bode.IdReferencia] += 1
            else:
                listado_en_transito[bode.IdReferencia] = 1
        en_transito_zipped = zip(listado_en_transito.keys(), listado_en_transito.values())
    
        context = {'form': form, 'bodega': bodega[0], 'bodegas_zipped': bodegas_zipped, 'en_transito_zipped': en_transito_zipped}
        return render(request, 'base/transferencias/recepcion_stock.html', context)


def transferencias_stock_cambio(request):
    current_user = request.user if request.user.is_authenticated else None

    if request.method == 'POST':
        los_productos = {}
        los_productos['IdReferencia'] = request.POST.get('IdReferencia')
        los_productos['IdEstado_producto'] = request.POST.get('IdEstado_producto')
        los_productos['IdBodega'] = request.POST.get('IdBodega')
        los_productos['qr'] = request.POST.get('codigoQR')
        los_productos['ids_queryset'] = request.POST.get('ids_queryset')
        los_productos['cantidad_manual'] = int(request.POST.get('cantidad_manual'))
        ids_queryset_str = los_productos['ids_queryset']
        ids_queryset_str = ids_queryset_str[1:len(ids_queryset_str)-2]
        ids_queryset_str = ids_queryset_str.replace('<Producto: ', '')
        list_str = ids_queryset_str.split('>, ')
        print(los_productos)
        # print(list_str[1])
        print(ids_queryset_str)

        new_request = request.POST.copy()
        new_request.pop('cantidad_manual')
        new_request.pop('ids_queryset')

        for i in range(los_productos['cantidad_manual']):
            cambio_producto = Producto.objects.get(id=list_str[i])
            form = ProductoForm(instance=cambio_producto)
            form = ProductoForm(new_request, instance=cambio_producto)
            if form.is_valid():
                form.save()


        context = {'qr': los_productos['qr'], 'ids_queryset': los_productos['ids_queryset']}
        return render(request, 'base/transferencias/transferencias_stock_cambio.html', context)


def ajuste_de_inventario(request):
    return render(request, 'base/DeEjemplo/ajuste_de_inventario.html')

def ordenes_de_ventas(request):
    return render(request, 'base/DeEjemplo/ordenes_de_ventas.html')


def excel_on_click(request):
    
    tipo_producto = request.GET.get('id_producto')

    los_productos = Producto.objects.all().filter(IdReferencia__tipo=tipo_producto)
    referencias = {}

    for prod in los_productos:
        if prod.IdReferencia in referencias.keys():
            referencias[prod.IdReferencia] += 1
        else:
            referencias[prod.IdReferencia] = 1

    las_referencias = referencias.keys()
    cantidades = referencias.values()

    data = {
        'Referencias': list(las_referencias),
        'Cantidad total': list(cantidades)
    }

    # Create a DataFrame
    df = pd.DataFrame(data)

    

    # Create Excel file from DataFrame
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)

    # Create HTTP response
    response = HttpResponse(excel_file.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="sample_excel.xlsx"'

    return response