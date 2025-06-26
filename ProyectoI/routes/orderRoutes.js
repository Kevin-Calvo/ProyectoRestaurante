const express = require('express');
const { createOrder } = require('../controllers/orderController');
const authMiddleware = require('../middleware/authMiddleware');

const router = express.Router();
require('dotenv').config(); 

/**
 * @openapi
 * /orders:
 *   post:
 *     summary: Crear un nuevo pedido
 *     tags: [Orders]
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
 *               items:
 *                 type: array
 *                 items:
 *                   type: object
 *                   properties:
 *                     menuItemId:
 *                       type: integer
 *                     cantidad:
 *                       type: integer
 *     responses:
 *       201:
 *         description: Pedido creado exitosamente
 */
router.post('/', authMiddleware, createOrder);

module.exports = router;
