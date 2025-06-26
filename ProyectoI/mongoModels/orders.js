const mongoose = require('mongoose');

const orderSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User', // Referencia al modelo User
    required: true
  },
  restaurantId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Restaurant', // Referencia al modelo Restaurant
    required: true
  },
  status: {
    type: String,
    required: true,
    default: 'pendiente' // Estado inicial del pedido
  }
}, {
  timestamps: true,
  collection: 'orders'
});

module.exports = mongoose.model('Order', orderSchema);
