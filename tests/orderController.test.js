const { createOrder } = require('../controllers/orderControllerPostgres');
const Order = require('../models/Order');
const Restaurant = require('../models/Restaurant');

jest.mock('../models/Order');
jest.mock('../models/Restaurant');

describe('orderController - createOrder', () => {
  it('debería crear una orden si el restaurante existe', async () => {
    const mockRestaurant = { id: 1 };
    const mockOrder = {
      id: 10,
      userId: 5,
      restaurantId: 1,
      status: 'pendiente'
    };

    Restaurant.findByPk.mockResolvedValue(mockRestaurant);
    Order.create.mockResolvedValue(mockOrder);

    const req = {
      user: { id: 5 },
      body: { restaurantId: 1 }
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
    Restaurant.findByPk.mockResolvedValue(null); // Restaurante no existe

    const req = {
      user: { id: 5 },
      body: { restaurantId: 999 }
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
