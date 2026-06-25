# Testing Dashboard Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a frontend-only dark-mode testing dashboard with sidebar navigation for Smoke Testing, e2e Testing, and Settings.

**Architecture:** Use a shared dashboard shell around App Router pages. Keep mock data centralized in one typed module, and keep interactive UI in small client components that consume that mock data through props or imports.

**Tech Stack:** Next.js App Router, React 19, TypeScript, Tailwind CSS, existing shadcn-style UI components, lucide-react icons.

---

## File Structure

- Modify: `$HOME/Documents/Programming/mihc/nextjs/app/layout.tsx`
  - Set dark-first HTML/body classes and product metadata.
- Modify: `$HOME/Documents/Programming/mihc/nextjs/app/page.tsx`
  - Redirect `/` to `/smoke-testing`.
- Create: `$HOME/Documents/Programming/mihc/nextjs/components/app-shell.tsx`
  - Shared sidebar layout using existing sidebar primitives.
- Create: `$HOME/Documents/Programming/mihc/nextjs/lib/mock-testing-data.ts`
  - Typed mock data for smoke apps, smoke runs, profiles, scenarios, and e2e run steps.
- Create: `$HOME/Documents/Programming/mihc/nextjs/app/smoke-testing/page.tsx`
  - Thin server route rendering the smoke testing client component.
- Create: `$HOME/Documents/Programming/mihc/nextjs/app/smoke-testing/smoke-testing-client.tsx`
  - Interactive smoke status cards, filters, history table, and local manual-run simulation.
- Create: `$HOME/Documents/Programming/mihc/nextjs/app/e2e-testing/page.tsx`
  - Thin server route rendering the e2e testing client component.
- Create: `$HOME/Documents/Programming/mihc/nextjs/app/e2e-testing/e2e-testing-client.tsx`
  - Profiles table, `profile=` route-tied side sheet, scenario multi-select, and local run progress.
- Create: `$HOME/Documents/Programming/mihc/nextjs/app/settings/page.tsx`
  - Minimal KISS settings surface.

## Task 1: App Shell And Routes

**Files:**
- Modify: `$HOME/Documents/Programming/mihc/nextjs/app/layout.tsx`
- Modify: `$HOME/Documents/Programming/mihc/nextjs/app/page.tsx`
- Create: `$HOME/Documents/Programming/mihc/nextjs/components/app-shell.tsx`

- [ ] **Step 1: Confirm a clean starting point**

Run:

```powershell
git status --short
git diff
```

Expected: no output, or only user-owned changes that are unrelated and must be preserved.

- [ ] **Step 2: Replace root page with a redirect**

Edit `$HOME/Documents/Programming/mihc/nextjs/app/page.tsx` to:

```tsx
import { redirect } from "next/navigation";

export default function Home() {
  redirect("/smoke-testing");
}
```

- [ ] **Step 3: Update layout metadata and dark-first classes**

Edit `$HOME/Documents/Programming/mihc/nextjs/app/layout.tsx` to keep the existing fonts and imports, but use this metadata and markup:

```tsx
export const metadata: Metadata = {
  title: "MMDC Testing Dashboard",
  description: "Frontend dashboard for smoke and e2e test operations",
};
```

The returned markup should be:

```tsx
return (
  <html
    lang="en"
    className={cn(
      "dark h-full",
      "antialiased",
      geistSans.variable,
      geistMono.variable,
      "font-sans",
      inter.variable
    )}
  >
    <body className="min-h-full bg-background text-foreground">
      {children}
    </body>
  </html>
);
```

- [ ] **Step 4: Create the shared app shell**

Create `$HOME/Documents/Programming/mihc/nextjs/components/app-shell.tsx`:

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ActivityIcon,
  ClipboardCheckIcon,
  SettingsIcon,
  ShieldCheckIcon,
} from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";

const navItems = [
  { href: "/smoke-testing", label: "Smoke Testing", icon: ActivityIcon },
  { href: "/e2e-testing", label: "e2e Testing", icon: ClipboardCheckIcon },
  { href: "/settings", label: "Settings", icon: SettingsIcon },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <SidebarProvider>
      <Sidebar collapsible="icon" className="border-r border-sidebar-border">
        <SidebarHeader className="border-b border-sidebar-border px-3 py-4">
          <div className="flex items-center gap-2">
            <div className="flex size-8 items-center justify-center rounded-md bg-sidebar-primary text-sidebar-primary-foreground">
              <ShieldCheckIcon className="size-4" />
            </div>
            <div className="min-w-0 group-data-[collapsible=icon]:hidden">
              <p className="truncate text-sm font-medium">MMDC Testing</p>
              <p className="truncate text-xs text-sidebar-foreground/60">
                Maintainer Console
              </p>
            </div>
          </div>
        </SidebarHeader>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Testing</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = pathname === item.href;

                  return (
                    <SidebarMenuItem key={item.href}>
                      <SidebarMenuButton
                        isActive={isActive}
                        tooltip={item.label}
                        render={<Link href={item.href} />}
                      >
                        <Icon />
                        <span>{item.label}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  );
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
      </Sidebar>
      <SidebarInset className="min-w-0 bg-background">
        <header className="flex h-14 items-center gap-3 border-b px-4 md:hidden">
          <SidebarTrigger />
          <span className="text-sm font-medium">MMDC Testing</span>
        </header>
        <main className="min-h-svh px-4 py-5 md:px-6 lg:px-8">
          {children}
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}
```

- [ ] **Step 5: Verify shell compiles before routes exist**

Run:

```powershell
cd nextjs
pnpm lint
```

Expected: lint may fail because route pages are not created yet if imports are not used. If it fails for unrelated pre-existing code, record the exact error and continue only when the shell file has no syntax errors.

## Task 2: Central Mock Data

**Files:**
- Create: `$HOME/Documents/Programming/mihc/nextjs/lib/mock-testing-data.ts`

- [ ] **Step 1: Create typed mock data module**

Create `$HOME/Documents/Programming/mihc/nextjs/lib/mock-testing-data.ts`:

```ts
export type SmokeStatus = "operational" | "degraded" | "down";
export type RunResult = "success" | "failure";
export type RunTrigger = "scheduled" | "manual";
export type E2eStepStatus = "queued" | "running" | "success" | "failure";

export type SmokeApp = {
  id: string;
  name: string;
  description: string;
  status: SmokeStatus;
  uptime: string;
  lastChecked: string;
};

export type SmokeRun = {
  id: string;
  appId: string;
  result: RunResult;
  trigger: RunTrigger;
  duration: string;
  checkedAt: string;
  detail: string;
};

export type Profile = {
  id: string;
  name: string;
  email: string;
  program: string;
  cohort: string;
  status: "ready" | "needs review";
  lastRun: string;
};

export type Scenario = {
  id: string;
  label: string;
  description: string;
};

export type E2eRunStep = {
  scenarioId: string;
  status: E2eStepStatus;
  duration: string;
  note: string;
};

export const smokeApps: SmokeApp[] = [
  {
    id: "website",
    name: "Website",
    description: "Public marketing and admissions website",
    status: "operational",
    uptime: "99.98%",
    lastChecked: "2 min ago",
  },
  {
    id: "enrollmate",
    name: "Enrollmate",
    description: "Student enrollment workflow",
    status: "operational",
    uptime: "99.91%",
    lastChecked: "5 min ago",
  },
  {
    id: "enrollmate-clp",
    name: "Enrollmate CLP",
    description: "CLP enrollment support surface",
    status: "degraded",
    uptime: "98.74%",
    lastChecked: "8 min ago",
  },
  {
    id: "n8n",
    name: "Self-hosted n8n",
    description: "Automation workflow instance",
    status: "operational",
    uptime: "99.43%",
    lastChecked: "1 min ago",
  },
];

export const smokeRuns: SmokeRun[] = [
  { id: "run-001", appId: "website", result: "success", trigger: "scheduled", duration: "18s", checkedAt: "Today 14:10", detail: "Homepage, lead form, and core assets responded." },
  { id: "run-002", appId: "website", result: "success", trigger: "manual", duration: "21s", checkedAt: "Today 12:42", detail: "Manual verification completed." },
  { id: "run-003", appId: "enrollmate", result: "success", trigger: "scheduled", duration: "32s", checkedAt: "Today 14:05", detail: "Login and enrollment summary loaded." },
  { id: "run-004", appId: "enrollmate", result: "failure", trigger: "scheduled", duration: "45s", checkedAt: "Today 10:05", detail: "Payment status endpoint timed out." },
  { id: "run-005", appId: "enrollmate-clp", result: "failure", trigger: "scheduled", duration: "39s", checkedAt: "Today 13:58", detail: "CLP dashboard returned a 500 response." },
  { id: "run-006", appId: "enrollmate-clp", result: "success", trigger: "manual", duration: "34s", checkedAt: "Yesterday 18:22", detail: "Retry passed after deployment." },
  { id: "run-007", appId: "n8n", result: "success", trigger: "scheduled", duration: "16s", checkedAt: "Today 14:11", detail: "Webhook health and queue probe responded." },
  { id: "run-008", appId: "n8n", result: "failure", trigger: "scheduled", duration: "27s", checkedAt: "Yesterday 22:11", detail: "Worker heartbeat was stale." },
];

export const profiles: Profile[] = [
  { id: "profile-001", name: "Ari Santos", email: "ari.santos@example.edu", program: "BS IT", cohort: "2026-A", status: "ready", lastRun: "Today 11:32" },
  { id: "profile-002", name: "Mika Reyes", email: "mika.reyes@example.edu", program: "BSBA", cohort: "2026-A", status: "ready", lastRun: "Yesterday 16:12" },
  { id: "profile-003", name: "Noel Cruz", email: "noel.cruz@example.edu", program: "BS CS", cohort: "2025-B", status: "needs review", lastRun: "Jun 24, 09:41" },
  { id: "profile-004", name: "Sam Lim", email: "sam.lim@example.edu", program: "BSEd", cohort: "2025-B", status: "ready", lastRun: "Jun 23, 15:03" },
];

export const scenarios: Scenario[] = [
  { id: "stage-1", label: "Stage 1", description: "Authenticate and load the student dashboard." },
  { id: "stage-2", label: "Stage 2", description: "Complete profile and enrollment prerequisites." },
  { id: "stage-3", label: "Stage 3", description: "Validate course selection and document steps." },
  { id: "stage-4", label: "Stage 4", description: "Confirm submission and post-enrollment state." },
];

export const profileRuns: Record<string, E2eRunStep[]> = {
  "profile-001": [
    { scenarioId: "stage-1", status: "success", duration: "41s", note: "Dashboard loaded with active student state." },
    { scenarioId: "stage-2", status: "success", duration: "1m 12s", note: "Prerequisite checklist accepted mock values." },
    { scenarioId: "stage-3", status: "queued", duration: "-", note: "Awaiting selected run." },
    { scenarioId: "stage-4", status: "queued", duration: "-", note: "Awaiting selected run." },
  ],
};
```

- [ ] **Step 2: Run type-aware lint**

Run:

```powershell
cd nextjs
pnpm lint
```

Expected: PASS, or only pre-existing lint failures unrelated to the new mock data.

## Task 3: Smoke Testing Page

**Files:**
- Create: `$HOME/Documents/Programming/mihc/nextjs/app/smoke-testing/page.tsx`
- Create: `$HOME/Documents/Programming/mihc/nextjs/app/smoke-testing/smoke-testing-client.tsx`

- [ ] **Step 1: Create the route page**

Create `$HOME/Documents/Programming/mihc/nextjs/app/smoke-testing/page.tsx`:

```tsx
import { AppShell } from "@/components/app-shell";
import { smokeApps, smokeRuns } from "@/lib/mock-testing-data";
import { SmokeTestingClient } from "./smoke-testing-client";

export default function SmokeTestingPage() {
  return (
    <AppShell>
      <SmokeTestingClient apps={smokeApps} initialRuns={smokeRuns} />
    </AppShell>
  );
}
```

- [ ] **Step 2: Implement the smoke testing client**

Create `$HOME/Documents/Programming/mihc/nextjs/app/smoke-testing/smoke-testing-client.tsx` with:

```tsx
"use client";

import { useMemo, useState } from "react";
import { PlayIcon } from "lucide-react";

import type { RunResult, SmokeApp, SmokeRun } from "@/lib/mock-testing-data";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type FilterValue = "all" | RunResult;

function resultClasses(result: RunResult) {
  return result === "success"
    ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
    : "border-red-500/30 bg-red-500/10 text-red-300";
}

export function SmokeTestingClient({
  apps,
  initialRuns,
}: {
  apps: SmokeApp[];
  initialRuns: SmokeRun[];
}) {
  const [selectedAppId, setSelectedAppId] = useState(apps[0]?.id ?? "");
  const [filter, setFilter] = useState<FilterValue>("all");
  const [runs, setRuns] = useState(initialRuns);

  const selectedApp = apps.find((app) => app.id === selectedAppId) ?? apps[0];
  const selectedRuns = useMemo(() => {
    return runs.filter((run) => {
      const matchesApp = run.appId === selectedApp?.id;
      const matchesFilter = filter === "all" || run.result === filter;
      return matchesApp && matchesFilter;
    });
  }, [filter, runs, selectedApp?.id]);

  function runManualSmokeTest() {
    if (!selectedApp) return;

    const nextRun: SmokeRun = {
      id: `manual-${Date.now()}`,
      appId: selectedApp.id,
      result: "success",
      trigger: "manual",
      duration: "3s",
      checkedAt: "Just now",
      detail: "Frontend-only manual run queued and marked successful.",
    };

    setRuns((currentRuns) => [nextRun, ...currentRuns]);
  }

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-normal">Smoke Testing</h1>
        <p className="max-w-2xl text-sm text-muted-foreground">
          Health checks for MMDC-maintained applications, with manual smoke runs
          and recent history for maintainers.
        </p>
      </div>

      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {apps.map((app) => {
          const appRuns = runs.filter((run) => run.appId === app.id).slice(0, 5);
          const lastRun = appRuns[0];
          const isSelected = selectedAppId === app.id;

          return (
            <button
              key={app.id}
              type="button"
              onClick={() => setSelectedAppId(app.id)}
              className="text-left"
            >
              <Card
                className={
                  isSelected
                    ? "border-primary bg-card"
                    : "border-border bg-card/80 hover:border-primary/40"
                }
              >
                <CardHeader className="space-y-2">
                  <div className="flex items-start justify-between gap-3">
                    <CardTitle className="text-base">{app.name}</CardTitle>
                    <Badge variant="outline">{app.status}</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {app.description}
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-2xl font-semibold">{app.uptime}</p>
                    <p className="text-xs text-muted-foreground">
                      Last checked {app.lastChecked}
                    </p>
                  </div>
                  <div className="flex items-center gap-1">
                    {appRuns.map((run) => (
                      <span
                        key={run.id}
                        className={
                          run.result === "success"
                            ? "h-2 flex-1 rounded-sm bg-emerald-400"
                            : "h-2 flex-1 rounded-sm bg-red-400"
                        }
                      />
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Last run: {lastRun?.result ?? "No runs yet"}
                  </p>
                </CardContent>
              </Card>
            </button>
          );
        })}
      </section>

      <section className="space-y-3">
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div>
            <h2 className="text-lg font-medium">{selectedApp?.name} history</h2>
            <p className="text-sm text-muted-foreground">
              Filter historical smoke runs or trigger a frontend-only manual run.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {(["all", "success", "failure"] as FilterValue[]).map((value) => (
              <Button
                key={value}
                type="button"
                variant={filter === value ? "default" : "outline"}
                size="sm"
                onClick={() => setFilter(value)}
              >
                {value}
              </Button>
            ))}
            <Button type="button" size="sm" onClick={runManualSmokeTest}>
              <PlayIcon className="size-4" />
              Run smoke test
            </Button>
          </div>
        </div>

        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Result</TableHead>
                <TableHead>Trigger</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Checked</TableHead>
                <TableHead>Detail</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {selectedRuns.map((run) => (
                <TableRow key={run.id}>
                  <TableCell>
                    <Badge variant="outline" className={resultClasses(run.result)}>
                      {run.result}
                    </Badge>
                  </TableCell>
                  <TableCell>{run.trigger}</TableCell>
                  <TableCell>{run.duration}</TableCell>
                  <TableCell>{run.checkedAt}</TableCell>
                  <TableCell className="whitespace-normal text-muted-foreground">
                    {run.detail}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </section>
    </div>
  );
}
```

- [ ] **Step 3: Verify the route**

Run:

```powershell
cd nextjs
pnpm lint
```

Expected: PASS.

## Task 4: e2e Testing Page

**Files:**
- Create: `$HOME/Documents/Programming/mihc/nextjs/app/e2e-testing/page.tsx`
- Create: `$HOME/Documents/Programming/mihc/nextjs/app/e2e-testing/e2e-testing-client.tsx`

- [ ] **Step 1: Create the route page**

Create `$HOME/Documents/Programming/mihc/nextjs/app/e2e-testing/page.tsx`:

```tsx
import { AppShell } from "@/components/app-shell";
import { profileRuns, profiles, scenarios } from "@/lib/mock-testing-data";
import { E2eTestingClient } from "./e2e-testing-client";

export default function E2eTestingPage() {
  return (
    <AppShell>
      <E2eTestingClient
        profileRuns={profileRuns}
        profiles={profiles}
        scenarios={scenarios}
      />
    </AppShell>
  );
}
```

- [ ] **Step 2: Implement the e2e client**

Create `$HOME/Documents/Programming/mihc/nextjs/app/e2e-testing/e2e-testing-client.tsx`. Use `useRouter`, `usePathname`, and `useSearchParams` to set and clear `profile=`. Import existing `Sheet`, `Checkbox`, `Button`, `Badge`, `Card`, and `Table` components. The component must:

```tsx
"use client";

import { useMemo, useState } from "react";
import { PlayIcon, StepForwardIcon } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import type {
  E2eRunStep,
  Profile,
  Scenario,
} from "@/lib/mock-testing-data";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export function E2eTestingClient({
  profiles,
  scenarios,
  profileRuns,
}: {
  profiles: Profile[];
  scenarios: Scenario[];
  profileRuns: Record<string, E2eRunStep[]>;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const selectedProfileId = searchParams.get("profile");
  const selectedProfile = profiles.find((profile) => profile.id === selectedProfileId);
  const [selectedScenarioIds, setSelectedScenarioIds] = useState<string[]>(
    scenarios.map((scenario) => scenario.id)
  );
  const [runSteps, setRunSteps] = useState<E2eRunStep[]>(
    profileRuns["profile-001"] ?? []
  );

  const selectedScenarios = useMemo(
    () => scenarios.filter((scenario) => selectedScenarioIds.includes(scenario.id)),
    [scenarios, selectedScenarioIds]
  );

  function openProfile(profileId: string) {
    router.push(`${pathname}?profile=${profileId}`);
    setRunSteps(profileRuns[profileId] ?? scenarios.map((scenario) => ({
      scenarioId: scenario.id,
      status: "queued",
      duration: "-",
      note: "Ready for selected run.",
    })));
  }

  function closeProfile() {
    router.push(pathname);
  }

  function toggleScenario(scenarioId: string) {
    setSelectedScenarioIds((current) =>
      current.includes(scenarioId)
        ? current.filter((id) => id !== scenarioId)
        : [...current, scenarioId]
    );
  }

  function runAutomated() {
    setRunSteps(
      selectedScenarios.map((scenario) => ({
        scenarioId: scenario.id,
        status: "success",
        duration: "52s",
        note: `${scenario.label} completed through automated mock execution.`,
      }))
    );
  }

  function runNextManualStep() {
    const completedIds = new Set(
      runSteps.filter((step) => step.status === "success").map((step) => step.scenarioId)
    );
    const nextScenario = selectedScenarios.find((scenario) => !completedIds.has(scenario.id));

    if (!nextScenario) return;

    setRunSteps((current) => [
      ...current.filter((step) => step.scenarioId !== nextScenario.id),
      {
        scenarioId: nextScenario.id,
        status: "success",
        duration: "manual",
        note: `${nextScenario.label} marked complete by manual operator action.`,
      },
    ]);
  }

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-normal">e2e Testing</h1>
        <p className="max-w-2xl text-sm text-muted-foreground">
          Select a profile, choose stages, and simulate automated or manual e2e
          scenario runs.
        </p>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Profile</TableHead>
              <TableHead>Program</TableHead>
              <TableHead>Cohort</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Last Run</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {profiles.map((profile) => (
              <TableRow
                key={profile.id}
                className="cursor-pointer"
                onClick={() => openProfile(profile.id)}
              >
                <TableCell>
                  <div>
                    <p className="font-medium">{profile.name}</p>
                    <p className="text-xs text-muted-foreground">{profile.email}</p>
                  </div>
                </TableCell>
                <TableCell>{profile.program}</TableCell>
                <TableCell>{profile.cohort}</TableCell>
                <TableCell>
                  <Badge variant="outline">{profile.status}</Badge>
                </TableCell>
                <TableCell>{profile.lastRun}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      <Sheet open={Boolean(selectedProfile)} onOpenChange={(open) => !open && closeProfile()}>
        <SheetContent className="w-full overflow-y-auto sm:max-w-xl">
          <SheetHeader>
            <SheetTitle>{selectedProfile?.name ?? "Profile"}</SheetTitle>
          </SheetHeader>
          {selectedProfile ? (
            <div className="flex flex-col gap-4 px-4 pb-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Profile Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-1 text-sm text-muted-foreground">
                  <p>{selectedProfile.email}</p>
                  <p>{selectedProfile.program} · {selectedProfile.cohort}</p>
                  <p>Last run: {selectedProfile.lastRun}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Scenarios</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {scenarios.map((scenario) => (
                    <label key={scenario.id} className="flex gap-3 rounded-md border p-3">
                      <Checkbox
                        checked={selectedScenarioIds.includes(scenario.id)}
                        onCheckedChange={() => toggleScenario(scenario.id)}
                      />
                      <span>
                        <span className="block text-sm font-medium">{scenario.label}</span>
                        <span className="block text-xs text-muted-foreground">
                          {scenario.description}
                        </span>
                      </span>
                    </label>
                  ))}
                  <div className="flex flex-wrap gap-2 pt-1">
                    <Button type="button" onClick={runAutomated}>
                      <PlayIcon className="size-4" />
                      Run automated
                    </Button>
                    <Button type="button" variant="outline" onClick={runNextManualStep}>
                      <StepForwardIcon className="size-4" />
                      Run next manual stage
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Run Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {runSteps.map((step) => {
                    const scenario = scenarios.find((item) => item.id === step.scenarioId);
                    return (
                      <div key={step.scenarioId} className="rounded-md border p-3">
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-medium">{scenario?.label}</p>
                          <Badge variant="outline">{step.status}</Badge>
                        </div>
                        <p className="mt-1 text-xs text-muted-foreground">
                          {step.duration} · {step.note}
                        </p>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>
            </div>
          ) : null}
        </SheetContent>
      </Sheet>
    </div>
  );
}
```

- [ ] **Step 3: Verify route and query behavior compiles**

Run:

```powershell
cd nextjs
pnpm lint
```

Expected: PASS.

## Task 5: Settings Page

**Files:**
- Create: `$HOME/Documents/Programming/mihc/nextjs/app/settings/page.tsx`

- [ ] **Step 1: Implement minimal settings page**

Create `$HOME/Documents/Programming/mihc/nextjs/app/settings/page.tsx`:

```tsx
import { AppShell } from "@/components/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";

export default function SettingsPage() {
  return (
    <AppShell>
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-6">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-semibold tracking-normal">Settings</h1>
          <p className="max-w-2xl text-sm text-muted-foreground">
            Minimal frontend-only settings for the testing dashboard mock.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Runtime Defaults</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 text-sm">
            <div className="flex items-center justify-between gap-4 rounded-md border p-3">
              <div>
                <p className="font-medium">Environment</p>
                <p className="text-muted-foreground">Staging</p>
              </div>
              <Badge variant="outline">mock</Badge>
            </div>
            <div className="flex items-center justify-between gap-4 rounded-md border p-3">
              <div>
                <p className="font-medium">Default runner mode</p>
                <p className="text-muted-foreground">Automated runs first</p>
              </div>
              <Switch checked disabled />
            </div>
            <div className="flex items-center justify-between gap-4 rounded-md border p-3">
              <div>
                <p className="font-medium">Integrations</p>
                <p className="text-muted-foreground">
                  Frontend-only mock, no backend connected.
                </p>
              </div>
              <Badge variant="secondary">offline</Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
```

- [ ] **Step 2: Verify settings route compiles**

Run:

```powershell
cd nextjs
pnpm lint
```

Expected: PASS.

## Task 6: Final Verification

**Files:**
- Verify all files modified or created in Tasks 1-5.

- [ ] **Step 1: Run lint**

Run:

```powershell
cd nextjs
pnpm lint
```

Expected: PASS.

- [ ] **Step 2: Run production build**

Run:

```powershell
cd nextjs
pnpm build
```

Expected: PASS.

- [ ] **Step 3: Start dev server**

Run:

```powershell
cd nextjs
pnpm dev
```

Expected: local Next.js URL printed in the terminal, commonly `http://localhost:3000`.

- [ ] **Step 4: Manual browser verification**

Open the dev server and verify:

- `/` redirects to `/smoke-testing`.
- Sidebar contains Smoke Testing, e2e Testing, and Settings.
- Smoke Testing shows Website, Enrollmate, Enrollmate CLP, and Self-hosted n8n cards.
- Selecting each smoke card changes the history table.
- The all, success, and failure filters change table rows.
- Run smoke test adds a local manual run row.
- e2e Testing shows profile rows.
- Clicking a profile opens the side sheet and sets `profile=<id>` in the URL.
- Closing the side sheet removes `profile=`.
- Stage 1 through Stage 4 can be multi-selected.
- Run automated updates run details.
- Run next manual stage advances one selected scenario per click.
- Settings stays small and mock-only.

- [ ] **Step 5: Confirm only intended files changed**

Run:

```powershell
git status --short
git diff --stat
git diff
```

Expected: changes are limited to the app shell, three routes, two client components, mock data, and layout/root redirect.

- [ ] **Step 6: Commit implementation**

Run:

```powershell
git add app components lib
git commit -m "feat: add testing dashboard frontend"
```

Expected: one commit containing only the frontend dashboard implementation.

## Self-Review

- Spec coverage: covered sidebar routes, smoke app cards, smoke history filter, manual smoke run simulation, e2e profiles table, `profile=` side panel, stage selection, automated/manual mock runs, KISS settings, centralized mock data, and dark-first styling.
- Red-flag scan: no unresolved implementation gaps remain in the plan.
- Type consistency: `SmokeApp`, `SmokeRun`, `Profile`, `Scenario`, and `E2eRunStep` are defined before use and match later task imports.
