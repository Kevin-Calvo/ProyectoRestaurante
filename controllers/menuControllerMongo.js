const Menu = require('../mongoModels/menus'); // Ajusta la ruta si es necesario
const Restaurant = require('../mongoModels/restaurants');
const mongoConnector = require('../config/mongo');
const { generarClave } = require('../controllers/hashgenerator');
const redis = require('../config/redis'); 

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
    const categoria = 'menu';
    const { restaurantId } = req.params;
    const cacheKey = generarClave(categoria, restaurantId);

    // 1. Buscar en Redis
    const cacheValue = await redis.get(cacheKey);
    if (cacheValue) {
      console.log('Menú desde caché Redis');
      return res.json(JSON.parse(cacheValue));
    }

    // 2. Buscar en Mongo
    await mongoConnector();
    const menu = await Menu.find({ restaurantId });

    console.log('📦 Menú desde MongoDB y guardado en Redis');
    res.json(menu);
  } catch (error) {
    console.error('Error al obtener el menú:', error);
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

    await menuItem.deleteOne(); 

    res.json({ message: 'Plato eliminado correctamente' });
  } catch (error) {
    res.status(500).json({ message: 'Error al eliminar el plato', error });
  }
};
