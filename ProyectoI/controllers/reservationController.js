// controllers/reservationController.js
require('dotenv').config();

let controller;

switch (process.env.DB_MODE) {
  case 'mongo':
    console.log('[reservationController] Usando controlador MongoDB');
    controller = require('./reservationControllerMongo');
    break;

  case 'postgres':
    console.log('[reservationController] Usando controlador PostgreSQL');
    controller = require('./reservationControllerPostgres');
    break;

  default:
    throw new Error(`[reservationController] Tipo de base de datos no soportado: ${process.env.DB_MODE}`);
}

module.exports = {
  createReservation: controller.createReservation,
  cancelReservation: controller.cancelReservation,
  checkAvailability: controller.checkAvailability,
};
