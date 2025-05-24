const Menu = require('../models/Menu');
const Restaurant = require('../models/Restaurant');

// Crear un plato en un restaurante (solo administradores)
exports.createMenuItem = async (req, res) => {
    try {
        if (req.user.role !== 'admin') {
            return res.status(403).json({ message: 'No autorizado' });
        }

        const { name, description, price, restaurantId } = req.body;

        const restaurant = await Restaurant.findByPk(restaurantId);
        if (!restaurant) {
            return res.status(404).json({ message: 'Restaurante no encontrado' });
        }

        const menuItem = await Menu.create({ name, description, price, restaurantId });

        res.status(201).json({ message: 'Plato agregado al menú', menuItem });
    } catch (error) {
        res.status(500).json({ message: 'Error al agregar el plato', error });
    }
};

exports.generate = async (req, res) => {
    res.json({message: "Funcion no valida para esta base de datos"});
};

//  Obtener el menú de un restaurante
exports.getMenuByRestaurant = async (req, res) => {
    try {
        const restaurantId = req.params.restaurantId;

        const menu = await Menu.findAll({ where: { restaurantId } });

        res.json(menu);
    } catch (error) {
        res.status(500).json({ message: 'Error al obtener el menú', error });
    }
};

//  Actualizar un plato en el menú (solo administradores)
exports.updateMenuItem = async (req, res) => {
    try {
        const menuItem = await Menu.findByPk(req.params.id);

        if (!menuItem) {
            return res.status(404).json({ message: 'Plato no encontrado' });
        }

        if (req.user.role !== 'admin') {
            return res.status(403).json({ message: 'No autorizado' });
        }

        const { name, description, price } = req.body;
        if (name) menuItem.name = name;
        if (description) menuItem.description = description;
        if (price) menuItem.price = price;

        await menuItem.save();
        res.json({ message: 'Plato actualizado', menuItem });
    } catch (error) {
        res.status(500).json({ message: 'Error al actualizar el plato', error });
    }
};

//  Eliminar un plato del menú (solo administradores)
exports.deleteMenuItem = async (req, res) => {
    try {
        const menuItem = await Menu.findByPk(req.params.id);

        if (!menuItem) {
            return res.status(404).json({ message: 'Plato no encontrado' });
        }

        if (req.user.role !== 'admin') {
            return res.status(403).json({ message: 'No autorizado' });
        }

        await menuItem.destroy();
        res.json({ message: 'Plato eliminado correctamente' });
    } catch (error) {
        res.status(500).json({ message: 'Error al eliminar el plato', error });
    }
};
