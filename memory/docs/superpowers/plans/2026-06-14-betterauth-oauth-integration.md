# BetterAuth OAuth Integration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace fake cookie-based auth with BetterAuth (GitHub OAuth + Drizzle/PostgreSQL sessions + proxy-based route protection).

**Architecture:** BetterAuth server instance with Drizzle adapter (`@better-auth/drizzle-adapter`), `toNextJsHandler` for the API route, `nextCookies()` plugin for server action cookie handling, and `proxy.ts` for `/app` route protection using `auth.api.getSession()`. OAuth flow hits GitHub → callback at `/api/auth/callback/github` → session persisted in PostgreSQL.

**Tech Stack:** better-auth (1.6.19), @better-auth/drizzle-adapter, better-auth/next-js, Next.js 16, Drizzle ORM 0.45.2, PostgreSQL, React 19

---

### Task 1: Install Dependencies

**Files:**
- Modify: `package.json`
- Modify: `pnpm-lock.yaml` (auto)

- [ ] **Step 1: Add better-auth + adapter packages**

Run: `pnpm add better-auth @better-auth/drizzle-adapter`

Expected: Packages installed at latest versions (better-auth ~1.6.19).

- [ ] **Step 2: Verify install**

Run: `pnpm ls better-auth @better-auth/drizzle-adapter`

Expected: Both packages listed with versions.

---

### Task 2: Add BetterAuth Tables to Drizzle Schema

**Files:**
- Modify: `lib/db/schema.ts`

BetterAuth requires three tables for its core functionality: `user`, `session`, `account`.

- [ ] **Step 1: Add auth tables to schema**

In `lib/db/schema.ts`, append the following after the existing `documents` table:

```typescript
import { relations } from "drizzle-orm"
import { boolean, index } from "drizzle-orm/pg-core"

export const users = pgTable(
  "user",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    name: text("name"),
    email: text("email").notNull().unique(),
    emailVerified: boolean("email_verified").notNull().default(false),
    image: text("image"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .defaultNow()
      .notNull()
      .$onUpdate(() => new Date()),
  },
  (table) => [index("user_email_idx").on(table.email)],
)

export const sessions = pgTable(
  "session",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    expiresAt: timestamp("expires_at", { withTimezone: true }).notNull(),
    token: text("token").notNull().unique(),
    ipAddress: text("ip_address"),
    userAgent: text("user_agent"),
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    createdAt: timestamp("created_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .defaultNow()
      .notNull()
      .$onUpdate(() => new Date()),
  },
  (table) => [
    index("session_token_idx").on(table.token),
    index("session_user_id_idx").on(table.userId),
  ],
)

export const accounts = pgTable(
  "account",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    accountId: text("account_id").notNull(),
    providerId: text("provider_id").notNull(),
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    accessToken: text("access_token"),
    refreshToken: text("refresh_token"),
    idToken: text("id_token"),
    expiresAt: timestamp("expires_at", { withTimezone: true }),
    scope: text("scope"),
    password: text("password"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .defaultNow()
      .notNull()
      .$onUpdate(() => new Date()),
  },
  (table) => [
    index("account_user_id_idx").on(table.userId),
    index("account_provider_id_idx").on(table.providerId, table.accountId),
  ],
)

export const usersRelations = relations(users, ({ many }) => ({
  sessions: many(sessions),
  accounts: many(accounts),
}))

export const sessionsRelations = relations(sessions, ({ one }) => ({
  user: one(users, { fields: [sessions.userId], references: [users.id] }),
}))

export const accountsRelations = relations(accounts, ({ one }) => ({
  user: one(users, { fields: [accounts.userId], references: [users.id] }),
}))
```

The existing imports at the top of the file need to add `boolean, index` from `drizzle-orm/pg-core` and `relations` from `drizzle-orm`. The final top imports should be:

```typescript
import { relations } from "drizzle-orm"
import {
  boolean,
  index,
  pgEnum,
  pgTable,
  text,
  timestamp,
  uniqueIndex,
  uuid,
} from "drizzle-orm/pg-core"
```

---

### Task 3: Generate and Run Migration

**Files:**
- Create: `lib/db/migrations/0001_*.sql` (auto-generated)

- [ ] **Step 1: Generate migration**

Run: `pnpm db:generate`

Expected: Creates a new SQL file in `lib/db/migrations/` with CREATE TABLE statements for `user`, `session`, `account`.

- [ ] **Step 2: Run migration**

Run: `pnpm db:migrate`

Expected: Tables created in PostgreSQL. Output shows successful migration.

---

### Task 4: Create BetterAuth Server Config

**Files:**
- Create: `lib/auth/index.ts`

- [ ] **Step 1: Create auth config file**

Create `lib/auth/index.ts`:

```typescript
import { betterAuth } from "better-auth"
import { drizzleAdapter } from "@better-auth/drizzle-adapter"
import { nextCookies } from "better-auth/next-js"

import { getDb } from "@/lib/db"

export const auth = betterAuth({
  database: drizzleAdapter(getDb(), {
    provider: "pg",
    schema: {
      user: "user",
      session: "session",
      account: "account",
    },
  }),
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
  },
  plugins: [nextCookies()],
})
```

The `drizzleAdapter` receives the Drizzle instance from `getDb()`. The `provider: "pg"` tells it we're using PostgreSQL. The `schema` mapping ensures the adapter finds our tables (default names `user`, `session`, `account`).

`nextCookies()` plugin enables cookies to be set in server actions.

- [ ] **Step 2: Verify the file compiles**

Run: `pnpm exec tsc --noEmit --pretty lib/auth/index.ts`

Expected: No type errors.

---

### Task 5: Create BetterAuth API Route Handler

**Files:**
- Create: `app/api/auth/[...all]/route.ts`

- [ ] **Step 1: Create route handler**

Create `app/api/auth/[...all]/route.ts`:

```typescript
import { toNextJsHandler } from "better-auth/next-js"

import { auth } from "@/lib/auth"

export const { GET, POST } = toNextJsHandler(auth)
```

BetterAuth's `toNextJsHandler` handles all auth endpoints: sign-in, callback, session retrieval, sign-out, etc.

---

### Task 6: Create Proxy for Route Protection

**Files:**
- Create: `proxy.ts`

**Note:** Next.js 16 renamed `middleware.ts` to `proxy.ts`. The function export must be named `proxy`.

- [ ] **Step 1: Create proxy.ts at project root**

Create `proxy.ts`:

```typescript
import { headers } from "next/headers"
import { type NextRequest, NextResponse } from "next/server"

import { auth } from "@/lib/auth"

export async function proxy(request: NextRequest) {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    return NextResponse.redirect(new URL("/login", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    "/app/:path*",
  ],
}
```

The proxy runs on all `/app/*` paths, validates the session via BetterAuth (which checks the session cookie and validates against the database), and redirects unauthenticated users to `/login`.

Skip paths: `/login`, `/api/auth/*`, public routes (`/`, `/docs`, `/_next/*`, static files) — these are naturally excluded because the `matcher` only targets `/app/:path*`.

---

### Task 7: Update Login Page with OAuth Button

**Files:**
- Modify: `app/login/page.tsx`

- [ ] **Step 1: Rewrite login page to add GitHub OAuth button**

Replace `app/login/page.tsx` with:

```typescript
import Image from "next/image"
import Link from "next/link"

import { buttonVariants } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import { signIn } from "./actions"

export default function LoginPage() {
  return (
    <main
      className="flex min-h-screen items-center justify-center px-4 py-10 text-foreground sm:px-6"
      style={{
        backgroundImage: `
          radial-gradient(circle at 1px 1px, color-mix(in oklch, var(--line) 58%, transparent) 1px, transparent 0),
          radial-gradient(circle at 12px 12px, color-mix(in oklch, var(--line) 25%, transparent) 0.5px, transparent 0)
        `,
        backgroundSize: "24px 24px, 24px 24px",
        backgroundRepeat: "repeat, repeat",
      }}
    >
      <section className="w-full max-w-[27rem] rounded-[2rem] border border-(--line-strong) bg-(--panel) p-5 shadow-(--shadow-doc) sm:p-6">
        <div className="flex items-center justify-between gap-4">
          <Link
            href="/"
            className="inline-flex items-center rounded-full focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50"
          >
            <Image
              src="/brand/full-logo.svg"
              alt="Markdown2Share"
              width={178}
              height={20}
              priority
              className="h-6 w-auto"
            />
          </Link>

          <Link
            href="/docs"
            className="inline-flex h-10 items-center rounded-full px-3 text-sm font-medium text-muted-foreground transition-colors hover:bg-(--accent-soft) hover:text-(--accent-ink) focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50"
          >
            Docs
          </Link>
        </div>

        <div className="mt-9 space-y-2.5">
          <h1 className="font-sans text-3xl font-semibold tracking-[-0.03em] text-balance">
            Sign in to your workspace
          </h1>
          <p className="text-base leading-7 text-foreground/75 text-pretty">
            Continue to your Markdown pages, drafts, and shared document sets.
          </p>
        </div>

        <form action={signIn} className="mt-8">
          <button
            type="submit"
            className={cn(
              buttonVariants({ size: "lg" }),
              "h-12 w-full rounded-2xl text-base",
            )}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="currentColor"
              aria-hidden
            >
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
            Continue with GitHub
          </button>
        </form>

        <div className="my-6 flex items-center gap-3">
          <div className="h-px flex-1 bg-(--line-strong)" />
          <span className="text-sm text-muted-foreground">
            or continue with
          </span>
          <div className="h-px flex-1 bg-(--line-strong)" />
        </div>

        <form className="space-y-5">
          <div className="space-y-2">
            <Label htmlFor="email">Email address</Label>
            <Input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              className="h-12 rounded-2xl bg-background px-4 placeholder:text-foreground/55"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              className="h-12 rounded-2xl bg-background px-4"
            />
          </div>

          <button
            type="submit"
            disabled
            className={cn(
              buttonVariants({ size: "lg" }),
              "h-12 w-full rounded-2xl text-base opacity-50 cursor-not-allowed",
            )}
          >
            Sign in with email
          </button>
        </form>

        <p className="mt-6 text-center text-sm leading-6 text-muted-foreground">
          Email sign-in coming soon. Use GitHub to continue.
        </p>
      </section>
    </main>
  )
}
```

- [ ] **Step 2: Create the signIn server action**

Create `app/login/actions.ts`:

```typescript
"use server"

import { redirect } from "next/navigation"
import { auth } from "@/lib/auth"

export async function signIn() {
  await auth.api.signInSocial({
    body: {
      provider: "github",
      callbackURL: "/app",
    },
    headers: new Headers(),
  })
}
```

Note: `signInSocial` returns a redirect response; BetterAuth handles the redirect to GitHub OAuth.

---

### Task 8: Remove Layout Auth Guard

**Files:**
- Modify: `app/(auth)/app/layout.tsx`

- [ ] **Step 1: Remove redirect guard from layout**

Replace `app/(auth)/app/layout.tsx` with:

```typescript
import { SectionShell } from "@/components/layout/section-shell"

export default function AuthenticatedAppLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <SectionShell
      eyebrow="Authoring"
      title="Authenticated app"
      description="Private authoring surfaces live under /app and require a session."
    >
      {children}
    </SectionShell>
  )
}
```

The proxy handles route protection. The layout no longer needs `hasSession()` or `redirect()`.

---

### Task 9: Delete Old Auth File

**Files:**
- Delete: `lib/auth/session.ts`

- [ ] **Step 1: Remove old session utility**

Run: `Remove-Item -LiteralPath "lib\auth\session.ts"`

The fake cookie-based auth is fully replaced by BetterAuth.

---

### Task 10: Update Environment Variables

**Files:**
- Modify: `.env.example`

- [ ] **Step 1: Add BetterAuth + OAuth env vars**

Replace `.env.example` content with:

```
# Postgres connection string used by Drizzle ORM
# Format: postgres://user:password@host:port/database
DATABASE_URL="postgres://postgres:postgres@localhost:5432/markdown2share"

# BetterAuth base URL (your app's URL)
BETTER_AUTH_URL="http://localhost:3000"

# GitHub OAuth App credentials (create at https://github.com/settings/developers)
# Set Authorization callback URL to: http://localhost:3000/api/auth/callback/github
GITHUB_CLIENT_ID=""
GITHUB_CLIENT_SECRET=""
```

- [ ] **Step 2: Remind about local .env**

Note to the user: Create a `.env` file from the example and fill in GitHub OAuth credentials from [GitHub Developer Settings](https://github.com/settings/developers). The callback URL must be set to `http://localhost:3000/api/auth/callback/github`.

---

### Task 11: Verify Build and Lint

**Files:**
- None (validation only)

- [ ] **Step 1: Check TypeScript**

Run: `pnpm exec tsc --noEmit`

Expected: No type errors. If errors appear, fix them before proceeding.

- [ ] **Step 2: Run lint**

Run: `pnpm run lint`

Expected: No lint errors.

- [ ] **Step 3: Run build**

Run: `pnpm run build`

Expected: Successful build.
