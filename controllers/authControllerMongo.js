const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../mongoModels/users');
const mongoConnector = require('../config/mongo');
const { generarClave } = require('../controllers/hashgenerator');
const redis = require('../config/redis'); 
const { faker } = require('@faker-js/faker');
require('dotenv').config();

const register = async (req, res) => {
  try {
    await mongoConnector();

    const { name, email, password, role } = req.body;

    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ message: 'El usuario ya existe' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const user = new User({
      name,
      email,
      password: hashedPassword,
      role,
    });

    await user.save();

    res.status(201).json({ message: 'Usuario registrado con éxito'});
  } catch (error) {
    console.error('Error al registrar usuario:', error);
    res.status(500).json({ message: 'Error en el servidor', error });
  }
};
const generate = async(req,res) => {
  try {
      const users = [];

      // 15 admins
      for (let i = 0; i < 15; i++) {
        users.push({
          name: faker.person.findName(),
          email: faker.internet.email().toLowerCase(),
          password: faker.internet.password(10),
          role: 'admin'
        });
      }

      // 45 clients
      for (let i = 0; i < 45; i++) {
        users.push({
          name: faker.person.findName(),
          email: faker.internet.email().toLowerCase(),
          password: faker.internet.password(10),
          role: 'client'
        });
      }

      const inserted = await User.insertMany(users);
      res.status(201).json({ message: `Usuarios generados: ${inserted.length}` });
    } catch (error) {
      res.status(500).json({ message: 'Error al generar usuarios', error });
    }
};

const login = async (req, res) => {
  try {
    await mongoConnector();

    const { email, password } = req.body;

    const user = await User.findOne({ email });
    if (!user) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(401).json({ message: 'Contraseña incorrecta' });
    }

    const token = jwt.sign(
      { id: user._id, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    res.json({ token });
  } catch (error) {
    console.error('Error en login:', error);
    res.status(500).json({ message: 'Error en el servidor', error });
  }
};

const updateUser = async (req, res) => {
  try {
    await mongoConnector();

    const { name, email, password } = req.body;

    const user = await User.findById(req.user.id);

    if (!user) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    if (name) user.name = name;
    if (email) user.email = email;
    if (password) {
      const salt = await bcrypt.genSalt(10);
      user.password = await bcrypt.hash(password, salt);
    }

    await user.save();

    // === ELIMINAR DE CACHÉ ===
    const categoria = 'usuario';
    const cacheKey = generarClave(categoria, req.user.id);
    await redis.del(cacheKey); 

    res.json({ message: 'Usuario actualizado correctamente' });
  } catch (error) {
    console.error('Error en updateUser:', error);
    res.status(500).json({ message: 'Error al actualizar usuario', error });
  }
};

const deleteUser = async (req, res) => {
  try {
    await mongoConnector();

    const user = await User.findById(req.params.id);

    if (!user) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    await user.deleteOne();

    // === ELIMINAR DE CACHÉ ===
    const categoria = 'usuario';
    const cacheKey = generarClave(categoria, req.user.id);
    await redis.del(cacheKey);

    res.json({ message: 'Usuario eliminado correctamente' });
  } catch (error) {
    res.status(500).json({ message: 'Error al eliminar usuario', error });
  }
};

const getMe = async (req, res) => {
  try {
    const categoria = 'usuario';
    const id = req.user.id;
    const cacheKey = generarClave(categoria, id);

    // 1. Buscar en Redis
    const cacheValue = await redis.get(cacheKey);
    if (cacheValue) {
      console.log('Datos desde caché Redis');
      return res.json(JSON.parse(cacheValue));
    }

    // 2. Buscar en Mongo
    await mongoConnector();
    const user = await User.findById(id).select('-password');
    if (!user) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    // 3. Guardar en Redis
    await redis.set(cacheKey, JSON.stringify(user), 3600); // 1 hora

    res.json(user);
  } catch (error) {
    console.error('Error al obtener usuario:', error);
    res.status(500).json({ message: 'Error al obtener usuario', error });
  }
};


module.exports = { register, generate, login, updateUser, deleteUser, getMe };
