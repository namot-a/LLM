import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;
  
  // Публичные роуты
  if (path === '/login') {
    return NextResponse.next();
  }
  
  // Проверяем cookie
  const authCookie = request.cookies.get('admin_auth')?.value;
  
  if (!authCookie || authCookie !== 'authenticated') {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|login).*)'],
};

