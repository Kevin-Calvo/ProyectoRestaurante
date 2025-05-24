const Restaurant = require('../mongoModels/restaurants');
const mongoConnector = require('../config/mongo');
const { faker } = require('@faker-js/faker');

// Crear un restaurante (solo administradores)
exports.createRestaurant = async (req, res) => {
    try {
        await mongoConnector();

        if (req.user.role !== 'admin') {
            return res.status(403).json({ message: 'No autorizado' });
        }

        const { name, address } = req.body;

        const restaurant = new Restaurant({
            name,
            address,
            owner_id: req.user.id
        });

        await restaurant.save();

        res.status(201).json({ message: 'Restaurante registrado con éxito', restaurant });
    } catch (error) {
        res.status(500).json({ message: 'Error al registrar el restaurante', error });
    }
};

exports.generate = async (req, res) => {
    try {
        await mongoConnector();

        if (req.user.role !== 'admin') {
            return res.status(403).json({ message: 'No autorizado' });
        }

        const restaurants = [];

        for (let i = 0; i < 20; i++) {
            restaurants.push({
                name: faker.company.companyName(),
                address: faker.address.streetAddress(),
                owner_id: req.user.id
            });
        }

        const created = await Restaurant.insertMany(restaurants);

        res.status(201).json({
            message: '20 restaurantes registrados con éxito',
            restaurantes: created
        });
    } catch (error) {
        res.status(500).json({
            message: 'Error al registrar los restaurantes',
            error
        });
    }
};

// Obtener todos los restaurantes
exports.getRestaurants = async (req, res) => {
    try {
        await mongoConnector();

        const restaurants = await Restaurant.find();
        res.json(restaurants);
    } catch (error) {
        res.status(500).json({ message: 'Error al obtener los restaurantes', error });
    }
};

// Actualizar un restaurante (solo el dueño o admin)
exports.updateRestaurant = async (req, res) => {
    try {
        await mongoConnector();

        const restaurant = await Restaurant.findById(req.params.id);

        if (!restaurant) {
            return res.status(404).json({ message: 'Restaurante no encontrado' });
        }

        if (req.user.role !== 'admin' && req.user.id !== restaurant.owner_id.toString()) {
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

// Eliminar un restaurante (solo el dueño o admin)
exports.deleteRestaurant = async (req, res) => {
    try {
        await mongoConnector();
        
        const restaurant = await Restaurant.findById(req.params.id);

        if (!restaurant) {
            return res.status(404).json({ message: 'Restaurante no encontrado' });
        }

        if (req.user.role !== 'admin' && req.user.id !== restaurant.owner_id.toString()) {
            return res.status(403).json({ message: 'No autorizado' });
        }

        await restaurant.deleteOne();
        res.json({ message: 'Restaurante eliminado correctamente' });
    } catch (error) {
        res.status(500).json({ message: 'Error al eliminar el restaurante', error });
    }
};
