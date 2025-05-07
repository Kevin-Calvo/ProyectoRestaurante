

# Reserva Inteligente de Restaurantes

**Reserva Inteligente de Restaurantes** es una API RESTful para gestionar la **reservación de mesas y pedidos en restaurantes**. El sistema permite registrar usuarios tanto **clientes** (que realizan reservas y órdenes) como **administradores de restaurante** (que gestionan sus restaurantes y menús). Forma parte de un proyecto académico, siguiendo buenas prácticas de desarrollo backend: autenticación segura con JWT, documentación de endpoints con Swagger y despliegue en contenedores Docker.

## Descripción General del Sistema

Este proyecto proporciona una base para administrar los datos y operaciones de un sistema de reservas de restaurantes. Incluye funcionalidades para:

- **Autenticación de usuarios**: registro y login de usuarios (clientes y administradores) con generación de tokens JWT para sesiones seguras.
- **Gestión de usuarios**: CRUD de usuarios con distinción de roles *(cliente* vs *admin*).
- **Gestión de restaurantes**: creación, actualización, consulta y eliminación de restaurantes (solo por administradores).
- **Gestión de menús**: los administradores pueden agregar, editar o quitar elementos del menú de un restaurante; los clientes pueden consultar los menús disponibles.
- **Reservas de mesas**: los clientes pueden crear y cancelar reservas de mesas en restaurantes, verificando disponibilidad.
- **Pedidos**: creación de pedidos de comida (por clientes) asociados a sus reservas o para llevar.

El enfoque es construir una API bien estructurada, modular y segura, que sirva como backend para una futura aplicación de reservas. Todas las operaciones críticas están protegidas mediante autenticación JWT y se documentan para su fácil consumo.

## Tecnologías Utilizadas

Las principales tecnologías y herramientas usadas en este proyecto son:

- **Node.js & Express** – Plataforma JavaScript de servidor y framework web para construir la API REST.
- **Sequelize** – ORM (Object Relational Mapper) de Node.js para manejar la base de datos relacional con modelos JavaScript.
- **PostgreSQL** – Sistema de Base de Datos relacional donde se almacenan usuarios, restaurantes, menús, reservas y pedidos.
- **Docker & Docker Compose** – Contenedorización de la aplicación y orquestación de múltiples servicios (API, base de datos, etc.) para facilitar el despliegue con un solo comando.
- **Swagger (OpenAPI)** – Documentación interactiva de la API. Permite describir los endpoints y probarlas desde un navegador (disponible en la ruta `/docs`).
- **JSON Web Tokens (JWT)** – Mecanismo de autenticación basado en tokens firmado digitalmente para proteger las rutas de la API.

## Instalación y Ejecución con Docker Compose

Siga estos pasos para levantar el sistema usando Docker Compose:

1. **Prerequisitos**: Tener instalados **Docker** y **Docker Compose** en su entorno.
2. **Clonar el repositorio**: Obtener una copia del código fuente del proyecto en su máquina local (por ejemplo, usando `git clone`).
3. **Configurar variables de entorno**: En la raíz del proyecto, cree un archivo `.env` con la configuración necesaria. Debe incluir las credenciales de la base de datos PostgreSQL y la clave secreta para JWT, entre otros. Por ejemplo, defina variables como `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` y `JWT_SECRET` según su entorno. Asegúrese de que estos valores coincidan con los configurados en el Docker Compose (por defecto, el servicio de base de datos en Docker podría usar host `db`, puerto `5432`, usuario/password `postgres`, etc., y un nombre de base de datos específico).
4. **Construir y levantar los contenedores**: Ejecute el comando **`docker-compose up --build`** en la raíz del proyecto. Este comando construirá la imagen Docker de la API y levantará tanto el contenedor de la API como el de la base de datos. *(Puede agregar el flag `-d` para ejecutar en modo desacoplado/background.)*
5. **Acceder a la API**: Una vez que los contenedores estén corriendo, la API estará disponible en el puerto configurado (por defecto `http://localhost:3000`). Puede verificar el funcionamiento accediendo a `http://localhost:3000/docs` en un navegador web, donde encontrará la documentación Swagger de la API (ver sección siguiente). Desde ahí, es posible probar endpoints (registro, login, CRUD, etc.) interactivamente. También puede usar herramientas como **curl** o **Postman** para hacer peticiones HTTP a los endpoints de la API.
6. **Detener el sistema**: Cuando desee bajar los servicios, ejecute **`docker-compose down`** para detener y eliminar los contenedores creados.

## Documentación de la API (Swagger)

La API está documentada utilizando **Swagger** (especificación OpenAPI). Al tener el servidor en funcionamiento, navegue a la ruta **`/docs`** (por ejemplo, [http://localhost:3000/docs](http://localhost:3000/docs)) para ver la documentación interactiva. En la interfaz de Swagger UI se listan todos los endpoints disponibles junto con sus detalles (métodos HTTP, parámetros de entrada, esquemas de respuesta y códigos de estado). 

Desde Swagger UI, puede **probar las distintas operaciones** de la API de forma directa: por ejemplo, registrarse como usuario nuevo, hacer login para obtener un token JWT, crear un restaurante nuevo (como administrador), listar restaurantes, hacer una reserva, etc. Simplemente seleccione el endpoint en la documentación, llene los parámetros necesarios y ejecute la petición para ver la respuesta del servidor. Esto facilita la verificación y prueba de la API sin necesidad de herramientas externas.

## Estructura de Carpetas del Proyecto

El proyecto está organizado en una estructura de carpetas que separa responsabilidades, lo que mejora la mantenibilidad y claridad del código. A continuación se muestra el esquema principal de directorios y archivos:

```
📦 Reserva-Inteligente-Restaurantes
├── controllers/       # Controladores: lógica de negocio de cada entidad (usuarios, restaurantes, etc.)
├── models/            # Modelos de datos definidos con Sequelize (User, Restaurant, Menu, Reservation, Order)
├── routes/            # Rutas de Express organizadas por recurso (mapean endpoints HTTP a controladores)
├── middleware/        # Middlewares (ej: autenticación JWT, verificación de rol admin)
├── config/            # Configuración de la app (por ejemplo, inicialización de Sequelize con PostgreSQL)
├── Dockerfile         # Definición de la imagen Docker para la API
├── docker-compose.yml # Configuración de servicios Docker (API, base de datos, etc.)
└── package.json       # Dependencias y scripts del proyecto
```

En resumen, el código fuente sigue un patrón MVC simplificado: los **modelos** definen la estructura de datos y reglas de negocio básicas, los **controladores** contienen la lógica aplicada a esos datos (operaciones CRUD y otras acciones), y las **rutas** exponen endpoints REST que invocan a los controladores correspondientes. Los **middlewares** (como la autenticación JWT) proveen funcionalidades transversales reutilizables, y la **configuración** de la aplicación (por ejemplo la conexión a la base de datos) se aísla en su propio módulo. Esta estructura modular facilita añadir o modificar funcionalidades de forma organizada.

## Autenticación y Autorización (JWT)

La seguridad de la API se implementa mediante **JWT (JSON Web Tokens)** para autenticar y autorizar las peticiones:

- **Obtención del token**: Para acceder a rutas protegidas, primero el cliente debe registrarse (`POST /auth/register`) y luego iniciar sesión mediante `POST /auth/login`. Al hacer login con credenciales válidas, el servidor genera un token JWT firmado con una clave secreta (definida en las variables de entorno). Este token contiene información del usuario (por ejemplo, su ID y rol).
- **Uso del token**: El cliente debe enviar el JWT en cada petición subsiguiente a rutas protegidas, usando la cabecera HTTP `Authorization` con el formato:  
  `Authorization: Bearer <token_jwt>`.  
  Un **middleware de autenticación** (`authMiddleware`) intercepta estas peticiones en el servidor: verifica y decodifica el token usando la clave secreta. Si el token es válido, se permite el acceso y la información del usuario autenticado se adjunta al `req` (request) para su uso en los controladores; si el token es inválido o no está presente, la API responde con un error **401 Unauthorized**.
- **Roles y permisos**: Existe una distinción de roles de usuario (*cliente* vs *admin*). Ciertas rutas requieren no solo un usuario autenticado, sino también un **administrador**. Por ejemplo, solo un admin puede crear o eliminar restaurantes, o añadir elementos de menú. Para estas situaciones, se emplea un segundo middleware (`adminMiddleware`) que, tras la autenticación JWT, verifica el rol del usuario (`req.user.role`). Si el rol no es *admin*, la API responde con **403 Forbidden**. De este modo, la autorización por roles se maneja de forma centralizada. En cambio, operaciones como crear reservas o hacer pedidos requieren ser un usuario autenticado (sin importar rol, asumiendo que solo clientes realizarán estas acciones).

En resumen, JWT asegura que solo usuarios con identidad verificada accedan a las funciones correspondientes, y los middlewares de autenticación/autorización simplifican la protección de múltiples endpoints de la API.

## Créditos

Proyecto desarrollado por **Samuel Duran y Cristhian Rivas** como parte de una entrega académica al Tecnológico de Costa Rica. ¡Gracias por revisar este repositorio!