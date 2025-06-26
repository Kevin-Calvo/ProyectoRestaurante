const mongoose = require('mongoose');

const reservationSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User', // referencia al modelo User
    required: true
  },
  restaurantId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Restaurant', // referencia al modelo Restaurant
    required: true
  },
  date: {
    type: Date,
    required: true
  },
  guests: {
    type: Number,
    required: true
  }
}, {
  timestamps: true,
  collection: 'reservations'
});

module.exports = mongoose.model('Reservation', reservationSchema);
