// controllers/orderController.js
require('dotenv').config();

let controller;

switch (process.env.DB_TYPE) {
  case 'mongo':
    console.log('[orderController] Usando controlador MongoDB');
    controller = require('./orderControllerMongo');
    break;

  case 'postgres':
    console.log('[orderController] Usando controlador PostgreSQL');
    controller = require('./orderControllerPostgres');
    break;

  default:
    throw new Error(`[orderController] Tipo de base de datos no soportado: ${process.env.DB_TYPE}`);
}

module.exports = {
  createOrder: controller.createOrder,
  getUserOrders: controller.getUserOrders,
  cancelOrder: controller.cancelOrder,
};
