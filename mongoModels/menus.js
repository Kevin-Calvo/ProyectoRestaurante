{
  _id: UUID,
  name: String,
  description: String,
  price: Number,
  restaurantId: UUID, // referencia a `restaurants._id`
  createdAt: Date,
  updatedAt: Date
}
