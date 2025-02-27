from django.shortcuts import render, get_object_or_404, redirect
from .models import Categoria, Producto
from .carrito import Cart

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
