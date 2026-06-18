# MDP-04: Shared Application Shells & Environment Contract — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract reusable `PublicShell` and `AuthenticatedShell` layout components, and expand `.env.example` with documented environment variable contracts.

**Architecture:** Two new server-component shells in `components/layout/`. PublicShell wraps `/` and `/docs` with header and footer. AuthenticatedShell wraps `/app/*` with sidebar, header (search bar via client wrapper using `useSearchParams`), and user dropdown. Remove `SectionShell` when no longer referenced.

**Tech Stack:** Next.js 16 App Router, React 19, TypeScript, Tailwind CSS v4, BetterAuth v1.6, lucide-react, shadcn/ui

---

### Task 1: Expand `.env.example` with documented environment contracts

**Files:**
- Modify: `.env.example`

- [ ] **Step 1: Replace `.env.example` with documented contract**

```bash
# === Database ===
# PostgreSQL connection string used by Drizzle ORM for all database operations.
# Format: postgresql://user:password@host:port/database
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/markdown2share"

# === Authentication (BetterAuth) ===
# Base URL of the application — used by BetterAuth for redirects, callbacks, and cookie domain.
# In development this is typically http://localhost:3000.
BETTER_AUTH_URL="http://localhost:3000"

# BetterAuth signing secret — used to sign session tokens and cookies.
# Generate with: npx auth secret
BETTER_AUTH_SECRET=""

# === GitHub OAuth ===
# Create an OAuth App at https://github.com/settings/developers
# Set Authorization callback URL to: http://localhost:3000/api/auth/callback/github
GITHUB_CLIENT_ID=""
GITHUB_CLIENT_SECRET=""

# === Cache Revalidation (planned) ===
# On-demand revalidation token for Next.js Incremental Static Regeneration.
# When set, allows purging cached pages via /api/revalidate?secret=<token>.
# REVALIDATE_SECRET=""

# === MCP (planned) ===
# API key for connecting to a Model Context Protocol server.
# When set, enables MCP-based tool integrations.
# MCP_API_KEY=""
```

---

### Task 2: Create `SearchBar` client wrapper for use inside AuthenticatedShell

**Files:**
- Create: `components/layout/search-bar.tsx`

The authenticated header contains a search bar that reads the current query from URL params. Since AuthenticatedShell is a layout (server component, no `searchParams`), the search bar must be a client component using `useSearchParams()`.

- [ ] **Step 1: Write `components/layout/search-bar.tsx`**

```tsx
"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { DataTableSearch } from "@/components/blocks/data-table";

function SearchBarInner() {
  const searchParams = useSearchParams();
  const query = searchParams.get("q") ?? "";

  return (
    <DataTableSearch
      action="/app"
      value={query}
      placeholder="Search Markdown files"
      inputClassName="h-12 border-(--line-strong) bg-(--panel-2) pl-12 pr-5 text-base shadow-(--shadow-doc) placeholder:text-foreground/60 focus-visible:border-primary focus-visible:ring-primary/20 md:text-base"
      iconClassName="left-4 size-5"
    />
  );
}

export function SearchBar() {
  return (
    <Suspense>
      <SearchBarInner />
    </Suspense>
  );
}
```

---

### Task 3: Create `PublicShell` server component

**Files:**
- Create: `components/layout/public-shell.tsx`

Header bar matches the existing home page header (logo, docs link, conditional auth links) plus a footer.

- [ ] **Step 1: Write `components/layout/public-shell.tsx`**

```tsx
import Link from "next/link";
import { getSession } from "@/features/auth/actions/auth.action";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export async function PublicShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getSession();

  return (
    <div
      className="min-h-screen text-foreground"
      style={{
        backgroundImage: `
          radial-gradient(circle at 1px 1px, color-mix(in oklch, var(--line) 55%, transparent) 1px, transparent 0),
          radial-gradient(circle at 12px 12px, color-mix(in oklch, var(--line) 25%, transparent) 0.5px, transparent 0)
        `,
        backgroundSize: "24px 24px, 24px 24px",
        backgroundRepeat: "repeat, repeat",
        backgroundColor: "transparent",
      }}
    >
      <header className="border-b border-(--line-strong) bg-(--panel)/95">
        <div className="mx-auto flex w-full max-w-[min(90vw,1600px)] flex-col gap-3 px-4 py-3.5 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between sm:px-8 lg:px-10">
          <Link
            href="/"
            className="inline-flex items-center text-foreground"
            aria-label="Markdown2Share home"
          >
            <svg
              viewBox="21 15 89 88"
              className="size-10 sm:hidden"
              role="img"
              aria-label="Markdown2Share"
            >
              <g transform="translate(0,2)">
                <text
                  x="64" y="75"
                  textAnchor="middle"
                  fontFamily="Figtree, Inter, ui-sans-serif, system-ui, sans-serif"
                  fontSize="62" fontWeight="800" letterSpacing="-5"
                  fill="currentColor"
                >
                  M
                </text>
                <rect x="55" y="84" width="30" height="7" rx="3.5" fill="var(--primary)" />
                <circle cx="96" cy="87.5" r="4.5" fill="var(--primary)" />
              </g>
            </svg>
            <svg
              viewBox="0 0 640 72"
              className="hidden size-11 w-auto sm:block"
              role="img"
              aria-label="Markdown2Share"
            >
              <g transform="translate(0, -9) scale(0.8)">
                <text
                  x="64" y="75"
                  textAnchor="middle"
                  fontFamily="Figtree, Inter, ui-sans-serif, system-ui, sans-serif"
                  fontSize="62" fontWeight="800" letterSpacing="-5"
                  fill="currentColor"
                >
                  M
                </text>
                <rect x="55" y="84" width="30" height="7" rx="3.5" fill="var(--primary)" />
                <circle cx="96" cy="87.5" r="4.5" fill="var(--primary)" />
              </g>
              <line x1="96" y1="10" x2="96" y2="62" stroke="var(--primary)" strokeOpacity="0.42" strokeWidth="2" />
              <text
                x="112" y="50"
                fontFamily="Figtree, Inter, ui-sans-serif, system-ui, sans-serif"
                fontSize="48" fontWeight="700" letterSpacing="-2"
                fill="currentColor"
              >
                Markdown<tspan fill="var(--primary)">2Share</tspan>
              </text>
            </svg>
          </Link>

          <div className="flex w-full flex-wrap items-center gap-2 sm:w-auto sm:justify-end sm:gap-3">
            <nav aria-label="Primary" className="flex min-w-0 items-center">
              <Link
                href="/docs"
                className="inline-flex h-11 items-center justify-center rounded-full px-4 text-sm font-medium text-muted-foreground transition-colors hover:bg-(--accent-soft) hover:text-(--accent-ink) focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50"
              >
                Docs
              </Link>
            </nav>
            {session ? (
              <Link
                href="/app"
                className={cn(
                  buttonVariants({ variant: "outline" }),
                  "h-11 flex-1 rounded-full px-4 sm:flex-none",
                )}
              >
                Authoring
              </Link>
            ) : (
              <>
                <Link
                  href="/login"
                  className={cn(
                    buttonVariants({ variant: "outline" }),
                    "h-11 flex-1 rounded-full px-4 sm:flex-none",
                  )}
                >
                  Log in
                </Link>
                <Link
                  href="/login"
                  className={cn(
                    buttonVariants({ size: "default" }),
                    "h-11 flex-1 rounded-full px-4 sm:flex-none",
                  )}
                >
                  Try it out
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {children}

      <footer className="border-t border-(--line-strong) bg-(--panel-2)">
        <div className="mx-auto flex w-full max-w-[min(90vw,1600px)] flex-col items-center justify-between gap-4 px-8 py-6 text-sm text-muted-foreground sm:flex-row lg:px-10">
          <p>&copy; Markdown2Share</p>
          <nav className="flex items-center gap-6">
            <Link href="/docs" className="transition-colors hover:text-foreground">
              Docs
            </Link>
            <Link href={session ? "/app" : "/login"} className="transition-colors hover:text-foreground">
              {session ? "Authoring" : "Log in"}
            </Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
```

---

### Task 4: Update home page to use `PublicShell`

**Files:**
- Modify: `app/page.tsx`

Remove the inline header markup, wrap content in `<PublicShell>`.

- [ ] **Step 1: Rewrite `app/page.tsx`**

```tsx
import Link from "next/link";

import { PublicShell } from "@/components/layout/public-shell";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  MainFade,
  StaggerItem,
  SlideUp,
} from "@/components/layout/animated-content";
import { NeovimTypewriter } from "@/components/layout/neovim-typewriter";

const docTree = [
  "Overview",
  "Setup guide",
  "Publishing workflow",
  "Permissions",
  "Team handoff",
];

export default function HomePage() {
  return (
    <PublicShell>
      <MainFade>
        <section className="mx-auto grid min-h-[calc(100vh-4.75rem)] w-full items-center gap-8 px-4 py-8 sm:gap-10 sm:py-10 lg:grid-cols-[minmax(340px,0.58fr)_minmax(440px,1.42fr)] lg:gap-14 lg:px-10 xl:max-w-[1600px] xl:px-8 xl:py-12">
          <div className="w-full space-y-5 xl:max-w-xl">
            <p className="text-sm font-semibold text-(--accent-ink)">
              Markdown in. Shareable docs out.
            </p>

            <div className="space-y-4.5">
              <h1 className="max-w-xl font-sans text-[clamp(2.1rem,5vw,3.35rem)] font-semibold leading-[1.03] tracking-[-0.03em] text-balance">
                Publish Markdown as navigable pages.
              </h1>
              <p className="max-w-lg text-base leading-7 text-foreground/80 text-pretty sm:text-lg sm:leading-8">
                Turn drafts, runbooks, and team notes into polished public links
                without standing up a full documentation stack.
              </p>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
              <Link
                href="/login"
                className={cn(
                  buttonVariants({ size: "default" }),
                  "h-11 w-full rounded-full px-5 sm:w-auto",
                )}
              >
                Try it out
              </Link>
              <Link
                href="/docs"
                className={cn(
                  buttonVariants({ variant: "ghost", size: "default" }),
                  "h-11 w-full rounded-full px-5 text-muted-foreground hover:bg-(--accent-soft) hover:text-(--accent-ink) sm:w-auto",
                )}
              >
                View docs
              </Link>
            </div>

            <div className="border-t border-(--line) pt-6">
              <ul className="grid gap-2 sm:grid-cols-2 sm:gap-x-4 sm:gap-y-3">
                <StaggerItem delay={0} className="rounded-xl px-3 py-2">
                  <p className="text-sm font-medium text-foreground">
                    Instant publish
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Drop in Markdown and get a link in seconds
                  </p>
                </StaggerItem>
                <StaggerItem delay={0.08} className="rounded-xl px-3 py-2">
                  <p className="text-sm font-medium text-foreground">
                    Navigable docs
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Related pages become a browsable set
                  </p>
                </StaggerItem>
                <StaggerItem delay={0.16} className="rounded-xl px-3 py-2">
                  <p className="text-sm font-medium text-foreground">
                    Team handoff
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Share references without copy-paste drift
                  </p>
                </StaggerItem>
                <StaggerItem delay={0.24} className="rounded-xl px-3 py-2">
                  <p className="text-sm font-medium text-foreground">
                    Clean rendering
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Responsive pages that stay easy to read
                  </p>
                </StaggerItem>
              </ul>
            </div>
          </div>
          <SlideUp delay={0.15}>
            <section
              aria-label="Product preview"
              className="min-w-0 overflow-hidden rounded-xl border border-(--line-strong) bg-(--panel) shadow-(--shadow-doc) sm:rounded-2xl"
            >
              <div className="flex items-start justify-between gap-3 border-b border-border bg-(--panel-2) px-4 py-3.5 sm:px-5">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-foreground">
                    Shareable page set
                  </p>
                  <p className="text-xs leading-5 text-muted-foreground">
                    Draft in Markdown, publish as a linked document set
                  </p>
                </div>
                <div className="shrink-0 rounded-full border border-(--line) bg-(--accent-soft) px-3 py-1 text-xs font-medium text-(--accent-ink)">
                  Published
                </div>
              </div>

              <div className="grid min-w-0 gap-px bg-(--line) sm:grid-cols-[136px_minmax(0,1fr)] lg:grid-cols-[196px_minmax(0,1fr)]">
                <div className="min-w-0 bg-(--panel) px-4 py-4.5">
                  <p className="text-xs font-semibold text-(--accent-ink)">
                    Documents
                  </p>
                  <ul className="mt-3 flex gap-2 overflow-x-auto pb-1 text-sm sm:block sm:space-y-1.5 sm:overflow-visible sm:pb-0">
                    {docTree.map((item, index) => (
                      <li
                        key={item}
                        className={cn(
                          "shrink-0 rounded-md px-3 py-1.5 transition-colors sm:shrink",
                          index === 2
                            ? "bg-accent text-(--accent-ink)"
                            : "text-muted-foreground",
                        )}
                      >
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="grid min-w-0 gap-px bg-(--line) sm:grid-rows-[auto_auto]">
                  <div className="min-w-0 bg-(--panel) px-4 py-4.5 sm:px-5">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <p className="text-sm font-medium text-foreground">
                        Published page
                      </p>
                      <span className="text-xs text-muted-foreground">
                        Live link
                      </span>
                    </div>
                    <div className="mt-3 min-w-0 rounded-lg border border-(--line-strong) bg-background p-4 sm:rounded-xl sm:p-4.5">
                      <p className="text-sm font-medium text-(--accent-ink)">
                        Publishing workflow
                      </p>
                      <h2 className="mt-2.5 font-sans text-[clamp(1.2rem,3.5vw,1.8rem)] font-semibold tracking-tight text-balance text-foreground">
                        Ship updates without rebuilding the docs stack.
                      </h2>
                      <p className="mt-2.5 text-sm leading-6 text-muted-foreground">
                        Keep Markdown as the source of truth, publish a clean
                        page, and let readers move through related docs from one
                        shared navigation.
                      </p>
                      <div className="mt-4 flex flex-wrap gap-2 text-xs text-(--accent-ink)">
                        <span className="rounded-full border border-(--line) bg-(--accent-soft) px-3 py-1">
                          Public URL
                        </span>
                        <span className="rounded-full border border-(--line) bg-(--panel-2) px-3 py-1 text-foreground/80">
                          Linked docs
                        </span>
                        <span className="rounded-full border border-(--line) bg-(--panel-2) px-3 py-1 text-foreground/80">
                          Team-ready
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="min-w-0 bg-(--panel) px-4 py-4.5 sm:px-5">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-foreground">
                        Markdown
                      </p>
                      <span className="text-xs text-muted-foreground">
                        Draft
                      </span>
                    </div>
                    <pre className="mt-3 overflow-x-auto rounded-lg bg-(--code-bg) p-4 text-xs leading-6 text-(--code-text) sm:rounded-xl sm:text-sm">
                      <code>
                        <NeovimTypewriter />
                      </code>
                    </pre>
                  </div>
                </div>
              </div>
            </section>
          </SlideUp>
        </section>
      </MainFade>
    </PublicShell>
  );
}
```

---

### Task 5: Update docs layout to use `PublicShell`

**Files:**
- Modify: `app/(public)/docs/layout.tsx`

Replace `SectionShell` with `PublicShell`.

- [ ] **Step 1: Rewrite `app/(public)/docs/layout.tsx`**

```tsx
import { PublicShell } from "@/components/layout/public-shell";

export default function PublicLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return <PublicShell>{children}</PublicShell>;
}
```

---

### Task 6: Create `AuthenticatedShell` server component

**Files:**
- Create: `components/layout/authenticated-shell.tsx`

Extract sidebar, header, and user dropdown from `app/(auth)/app/page.tsx`. The search bar uses the `SearchBar` client wrapper.

- [ ] **Step 1: Write `components/layout/authenticated-shell.tsx`**

```tsx
import Image from "next/image";
import Link from "next/link";
import {
  FileTextIcon,
  FolderIcon,
  LogOutIcon,
  SettingsIcon,
  Share2Icon,
} from "lucide-react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { getSession, signOut } from "@/features/auth/actions/auth.action";
import { SearchBar } from "@/components/layout/search-bar";
import { buttonVariants } from "@/components/ui/button";

const workspaceLinks = [
  { label: "All", icon: FileTextIcon, current: true },
  { label: "Shared", icon: Share2Icon, current: false },
  { label: "Folders", icon: FolderIcon, current: false },
];

export async function AuthenticatedShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getSession();
  const userName = session?.user.name || session?.user.email || "Workspace";
  const userEmail = session?.user.email || "";
  const userInitial = userName.charAt(0).toUpperCase();

  return (
    <div className="min-h-screen bg-(--panel-2) text-foreground lg:grid lg:grid-cols-[17rem_minmax(0,1fr)] lg:grid-rows-[auto_1fr]">
      <aside className="hidden border-r border-(--line-strong) bg-(--panel) px-5 py-6 lg:row-span-2 lg:flex lg:min-h-screen lg:flex-col">
        <div className="space-y-10">
          <Link
            href="/app"
            className="flex w-full justify-center rounded-xl focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50"
          >
            <Image
              src="/brand/full-logo.svg"
              alt="Markdown2Share"
              width={226}
              height={26}
              priority
              className="h-8 w-auto"
            />
          </Link>

          <nav aria-label="Workspace" className="space-y-2">
            {workspaceLinks.map((item) => (
              <button
                key={item.label}
                type="button"
                aria-pressed={item.current}
                className={cn(
                  "flex h-11 w-full items-center gap-3 rounded-lg border border-transparent px-3.5 text-left text-sm font-medium text-muted-foreground transition-colors hover:border-(--line) hover:bg-(--panel-2) hover:text-foreground focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50",
                  item.current &&
                    "border-primary bg-primary text-primary-foreground hover:border-primary hover:bg-primary/90 hover:text-primary-foreground",
                )}
              >
                <item.icon aria-hidden className="size-4" />
                {item.label}
              </button>
            ))}
          </nav>
        </div>
      </aside>

      <header className="sticky top-0 z-20 bg-background">
        <div className="flex min-h-16 w-full items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
          <Link
            href="/app"
            className="inline-flex items-center rounded-xl focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50 lg:hidden"
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

          <div className="flex min-w-0 flex-1 items-center gap-4">
            <div className="hidden w-[min(42rem,62vw)] min-w-80 sm:block">
              <SearchBar />
            </div>

            <button
              type="button"
              aria-label="Settings"
              className={cn(
                buttonVariants({ variant: "ghost", size: "icon-lg" }),
                "ml-auto rounded-full border-0 bg-transparent hover:bg-(--panel-2)",
              )}
            >
              <SettingsIcon aria-hidden className="size-5" />
            </button>

            <DropdownMenu>
              <DropdownMenuTrigger className="rounded-full border-0 outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50">
                <Avatar size="lg" className="bg-(--accent-soft) cursor-pointer">
                  <AvatarImage src={session?.user.image || undefined} alt="" />
                  <AvatarFallback className="bg-(--accent-soft) font-medium text-(--accent-ink)">
                    {userInitial}
                  </AvatarFallback>
                </Avatar>
              </DropdownMenuTrigger>
              <DropdownMenuGroup>
                <DropdownMenuContent align="end" className="w-64">
                  <DropdownMenuLabel>
                    <span className="block truncate font-medium text-foreground">
                      {userName}
                    </span>
                    {userEmail ? (
                      <span className="mt-0.5 block truncate text-xs text-muted-foreground">
                        {userEmail}
                      </span>
                    ) : null}
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <form action={signOut}>
                    <button
                      type="submit"
                      className="flex w-full items-center gap-2.5 rounded-b-lg px-3 py-2 text-left text-sm text-destructive outline-none transition-colors hover:bg-destructive/10 focus-visible:bg-destructive/10"
                    >
                      <LogOutIcon aria-hidden className="size-4" />
                      Log out
                    </button>
                  </form>
                </DropdownMenuContent>
              </DropdownMenuGroup>
            </DropdownMenu>
          </div>
        </div>
      </header>

      <main className="min-w-0 bg-background">{children}</main>
    </div>
  );
}
```

---

### Task 7: Update authenticated app layout to use `AuthenticatedShell`

**Files:**
- Modify: `app/(auth)/app/layout.tsx`

- [ ] **Step 1: Rewrite `app/(auth)/app/layout.tsx`**

```tsx
import { requireAuthentication } from "@/features/auth/auth-guards";
import { AuthenticatedShell } from "@/components/layout/authenticated-shell";

export default async function AuthenticatedAppLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  await requireAuthentication();

  return <AuthenticatedShell>{children}</AuthenticatedShell>;
}
```

---

### Task 8: Strip chrome from authenticated page (keep only content)

**Files:**
- Modify: `app/(auth)/app/page.tsx`

Remove sidebar, header, user dropdown, search — everything is now in `AuthenticatedShell`. Keep only the `<main>` content section.

- [ ] **Step 1: Rewrite `app/(auth)/app/page.tsx`**

```tsx
import { format } from "date-fns";
import {
  ChevronDownIcon,
  FilePlus2Icon,
  PlusIcon,
  UploadIcon,
} from "lucide-react";

import { buttonVariants } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { getAllMarkdownFiles } from "@/features/markdown/services/markdown.service";
import { getSession } from "@/features/auth/actions/auth.action";
import {
  DataTable,
  type DataTableColumn,
} from "@/components/blocks/data-table";

export const dynamic = "force-dynamic";

const pageLimits = [5, 10, 20];
const defaultPageLimit = 10;

type MarkdownFile = Awaited<ReturnType<typeof getAllMarkdownFiles>>[number];

const fileColumns: DataTableColumn<MarkdownFile>[] = [
  {
    id: "name",
    header: "Name",
    cell: (file) => (
      <div className="min-w-0">
        <p className="truncate text-sm font-semibold text-foreground">{file.title}</p>
        <p className="truncate text-sm text-muted-foreground">{file.slug}.md</p>
      </div>
    ),
  },
  {
    id: "status",
    header: "Status",
    cell: (file) => (
      <span
        className={cn(
          "inline-flex w-fit rounded-full border border-(--line) px-2.5 py-1 text-xs font-medium capitalize text-muted-foreground",
          file.status === "published" &&
            "border-transparent bg-(--accent-soft) text-(--accent-ink)",
        )}
      >
        {file.status}
      </span>
    ),
    mobile: { hidden: true },
  },
  {
    id: "updated",
    header: "Updated",
    headerClassName: "text-right md:text-left",
    className: "text-right md:text-left",
    mobile: { align: "right" },
    cell: (file) => (
      <time dateTime={file.updatedAt.toISOString()} className="text-sm text-muted-foreground">
        {format(file.updatedAt, "MMM d, yyyy")}
      </time>
    ),
  },
];

export default async function AuthoringHomePage({
  searchParams,
}: {
  searchParams?: Promise<{
    q?: string | string[];
    page?: string | string[];
    limit?: string | string[];
  }>;
}) {
  const session = await getSession();
  const params = await searchParams;
  const query = typeof params?.q === "string" ? params.q.trim() : "";
  const requestedPage = typeof params?.page === "string" ? Number(params.page) : 1;
  const requestedLimit = typeof params?.limit === "string" ? Number(params.limit) : defaultPageLimit;
  const pageLimit = pageLimits.includes(requestedLimit) ? requestedLimit : defaultPageLimit;

  let files: Awaited<ReturnType<typeof getAllMarkdownFiles>> = [];
  let loadError = false;

  try {
    files = session?.user.id ? await getAllMarkdownFiles(session.user.id) : [];
  } catch {
    loadError = true;
  }

  const visibleFiles = query
    ? files.filter((file) => {
        const match = query.toLowerCase();
        return (
          file.title.toLowerCase().includes(match) ||
          file.slug.toLowerCase().includes(match)
        );
      })
    : files;
  const totalPages = Math.max(1, Math.ceil(visibleFiles.length / pageLimit));
  const currentPage = Math.min(
    totalPages,
    Math.max(1, Number.isFinite(requestedPage) ? requestedPage : 1),
  );
  const paginatedFiles = visibleFiles.slice(
    (currentPage - 1) * pageLimit,
    currentPage * pageLimit,
  );
  const getTableHref = (page: number, limit = pageLimit) => {
    const nextParams = new URLSearchParams();
    if (query) nextParams.set("q", query);
    if (page > 1) nextParams.set("page", String(page));
    if (limit !== defaultPageLimit) nextParams.set("limit", String(limit));
    const nextQuery = nextParams.toString();
    return nextQuery ? `/app?${nextQuery}` : "/app";
  };

  return (
    <div className="w-full">
      <section
        aria-labelledby="files-title"
        className="min-w-0 px-4 py-8 sm:px-6 sm:py-10 lg:px-8"
      >
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h1
            id="files-title"
            className="font-sans text-2xl font-semibold tracking-[-0.02em]"
          >
            Markdown files
          </h1>

          <div className="sm:ml-auto">
            <DropdownMenu>
              <DropdownMenuTrigger
                className={cn(
                  buttonVariants({ size: "lg" }),
                  "h-10 w-full rounded-full sm:w-auto",
                )}
              >
                <PlusIcon aria-hidden className="size-4" />
                Create
                <ChevronDownIcon aria-hidden className="size-4" />
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-64">
                <DropdownMenuGroup>
                  <DropdownMenuLabel>
                    Start a Markdown file
                  </DropdownMenuLabel>
                  <DropdownMenuItem>
                    <UploadIcon aria-hidden className="size-4" />
                    <div>
                      <p className="font-medium">Upload Markdown</p>
                      <p className="text-xs text-muted-foreground">
                        Bring in an existing .md file
                      </p>
                    </div>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <FilePlus2Icon aria-hidden className="size-4" />
                    <div>
                      <p className="font-medium">Create new file</p>
                      <p className="text-xs text-muted-foreground">
                        Editor page comes next
                      </p>
                    </div>
                  </DropdownMenuItem>
                </DropdownMenuGroup>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {loadError ? (
          <div className="mt-6 rounded-xl bg-(--panel-2) px-4 py-12 text-center sm:px-6">
            <h2 className="font-sans text-lg font-semibold tracking-tight">
              We could not load your files.
            </h2>
            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-muted-foreground">
              Check the database connection and refresh this page.
            </p>
          </div>
        ) : files.length === 0 ? (
          <div className="mt-6 rounded-xl bg-(--panel-2) px-4 py-14 text-center sm:px-6">
            <h2 className="font-sans text-lg font-semibold tracking-tight">
              No Markdown files yet.
            </h2>
            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-muted-foreground">
              Upload an existing file or start a blank one when the editor
              is ready.
            </p>
            <div className="mt-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <button
                type="button"
                className={cn(
                  buttonVariants({ size: "lg" }),
                  "w-full rounded-full sm:w-auto",
                )}
              >
                <UploadIcon aria-hidden className="size-4" />
                Upload Markdown
              </button>
              <button
                type="button"
                className={cn(
                  buttonVariants({ variant: "outline", size: "lg" }),
                  "w-full rounded-full sm:w-auto",
                )}
              >
                <FilePlus2Icon aria-hidden className="size-4" />
                Create new file
              </button>
            </div>
          </div>
        ) : visibleFiles.length === 0 ? (
          <div className="mt-6 rounded-xl bg-(--panel-2) px-4 py-12 text-center sm:px-6">
            <h2 className="font-sans text-lg font-semibold tracking-tight">
              No matching files.
            </h2>
            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-muted-foreground">
              Try a different title or slug.
            </p>
          </div>
        ) : (
          <DataTable
            className="mt-6"
            columns={fileColumns}
            data={paginatedFiles}
            getRowKey={(file) => file.id}
            rowsSelector={{
              value: pageLimit,
              options: pageLimits,
              getHref: (limit) => getTableHref(1, limit),
            }}
            pagination={{
              page: currentPage,
              totalPages,
              getHref: (page) => getTableHref(page),
            }}
          />
        )}
      </section>
    </div>
  );
}
```

---

### Task 9: Remove `SectionShell` (no longer referenced)

**Files:**
- Remove: `components/layout/section-shell.tsx`

- [ ] **Step 1: Delete `components/layout/section-shell.tsx`**

```bash
Remove-Item -LiteralPath "components/layout/section-shell.tsx"
```

---

### Task 10: Verify — build check

- [ ] **Step 1: Run build (includes TypeScript check)**

```bash
pnpm run build
```

Expected: successful build with zero errors.

- [ ] **Step 2: Run lint**

```bash
pnpm run lint
```

Expected: zero errors.

---

### Task 11: Commit all changes

- [ ] **Step 1: Stage and commit**

Use `$git-commit` (skill) for the commit with a conventional commit message.
