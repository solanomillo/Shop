from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import Categoria, Producto, Cliente, Pedido, PedidoDetalle
from .carrito import Cart
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .forms import ClienteForm
from django.contrib.auth.decorators import login_required
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings

""" VISTAS PARA EL CATALOGO DEL PRODUCTO """


def index(request):
    listaProuctos = Producto.objects.all()
    listaCategorias = Categoria.objects.all()
    return render(request, 'index.html', {
        'productos': listaProuctos,
        'categorias': listaCategorias
    })


def productosPorCategoria(request, categoria_id):
    """ vista para filtar productos por categoria """
    objCategoria = Categoria.objects.get(pk=categoria_id)
    listaProductos = objCategoria.producto_set.all()

    listaCategorias = Categoria.objects.all()

    return render(request, 'index.html', {
        'categorias': listaCategorias,
        'productos': listaProductos
    })


def productosPorNombre(request):
    """ vista para filtrado de productos por nombre"""
    nombre = request.POST['nombre']
    listaProductos = Producto.objects.filter(nombre__contains=nombre)
    listaCategorias = Categoria.objects.all()

    return render(request, 'index.html', {
        'categorias': listaCategorias,
        'productos': listaProductos
    })


def detalleProducto(request, producto_id):
    """ Vista del detalle del producto """
    # objProducto = Producto.objects.get(pk=producto_id)
    objProducto = get_object_or_404(Producto, pk=producto_id)

    return render(request, 'producto.html', {
        'producto': objProducto
    })


""" VISTAS PARA EL CARRITO DE COMPRAS """


def carrito(request):
    return render(request, 'carrito.html', {})


def agregarCarrito(request, producto_id):
    if request.method == 'POST':
        cantidad = int(request.POST['cantidad'])
    else:
        cantidad = 1
    objProducto = Producto.objects.get(pk=producto_id)
    carritoProducto = Cart(request)
    carritoProducto.add(objProducto, cantidad)

    if request.method == 'GET':
        return redirect('/')

    return render(request, 'carrito.html', {})


def eliminarProductoCarrito(request, producto_id):
    objProducto = Producto.objects.get(pk=producto_id)
    carritoProducto = Cart(request)
    carritoProducto.delete(objProducto)

    return render(request, 'carrito.html', {})


def limpiarCarrito(request):
    carritoProducto = Cart(request)
    carritoProducto.clear()

    return render(request, 'carrito.html', {})


""" VISTAS PARA CLIENTES Y USARIOS """


def crearUsuario(request):
    if request.method == 'POST':
        dataUsuario = request.POST['nuevoUsuario']
        dataPassword = request.POST['nuevoPassword']

        nuevoUsuario = User.objects.create_user(username=dataUsuario, password=dataPassword)
        if nuevoUsuario is not None:
            login(request, nuevoUsuario)
            return redirect('/cuenta')

    return render(request, 'login.html', {})


def loginUsuario(request):
    pagDestino = request.GET.get('next', '/cuenta')  # Redirige a /cuenta si no hay otro destino
    context = {'destino': pagDestino}

    if request.method == 'POST':
        dataUsuario = request.POST['usuario']
        dataPassword = request.POST['password']
        dataDestino = request.POST.get('destino', '/cuenta')  # Asegura que haya un destino válido

        authUsuario = authenticate(request, username=dataUsuario, password=dataPassword)

        if authUsuario is not None:
            login(request, authUsuario)
            if dataDestino and dataDestino != 'None':
                return redirect(dataDestino)  # Redirige solo si es válido
            return redirect('/cuenta')
        else:
            context['mensaje_error'] = 'Datos Incorrectos'  # Mantiene el contexto original

    return render(request, 'login.html', context)


def logoutUsuario(request):
    logout(request)
    return render(request, 'login.html')


def cuentaUsuario(request):
    try:
        clienteEditar = Cliente.objects.get(usuario=request.user)

        dataCliente = {
            'nombre': request.user.first_name,
            'apellido': request.user.last_name,
            'email': request.user.email,
            'direccion': clienteEditar.direccion,
            'telefono': clienteEditar.telefono,
            'dni': clienteEditar.dni,
            'sexo': clienteEditar.sexo,
            'fecha_nacimiento': clienteEditar.fecha_nacimiento
        }
    except:
        dataCliente = {
            'nombre': request.user.first_name,
            'apellido': request.user.last_name,
            'email': request.user.email,
        }

    formCliente = ClienteForm(dataCliente)

    return render(request, 'cuenta.html', {
        'formCliente': formCliente
    })


def actualizarCliente(request):
    mensaje = ""

    if request.method == 'POST':
        formCliente = ClienteForm(request.POST)
        if formCliente.is_valid():
            datacliente = formCliente.cleaned_data

            # actualizar usuario
            actUsuario = User.objects.get(pk=request.user.id)
            actUsuario.first_name = datacliente['nombre']
            actUsuario.last_name = datacliente['apellido']
            actUsuario.email = datacliente['email']
            actUsuario.save()

            # registro cliente
            nuevoCliente = Cliente()
            nuevoCliente.usuario = actUsuario
            nuevoCliente.dni = datacliente['dni']
            nuevoCliente.direccion = datacliente['direccion']
            nuevoCliente.telefono = datacliente['telefono']
            nuevoCliente.sexo = datacliente['sexo']
            nuevoCliente.fecha_nacimiento = datacliente['fecha_nacimiento']
            nuevoCliente.save()

            mensaje = 'Datos Actualizados'

    return render(request, 'cuenta.html', {
        'mensaje': mensaje,
        'formCliente': formCliente
    })


""" VISTAS PARA EL PROCESO DE COMPRAS """


@login_required(login_url='/login')
def registarPedido(request):
    try:
        clienteEditar = Cliente.objects.get(usuario=request.user)

        dataCliente = {
            'nombre': request.user.first_name,
            'apellido': request.user.last_name,
            'email': request.user.email,
            'direccion': clienteEditar.direccion,
            'telefono': clienteEditar.telefono,
            'dni': clienteEditar.dni,
            'sexo': clienteEditar.sexo,
            'fecha_nacimiento': clienteEditar.fecha_nacimiento
        }
    except:
        dataCliente = {
            'nombre': request.user.first_name,
            'apellido': request.user.last_name,
            'email': request.user.email,
        }

    formCliente = ClienteForm(dataCliente)

    return render(request, 'pedido.html',
                  {'formCliente': formCliente
                   }
                  )


@login_required(login_url='/login')
def confirmarPedido(request):
    if request.method == 'POST':
        # actualizar datos del usuario
        actUsuario = User.objects.get(pk=request.user.id)
        actUsuario.first_name = request.POST['nombre']
        actUsuario.last_name = request.POST['apellido']
        actUsuario.save()

        # registro o actualizacion del cliente
        try:
            clientePedido = Cliente.objects.get(usuario=request.user)
            clientePedido.telefono = request.POST['telefono']
            clientePedido.direccion = request.POST['direccion']
            clientePedido.save()
        except:
            clientePedido = Cliente()
            clientePedido.usuario = actUsuario
            clientePedido.telefono = request.POST['telefono']
            clientePedido.direccion = request.POST['direccion']
            clientePedido.save()

        # registro de nuevo pedido
        nroPedido = ''
        montoTotal = request.session.get('cartMontoTotal')
        nuevoPedido = Pedido()
        nuevoPedido.cliente = clientePedido
        nuevoPedido.save()

        # registro del detalle pedido
        carritoPedido = request.session.get('cart')
        for key, value in carritoPedido.items():
            productoPedido = Producto.objects.get(pk=value['producto_id'])
            detalle = PedidoDetalle()
            detalle.pedido = nuevoPedido
            detalle.producto = productoPedido
            detalle.cantidad = int(value['cantidad'])
            detalle.subtotal = float(value['subtotal'])
            detalle.save()

        # actualizar el pedido
        nroPedido = f'PED{nuevoPedido.fecha_registro.strftime("%Y")} {str(nuevoPedido.id)}'
        nuevoPedido.nro_pedido = nroPedido
        nuevoPedido.monto_total = montoTotal
        nuevoPedido.save()

        # registrar variable de sesion para el pedido
        request.session['pedidoId'] = nuevoPedido.id

        # creación del boton del paypal
        paypal_dict = {
            "business": settings.PAYPAL_USER_EMAIL,
            "amount": montoTotal,
            "item_name": f"PEDIDO CODIGO: {nroPedido}",
            "invoice": nroPedido,
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return": request.build_absolute_uri('/gracias'),
            "cancel_return": request.build_absolute_uri('/'),
        }

        # Create the instance.
        formPaypal = PayPalPaymentsForm(initial=paypal_dict)

        # limpiar carrito de compras
        carrito = Cart(request)
        carrito.clear()

    return render(request, 'compra.html', {
        'pedido': nuevoPedido,
        'formPaypal': formPaypal
    })


@login_required(login_url='/login')
def gracias(request):
    paypaldID = request.GET.get('PayerID', None)

    if paypaldID is not None:
        pedidoId = request.session.get('pedidoId')
        pedido = Pedido.objects.get(pk=pedidoId)
        pedido.estado = '1'
        pedido.save()

        send_mail(
            'GRACIAS POR TU COMPRA',
            f'Tu nro de pedido es: {pedido.nro_pedido}',
            settings.ADMIN_USER_EMAIL,
            [request.user.email],
            fail_silently=False,
        )
    else:
        return redirect('/')

    return render(request, 'gracias.html', {
        'pedido': pedido
    })
