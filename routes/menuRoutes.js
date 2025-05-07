const express = require('express');
const { createMenuItem, getMenuByRestaurant, updateMenuItem, deleteMenuItem } = require('../controllers/menuController');
const authMiddleware = require('../middleware/authMiddleware');

const router = express.Router();

/**
 * @openapi
 * /menus:
 *   post:
 *     summary: Agregar un plato al menú
 *     tags: [Menus]
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
 *               descripcion:
 *                 type: string
 *               precio:
 *                 type: number
 *               restaurantId:
 *                 type: integer
 *     responses:
 *       201:
 *         description: Plato agregado al menú
 */
router.post('/', authMiddleware, createMenuItem);

/**
 * @openapi
 * /menus/{restaurantId}:
 *   get:
 *     summary: Obtener el menú de un restaurante
 *     tags: [Menus]
 *     parameters:
 *       - in: path
 *         name: restaurantId
 *         required: true
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: Menú del restaurante
 */
router.get('/:restaurantId', getMenuByRestaurant);

/**
 * @openapi
 * /menus/{id}:
 *   put:
 *     summary: Actualizar un plato del menú
 *     tags: [Menus]
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
 *               descripcion:
 *                 type: string
 *               precio:
 *                 type: number
 *     responses:
 *       200:
 *         description: Plato actualizado
 */
router.put('/:id', authMiddleware, updateMenuItem);

/**
 * @openapi
 * /menus/{id}:
 *   delete:
 *     summary: Eliminar un plato del menú
 *     tags: [Menus]
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
 *         description: Plato eliminado
 */
router.delete('/:id', authMiddleware, deleteMenuItem);

module.exports = router;

