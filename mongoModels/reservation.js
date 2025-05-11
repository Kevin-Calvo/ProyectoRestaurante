{
  _id: UUID,
  userId: UUID,        // referencia a `users._id`
  restaurantId: UUID,  // referencia a `restaurants._id`
  date: Date,
  guests: Number
}
