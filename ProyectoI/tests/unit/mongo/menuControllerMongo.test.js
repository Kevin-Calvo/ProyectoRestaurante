const { createMenuItem } = require('../../../controllers/menuControllerMongo');
const Menu = require('../../../mongoModels/menus');
const Restaurant = require('../../../mongoModels/restaurants');

jest.mock('../../../mongoModels/menus');
jest.mock('../../../mongoModels/restaurants');
jest.mock('../../../config/mongo', () => jest.fn().mockResolvedValue()); // mock de la conexión

describe('menuControllerMongo - createMenuItem', () => {
  it('debería agregar un plato si el usuario es admin y el restaurante existe', async () => {
    const mockRestaurant = { id: 'rest123' };
    const mockMenuItem = { name: 'Casado', description: 'Comida típica', price: 4500 };

    Restaurant.findById.mockResolvedValue(mockRestaurant);
    Menu.prototype.save = jest.fn().mockResolvedValue(mockMenuItem);

    const req = {
      user: { role: 'admin' },
      body: {
        name: 'Casado',
        description: 'Comida típica',
        price: 4500,
        restaurantId: 'rest123'
      }
    };

    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    await createMenuItem(req, res);

    expect(res.status).toHaveBeenCalledWith(201);
    expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
      message: 'Plato agregado al menú'
    }));
  });

  it('debería retornar 403 si el usuario no es admin', async () => {
    const req = {
      user: { role: 'client' },
      body: {
        name: 'Casado',
        description: 'Comida típica',
        price: 4500,
        restaurantId: 'rest123'
      }
    };

    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    await createMenuItem(req, res);

    expect(res.status).toHaveBeenCalledWith(403);
    expect(res.json).toHaveBeenCalledWith({ message: 'No autorizado' });
  });
});
