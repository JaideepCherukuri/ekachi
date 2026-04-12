<template>
  <div class="flex flex-col gap-4 w-full">
    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <div class="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
            Official Connectors
          </div>
          <div class="text-[22px] font-semibold text-[var(--text-primary)] mt-1">
            Curated MCP Install Flows
          </div>
          <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6 max-w-3xl">
            Ekachi now treats high-value integrations as first-class product surfaces. Install, configure, and remove official connector templates without editing raw MCP JSON, then drop down to advanced mode when you need custom servers.
          </div>
        </div>
        <button
          type="button"
          class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)] disabled:opacity-50"
          :disabled="connectorLoading"
          @click="loadConnectorCatalog"
        >
          {{ connectorLoading ? 'Refreshing...' : 'Refresh Connectors' }}
        </button>
      </div>

      <div class="mt-5 grid grid-cols-1 xl:grid-cols-2 gap-3">
        <article
          v-for="connector in connectorCatalog"
          :key="connector.connector_id"
          class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4 flex flex-col gap-3"
        >
          <div class="flex items-start justify-between gap-3 flex-wrap">
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <div class="text-base font-semibold text-[var(--text-primary)]">{{ connector.name }}</div>
                <span class="px-2.5 py-1 rounded-full border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] text-[11px] text-[var(--text-secondary)]">
                  {{ connector.category }}
                </span>
                <StatusChip :active="connector.configured" :label="connector.configured ? 'Configured' : connector.installed ? 'Needs setup' : 'Not installed'" />
              </div>
              <div class="text-sm text-[var(--text-secondary)] leading-6 mt-2">
                {{ connector.description }}
              </div>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
              <button
                type="button"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)]"
                @click="openConnectorEditor(connector.connector_id)"
              >
                {{ connector.installed ? 'Update' : 'Configure' }}
              </button>
              <button
                v-if="connector.installed"
                type="button"
                class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--function-error)] text-sm font-medium hover:bg-[var(--glass-surface)] disabled:opacity-50"
                :disabled="removingConnectorId === connector.connector_id"
                @click="removeConnectorInstallation(connector)"
              >
                {{ removingConnectorId === connector.connector_id ? 'Removing...' : 'Remove' }}
              </button>
            </div>
          </div>

          <div class="flex items-center gap-2 flex-wrap text-xs text-[var(--text-tertiary)]">
            <span class="px-2.5 py-1 rounded-full border border-[var(--glass-border-strong)] bg-[var(--glass-surface)]">
              {{ connector.transport }}
            </span>
            <span class="px-2.5 py-1 rounded-full border border-[var(--glass-border-strong)] bg-[var(--glass-surface)]">
              {{ connector.enabled ? 'Enabled' : 'Disabled' }}
            </span>
            <span
              v-for="tag in connector.tags"
              :key="`${connector.connector_id}-${tag}`"
              class="px-2.5 py-1 rounded-full border border-[var(--glass-border-strong)] bg-[var(--glass-surface)]"
            >
              {{ tag }}
            </span>
          </div>

          <div class="text-xs text-[var(--text-tertiary)] leading-6 break-all">
            Runtime:
            <span class="text-[var(--text-secondary)]">{{ formatConnectorRuntime(connector) }}</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
            <div
              v-for="field in connector.field_states"
              :key="`${connector.connector_id}-${field.key}`"
              class="rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3"
            >
              <div class="flex items-center justify-between gap-2">
                <div class="text-sm font-medium text-[var(--text-primary)]">{{ field.label }}</div>
                <StatusChip :active="field.configured" :label="field.configured ? 'Set' : field.required ? 'Required' : 'Optional'" />
              </div>
              <div class="text-xs text-[var(--text-tertiary)] mt-2 leading-5">
                {{ field.description || 'Configuration value for this connector.' }}
              </div>
              <div v-if="!field.secret && field.value" class="text-xs text-[var(--text-secondary)] mt-2 break-all">
                {{ field.value }}
              </div>
              <div v-else-if="field.secret && field.configured" class="text-xs text-[var(--text-secondary)] mt-2">
                Secret is configured and stays redacted.
              </div>
            </div>
          </div>

          <div class="flex items-center justify-between gap-3 flex-wrap">
            <a
              v-if="connector.docs_url"
              :href="connector.docs_url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-sm text-[var(--text-brand)] hover:underline"
            >
              Open setup docs
            </a>
            <div v-if="connector.missing_required_fields.length" class="text-xs text-[var(--function-error)]">
              Missing: {{ connector.missing_required_fields.join(', ') }}
            </div>
          </div>
        </article>
      </div>
    </section>

    <section
      v-if="selectedConnector"
      class="ek-glass-card rounded-[20px] p-5"
    >
      <div class="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <div class="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
            Connector Editor
          </div>
          <div class="text-[22px] font-semibold text-[var(--text-primary)] mt-1">
            {{ selectedConnector.name }}
          </div>
          <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6 max-w-3xl">
            {{ selectedConnector.description }}
          </div>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <StatusChip :active="selectedConnector.configured" :label="selectedConnector.configured ? 'Ready' : 'Configuration required'" />
          <button
            type="button"
            class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)]"
            @click="resetConnectorEditor"
          >
            Close
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-2 gap-3 mt-5">
        <label
          v-for="field in selectedConnector.field_states"
          :key="`${selectedConnector.connector_id}-${field.key}`"
          class="flex flex-col gap-2 rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4"
        >
          <div class="flex items-center justify-between gap-2 flex-wrap">
            <span class="text-sm font-medium text-[var(--text-primary)]">{{ field.label }}</span>
            <StatusChip :active="field.configured" :label="field.required ? 'Required' : 'Optional'" />
          </div>
          <span class="text-xs text-[var(--text-tertiary)] leading-5">
            {{ field.description || 'Configuration value for this connector.' }}
          </span>
          <input
            v-model="connectorFieldValues[field.key]"
            :type="field.secret ? 'password' : 'text'"
            class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
            :placeholder="fieldPlaceholder(field)"
          />
          <label
            v-if="field.secret && field.configured"
            class="inline-flex items-center gap-2 text-xs text-[var(--text-secondary)]"
          >
            <input
              v-model="connectorClearFlags[field.key]"
              type="checkbox"
              class="rounded border-[var(--glass-border-strong)]"
            />
            Clear stored secret instead of preserving it
          </label>
          <div
            v-else-if="!field.secret && field.value"
            class="text-xs text-[var(--text-secondary)] break-all"
          >
            Current value: {{ field.value }}
          </div>
        </label>
      </div>

      <div class="flex items-center gap-5 flex-wrap mt-5">
        <label class="inline-flex items-center gap-2 text-sm text-[var(--text-primary)]">
          <input v-model="connectorEditorEnabled" type="checkbox" class="rounded border-[var(--glass-border-strong)]" />
          Enable this connector immediately
        </label>
      </div>

      <div class="flex items-center gap-2 flex-wrap mt-5">
        <button
          type="button"
          class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90 disabled:opacity-50"
          :disabled="connectorSaving"
          @click="saveConnectorConfig"
        >
          {{ connectorSaving ? 'Saving...' : selectedConnector.installed ? 'Save Connector' : 'Install Connector' }}
        </button>
        <button
          type="button"
          class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)]"
          @click="resetConnectorEditor"
        >
          Cancel
        </button>
      </div>
    </section>

    <section class="ek-glass-card rounded-[20px] p-5">
      <div class="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <div class="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
            Advanced Mode
          </div>
          <div class="text-[22px] font-semibold text-[var(--text-primary)] mt-1">
            {{ mcpInventory.servers.length }} Configured Server{{ mcpInventory.servers.length === 1 ? '' : 's' }}
          </div>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <button
            type="button"
            class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90"
            @click="openComposer"
          >
            {{ composerOpen ? 'Close MCP Composer' : 'New MCP Server' }}
          </button>
          <button
            type="button"
            class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)] disabled:opacity-50"
            :disabled="mcpLoading"
            @click="loadMcpInventory"
          >
            {{ mcpLoading ? 'Refreshing...' : 'Refresh MCP Inventory' }}
          </button>
        </div>
      </div>
      <div class="text-sm text-[var(--text-secondary)] mt-2 leading-6">
        The raw MCP composer is still available for custom servers, local experiments, or any runtime the curated catalog does not cover yet.
      </div>

      <div class="mt-5 grid grid-cols-1 xl:grid-cols-2 gap-3">
        <article class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] p-4 flex flex-col gap-4">
          <div>
            <div class="text-base font-semibold text-[var(--text-primary)]">Import Local MCP JSON</div>
            <div class="text-sm text-[var(--text-secondary)] mt-1">
              Paste an `mcpServers` object to bulk import local or stdio-based servers.
            </div>
          </div>
          <textarea
            v-model="localImportText"
            rows="8"
            class="rounded-[16px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3 text-sm text-[var(--text-primary)] resize-y min-h-[180px]"
            placeholder='{"mcpServers":{"filesystem":{"command":"npx","args":["-y","@modelcontextprotocol/server-filesystem","/tmp"],"transport":"stdio","enabled":true}}}'
          />
          <div class="flex items-center gap-2 flex-wrap">
            <button
              type="button"
              class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90 disabled:opacity-50"
              :disabled="mcpImporting"
              @click="importLocalConfig"
            >
              {{ mcpImporting ? 'Importing...' : 'Import JSON' }}
            </button>
          </div>
        </article>

        <article class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] p-4 flex flex-col gap-4">
          <div>
            <div class="text-base font-semibold text-[var(--text-primary)]">Import Remote MCP</div>
            <div class="text-sm text-[var(--text-secondary)] mt-1">
              Register a hosted MCP endpoint into the runtime file without manually building the raw server stanza.
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input
              v-model="remoteImportForm.name"
              class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
              placeholder="acme-mcp"
            />
            <Select v-model="remoteImportForm.transport">
              <SelectTrigger class="w-full h-[42px]">
                <SelectValue placeholder="Select transport" />
              </SelectTrigger>
              <SelectContent :side-offset="6">
                <SelectItem value="streamable-http">streamable-http</SelectItem>
                <SelectItem value="sse">sse</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <input
            v-model="remoteImportForm.url"
            class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
            placeholder="https://mcp.example.com/server"
          />
          <input
            v-model="remoteImportForm.description"
            class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
            placeholder="Hosted MCP endpoint"
          />
          <div class="flex items-center gap-2 flex-wrap">
            <button
              type="button"
              class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90 disabled:opacity-50"
              :disabled="mcpImporting"
              @click="importRemoteConfig"
            >
              {{ mcpImporting ? 'Importing...' : 'Import Remote Server' }}
            </button>
            <button
              type="button"
              class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)] disabled:opacity-50"
              :disabled="mcpExporting"
              @click="loadExportConfig"
            >
              {{ mcpExporting ? 'Refreshing Export...' : 'Refresh Export JSON' }}
            </button>
          </div>
          <textarea
            v-model="exportConfigText"
            rows="8"
            class="rounded-[16px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3 text-sm text-[var(--text-primary)] resize-y min-h-[180px]"
            placeholder='{"mcpServers":{}}'
          />
        </article>
      </div>

      <div v-if="composerOpen" class="mt-5 rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] p-4 flex flex-col gap-4">
        <div class="flex items-center justify-between gap-3 flex-wrap">
          <div>
            <div class="text-base font-semibold text-[var(--text-primary)]">
              {{ editingServerName ? 'Edit MCP Server' : 'Create MCP Server' }}
            </div>
            <div class="text-sm text-[var(--text-secondary)] mt-1">
              Configure stdio or HTTP-based MCP servers without editing the config file manually.
            </div>
          </div>
          <StatusChip :active="mcpForm.enabled" :label="mcpForm.enabled ? 'Enabled' : 'Disabled'" />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <label class="flex flex-col gap-2">
            <span class="text-sm font-medium text-[var(--text-primary)]">Name</span>
            <input
              v-model="mcpForm.name"
              class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
              placeholder="custom-server"
            />
          </label>

          <label class="flex flex-col gap-2">
            <span class="text-sm font-medium text-[var(--text-primary)]">Transport</span>
            <Select v-model="mcpForm.transport">
              <SelectTrigger class="w-full h-[42px]">
                <SelectValue placeholder="Select transport" />
              </SelectTrigger>
              <SelectContent :side-offset="6">
                <SelectItem value="stdio">stdio</SelectItem>
                <SelectItem value="sse">sse</SelectItem>
                <SelectItem value="streamable-http">streamable-http</SelectItem>
              </SelectContent>
            </Select>
          </label>
        </div>

        <label class="flex flex-col gap-2">
          <span class="text-sm font-medium text-[var(--text-primary)]">Description</span>
          <input
            v-model="mcpForm.description"
            class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
            placeholder="Workspace integration for documents or tools"
          />
        </label>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <label v-if="mcpForm.transport === 'stdio'" class="flex flex-col gap-2">
            <span class="text-sm font-medium text-[var(--text-primary)]">Command</span>
            <input
              v-model="mcpForm.command"
              class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
              placeholder="npx"
            />
          </label>

          <label v-else class="flex flex-col gap-2">
            <span class="text-sm font-medium text-[var(--text-primary)]">URL</span>
            <input
              v-model="mcpForm.url"
              class="h-11 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 text-sm text-[var(--text-primary)]"
              placeholder="https://mcp.example.com/server"
            />
          </label>

          <label class="flex items-center gap-3 rounded-[14px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3">
            <input v-model="mcpForm.enabled" type="checkbox" class="size-4 rounded border-[var(--glass-border-strong)]" />
            <span class="text-sm text-[var(--text-primary)]">Enable this server immediately</span>
          </label>
        </div>

        <label v-if="mcpForm.transport === 'stdio'" class="flex flex-col gap-2">
          <span class="text-sm font-medium text-[var(--text-primary)]">Arguments</span>
          <textarea
            v-model="mcpForm.argsText"
            rows="4"
            class="rounded-[16px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3 text-sm text-[var(--text-primary)] resize-y min-h-[110px]"
            placeholder="-y&#10;@modelcontextprotocol/server-filesystem&#10;/tmp"
          />
          <span class="text-xs text-[var(--text-tertiary)]">One argument per line.</span>
        </label>

        <div class="grid grid-cols-1 xl:grid-cols-2 gap-3">
          <label class="flex flex-col gap-2">
            <span class="text-sm font-medium text-[var(--text-primary)]">Headers JSON</span>
            <textarea
              v-model="mcpForm.headersText"
              rows="6"
              class="rounded-[16px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3 text-sm text-[var(--text-primary)] resize-y min-h-[140px]"
              placeholder='{"Authorization":"Bearer token"}'
            />
          </label>
          <label class="flex flex-col gap-2">
            <span class="text-sm font-medium text-[var(--text-primary)]">Environment JSON</span>
            <textarea
              v-model="mcpForm.envText"
              rows="6"
              class="rounded-[16px] border border-[var(--glass-border-strong)] bg-[var(--glass-surface)] px-3 py-3 text-sm text-[var(--text-primary)] resize-y min-h-[140px]"
              placeholder='{"NODE_ENV":"production"}'
            />
          </label>
        </div>

        <div class="flex items-center gap-2 flex-wrap">
          <button
            type="button"
            @click="saveServer"
            :disabled="mcpSaving"
            class="px-4 py-2 rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] text-sm font-medium hover:opacity-90 disabled:opacity-50"
          >
            {{ mcpSaving ? 'Saving...' : editingServerName ? 'Save MCP Server' : 'Create MCP Server' }}
          </button>
          <button
            type="button"
            @click="resetComposer"
            class="px-4 py-2 rounded-[14px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface-soft)]"
          >
            Cancel
          </button>
        </div>
      </div>

      <div class="mt-4 grid grid-cols-1 xl:grid-cols-2 gap-3">
        <article
          v-for="server in mcpInventory.servers"
          :key="server.name"
          class="rounded-[18px] border border-[var(--glass-border)] bg-[var(--glass-surface-soft)] px-4 py-4 flex flex-col gap-2"
        >
          <div class="flex items-center justify-between gap-3 flex-wrap">
            <div class="text-base font-semibold text-[var(--text-primary)]">{{ server.name }}</div>
            <StatusChip :active="server.enabled" :label="server.enabled ? 'Enabled' : 'Disabled'" />
          </div>
          <div class="flex items-center gap-2 flex-wrap text-xs text-[var(--text-tertiary)]">
            <span class="px-2.5 py-1 rounded-full border border-[var(--glass-border-strong)] bg-[var(--glass-surface)]">
              {{ server.transport }}
            </span>
            <span v-if="server.has_env" class="px-2.5 py-1 rounded-full border border-[var(--glass-border-strong)] bg-[var(--glass-surface)]">
              Has env
            </span>
            <span v-if="server.has_headers" class="px-2.5 py-1 rounded-full border border-[var(--glass-border-strong)] bg-[var(--glass-surface)]">
              Has headers
            </span>
          </div>
          <div v-if="server.description" class="text-sm text-[var(--text-secondary)] leading-6">
            {{ server.description }}
          </div>
          <div v-if="server.command" class="text-sm text-[var(--text-primary)] break-all">
            Command: <span class="text-[var(--text-secondary)]">{{ server.command }}{{ server.args.length ? ` ${server.args.join(' ')}` : '' }}</span>
          </div>
          <div v-if="server.url" class="text-sm text-[var(--text-primary)] break-all">
            URL: <span class="text-[var(--text-secondary)]">{{ server.url }}</span>
          </div>
          <div class="flex items-center gap-2 flex-wrap mt-2">
            <button
              type="button"
              @click="toggleServer(server.name)"
              :disabled="mcpSaving"
              class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)] disabled:opacity-50"
            >
              {{ server.enabled ? 'Disable' : 'Enable' }}
            </button>
            <button
              type="button"
              @click="startEditing(server.name)"
              :disabled="mcpSaving"
              class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--text-primary)] text-sm font-medium hover:bg-[var(--glass-surface)] disabled:opacity-50"
            >
              Edit
            </button>
            <button
              type="button"
              @click="removeServer(server.name)"
              :disabled="mcpSaving"
              class="px-3 py-2 rounded-[12px] border border-[var(--glass-border-strong)] text-[var(--function-error)] text-sm font-medium hover:bg-[var(--glass-surface)] disabled:opacity-50"
            >
              Delete
            </button>
          </div>
        </article>
        <div
          v-if="!mcpLoading && mcpInventory.servers.length === 0"
          class="rounded-[18px] border border-dashed border-[var(--glass-border-strong)] px-4 py-8 text-center text-sm text-[var(--text-tertiary)] xl:col-span-2"
        >
          No MCP servers are configured in the runtime file.
        </div>
      </div>
    </section>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4 w-full">
      <article class="ek-glass-card rounded-[20px] p-5 flex flex-col gap-2">
        <div class="flex items-center justify-between gap-3">
          <div class="text-base font-semibold text-[var(--text-primary)]">MCP</div>
          <StatusChip :active="!!controlPlaneConfig?.mcp_configured" />
        </div>
        <div class="text-sm text-[var(--text-secondary)] leading-6">
          Model Context Protocol support exists in the backend runtime.
        </div>
        <div class="text-sm text-[var(--text-primary)]">
          {{ controlPlaneConfig?.mcp_configured ? 'An MCP config file is present for the runtime.' : 'No runtime MCP config file detected.' }}
        </div>
      </article>

      <article class="ek-glass-card rounded-[20px] p-5 flex flex-col gap-2">
        <div class="flex items-center justify-between gap-3">
          <div class="text-base font-semibold text-[var(--text-primary)]">Ekachi Claw</div>
          <StatusChip :active="!!controlPlaneConfig?.claw_enabled" />
        </div>
        <div class="text-sm text-[var(--text-secondary)] leading-6">
          Dedicated OpenClaw companion mode running alongside the main agent workspace.
        </div>
      </article>

      <article class="ek-glass-card rounded-[20px] p-5 flex flex-col gap-2">
        <div class="flex items-center justify-between gap-3">
          <div class="text-base font-semibold text-[var(--text-primary)]">Password Reset Email</div>
          <StatusChip :active="!!controlPlaneConfig?.email_enabled" />
        </div>
        <div class="text-sm text-[var(--text-secondary)] leading-6">
          Password reset only works operationally when SMTP is configured.
        </div>
      </article>

      <article class="ek-glass-card rounded-[20px] p-5 flex flex-col gap-2">
        <div class="flex items-center justify-between gap-3">
          <div class="text-base font-semibold text-[var(--text-primary)]">Google Analytics</div>
          <StatusChip :active="!!controlPlaneConfig?.google_analytics_enabled" />
        </div>
        <div class="text-sm text-[var(--text-secondary)] leading-6">
          Client analytics initialization is controlled by runtime config.
        </div>
      </article>

      <article class="ek-glass-card rounded-[20px] p-5 flex flex-col gap-2">
        <div class="flex items-center justify-between gap-3">
          <div class="text-base font-semibold text-[var(--text-primary)]">GitHub Link</div>
          <StatusChip :active="!!controlPlaneConfig?.show_github_button" :label="controlPlaneConfig?.show_github_button ? 'Visible' : 'Hidden'" />
        </div>
        <a
          :href="controlPlaneConfig?.github_repository_url || '#'"
          target="_blank"
          rel="noopener noreferrer"
          class="text-sm text-[var(--text-brand)] hover:underline break-all"
        >
          {{ controlPlaneConfig?.github_repository_url || 'Unavailable' }}
        </a>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import type { ControlPlaneConfigResponse } from '@/api/config'
import {
  configureMcpConnector,
  createMcpServer,
  deleteMcpConnector,
  deleteMcpServer,
  exportMcpConfig,
  getMcpConnector,
  getMcpConnectors,
  getMcpServer,
  getMcpServers,
  importLocalMcpServers,
  importRemoteMcpServer,
  updateMcpServer,
  type MCPConnectorFieldState,
  type MCPConnectorStatus,
  type MCPServersResponse,
  type MCPTransport,
} from '@/api/mcp'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { showErrorToast, showSuccessToast } from '@/utils/toast'
import StatusChip from './StatusChip.vue'

const props = defineProps<{
  controlPlaneConfig: ControlPlaneConfigResponse | null
  dialogOpen?: boolean
}>()

const connectorLoading = ref(false)
const connectorSaving = ref(false)
const removingConnectorId = ref<string | null>(null)
const connectorCatalog = ref<MCPConnectorStatus[]>([])
const selectedConnector = ref<MCPConnectorStatus | null>(null)
const connectorEditorEnabled = ref(true)
const connectorFieldValues = reactive<Record<string, string>>({})
const connectorClearFlags = reactive<Record<string, boolean>>({})

const mcpLoading = ref(false)
const mcpInventory = ref<MCPServersResponse>({
  configured: false,
  servers: [],
})
const mcpSaving = ref(false)
const composerOpen = ref(false)
const editingServerName = ref<string | null>(null)
const mcpImporting = ref(false)
const mcpExporting = ref(false)
const localImportText = ref('')
const exportConfigText = ref('')
const remoteImportForm = reactive({
  name: '',
  url: '',
  transport: 'streamable-http' as MCPTransport,
  description: '',
})
const mcpForm = reactive({
  name: '',
  transport: 'streamable-http' as MCPTransport,
  enabled: true,
  description: '',
  command: '',
  argsText: '',
  url: '',
  headersText: '',
  envText: '',
})

const clearReactiveRecord = (record: Record<string, string | boolean>) => {
  for (const key of Object.keys(record)) {
    delete record[key]
  }
}

const fieldPlaceholder = (field: MCPConnectorFieldState) => {
  if (field.secret && field.configured) {
    return 'Leave blank to keep existing secret'
  }
  return field.placeholder || ''
}

const formatConnectorRuntime = (connector: MCPConnectorStatus) => {
  if (connector.command) {
    return `${connector.command}${connector.args.length ? ` ${connector.args.join(' ')}` : ''}`
  }
  return connector.url || 'Custom runtime'
}

const hydrateConnectorEditor = (connector: MCPConnectorStatus) => {
  selectedConnector.value = connector
  connectorEditorEnabled.value = connector.installed ? connector.enabled : true
  clearReactiveRecord(connectorFieldValues)
  clearReactiveRecord(connectorClearFlags)

  for (const field of connector.field_states) {
    connectorFieldValues[field.key] = field.secret ? '' : field.value || ''
    connectorClearFlags[field.key] = false
  }
}

const resetConnectorEditor = () => {
  selectedConnector.value = null
  connectorEditorEnabled.value = true
  clearReactiveRecord(connectorFieldValues)
  clearReactiveRecord(connectorClearFlags)
}

const loadConnectorCatalog = async () => {
  connectorLoading.value = true
  try {
    connectorCatalog.value = await getMcpConnectors()
    if (selectedConnector.value) {
      const refreshed = connectorCatalog.value.find(
        (connector) => connector.connector_id === selectedConnector.value?.connector_id,
      )
      if (refreshed) {
        hydrateConnectorEditor(await getMcpConnector(refreshed.connector_id))
      }
    }
  } catch (error) {
    console.error('Failed to load connector catalog:', error)
    showErrorToast('Failed to load connectors')
  } finally {
    connectorLoading.value = false
  }
}

const openConnectorEditor = async (connectorId: string) => {
  connectorSaving.value = true
  try {
    const connector = await getMcpConnector(connectorId)
    hydrateConnectorEditor(connector)
  } catch (error) {
    console.error('Failed to load connector:', error)
    showErrorToast('Failed to load connector')
  } finally {
    connectorSaving.value = false
  }
}

const saveConnectorConfig = async () => {
  if (!selectedConnector.value) return

  const values: Record<string, string | null> = {}
  const clearKeys: string[] = []

  for (const field of selectedConnector.value.field_states) {
    const normalized = (connectorFieldValues[field.key] || '').trim()
    if (normalized) {
      values[field.key] = normalized
    } else if (field.secret && connectorClearFlags[field.key]) {
      clearKeys.push(field.key)
    } else if (!field.secret && field.configured) {
      clearKeys.push(field.key)
    }
  }

  connectorSaving.value = true
  try {
    await configureMcpConnector(selectedConnector.value.connector_id, {
      enabled: connectorEditorEnabled.value,
      values,
      clear_keys: clearKeys,
    })
    showSuccessToast(selectedConnector.value.installed ? 'Connector updated' : 'Connector installed')
    await Promise.all([loadConnectorCatalog(), loadMcpInventory()])
    resetConnectorEditor()
  } catch (error) {
    console.error('Failed to save connector:', error)
    showErrorToast('Failed to save connector')
  } finally {
    connectorSaving.value = false
  }
}

const removeConnectorInstallation = async (connector: MCPConnectorStatus) => {
  if (!window.confirm(`Remove ${connector.name} from the MCP runtime?`)) return
  removingConnectorId.value = connector.connector_id
  try {
    await deleteMcpConnector(connector.connector_id)
    showSuccessToast('Connector removed')
    await Promise.all([loadConnectorCatalog(), loadMcpInventory()])
    if (selectedConnector.value?.connector_id === connector.connector_id) {
      resetConnectorEditor()
    }
  } catch (error) {
    console.error('Failed to remove connector:', error)
    showErrorToast('Failed to remove connector')
  } finally {
    removingConnectorId.value = null
  }
}

const resetComposer = () => {
  composerOpen.value = false
  editingServerName.value = null
  mcpForm.name = ''
  mcpForm.transport = 'streamable-http'
  mcpForm.enabled = true
  mcpForm.description = ''
  mcpForm.command = ''
  mcpForm.argsText = ''
  mcpForm.url = ''
  mcpForm.headersText = ''
  mcpForm.envText = ''
}

const openComposer = () => {
  if (composerOpen.value && !editingServerName.value) {
    resetComposer()
    return
  }
  composerOpen.value = true
  if (!editingServerName.value) {
    mcpForm.name = ''
  }
}

const loadMcpInventory = async () => {
  mcpLoading.value = true
  try {
    mcpInventory.value = await getMcpServers()
  } catch (error) {
    console.error('Failed to load MCP inventory:', error)
    showErrorToast('Failed to load MCP inventory')
  } finally {
    mcpLoading.value = false
  }
}

const loadExportConfig = async () => {
  mcpExporting.value = true
  try {
    const payload = await exportMcpConfig()
    exportConfigText.value = JSON.stringify(payload, null, 2)
  } catch (error) {
    console.error('Failed to export MCP config:', error)
    showErrorToast('Failed to export MCP config')
  } finally {
    mcpExporting.value = false
  }
}

const parseJsonRecord = (raw: string, label: string): Record<string, string> | null => {
  if (!raw.trim()) return null

  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  } catch {
    throw new Error(`${label} must be valid JSON`)
  }

  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new Error(`${label} must be a JSON object`)
  }

  return Object.fromEntries(
    Object.entries(parsed as Record<string, unknown>).map(([key, value]) => [key, String(value)]),
  )
}

const buildServerPayload = () => {
  return {
    name: mcpForm.name.trim(),
    transport: mcpForm.transport,
    enabled: mcpForm.enabled,
    description: mcpForm.description.trim() || null,
    command: mcpForm.transport === 'stdio' ? mcpForm.command.trim() || null : null,
    args: mcpForm.transport === 'stdio'
      ? mcpForm.argsText.split('\n').map((line) => line.trim()).filter(Boolean)
      : [],
    url: mcpForm.transport === 'stdio' ? null : mcpForm.url.trim() || null,
    headers: parseJsonRecord(mcpForm.headersText, 'Headers'),
    env: parseJsonRecord(mcpForm.envText, 'Environment'),
  }
}

const saveServer = async () => {
  let payload
  try {
    payload = buildServerPayload()
  } catch (error) {
    showErrorToast(error instanceof Error ? error.message : 'Invalid MCP server payload')
    return
  }

  if (!payload.name) {
    showErrorToast('MCP server name is required')
    return
  }

  mcpSaving.value = true
  try {
    if (editingServerName.value) {
      await updateMcpServer(editingServerName.value, payload)
      showSuccessToast('MCP server updated')
    } else {
      await createMcpServer(payload)
      showSuccessToast('MCP server created')
    }
    await Promise.all([loadConnectorCatalog(), loadMcpInventory()])
    resetComposer()
  } catch (error) {
    console.error('Failed to save MCP server:', error)
    showErrorToast('Failed to save MCP server')
  } finally {
    mcpSaving.value = false
  }
}

const importLocalConfig = async () => {
  let parsed: unknown
  try {
    parsed = JSON.parse(localImportText.value || '{}')
  } catch {
    showErrorToast('Import JSON must be valid JSON')
    return
  }
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed) || !('mcpServers' in parsed)) {
    showErrorToast('Import JSON must contain an mcpServers object')
    return
  }

  mcpImporting.value = true
  try {
    await importLocalMcpServers(parsed as { mcpServers: Record<string, Record<string, unknown>> })
    showSuccessToast('MCP servers imported')
    await Promise.all([loadConnectorCatalog(), loadMcpInventory(), loadExportConfig()])
    localImportText.value = ''
  } catch (error) {
    console.error('Failed to import MCP JSON:', error)
    showErrorToast('Failed to import MCP JSON')
  } finally {
    mcpImporting.value = false
  }
}

const importRemoteConfig = async () => {
  if (!remoteImportForm.name.trim() || !remoteImportForm.url.trim()) {
    showErrorToast('Remote MCP name and URL are required')
    return
  }

  mcpImporting.value = true
  try {
    await importRemoteMcpServer({
      name: remoteImportForm.name.trim(),
      url: remoteImportForm.url.trim(),
      transport: remoteImportForm.transport,
      enabled: true,
      description: remoteImportForm.description.trim() || null,
    })
    showSuccessToast('Remote MCP server imported')
    await Promise.all([loadConnectorCatalog(), loadMcpInventory(), loadExportConfig()])
    remoteImportForm.name = ''
    remoteImportForm.url = ''
    remoteImportForm.transport = 'streamable-http'
    remoteImportForm.description = ''
  } catch (error) {
    console.error('Failed to import remote MCP server:', error)
    showErrorToast('Failed to import remote MCP server')
  } finally {
    mcpImporting.value = false
  }
}

const startEditing = async (name: string) => {
  mcpSaving.value = true
  try {
    const server = await getMcpServer(name)
    editingServerName.value = name
    composerOpen.value = true
    mcpForm.name = server.name
    mcpForm.transport = server.transport
    mcpForm.enabled = server.enabled
    mcpForm.description = server.description || ''
    mcpForm.command = server.command || ''
    mcpForm.argsText = (server.args || []).join('\n')
    mcpForm.url = server.url || ''
    mcpForm.headersText = server.headers ? JSON.stringify(server.headers, null, 2) : ''
    mcpForm.envText = server.env ? JSON.stringify(server.env, null, 2) : ''
  } catch (error) {
    console.error('Failed to load MCP server detail:', error)
    showErrorToast('Failed to load MCP server')
  } finally {
    mcpSaving.value = false
  }
}

const toggleServer = async (name: string) => {
  mcpSaving.value = true
  try {
    const server = await getMcpServer(name)
    await updateMcpServer(name, {
      ...server,
      enabled: !server.enabled,
    })
    showSuccessToast(server.enabled ? 'MCP server disabled' : 'MCP server enabled')
    await Promise.all([loadConnectorCatalog(), loadMcpInventory()])
  } catch (error) {
    console.error('Failed to toggle MCP server:', error)
    showErrorToast('Failed to update MCP server')
  } finally {
    mcpSaving.value = false
  }
}

const removeServer = async (name: string) => {
  if (!window.confirm(`Delete MCP server "${name}"?`)) return
  mcpSaving.value = true
  try {
    await deleteMcpServer(name)
    showSuccessToast('MCP server deleted')
    await Promise.all([loadConnectorCatalog(), loadMcpInventory()])
    if (editingServerName.value === name) {
      resetComposer()
    }
  } catch (error) {
    console.error('Failed to delete MCP server:', error)
    showErrorToast('Failed to delete MCP server')
  } finally {
    mcpSaving.value = false
  }
}

watch(
  () => props.dialogOpen,
  (isOpen) => {
    if (isOpen) {
      void Promise.all([loadConnectorCatalog(), loadMcpInventory(), loadExportConfig()])
    }
  },
  { immediate: true },
)
</script>
