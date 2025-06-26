// controllers/restauranteController.js
require('dotenv').config();

let controller;
console.log('DEBUG - DB_MODE =', process.env.DB_MODE);

switch (process.env.DB_MODE) {
  case 'mongo':
    console.log('[restauranteController] Usando controlador MongoDB');
    controller = require('./restaurantControllerMongo');
    break;

  case 'postgres':
    console.log('[restauranteController] Usando controlador PostgreSQL');
    controller = require('./restaurantControllerPostgres');
    break;

  default:
    throw new Error(`[restauranteController] Tipo de base de datos no soportado: ${process.env.DB_MODE}`);
}

module.exports = {
  createRestaurant: controller.createRestaurant,
  generate: controller.generate,
  getRestaurants: controller.getRestaurants,
  updateRestaurant: controller.updateRestaurant,
  deleteRestaurant: controller.deleteRestaurant,
};
