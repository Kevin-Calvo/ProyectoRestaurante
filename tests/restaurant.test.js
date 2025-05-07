const request = require("supertest");
const app = require("../index");

describe("Restaurant API", () => {
  let token;

  beforeAll(async () => {
    // Simulación de autenticación
    const loginResponse = await request(app)
      .post("/auth/login")
      .send({ email: "admin@example.com", password: "adminpass" });

    token = loginResponse.body.token;
  });

  test("Debe crear un restaurante", async () => {
    const response = await request(app)
      .post("/restaurants")
      .set("Authorization", `Bearer ${token}`)
      .send({
        name: "Restaurante Prueba",
        address: "Calle 123"
      });

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty("message", "Restaurante creado con éxito");
  });

  test("Debe obtener la lista de restaurantes", async () => {
    const response = await request(app).get("/restaurants");

    expect(response.status).toBe(200);
    expect(response.body).toBeInstanceOf(Array);
  });
});
