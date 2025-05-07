const express = require('express');
const { createReservation, cancelReservation, checkAvailability } = require('../controllers/reservationController');
const authMiddleware = require('../middleware/authMiddleware');

const router = express.Router();

/**
 * @openapi
 * /reservations:
 *   post:
 *     summary: Crear una nueva reserva
 *     tags: [Reservations]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               restaurantId:
 *                 type: integer
 *               fecha:
 *                 type: string
 *                 format: date
 *               hora:
 *                 type: string
 *               cantidadPersonas:
 *                 type: integer
 *     responses:
 *       201:
 *         description: Reserva creada exitosamente
 */
router.post('/', authMiddleware, createReservation);

/**
 * @openapi
 * /reservations/{id}:
 *   delete:
 *     summary: Cancelar una reserva
 *     tags: [Reservations]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: Reserva cancelada
 */
router.delete('/:id', authMiddleware, cancelReservation);

/**
 * @openapi
 * /reservations/availability:
 *   get:
 *     summary: Verificar disponibilidad de mesas
 *     tags: [Reservations]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Disponibilidad consultada
 */
router.get('/availability', authMiddleware, checkAvailability);

module.exports = router;
