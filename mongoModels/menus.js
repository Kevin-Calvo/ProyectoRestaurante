const mongoose = require('mongoose');

const menuSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    maxlength: 100
  },
  description: {
    type: String,
    default: ''
  },
  price: {
    type: mongoose.Types.Decimal128, // Para manejar decimales con precisión
    required: true
  },
  restaurantId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Restaurant',
    required: true
  }
}, {
  timestamps: true,
  collection: 'menus'
});

module.exports = mongoose.model('Menu', menuSchema);

