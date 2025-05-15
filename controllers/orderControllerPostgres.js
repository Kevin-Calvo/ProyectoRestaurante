const Order = require('../models/Order'); 
const User = require('../models/User'); 
const Restaurant = require('../models/Restaurant'); 

// Crear una nueva orden
const createOrder = async (req, res) => {
    try {
        const { restaurantId } = req.body;
        const userId = req.user.id; // Obtener ID del usuario autenticado

        // Validar si el restaurante existe
        const restaurant = await Restaurant.findByPk(restaurantId);
        if (!restaurant) {
            return res.status(404).json({ message: 'Restaurante no encontrado' });
        }

        // Crear la orden
        const order = await Order.create({
            userId,
            restaurantId,
            status: 'pendiente' 
        });

        res.status(201).json(order);
    } catch (error) {
        res.status(500).json({ message: 'Error al crear la orden', error });
    }
};

// Obtener todas las órdenes de un usuario
const getUserOrders = async (req, res) => {
    try {
        const orders = await Order.findAll({
            where: { userId: req.user.id },
            include: [{ model: Restaurant, attributes: ['name'] }]
        });

        res.json(orders);
    } catch (error) {
        res.status(500).json({ message: 'Error al obtener las órdenes', error });
    }
};

// Cancelar una orden
const cancelOrder = async (req, res) => {
    try {
        const { id } = req.params;

        const order = await Order.findByPk(id);
        if (!order) {
            return res.status(404).json({ message: 'Orden no encontrada' });
        }

        // Verificar si el usuario es dueño de la orden
        if (order.userId !== req.user.id) {
            return res.status(403).json({ message: 'No puedes cancelar esta orden' });
        }

        await order.destroy();
        res.json({ message: 'Orden cancelada correctamente' });
    } catch (error) {
        res.status(500).json({ message: 'Error al cancelar la orden', error });
    }
};

module.exports = { createOrder, getUserOrders, cancelOrder };
