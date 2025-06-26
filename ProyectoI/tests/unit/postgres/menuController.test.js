const { getMenuByRestaurant } = require('../../../controllers/menuControllerPostgres');
const Menu = require('../../../models/Menu');

jest.mock('../../../models/Menu');

describe('menuController - getMenuByRestaurant', () => {
  it('debería retornar una lista de menús', async () => {
    const mockMenus = [
      { id: 1, name: 'Desayuno', restaurantId: 1 },
      { id: 2, name: 'Cena', restaurantId: 1 }
    ];

    Menu.findAll.mockResolvedValue(mockMenus);

    const req = { params: { restaurantId: 1 } };
    const res = {
      json: jest.fn(),
      status: jest.fn().mockReturnThis()
    };

    await getMenuByRestaurant(req, res);

    expect(res.json).toHaveBeenCalledWith(mockMenus);
  });

  it('debería retornar error 500 si ocurre una excepción', async () => {
    Menu.findAll.mockRejectedValue(new Error('Error interno'));

    const req = { params: { restaurantId: 1 } };
    const res = {
      json: jest.fn(),
      status: jest.fn().mockReturnThis()
    };

    await getMenuByRestaurant(req, res);

    expect(res.status).toHaveBeenCalledWith(500);
    expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
      message: 'Error al obtener el menú'
    }));
  });
});
