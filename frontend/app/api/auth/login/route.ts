import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const { username, password } = await request.json();

    // Простая проверка (логин и пароль из env)
    const validUsername = process.env.ADMIN_USERNAME || "admin";
    const validPassword = process.env.ADMIN_PASSWORD || "admin123";

    if (username === validUsername && password === validPassword) {
      const response = NextResponse.json({ success: true });
      
      // Устанавливаем cookie
      response.cookies.set("admin_auth", "authenticated", {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        maxAge: 60 * 60 * 24 * 7, // 7 дней
        path: "/",
      });

      return response;
    }

    return NextResponse.json(
      { error: "Неверный логин или пароль" },
      { status: 401 }
    );
  } catch (error) {
    return NextResponse.json(
      { error: "Ошибка сервера" },
      { status: 500 }
    );
  }
}

