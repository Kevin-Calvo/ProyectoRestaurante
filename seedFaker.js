const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');
const { faker } = require('@faker-js/faker');

const uri = 'mongodb://localhost:27017/reservas'; // Cambia si usás otro puerto

mongoose.connect(uri, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('Conectado a MongoDB'))
  .catch(err => console.error('Error de conexión', err));

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
  await mongoose.connection.dropDatabase();

  const users = [];
  for (let i = 0; i < 100; i++) {
    const email = faker.internet.email();
    users.push(new User({
      _id: uuidv4(),
      name: faker.person.fullName(),
      email,
      password: faker.internet.password(),
      role: faker.helpers.arrayElement(['client', 'admin']),
      shardkey_custom: email
    }));
  }
  await User.insertMany(users);

  const restaurants = [];
  for (let i = 0; i < 30; i++) {
    const owner = faker.helpers.arrayElement(users);
    const name = faker.company.name();
    restaurants.push(new Restaurant({
      _id: uuidv4(),
      name,
      address: faker.location.streetAddress(),
      owner_id: owner._id,
      shardkey_custom: name
    }));
  }
  await Restaurant.insertMany(restaurants);

  const menus = [];
  for (let i = 0; i < 150; i++) {
    const restaurant = faker.helpers.arrayElement(restaurants);
    const name = faker.commerce.productName();
    menus.push(new Menu({
      _id: uuidv4(),
      name,
      description: faker.commerce.productDescription(),
      price: parseFloat(faker.commerce.price()),
      restaurantId: restaurant._id,
      shardkey_custom: name
    }));
  }
  await Menu.insertMany(menus);

  const orders = [];
  for (let i = 0; i < 200; i++) {
    const user = faker.helpers.arrayElement(users);
    const restaurant = faker.helpers.arrayElement(restaurants);
    orders.push(new Order({
      _id: uuidv4(),
      userId: user._id,
      restaurantId: restaurant._id,
      status: faker.helpers.arrayElement(['pendiente', 'en camino', 'entregado']),
      shardkey_custom: user.email
    }));
  }
  await Order.insertMany(orders);

  const reservations = [];
  for (let i = 0; i < 100; i++) {
    const user = faker.helpers.arrayElement(users);
    const restaurant = faker.helpers.arrayElement(restaurants);
    reservations.push(new Reservation({
      _id: uuidv4(),
      userId: user._id,
      restaurantId: restaurant._id,
      date: faker.date.future(),
      guests: faker.number.int({ min: 1, max: 10 }),
      shardkey_custom: user.email
    }));
  }
  await Reservation.insertMany(reservations);

  console.log('🔥 Datos insertados exitosamente');
  mongoose.disconnect();
}

seed();
