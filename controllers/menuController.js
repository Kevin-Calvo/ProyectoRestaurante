// controllers/menuController.js
require('dotenv').config(); // Carga las variables del archivo .env

let controller;

// Selecciona el controlador según el tipo de base de datos definido en .env
switch (process.env.DB_MODE) {
  case 'mongo':
    console.log('[menuController] Usando controlador MongoDB');
    controller = require('./menuControllerMongo');
    break;

  case 'postgres':
    console.log('[menuController] Usando controlador PostgreSQL');
    controller = require('./menuControllerPostgres');
    break;

  default:
    throw new Error(`[menuController] Tipo de base de datos no soportado: ${process.env.DB_TYPE}`);
}

// Reexporta las funciones del controlador elegido
module.exports = {
  createMenuItem: controller.createMenuItem,
  getMenuByRestaurant: controller.getMenuByRestaurant,
  updateMenuItem: controller.updateMenuItem,
  deleteMenuItem: controller.deleteMenuItem,
};
