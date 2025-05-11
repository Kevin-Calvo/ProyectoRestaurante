{
  _id: UUID,
  name: String,
  address: String,
  owner_id: UUID, // referencia a `users._id`
  createdAt: Date,
  updatedAt: Date
}
