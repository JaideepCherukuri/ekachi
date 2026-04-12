import { AgentSSEEvent } from "./event";

export enum SessionStatus {
    PENDING = "pending",
    RUNNING = "running",
    WAITING = "waiting",
    COMPLETED = "completed"
}

export interface CreateSessionResponse {
    session_id: string;
    provider_id?: string | null;
    provider_label?: string | null;
    model_name?: string | null;
    project_id?: string | null;
    project_name?: string | null;
    project_color?: string | null;
    browser_cdp_url?: string | null;
    browser_cookie_profile?: string | null;
    browser_extension_paths?: string[];
    browser_cookies?: Record<string, unknown>[];
}

export interface GetSessionResponse {
    session_id: string;
    title: string | null;
    status: SessionStatus;
    events: AgentSSEEvent[];
    is_shared: boolean;
    project_id?: string | null;
    project_name?: string | null;
    project_color?: string | null;
    provider_id?: string | null;
    provider_label?: string | null;
    model_name?: string | null;
    browser_engine?: string | null;
    browser_cdp_url?: string | null;
    browser_cookie_profile?: string | null;
    browser_extension_paths?: string[];
    browser_cookies?: Record<string, unknown>[];
}

export interface ListSessionItem {
    session_id: string;
    title: string | null;
    latest_message: string | null;
    latest_message_at: number | null;
    status: SessionStatus;
    unread_message_count: number;
    is_shared: boolean;
    project_id?: string | null;
    project_name?: string | null;
    project_color?: string | null;
    provider_id?: string | null;
    provider_label?: string | null;
    model_name?: string | null;
    browser_engine?: string | null;
    browser_cdp_url?: string | null;
    browser_cookie_profile?: string | null;
    browser_extension_paths?: string[];
    browser_cookies?: Record<string, unknown>[];
}

export interface ListSessionResponse {
    sessions: ListSessionItem[];
}

export interface ProjectResponse {
    project_id: string;
    name: string;
    color: string;
    default_provider_id?: string | null;
    default_model_name?: string | null;
    preferred_search_provider?: string | null;
    preferred_browser_engine?: string | null;
    browser_cdp_url?: string | null;
    browser_pool?: ProjectBrowserPoolEntry[];
    browser_cookie_profile?: string | null;
    browser_extension_paths?: string[];
    browser_cookies?: Record<string, unknown>[];
    created_at: string;
    updated_at: string;
}

export interface ListProjectsResponse {
    projects: ProjectResponse[];
}

export enum TriggerType {
    MANUAL = "manual",
    WEBHOOK = "webhook",
    SCHEDULE = "schedule",
}

export enum TriggerStatus {
    ACTIVE = "active",
    INACTIVE = "inactive",
    COMPLETED = "completed",
}

export enum TriggerRunStatus {
    PENDING = "pending",
    RUNNING = "running",
    COMPLETED = "completed",
    FAILED = "failed",
    CANCELLED = "cancelled",
}

export interface TriggerResponse {
    trigger_id: string;
    project_id?: string | null;
    name: string;
    prompt: string;
    trigger_type: TriggerType;
    status: TriggerStatus;
    webhook_secret?: string | null;
    schedule_cron?: string | null;
    schedule_timezone: string;
    next_run_at?: string | null;
    last_run_at?: string | null;
    last_run_status?: TriggerRunStatus | null;
    execution_count: number;
    success_count: number;
    failure_count: number;
    cancelled_count: number;
    created_at: string;
    updated_at: string;
}

export interface ListTriggersResponse {
    triggers: TriggerResponse[];
}

export interface TriggerRunResponse {
    run_id: string;
    trigger_id: string;
    project_id?: string | null;
    session_id?: string | null;
    trigger_type: TriggerType;
    status: TriggerRunStatus;
    source: TriggerType;
    input_payload?: Record<string, unknown> | null;
    output_summary?: string | null;
    error_message?: string | null;
    duration_seconds?: number | null;
    attempt_number: number;
    started_at: string;
    completed_at?: string | null;
    created_at: string;
    updated_at: string;
}

export interface ListTriggerRunsResponse {
    runs: TriggerRunResponse[];
}

export interface SkillResponse {
    skill_id: string;
    project_id?: string | null;
    name: string;
    description?: string | null;
    instructions: string;
    source: 'user' | 'example';
    is_example: boolean;
    template_key?: string | null;
    enabled: boolean;
    created_at: string;
    updated_at: string;
}

export interface ListSkillsResponse {
    skills: SkillResponse[];
}

export interface MemoryResponse {
    memory_id?: string | null;
    project_id?: string | null;
    content: string;
    created_at?: string | null;
    updated_at?: string | null;
}

export type WorkerRole = 'coordinator' | 'research' | 'developer' | 'browser' | 'document' | 'automation' | 'custom'
export type WorkerLane = 'intake' | 'research' | 'execution' | 'delivery'

export interface WorkerResponse {
    worker_id: string;
    project_id?: string | null;
    name: string;
    description?: string | null;
    role: WorkerRole;
    lane: WorkerLane;
    instructions: string;
    tool_names: string[];
    enabled: boolean;
    created_at: string;
    updated_at: string;
}

export interface ListWorkersResponse {
    workers: WorkerResponse[];
}

export interface ConsoleRecord {
    ps1: string;
    command: string;
    output: string;
  }
  
  export interface ShellViewResponse {
    output: string;
    session_id: string;
    console: ConsoleRecord[];
  }

export interface FileViewResponse {
    content: string;
    file: string;
}

export interface SignedUrlResponse {
    signed_url: string;
    expires_in: number;
}

export interface ShareSessionResponse {
    session_id: string;
    is_shared: boolean;
}

export interface SharedSessionResponse {
    session_id: string;
    title: string | null;
    status: SessionStatus;
    events: AgentSSEEvent[];
    is_shared: boolean;
    project_id?: string | null;
    project_name?: string | null;
    project_color?: string | null;
    provider_id?: string | null;
    provider_label?: string | null;
    model_name?: string | null;
    browser_engine?: string | null;
    browser_cdp_url?: string | null;
    browser_cookie_profile?: string | null;
    browser_extension_paths?: string[];
    browser_cookies?: Record<string, unknown>[];
}

export interface BrowserConnectionResponse {
    cdp_url: string;
    ws_url: string;
    browser?: string | null;
    user_agent?: string | null;
    protocol_version?: string | null;
    context_count: number;
    page_count: number;
    total_cookie_count: number;
}

export interface BrowserPoolEntry {
    browser_id: string;
    label: string;
    cdp_url: string;
    source: string;
    active: boolean;
    healthy: boolean;
    browser?: string | null;
    page_count: number;
    total_cookie_count: number;
    error?: string | null;
}

export interface ProjectBrowserPoolEntry {
    browser_id: string;
    label: string;
    cdp_url: string;
    source: string;
    created_at: string;
    updated_at: string;
}

export interface BrowserPoolResponse {
    active_browser_id?: string | null;
    browsers: BrowserPoolEntry[];
}

export interface BrowserCookieDomainResponse {
    domain: string;
    root_domain: string;
    cookie_count: number;
    http_only_count: number;
    secure_count: number;
}

export interface BrowserCookieInventoryResponse {
    source: string;
    total_cookie_count: number;
    domains: BrowserCookieDomainResponse[];
}

export interface BrowserCookieMutationResponse {
    removed_count?: number;
    captured_count?: number;
    applied_count?: number;
    inventory: BrowserCookieInventoryResponse;
}
  
