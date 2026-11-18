// comprar.js
// Conecta los botones "Buy Now" y "Buy N products" de cart.html con la
// base de datos de inventario. No cambia nada del diseño.

document.addEventListener("DOMContentLoaded", function () {
  // Todas las filas de productos del carrito (en el mismo orden que en app.py)
  var filas = document.querySelectorAll(".cart-item");

  // Arma el "pedido" de una fila: su posición en el carrito y su cantidad
  function pedidoDeFila(indice) {
    var cantidadTexto = filas[indice].querySelector(".qty-value").textContent;
    var cantidad = parseInt(cantidadTexto, 10) || 1;
    return { indice: indice, cantidad: cantidad };
  }

  // Manda la compra al servidor (Flask) y muestra el resultado
  function enviarCompra(pedidos) {
    fetch("/comprar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pedidos: pedidos })
    })
      .then(function (respuesta) { return respuesta.json(); })
      .then(function (datos) {
        alert(datos.mensaje);
        if (datos.ok) {
          window.location.reload(); // recarga para que el carrito se vea actualizado
        }
      })
      .catch(function () {
        alert("No se pudo conectar con el servidor");
      });
  }

  // Botón "Buy Now" de cada producto: compra solo ese producto
  filas.forEach(function (fila, i) {
    var boton = fila.querySelector(".btn-buy-now");
    if (boton) {
      boton.addEventListener("click", function () {
        enviarCompra([pedidoDeFila(i)]);
      });
    }
  });

  // Botón grande "Buy N products": compra todos los productos marcados con el check
  var checkout = document.querySelector(".btn-checkout");
  if (checkout) {
    checkout.addEventListener("click", function () {
      var pedidos = [];
      filas.forEach(function (fila, i) {
        var check = fila.querySelector(".cart-item-checkbox");
        if (check && check.checked) {
          pedidos.push(pedidoDeFila(i));
        }
      });
      if (pedidos.length === 0) {
        alert("Selecciona al menos un producto");
        return;
      }
      enviarCompra(pedidos);
    });
  }
});