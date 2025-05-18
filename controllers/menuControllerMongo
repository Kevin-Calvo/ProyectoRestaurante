const Menu = require('../mongoModels/menus'); // Ajusta la ruta si es necesario
const Restaurant = require('../mongoModels/restaurants');
const mongoConnector = require('../config/mongo');

exports.createMenuItem = async (req, res) => {
  try {
    await mongoConnector();

    if (req.user.role !== 'admin') {
      return res.status(403).json({ message: 'No autorizado' });
    }

    const { name, description, price, restaurantId } = req.body;

    // Buscar restaurante en MongoDB
    const restaurant = await Restaurant.findById(restaurantId);
    if (!restaurant) {
      return res.status(404).json({ message: 'Restaurante no encontrado' });
    }

    // Crear nuevo plato en el menú
    const menuItem = new Menu({
      name,
      description,
      price,
      restaurantId
    });

    await menuItem.save();

    res.status(201).json({ message: 'Plato agregado al menú', menuItem });
  } catch (error) {
    res.status(500).json({ message: 'Error al agregar el plato', error });
  }
};

exports.getMenuByRestaurant = async (req, res) => {
  try {
    await mongoConnector();

    const { restaurantId } = req.params;

    // Buscar todos los platos cuyo restaurantId sea el dado
    const menu = await Menu.find({ restaurantId });

    res.json(menu);
  } catch (error) {
    res.status(500).json({ message: 'Error al obtener el menú', error });
  }
};

exports.updateMenuItem = async (req, res) => {
  try {
    await mongoConnector();

    if (req.user.role !== 'admin') {
      return res.status(403).json({ message: 'No autorizado' });
    }

    const { id } = req.params;
    const { name, description, price } = req.body;

    // Buscar el ítem del menú por ID
    const menuItem = await Menu.findById(id);

    if (!menuItem) {
      return res.status(404).json({ message: 'Plato no encontrado' });
    }

    // Actualizar solo los campos provistos
    if (name) menuItem.name = name;
    if (description) menuItem.description = description;
    if (price) menuItem.price = price;

    await menuItem.save();
    res.json({ message: 'Plato actualizado', menuItem });
  } catch (error) {
    res.status(500).json({ message: 'Error al actualizar el plato', error });
  }
};

// Eliminar un plato del menú (solo administradores)
exports.deleteMenuItem = async (req, res) => {
  try {
    await mongoConnector();
    
    if (req.user.role !== 'admin') {
      return res.status(403).json({ message: 'No autorizado' });
    }

    const menuItem = await Menu.findById(req.params.id);

    if (!menuItem) {
      return res.status(404).json({ message: 'Plato no encontrado' });
    }

    await menuItem.deleteOne(); // Método recomendado en Mongoose en lugar de destroy()
    res.json({ message: 'Plato eliminado correctamente' });
  } catch (error) {
    res.status(500).json({ message: 'Error al eliminar el plato', error });
  }
};
