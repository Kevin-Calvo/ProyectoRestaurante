const request = require("supertest");
const app = require("../index");

describe("Order API", () => {
  let token;
  let restaurantId;
  let menuId;

  beforeAll(async () => {
    const loginResponse = await request(app)
      .post("/auth/login")
      .send({ email: "client@example.com", password: "clientpass" });

    token = loginResponse.body.token;

    // Obtener un restaurante y un menú
    const restaurantResponse = await request(app).get("/restaurants");
    restaurantId = restaurantResponse.body[0].id;

    const menuResponse = await request(app).get(`/menus?restaurantId=${restaurantId}`);
    menuId = menuResponse.body[0].id;
  });

  test("Debe crear un pedido", async () => {
    const response = await request(app)
      .post("/orders")
      .set("Authorization", `Bearer ${token}`)
      .send({
        restaurantId,
        menuId,
        quantity: 2,
        pickup: true
      });

    expect(response.status).toBe(201);
  });
});
