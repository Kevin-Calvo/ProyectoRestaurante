const express = require('express');
const { createRestaurant, getRestaurants, updateRestaurant, deleteRestaurant } = require('../controllers/restaurantController');
const authMiddleware = require('../middleware/authMiddleware');

const router = express.Router();
require('dotenv').config(); 

/**
 * @openapi
 * /restaurants:
 *   post:
 *     summary: Crear un nuevo restaurante
 *     tags: [Restaurants]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               nombre:
 *                 type: string
 *               direccion:
 *                 type: string
 *     responses:
 *       201:
 *         description: Restaurante creado
 */
router.post('/', authMiddleware, createRestaurant);

/**
 * @openapi
 * /restaurants:
 *   get:
 *     summary: Obtener todos los restaurantes
 *     tags: [Restaurants]
 *     responses:
 *       200:
 *         description: Lista de restaurantes
 */
router.get('/', getRestaurants);

/**
 * @openapi
 * /restaurants/{id}:
 *   put:
 *     summary: Actualizar un restaurante
 *     tags: [Restaurants]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               nombre:
 *                 type: string
 *               direccion:
 *                 type: string
 *     responses:
 *       200:
 *         description: Restaurante actualizado
 */
router.put('/:id', authMiddleware, updateRestaurant);

/**
 * @openapi
 * /restaurants/{id}:
 *   delete:
 *     summary: Eliminar un restaurante
 *     tags: [Restaurants]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: Restaurante eliminado
 */
router.delete('/:id', authMiddleware, deleteRestaurant);

module.exports = router;