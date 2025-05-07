const request = require("supertest");
const app = require("../index");

describe("Menu API", () => {
  let token;
  let restaurantId;

  beforeAll(async () => {
    // Simulación de autenticación
    const loginResponse = await request(app)
      .post("/auth/login")
      .send({ email: "admin@example.com", password: "adminpass" });

    token = loginResponse.body.token;

    // Obtener ID de restaurante
    const restaurantResponse = await request(app).get("/restaurants");
    restaurantId = restaurantResponse.body[0].id;
  });

  test("Debe crear un menú", async () => {
    const response = await request(app)
      .post("/menus")
      .set("Authorization", `Bearer ${token}`)
      .send({
        name: "Pizza Margarita",
        description: "Pizza con queso y tomate",
        price: 8.99,
        restaurantId
      });

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty("message", "Menú creado con éxito");
  });

  test("Debe obtener los menús de un restaurante", async () => {
    const response = await request(app).get(`/menus?restaurantId=${restaurantId}`);

    expect(response.status).toBe(200);
    expect(response.body).toBeInstanceOf(Array);
  });
});
