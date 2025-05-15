const Restaurant = require('../models/Restaurant');
const User = require('../models/User');

//  Crear un restaurante (solo administradores)
exports.createRestaurant = async (req, res) => {
    try {
        if (req.user.role !== 'admin') {
            return res.status(403).json({ message: 'No autorizado' });
        }

        const { name, address } = req.body;

        const restaurant = await Restaurant.create({
            name,
            address,
            owner_id: req.user.id
        });

        res.status(201).json({ message: 'Restaurante registrado con éxito', restaurant });
    } catch (error) {
        res.status(500).json({ message: 'Error al registrar el restaurante', error });
    }
};

//  Obtener todos los restaurantes
exports.getRestaurants = async (req, res) => {
    try {
        const restaurants = await Restaurant.findAll();
        res.json(restaurants);
    } catch (error) {
        res.status(500).json({ message: 'Error al obtener los restaurantes', error });
    }
};

//  Actualizar un restaurante (solo el dueño o admin)
exports.updateRestaurant = async (req, res) => {
    try {
        const restaurant = await Restaurant.findByPk(req.params.id);

        if (!restaurant) {
            return res.status(404).json({ message: 'Restaurante no encontrado' });
        }

        if (req.user.role !== 'admin' && req.user.id !== restaurant.owner_id) {
            return res.status(403).json({ message: 'No autorizado' });
        }

        const { name, address } = req.body;
        if (name) restaurant.name = name;
        if (address) restaurant.address = address;

        await restaurant.save();
        res.json({ message: 'Restaurante actualizado', restaurant });
    } catch (error) {
        res.status(500).json({ message: 'Error al actualizar el restaurante', error });
    }
};

//  Eliminar un restaurante (solo el dueño o admin)
exports.deleteRestaurant = async (req, res) => {
    try {
        const restaurant = await Restaurant.findByPk(req.params.id);

        if (!restaurant) {
            return res.status(404).json({ message: 'Restaurante no encontrado' });
        }

        if (req.user.role !== 'admin' && req.user.id !== restaurant.owner_id) {
            return res.status(403).json({ message: 'No autorizado' });
        }

        await restaurant.destroy();
        res.json({ message: 'Restaurante eliminado correctamente' });
    } catch (error) {
        res.status(500).json({ message: 'Error al eliminar el restaurante', error });
    }
};
