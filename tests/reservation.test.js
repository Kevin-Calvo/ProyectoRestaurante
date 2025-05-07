const request = require("supertest");
const app = require("../index");

describe("Reservation API", () => {
  let token;
  let restaurantId;
  let reservationId;

  beforeAll(async () => {
    // Simulación de autenticación
    const loginResponse = await request(app)
      .post("/auth/login")
      .send({ email: "client@example.com", password: "clientpass" });

    token = loginResponse.body.token;

    // Obtener ID de restaurante
    const restaurantResponse = await request(app).get("/restaurants");
    restaurantId = restaurantResponse.body[0].id;
  });

  test("Debe crear una reserva", async () => {
    const response = await request(app)
      .post("/reservations")
      .set("Authorization", `Bearer ${token}`)
      .send({
        restaurantId,
        date: "2025-03-22T19:00:00Z",
        guests: 2
      });

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty("message", "Reserva creada con éxito");

    reservationId = response.body.reservation.id;
  });

  test("Debe verificar disponibilidad de mesas", async () => {
    const response = await request(app)
      .get(`/reservations/availability?restaurantId=${restaurantId}&date=2025-03-22T19:00:00Z`)
      .set("Authorization", `Bearer ${token}`);

    expect(response.status).toBe(200);
  });

  test("Debe cancelar una reserva", async () => {
    const response = await request(app)
      .delete(`/reservations/${reservationId}`)
      .set("Authorization", `Bearer ${token}`);

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty("message", "Reserva cancelada con éxito");
  });
});
