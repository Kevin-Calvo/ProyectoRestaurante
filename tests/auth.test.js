const request = require("supertest");
const app = require("../index"); // Importa la app de Express

describe("Auth API", () => {
  test("Debe registrar un usuario correctamente", async () => {
    const response = await request(app)
      .post("/auth/register")
      .send({
        name: "Test User",
        email: "test@example.com",
        password: "password123",
        role: "client"
      });

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty("message", "Usuario registrado con éxito");
  });

  test("Debe iniciar sesión y devolver un token", async () => {
    const response = await request(app)
      .post("/auth/login")
      .send({
        email: "test@example.com",
        password: "password123"
      });

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty("token");
  });
});
