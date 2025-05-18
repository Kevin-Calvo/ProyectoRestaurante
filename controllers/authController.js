// controllers/menuController.js
require('dotenv').config(); // Carga las variables del archivo .env

let controller;

// Selecciona el controlador según el tipo de base de datos definido en .env
switch (process.env.DB_MODE) {
  case 'mongo':
    console.log('[authController] Usando controlador MongoDB');
    controller = require('./authControllerMongo');
    break;

  case 'postgres':
    console.log('[authontroller] Usando controlador PostgreSQL');
    controller = require('./authControllerPostgres');
    break;

  default:
    throw new Error(`[authController] Tipo de base de datos no soportado: ${process.env.DB_MODE}`);
}

// Reexporta las funciones del controlador elegido
module.exports = {
  register: controller.register,
  login: controller.login,
  updateUser: controller.updateUser,
  deleteUser: controller.deleteUser,
  getMe: controller.getMe
};
