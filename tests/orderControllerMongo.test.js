const { createOrder } = require('../controllers/orderControllerMongo');
const Order = require('../mongoModels/orders');
const Restaurant = require('../mongoModels/restaurants');

jest.mock('../mongoModels/orders');
jest.mock('../mongoModels/restaurants');
jest.mock('../config/mongo', () => jest.fn().mockResolvedValue()); // Mock de conexión Mongo

describe('orderControllerMongo - createOrder', () => {
  it('debería crear una orden si el restaurante existe', async () => {
    const mockRestaurant = { id: 'r1' };

    const mockOrder = {
      userId: 'u1',
      restaurantId: 'r1',
      status: 'pendiente',
      save: jest.fn().mockResolvedValue()
    };

    Restaurant.findById.mockResolvedValue(mockRestaurant);
    Order.mockImplementation(() => mockOrder);

    const req = {
      user: { id: 'u1' },
      body: { restaurantId: 'r1' }
    };

    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    await createOrder(req, res);

    expect(res.status).toHaveBeenCalledWith(201);
    expect(res.json).toHaveBeenCalledWith(mockOrder);
  });

  it('debería devolver 404 si el restaurante no existe', async () => {
    Restaurant.findById.mockResolvedValue(null); // Restaurante no encontrado

    const req = {
      user: { id: 'u1' },
      body: { restaurantId: 'r9' }
    };

    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    await createOrder(req, res);

    expect(res.status).toHaveBeenCalledWith(404);
    expect(res.json).toHaveBeenCalledWith({ message: 'Restaurante no encontrado' });
  });
});
