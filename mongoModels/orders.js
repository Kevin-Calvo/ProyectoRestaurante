{
  _id: UUID,
  userId: UUID,         // referencia a `users._id`
  restaurantId: UUID,   // referencia a `restaurants._id`
  status: String        // ejemplo: "pendiente", "confirmado", etc.
}
