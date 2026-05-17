import type { Plugin } from "@opencode-ai/plugin";
import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";

/* ------------------------------------------------------------------ */
//  Types
/* ------------------------------------------------------------------ */

interface ProviderStats {
  total_requests: number;
  today_requests: number;
  this_month_requests: number;
  last_request_at: string | null;
  estimated_limit: number | null;
  plan: string | null;
  custom_data: Record<string, unknown>;
}

interface UsageStore {
  version: number;
  providers: Record<string, ProviderStats>;
  history: {
    timestamp: string;
    model: string;
    provider: string;
    messages_count: number;
  }[];
}

/* ------------------------------------------------------------------ */
//  Config & helpers
/* ------------------------------------------------------------------ */

const STORE_FILE = path.join(os.homedir(), ".config", "opencode", "usage-tracker-store.json");

const PROVIDER_DEFAULTS: Record<string, Partial<ProviderStats>> = {
  github_copilot: {
    estimated_limit: 5000,
    plan: "pro",
  },
  codex: {
    estimated_limit: 5000,
    plan: "pro",
  },
  opencode_go: {
    estimated_limit: null,
    plan: null,
  },
};

function ensureDir(filePath: string): void {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function todayStr(): string {
  return new Date().toISOString().slice(0, 10);
}

function monthStr(): string {
  return new Date().toISOString().slice(0, 7);
}

function detectProvider(model?: string): string {
  if (!model) return "unknown";
  const m = model.toLowerCase();
  if (m.includes("copilot")) return "github_copilot";
  if (m.includes("codex")) return "codex";
  if (m.includes("opencode") || m.includes("kimi")) return "opencode_go";
  // Fallback heuristics
  if (m.startsWith("gpt-")) return "github_copilot";
  if (m.startsWith("claude")) return "github_copilot";
  return "unknown";
}

/* ------------------------------------------------------------------ */
//  Store I/O
/* ------------------------------------------------------------------ */

function loadStore(): UsageStore {
  ensureDir(STORE_FILE);
  if (fs.existsSync(STORE_FILE)) {
    try {
      const raw = fs.readFileSync(STORE_FILE, "utf-8");
      const parsed = JSON.parse(raw) as UsageStore;
      if (parsed.version === 1) return parsed;
    } catch {
      /* ignore corrupt store */
    }
  }
  return {
    version: 1,
    providers: {
      github_copilot: {
        total_requests: 0,
        today_requests: 0,
        this_month_requests: 0,
        last_request_at: null,
        estimated_limit: PROVIDER_DEFAULTS.github_copilot.estimated_limit ?? null,
        plan: PROVIDER_DEFAULTS.github_copilot.plan ?? null,
        custom_data: {},
      },
      codex: {
        total_requests: 0,
        today_requests: 0,
        this_month_requests: 0,
        last_request_at: null,
        estimated_limit: PROVIDER_DEFAULTS.codex.estimated_limit ?? null,
        plan: PROVIDER_DEFAULTS.codex.plan ?? null,
        custom_data: {},
      },
      opencode_go: {
        total_requests: 0,
        today_requests: 0,
        this_month_requests: 0,
        last_request_at: null,
        estimated_limit: PROVIDER_DEFAULTS.opencode_go.estimated_limit ?? null,
        plan: PROVIDER_DEFAULTS.opencode_go.plan ?? null,
        custom_data: {},
      },
    },
    history: [],
  };
}

function saveStore(store: UsageStore): void {
  ensureDir(STORE_FILE);
  fs.writeFileSync(STORE_FILE, JSON.stringify(store, null, 2));
}

function resetCountersIfNeeded(stats: ProviderStats): void {
  const now = new Date();
  const today = now.toISOString().slice(0, 10);
  const month = now.toISOString().slice(0, 7);

  if (stats.last_request_at) {
    const lastDate = stats.last_request_at.slice(0, 10);
    const lastMonth = stats.last_request_at.slice(0, 7);
    if (lastDate !== today) stats.today_requests = 0;
    if (lastMonth !== month) stats.this_month_requests = 0;
  }
}

/* ------------------------------------------------------------------ */
//  Plugin export
/* ------------------------------------------------------------------ */

export default (async ({ client, project, directory }) => {
  const store = loadStore();

  // Helper exposed on the module for debugging if needed
  (globalThis as any).__usageTrackerStore = store;

  return {
    /* -------------------------------------------------------------- */
    // 1. Track every outgoing chat message
    /* -------------------------------------------------------------- */
    "chat.message": async (input: any) => {
      const model: string | undefined = input?.model ?? input?.params?.model;
      const provider = detectProvider(model);
      const now = new Date().toISOString();

      if (!store.providers[provider]) {
        store.providers[provider] = {
          total_requests: 0,
          today_requests: 0,
          this_month_requests: 0,
          last_request_at: null,
          estimated_limit: null,
          plan: null,
          custom_data: {},
        };
      }

      const stats = store.providers[provider];
      resetCountersIfNeeded(stats);

      stats.total_requests += 1;
      stats.today_requests += 1;
      stats.this_month_requests += 1;
      stats.last_request_at = now;

      store.history.push({
        timestamp: now,
        model: model || "unknown",
        provider,
        messages_count: Array.isArray(input?.messages) ? input.messages.length : 1,
      });

      // Trim history to last 1000 entries to keep file small
      if (store.history.length > 1000) {
        store.history = store.history.slice(-1000);
      }

      saveStore(store);
    },

    /* -------------------------------------------------------------- */
    // 2. Sniff rate-limit headers from chat responses (best-effort)
    /* -------------------------------------------------------------- */
    "chat.headers": async (_input: any, output: any) => {
      // output.headers is a Record<string, string> on the response
      const headers: Record<string, string> = output?.headers ?? {};
      const h = Object.fromEntries(
        Object.entries(headers).map(([k, v]) => [k.toLowerCase(), v])
      );

      const remaining = h["x-ratelimit-remaining"];
      const limit = h["x-ratelimit-limit"];
      const reset = h["x-ratelimit-reset"];
      const provider = detectProvider(output?.model);

      if (remaining || limit) {
        const stats = store.providers[provider];
        if (stats) {
          stats.custom_data["last_rate_limit_remaining"] = remaining ?? null;
          stats.custom_data["last_rate_limit_total"] = limit ?? null;
          stats.custom_data["last_rate_limit_reset"] = reset ?? null;
          stats.custom_data["last_rate_limit_seen_at"] = new Date().toISOString();
          saveStore(store);
        }
      }
    },

    /* -------------------------------------------------------------- */
    // 3. Expose a custom tool: usage_tracker_status
    /* -------------------------------------------------------------- */
    tool: {
      usage_tracker_status: {
        description:
          "Returns current usage statistics for GitHub Copilot, Codex, and OpenCode Go. " +
          "Use this when the user asks about their quota, limits, or how many requests they have left.",
        parameters: {
          type: "object" as const,
          properties: {
            provider: {
              type: "string" as const,
              enum: ["github_copilot", "codex", "opencode_go", "all"],
              description: "Which provider to query. Use 'all' for a summary of every provider.",
            },
          },
          required: ["provider"],
        },
        execute: async ({ provider }: { provider: string }) => {
          const now = new Date().toISOString();
          const providersToReport =
            provider === "all" ? Object.keys(store.providers) : [provider];

          const report: Record<string, any> = {};

          for (const key of providersToReport) {
            const stats = store.providers[key];
            if (!stats) {
              report[key] = { error: "No data yet for this provider" };
              continue;
            }

            resetCountersIfNeeded(stats);

            const remaining =
              stats.estimated_limit != null
                ? Math.max(0, stats.estimated_limit - stats.this_month_requests)
                : null;

            report[key] = {
              total_requests: stats.total_requests,
              today_requests: stats.today_requests,
              this_month_requests: stats.this_month_requests,
              estimated_limit: stats.estimated_limit,
              estimated_remaining: remaining,
              last_request_at: stats.last_request_at,
              plan: stats.plan,
              rate_limit_headers: {
                remaining: stats.custom_data["last_rate_limit_remaining"] ?? null,
                limit: stats.custom_data["last_rate_limit_total"] ?? null,
                reset: stats.custom_data["last_rate_limit_reset"] ?? null,
                seen_at: stats.custom_data["last_rate_limit_seen_at"] ?? null,
              },
            };
          }

          return {
            fetched_at: now,
            store_path: STORE_FILE,
            providers: report,
            note:
              "Limits are estimates unless real rate-limit headers have been captured. " +
              "Set your actual plan/limit in the store file to improve accuracy.",
          };
        },
      },
    },

    /* -------------------------------------------------------------- */
    // 4. Optional: log a compact summary on startup
    /* -------------------------------------------------------------- */
    config: (_cfg: any) => {
      const keys = Object.keys(store.providers);
      const active = keys.filter((k) => store.providers[k].total_requests > 0);
      if (active.length > 0) {
        console.log(
          `[usage-tracker] Tracking ${active.length} provider(s). Store: ${STORE_FILE}`
        );
      }
    },
  };
}) satisfies Plugin;
