import { NextResponse } from "next/server";

export async function POST() {
  const response = NextResponse.json({ success: true });
  
  // Удаляем cookie
  response.cookies.delete("admin_auth");
  
  return response;
}

