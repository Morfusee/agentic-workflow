# MDP-01 Next.js App Router Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold a Next.js App Router app that cleanly separates public docs routes from authenticated authoring routes and proves the separation works locally.

**Architecture:** Keep the repo minimal. Use route groups for organization, keep the public surface under `/docs/*`, keep the authenticated surface under `/app/*`, and enforce protection from the authenticated layout instead of introducing middleware or a full auth provider this early. Use a temporary cookie-backed session boundary so this ticket stays a scaffold task instead of turning into a full authentication project.

**Tech Stack:** Next.js 16 App Router, React 19, TypeScript, Tailwind CSS 4, server actions, `next/headers`, `next/navigation`.

**Assumptions:**
- This ticket is only for scaffolding, not for selecting or integrating a production auth provider.
- A temporary cookie-based login gate is acceptable for satisfying the current acceptance criteria.
- `/` should redirect to `/docs` so the public surface is the default entrypoint.

---

### Task 1: Replace the starter page with route-group structure

**Files:**
- Modify: `app/layout.tsx`
- Modify: `app/page.tsx`
- Create: `app/(public)/layout.tsx`
- Create: `app/(public)/docs/page.tsx`
- Create: `app/(authenticated)/app/layout.tsx`
- Create: `app/(authenticated)/app/page.tsx`
- Create: `components/layout/section-shell.tsx`

- [ ] **Step 1: Replace the default metadata in `app/layout.tsx`**

Use app-level metadata that matches the product instead of the `create-next-app` defaults.

```tsx
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Markdown2Share",
  description: "Publish public docs and manage authenticated authoring surfaces.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full bg-background text-foreground">{children}</body>
    </html>
  );
}
```

- [ ] **Step 2: Make `/` redirect to `/docs`**

Replace the starter homepage with a redirect so the public docs surface is the default experience.

```tsx
import { redirect } from "next/navigation";

export default function HomePage() {
  redirect("/docs");
}
```

- [ ] **Step 3: Create a shared shell component**

Create `components/layout/section-shell.tsx` so both route groups use one shared frame instead of duplicating structure.

```tsx
type SectionShellProps = {
  eyebrow: string;
  title: string;
  description: string;
  children: React.ReactNode;
};

export function SectionShell({
  eyebrow,
  title,
  description,
  children,
}: SectionShellProps) {
  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-950">
      <div className="mx-auto flex min-h-screen w-full max-w-5xl flex-col px-6 py-10">
        <header className="border-b border-zinc-200 pb-6">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-zinc-500">
            {eyebrow}
          </p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight">{title}</h1>
          <p className="mt-3 max-w-2xl text-base leading-7 text-zinc-600">
            {description}
          </p>
        </header>
        <main className="flex-1 py-8">{children}</main>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Add the public route-group layout**

Create `app/(public)/layout.tsx` and keep it thin. It should wrap children with the shared shell.

```tsx
import { SectionShell } from "@/components/layout/section-shell";

export default function PublicLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <SectionShell
      eyebrow="Public docs"
      title="Documentation"
      description="Public-facing product and publishing documentation."
    >
      {children}
    </SectionShell>
  );
}
```

- [ ] **Step 5: Add the first public docs page**

Create `app/(public)/docs/page.tsx` with simple scaffold content that proves the route exists without authentication.

```tsx
export default function DocsPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold tracking-tight">Docs Home</h2>
      <p className="max-w-2xl text-zinc-600">
        This route is intentionally public and should render without a session.
      </p>
    </div>
  );
}
```

### Task 2: Add a minimal session boundary for scaffold auth

**Files:**
- Create: `lib/auth/session.ts`
- Create: `app/login/page.tsx`

- [ ] **Step 1: Create `lib/auth/session.ts`**

Keep the auth surface tiny and explicit so a real provider can replace it later.

```ts
import { cookies } from "next/headers";

export const SESSION_COOKIE_NAME = "mdp_session";

export async function hasSession() {
  const cookieStore = await cookies();
  return cookieStore.get(SESSION_COOKIE_NAME)?.value === "authenticated";
}
```

- [ ] **Step 2: Create a minimal login page with a server action**

Use a server action that sets the session cookie and redirects to `/app`. Do not build a real credential system in this ticket.

```tsx
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { SESSION_COOKIE_NAME } from "@/lib/auth/session";

export default function LoginPage() {
  async function signIn() {
    "use server";

    const cookieStore = await cookies();
    cookieStore.set(SESSION_COOKIE_NAME, "authenticated", {
      httpOnly: true,
      path: "/",
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
    });

    redirect("/app");
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-md items-center px-6">
      <form action={signIn} className="w-full space-y-4 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">Sign in</h1>
          <p className="text-sm text-zinc-600">
            Temporary scaffold login used only to verify protected route wiring.
          </p>
        </div>
        <button className="inline-flex h-11 items-center justify-center rounded-full bg-zinc-950 px-5 text-sm font-medium text-white">
          Continue to authoring
        </button>
      </form>
    </div>
  );
}
```

### Task 3: Protect the authenticated authoring surface

**Files:**
- Modify: `app/(authenticated)/app/layout.tsx`
- Modify: `app/(authenticated)/app/page.tsx`

- [ ] **Step 1: Gate the authenticated route-group layout**

Create `app/(authenticated)/app/layout.tsx` as an async layout that checks the session and redirects to `/login` when absent.

```tsx
import { redirect } from "next/navigation";

import { SectionShell } from "@/components/layout/section-shell";
import { hasSession } from "@/lib/auth/session";

export default async function AuthenticatedAppLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const authenticated = await hasSession();

  if (!authenticated) {
    redirect("/login");
  }

  return (
    <SectionShell
      eyebrow="Authoring"
      title="Authenticated app"
      description="Private authoring surfaces live under /app and require a session."
    >
      {children}
    </SectionShell>
  );
}
```

- [ ] **Step 2: Create the first authenticated page**

Create `app/(authenticated)/app/page.tsx` with scaffold content that proves the protected route works.

```tsx
export default function AuthoringHomePage() {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold tracking-tight">Authoring Home</h2>
      <p className="max-w-2xl text-zinc-600">
        This route should only be reachable after the scaffold login flow sets a session cookie.
      </p>
    </div>
  );
}
```

### Task 4: Tighten the basic styling and route affordances

**Files:**
- Modify: `app/globals.css`
- Modify: `components/layout/section-shell.tsx`

- [ ] **Step 1: Clean up global styles for the scaffold surfaces**

Keep the CSS minimal. Remove the starter body font override so the Geist variables actually drive typography.

```css
@import "tailwindcss";

:root {
  --background: #ffffff;
  --foreground: #171717;
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --font-sans: var(--font-geist-sans);
  --font-mono: var(--font-geist-mono);
}

body {
  margin: 0;
  background: var(--background);
  color: var(--foreground);
  font-family: var(--font-geist-sans), Arial, Helvetica, sans-serif;
}
```

- [ ] **Step 2: Add simple navigation links in the shared shell**

Update `components/layout/section-shell.tsx` so engineers can manually verify both surfaces without typing every URL.

```tsx
import Link from "next/link";

// inside the header block
<nav className="mt-5 flex gap-4 text-sm text-zinc-600">
  <Link href="/docs" className="hover:text-zinc-950">
    Docs
  </Link>
  <Link href="/app" className="hover:text-zinc-950">
    Authoring
  </Link>
  <Link href="/login" className="hover:text-zinc-950">
    Login
  </Link>
</nav>
```

### Task 5: Verify the acceptance criteria locally

**Files:**
- Validate: `app/**`
- Validate: `components/layout/**`
- Validate: `lib/auth/**`

- [ ] **Step 1: Run static validation**

Run:

```powershell
pnpm lint
pnpm build
```

Expected: both commands succeed with no route or type errors.

- [ ] **Step 2: Run the app locally**

Run:

```powershell
pnpm dev
```

Expected: Next.js starts successfully and reports the local dev URL.

- [ ] **Step 3: Verify the public route**

Check these URLs in the browser:

```text
http://localhost:3000/
http://localhost:3000/docs
```

Expected:
- `/` redirects to `/docs`
- `/docs` renders without logging in

- [ ] **Step 4: Verify the protected route**

Check this URL before and after signing in:

```text
http://localhost:3000/app
```

Expected:
- without a session, `/app` redirects to `/login`
- after clicking the login button, `/app` renders successfully

- [ ] **Step 5: Check the resulting route structure**

Confirm the final filesystem shape looks like this:

```text
app/
  (authenticated)/
    app/
      layout.tsx
      page.tsx
  (public)/
    docs/
      page.tsx
    layout.tsx
  login/
    page.tsx
  globals.css
  layout.tsx
  page.tsx
components/
  layout/
    section-shell.tsx
lib/
  auth/
    session.ts
```

Expected: route groups separate public and authenticated surfaces without changing the intended URLs.

- [ ] **Step 6: Commit**

Run:

```powershell
git add app components lib
git commit -m "feat: scaffold public and authenticated app routes"
```

Expected: the commit contains only scaffold routing, shared layout, and temporary auth-boundary changes.
