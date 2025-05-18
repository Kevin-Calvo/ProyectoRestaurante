const Order = require('../mongoModels/orders');
const User = require('../mongoModels/users');
const Restaurant = require('../mongoModels/restaurants');
const mongoConnector = require('../config/mongo');

// Crear una nueva orden
const createOrder = async (req, res) => {
    try {
        await mongoConnector();

        const { restaurantId } = req.body;
        const userId = req.user.id;

        // Verificar que el restaurante existe
        const restaurant = await Restaurant.findById(restaurantId);
        if (!restaurant) {
            return res.status(404).json({ message: 'Restaurante no encontrado' });
        }

        // Crear la orden
        const order = new Order({
            userId,
            restaurantId,
            status: 'pendiente',
        });

        await order.save();
        res.status(201).json(order);
    } catch (error) {
        res.status(500).json({ message: 'Error al crear la orden', error });
    }
};

// Obtener todas las órdenes de un usuario
const getUserOrders = async (req, res) => {
    try {
        await mongoConnector();

        const orders = await Order.find({ userId: req.user.id })
            .populate('restaurantId', 'name'); // Solo traer el nombre del restaurante

        res.json(orders);
    } catch (error) {
        res.status(500).json({ message: 'Error al obtener las órdenes', error });
    }
};

// Cancelar una orden
const cancelOrder = async (req, res) => {
    try {
        await mongoConnector();
        
        const { id } = req.params;

        const order = await Order.findById(id);
        if (!order) {
            return res.status(404).json({ message: 'Orden no encontrada' });
        }

        // Verificar que el usuario es el dueño de la orden
        if (order.userId.toString() !== req.user.id) {
            return res.status(403).json({ message: 'No puedes cancelar esta orden' });
        }

        await order.deleteOne();
        res.json({ message: 'Orden cancelada correctamente' });
    } catch (error) {
        res.status(500).json({ message: 'Error al cancelar la orden', error });
    }
};

module.exports = { createOrder, getUserOrders, cancelOrder };
