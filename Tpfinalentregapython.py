"""
Sistema de Gestión de Inventario
Programa para administrar productos en una base de datos SQLite
"""

import sqlite3
from typing import Optional, List, Tuple

# Intentar importar colorama para mejorar la interfaz (opcional)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR_DISPONIBLE = True
except ImportError:
    COLOR_DISPONIBLE = False
    # Definir clases vacías si colorama no está disponible
    class Fore:
        GREEN = YELLOW = RED = CYAN = MAGENTA = BLUE = ""
    class Style:
        BRIGHT = RESET_ALL = ""


class GestorInventario:
    """Clase principal para gestionar el inventario de productos"""
    
    def __init__(self, nombre_bd: str = "inventario.db"):
        """
        Inicializa el gestor de inventario y crea la base de datos si no existe
        
        Args:
            nombre_bd: Nombre del archivo de base de datos SQLite
        """
        self.nombre_bd = nombre_bd
        self.crear_tabla()
    
    def crear_conexion(self) -> sqlite3.Connection:
        """Crea y retorna una conexión a la base de datos"""
        return sqlite3.connect(self.nombre_bd)
    
    def crear_tabla(self) -> None:
        """Crea la tabla 'productos' si no existe"""
        conn = self.crear_conexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL,
                categoria TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def registrar_producto(self, nombre: str, descripcion: str, cantidad: int, 
                          precio: float, categoria: str) -> bool:
        """
        Registra un nuevo producto en la base de datos
        
        Args:
            nombre: Nombre del producto
            descripcion: Descripción del producto
            cantidad: Cantidad disponible
            precio: Precio del producto
            categoria: Categoría del producto
            
        Returns:
            True si el registro fue exitoso, False en caso contrario
        """
        try:
            conn = self.crear_conexion()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, descripcion, cantidad, precio, categoria))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al registrar producto: {e}")
            return False
    
    def visualizar_productos(self) -> List[Tuple]:
        """
        Obtiene todos los productos de la base de datos
        
        Returns:
            Lista de tuplas con los datos de todos los productos
        """
        conn = self.crear_conexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        
        conn.close()
        return productos
    
    def buscar_producto_por_id(self, id_producto: int) -> Optional[Tuple]:
        """
        Busca un producto específico por su ID
        
        Args:
            id_producto: ID del producto a buscar
            
        Returns:
            Tupla con los datos del producto o None si no existe
        """
        conn = self.crear_conexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,))
        producto = cursor.fetchone()
        
        conn.close()
        return producto
    
    def buscar_productos_por_nombre(self, nombre: str) -> List[Tuple]:
        """
        Busca productos por nombre (búsqueda parcial)
        
        Args:
            nombre: Nombre o parte del nombre a buscar
            
        Returns:
            Lista de tuplas con los productos encontrados
        """
        conn = self.crear_conexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM productos WHERE nombre LIKE ?", (f"%{nombre}%",))
        productos = cursor.fetchall()
        
        conn.close()
        return productos
    
    def buscar_productos_por_categoria(self, categoria: str) -> List[Tuple]:
        """
        Busca productos por categoría
        
        Args:
            categoria: Categoría a buscar
            
        Returns:
            Lista de tuplas con los productos encontrados
        """
        conn = self.crear_conexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM productos WHERE categoria LIKE ?", (f"%{categoria}%",))
        productos = cursor.fetchall()
        
        conn.close()
        return productos
    
    def actualizar_producto(self, id_producto: int, nombre: str = None, 
                           descripcion: str = None, cantidad: int = None,
                           precio: float = None, categoria: str = None) -> bool:
        """
        Actualiza los datos de un producto existente
        
        Args:
            id_producto: ID del producto a actualizar
            nombre: Nuevo nombre (opcional)
            descripcion: Nueva descripción (opcional)
            cantidad: Nueva cantidad (opcional)
            precio: Nuevo precio (opcional)
            categoria: Nueva categoría (opcional)
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        # Verificar que el producto existe
        if not self.buscar_producto_por_id(id_producto):
            print(f"{Fore.RED}El producto con ID {id_producto} no existe.")
            return False
        
        try:
            conn = self.crear_conexion()
            cursor = conn.cursor()
            
            # Construir la consulta SQL dinámicamente según los campos a actualizar
            campos_actualizar = []
            valores = []
            
            if nombre is not None:
                campos_actualizar.append("nombre = ?")
                valores.append(nombre)
            if descripcion is not None:
                campos_actualizar.append("descripcion = ?")
                valores.append(descripcion)
            if cantidad is not None:
                campos_actualizar.append("cantidad = ?")
                valores.append(cantidad)
            if precio is not None:
                campos_actualizar.append("precio = ?")
                valores.append(precio)
            if categoria is not None:
                campos_actualizar.append("categoria = ?")
                valores.append(categoria)
            
            if not campos_actualizar:
                print(f"{Fore.YELLOW}No se especificaron campos para actualizar.")
                return False
            
            valores.append(id_producto)
            consulta = f"UPDATE productos SET {', '.join(campos_actualizar)} WHERE id = ?"
            
            cursor.execute(consulta, valores)
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al actualizar producto: {e}")
            return False
    
    def eliminar_producto(self, id_producto: int) -> bool:
        """
        Elimina un producto de la base de datos
        
        Args:
            id_producto: ID del producto a eliminar
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        # Verificar que el producto existe
        if not self.buscar_producto_por_id(id_producto):
            print(f"{Fore.RED}El producto con ID {id_producto} no existe.")
            return False
        
        try:
            conn = self.crear_conexion()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al eliminar producto: {e}")
            return False
    
    def reporte_bajo_stock(self, limite: int) -> List[Tuple]:
        """
        Genera un reporte de productos con cantidad igual o inferior al límite
        
        Args:
            limite: Cantidad límite para el reporte
            
        Returns:
            Lista de tuplas con los productos que cumplen la condición
        """
        conn = self.crear_conexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM productos WHERE cantidad <= ?", (limite,))
        productos = cursor.fetchall()
        
        conn.close()
        return productos


def mostrar_menu_principal() -> None:
    """Muestra el menú principal de la aplicación"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*60}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'SISTEMA DE GESTIÓN DE INVENTARIO':^60}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'='*60}")
    print(f"{Fore.GREEN}1. {Fore.YELLOW}Registrar nuevo producto")
    print(f"{Fore.GREEN}2. {Fore.YELLOW}Visualizar todos los productos")
    print(f"{Fore.GREEN}3. {Fore.YELLOW}Buscar producto")
    print(f"{Fore.GREEN}4. {Fore.YELLOW}Actualizar producto")
    print(f"{Fore.GREEN}5. {Fore.YELLOW}Eliminar producto")
    print(f"{Fore.GREEN}6. {Fore.YELLOW}Reporte de bajo stock")
    print(f"{Fore.GREEN}0. {Fore.RED}Salir")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'='*60}")


def mostrar_producto(producto: Tuple) -> None:
    """
    Muestra los detalles de un producto de forma formateada
    
    Args:
        producto: Tupla con los datos del producto
    """
    print(f"{Fore.CYAN}{'─'*60}")
    print(f"{Fore.GREEN}ID:          {Fore.YELLOW}{producto[0]}")
    print(f"{Fore.GREEN}Nombre:      {Fore.YELLOW}{producto[1]}")
    print(f"{Fore.GREEN}Descripción: {Fore.YELLOW}{producto[2]}")
    print(f"{Fore.GREEN}Cantidad:    {Fore.YELLOW}{producto[3]}")
    print(f"{Fore.GREEN}Precio:      {Fore.YELLOW}${producto[4]:.2f}")
    print(f"{Fore.GREEN}Categoría:   {Fore.YELLOW}{producto[5]}")
    print(f"{Fore.CYAN}{'─'*60}")


def obtener_entero(mensaje: str) -> Optional[int]:
    """
    Solicita al usuario un número entero con validación
    
    Args:
        mensaje: Mensaje a mostrar al usuario
        
    Returns:
        Número entero ingresado o None si hubo error
    """
    try:
        return int(input(mensaje))
    except ValueError:
        print(f"{Fore.RED}Error: Debe ingresar un número entero válido.")
        return None


def obtener_decimal(mensaje: str) -> Optional[float]:
    """
    Solicita al usuario un número decimal con validación
    
    Args:
        mensaje: Mensaje a mostrar al usuario
        
    Returns:
        Número decimal ingresado o None si hubo error
    """
    try:
        return float(input(mensaje))
    except ValueError:
        print(f"{Fore.RED}Error: Debe ingresar un número válido.")
        return None


def opcion_registrar(gestor: GestorInventario) -> None:
    """Maneja la opción de registrar un nuevo producto"""
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}REGISTRAR NUEVO PRODUCTO")
    print(f"{Fore.CYAN}{'─'*60}")
    
    nombre = input(f"{Fore.GREEN}Nombre del producto: {Fore.YELLOW}")
    descripcion = input(f"{Fore.GREEN}Descripción: {Fore.YELLOW}")
    
    cantidad = obtener_entero(f"{Fore.GREEN}Cantidad: {Fore.YELLOW}")
    if cantidad is None:
        return
    
    precio = obtener_decimal(f"{Fore.GREEN}Precio: {Fore.YELLOW}$")
    if precio is None:
        return
    
    categoria = input(f"{Fore.GREEN}Categoría: {Fore.YELLOW}")
    
    if gestor.registrar_producto(nombre, descripcion, cantidad, precio, categoria):
        print(f"{Fore.GREEN}{Style.BRIGHT}✓ Producto registrado exitosamente.")
    else:
        print(f"{Fore.RED}{Style.BRIGHT}✗ Error al registrar el producto.")


def opcion_visualizar(gestor: GestorInventario) -> None:
    """Maneja la opción de visualizar todos los productos"""
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}LISTADO DE PRODUCTOS")
    
    productos = gestor.visualizar_productos()
    
    if not productos:
        print(f"{Fore.YELLOW}No hay productos registrados en el inventario.")
        return
    
    print(f"{Fore.CYAN}Se encontraron {len(productos)} producto(s):\n")
    for producto in productos:
        mostrar_producto(producto)


def opcion_buscar(gestor: GestorInventario) -> None:
    """Maneja la opción de buscar productos"""
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}BUSCAR PRODUCTO")
    print(f"{Fore.CYAN}{'─'*60}")
    print(f"{Fore.GREEN}1. {Fore.YELLOW}Buscar por ID")
    print(f"{Fore.GREEN}2. {Fore.YELLOW}Buscar por nombre")
    print(f"{Fore.GREEN}3. {Fore.YELLOW}Buscar por categoría")
    print(f"{Fore.CYAN}{'─'*60}")
    
    opcion = input(f"{Fore.GREEN}Seleccione una opción: {Fore.YELLOW}")
    
    if opcion == "1":
        id_producto = obtener_entero(f"{Fore.GREEN}Ingrese el ID del producto: {Fore.YELLOW}")
        if id_producto is None:
            return
        
        producto = gestor.buscar_producto_por_id(id_producto)
        if producto:
            print(f"\n{Fore.CYAN}Producto encontrado:")
            mostrar_producto(producto)
        else:
            print(f"{Fore.YELLOW}No se encontró ningún producto con ese ID.")
    
    elif opcion == "2":
        nombre = input(f"{Fore.GREEN}Ingrese el nombre a buscar: {Fore.YELLOW}")
        productos = gestor.buscar_productos_por_nombre(nombre)
        
        if productos:
            print(f"\n{Fore.CYAN}Se encontraron {len(productos)} producto(s):")
            for producto in productos:
                mostrar_producto(producto)
        else:
            print(f"{Fore.YELLOW}No se encontraron productos con ese nombre.")
    
    elif opcion == "3":
        categoria = input(f"{Fore.GREEN}Ingrese la categoría a buscar: {Fore.YELLOW}")
        productos = gestor.buscar_productos_por_categoria(categoria)
        
        if productos:
            print(f"\n{Fore.CYAN}Se encontraron {len(productos)} producto(s):")
            for producto in productos:
                mostrar_producto(producto)
        else:
            print(f"{Fore.YELLOW}No se encontraron productos en esa categoría.")
    
    else:
        print(f"{Fore.RED}Opción no válida.")


def opcion_actualizar(gestor: GestorInventario) -> None:
    """Maneja la opción de actualizar un producto"""
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}ACTUALIZAR PRODUCTO")
    print(f"{Fore.CYAN}{'─'*60}")
    
    id_producto = obtener_entero(f"{Fore.GREEN}Ingrese el ID del producto a actualizar: {Fore.YELLOW}")
    if id_producto is None:
        return
    
    producto = gestor.buscar_producto_por_id(id_producto)
    if not producto:
        print(f"{Fore.RED}El producto con ID {id_producto} no existe.")
        return
    
    print(f"\n{Fore.CYAN}Producto actual:")
    mostrar_producto(producto)
    
    print(f"\n{Fore.YELLOW}Ingrese los nuevos valores (presione Enter para mantener el actual):")
    
    nombre = input(f"{Fore.GREEN}Nuevo nombre [{producto[1]}]: {Fore.YELLOW}") or None
    descripcion = input(f"{Fore.GREEN}Nueva descripción [{producto[2]}]: {Fore.YELLOW}") or None
    
    cantidad_input = input(f"{Fore.GREEN}Nueva cantidad [{producto[3]}]: {Fore.YELLOW}")
    cantidad = int(cantidad_input) if cantidad_input else None
    
    precio_input = input(f"{Fore.GREEN}Nuevo precio [${producto[4]:.2f}]: {Fore.YELLOW}")
    precio = float(precio_input) if precio_input else None
    
    categoria = input(f"{Fore.GREEN}Nueva categoría [{producto[5]}]: {Fore.YELLOW}") or None
    
    if gestor.actualizar_producto(id_producto, nombre, descripcion, cantidad, precio, categoria):
        print(f"{Fore.GREEN}{Style.BRIGHT}✓ Producto actualizado exitosamente.")
        
        # Mostrar el producto actualizado
        producto_actualizado = gestor.buscar_producto_por_id(id_producto)
        print(f"\n{Fore.CYAN}Producto actualizado:")
        mostrar_producto(producto_actualizado)
    else:
        print(f"{Fore.RED}{Style.BRIGHT}✗ Error al actualizar el producto.")


def opcion_eliminar(gestor: GestorInventario) -> None:
    """Maneja la opción de eliminar un producto"""
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}ELIMINAR PRODUCTO")
    print(f"{Fore.CYAN}{'─'*60}")
    
    id_producto = obtener_entero(f"{Fore.GREEN}Ingrese el ID del producto a eliminar: {Fore.YELLOW}")
    if id_producto is None:
        return
    
    producto = gestor.buscar_producto_por_id(id_producto)
    if not producto:
        print(f"{Fore.RED}El producto con ID {id_producto} no existe.")
        return
    
    print(f"\n{Fore.CYAN}Producto a eliminar:")
    mostrar_producto(producto)
    
    confirmacion = input(f"\n{Fore.RED}¿Está seguro de eliminar este producto? (S/N): {Fore.YELLOW}")
    
    if confirmacion.upper() == "S":
        if gestor.eliminar_producto(id_producto):
            print(f"{Fore.GREEN}{Style.BRIGHT}✓ Producto eliminado exitosamente.")
        else:
            print(f"{Fore.RED}{Style.BRIGHT}✗ Error al eliminar el producto.")
    else:
        print(f"{Fore.YELLOW}Operación cancelada.")


def opcion_reporte_bajo_stock(gestor: GestorInventario) -> None:
    """Maneja la opción de generar reporte de bajo stock"""
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}REPORTE DE BAJO STOCK")
    print(f"{Fore.CYAN}{'─'*60}")
    
    limite = obtener_entero(f"{Fore.GREEN}Ingrese el límite de cantidad: {Fore.YELLOW}")
    if limite is None:
        return
    
    productos = gestor.reporte_bajo_stock(limite)
    
    if not productos:
        print(f"{Fore.YELLOW}No hay productos con cantidad igual o inferior a {limite}.")
        return
    
    print(f"\n{Fore.RED}{Style.BRIGHT}⚠ ALERTA: {len(productos)} producto(s) con bajo stock:")
    for producto in productos:
        mostrar_producto(producto)


def main():
    """Función principal del programa"""
    # Inicializar el gestor de inventario
    gestor = GestorInventario()
    
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     SISTEMA DE GESTIÓN DE INVENTARIO - Versión 1.0        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    if not COLOR_DISPONIBLE:
        print("\nNota: Para una mejor experiencia visual, instale 'colorama':")
        print("pip install colorama\n")
    
    # Bucle principal del programa
    while True:
        mostrar_menu_principal()
        opcion = input(f"{Fore.GREEN}Seleccione una opción: {Fore.YELLOW}")
        
        if opcion == "1":
            opcion_registrar(gestor)
        elif opcion == "2":
            opcion_visualizar(gestor)
        elif opcion == "3":
            opcion_buscar(gestor)
        elif opcion == "4":
            opcion_actualizar(gestor)
        elif opcion == "5":
            opcion_eliminar(gestor)
        elif opcion == "6":
            opcion_reporte_bajo_stock(gestor)
        elif opcion == "0":
            print(f"\n{Fore.CYAN}{Style.BRIGHT}Gracias por usar el Sistema de Gestión de Inventario.")
            print("¡Hasta pronto!")
            break
        else:
            print(f"{Fore.RED}Opción no válida. Por favor, intente nuevamente.")
        
        # Pausa antes de mostrar el menú nuevamente
        input(f"\n{Fore.CYAN}Presione Enter para continuar...")


if __name__ == "__main__":
    main()
