// controllers/restauranteController.js
require('dotenv').config();

let controller;

switch (process.env.DB_TYPE) {
  case 'mongo':
    console.log('[restauranteController] Usando controlador MongoDB');
    controller = require('./restauranteControllerMongo');
    break;

  case 'postgres':
    console.log('[restauranteController] Usando controlador PostgreSQL');
    controller = require('./restauranteControllerPostgres');
    break;

  default:
    throw new Error(`[restauranteController] Tipo de base de datos no soportado: ${process.env.DB_TYPE}`);
}

module.exports = {
  createRestaurant: controller.createRestaurant,
  getRestaurants: controller.getRestaurants,
  updateRestaurant: controller.updateRestaurant,
  deleteRestaurant: controller.deleteRestaurant,
};
