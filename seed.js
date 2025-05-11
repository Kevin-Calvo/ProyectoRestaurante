const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

// URL de conexión al router mongos
const uri = 'mongodb://localhost:27017/reservas';

mongoose.connect(uri, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('Conectado a MongoDB'))
  .catch(err => console.error('Error de conexión', err));

// Esquemas básicos
const userSchema = new mongoose.Schema({
  _id: { type: String, default: uuidv4 },
  name: String,
  email: String,
  password: String,
  role: String,
  shardkey_custom: String
});

const restaurantSchema = new mongoose.Schema({
  _id: { type: String, default: uuidv4 },
  name: String,
  address: String,
  owner_id: String,
  shardkey_custom: String
});

const menuSchema = new mongoose.Schema({
  _id: { type: String, default: uuidv4 },
  name: String,
  description: String,
  price: Number,
  restaurantId: String,
  shardkey_custom: String
});

const orderSchema = new mongoose.Schema({
  _id: { type: String, default: uuidv4 },
  userId: String,
  restaurantId: String,
  status: String,
  shardkey_custom: String
});

const reservationSchema = new mongoose.Schema({
  _id: { type: String, default: uuidv4 },
  userId: String,
  restaurantId: String,
  date: Date,
  guests: Number,
  shardkey_custom: String
});

const User = mongoose.model('User', userSchema);
const Restaurant = mongoose.model('Restaurant', restaurantSchema);
const Menu = mongoose.model('Menu', menuSchema);
const Order = mongoose.model('Order', orderSchema);
const Reservation = mongoose.model('Reservation', reservationSchema);

async function seed() {
  await mongoose.connection.dropDatabase(); // ⚠️ Solo para pruebas

  const user = await User.create({
    name: 'Juan Pérez',
    email: 'juan@example.com',
    password: '123456',
    role: 'client',
    shardkey_custom: 'juan@example.com'
  });

  const restaurant = await Restaurant.create({
    name: 'El Sabor Tico',
    address: 'San José Centro',
    owner_id: user._id,
    shardkey_custom: 'El Sabor Tico'
  });

  const menu = await Menu.create({
    name: 'Casado',
    description: 'Casado con carne, arroz y frijoles',
    price: 3500,
    restaurantId: restaurant._id,
    shardkey_custom: 'Casado'
  });

  const order = await Order.create({
    userId: user._id,
    restaurantId: restaurant._id,
    status: 'pendiente',
    shardkey_custom: user.email
  });

  const reservation = await Reservation.create({
    userId: user._id,
    restaurantId: restaurant._id,
    date: new Date(),
    guests: 2,
    shardkey_custom: user.email
  });

  console.log('Datos de ejemplo insertados ✅');
  mongoose.disconnect();
}

seed();
