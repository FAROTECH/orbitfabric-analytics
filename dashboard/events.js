const EVENT_DATA_URL = "./data/dashboard_data.json";

const eventDateFormat = new Intl.DateTimeFormat("it-IT", {
  day: "2-digit",
  month: "short",
  year: "numeric",
});

function eventAsDate(value) {
  return new Date(`${value}T12:00:00Z`);
}

function formatEventDate(value) {
  return eventDateFormat.format(eventAsDate(value));
}

function eventStatus(event, context) {
  if (event.date > context.timeline_end) {
    return "pending";
  }
  if (event.date < context.timeline_start) {
    return "before";
  }
  return "in-window";
}

function appendTextElement(parent, tag, className, text) {
  const element = document.createElement(tag);
  if (className) {
    element.className = className;
  }
  element.textContent = text;
  parent.appendChild(element);
  return element;
}

function renderEventTrack(data) {
  const track = document.querySelector("#event-track");
  const context = data.event_context;
  if (!track || !context) {
    return;
  }

  track.replaceChildren();

  const start = eventAsDate(context.timeline_start).getTime();
  const end = eventAsDate(context.timeline_end).getTime();
  const span = Math.max(end - start, 1);

  const line = document.createElement("div");
  line.className = "event-track-line";
  track.appendChild(line);

  const groups = new Map();
  for (const event of data.events ?? []) {
    if (eventStatus(event, context) !== "in-window") {
      continue;
    }
    const group = groups.get(event.date) ?? [];
    group.push(event);
    groups.set(event.date, group);
  }

  for (const [day, events] of groups.entries()) {
    const marker = document.createElement("button");
    marker.type = "button";
    marker.className = "event-track-marker";
    const position = ((eventAsDate(day).getTime() - start) / span) * 100;
    marker.style.left = `${Math.min(100, Math.max(0, position))}%`;
    marker.setAttribute(
      "aria-label",
      `${formatEventDate(day)}: ${events.map((event) => event.label).join("; ")}`,
    );
    marker.title = events.map((event) => event.label).join("\n");
    marker.textContent = events.length > 1 ? String(events.length) : "";
    marker.addEventListener("click", () => {
      document.querySelector(`#event-${CSS.escape(events[0].id)}`)?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    });
    line.appendChild(marker);
  }

  const range = document.createElement("div");
  range.className = "event-track-range";
  appendTextElement(range, "span", "", formatEventDate(context.timeline_start));
  appendTextElement(range, "span", "", formatEventDate(context.timeline_end));
  track.appendChild(range);
}

function renderEventSummary(data) {
  const summary = document.querySelector("#event-summary");
  const context = data.event_context;
  if (!summary || !context) {
    return;
  }

  const parts = [`${context.events_in_timeline} in traffic window`];
  if (context.events_pending) {
    parts.push(`${context.events_pending} awaiting traffic`);
  }
  if (context.events_before_timeline) {
    parts.push(`${context.events_before_timeline} before retained window`);
  }
  summary.textContent = parts.join(" · ");
}

function renderEventList(data) {
  const list = document.querySelector("#event-list");
  const context = data.event_context;
  if (!list || !context) {
    return;
  }

  list.replaceChildren();
  const events = [...(data.events ?? [])].sort((a, b) =>
    b.date.localeCompare(a.date) || a.id.localeCompare(b.id),
  );

  if (!events.length) {
    appendTextElement(list, "p", "event-empty", "No curated events yet.");
    return;
  }

  for (const event of events) {
    const status = eventStatus(event, context);
    const card = document.createElement("article");
    card.className = `event-card ${status}${event.type === "internal" ? " internal" : ""}`;
    card.id = `event-${event.id}`;

    const meta = document.createElement("div");
    meta.className = "event-card-meta";
    appendTextElement(meta, "span", "event-date", formatEventDate(event.date));
    appendTextElement(meta, "span", "event-badge", event.type);
    appendTextElement(meta, "span", "event-badge", event.channel);
    appendTextElement(meta, "span", `event-status ${status}`, status === "pending" ? "awaiting traffic" : status === "before" ? "before retained window" : "in traffic window");
    card.appendChild(meta);

    appendTextElement(card, "h4", "event-label", event.label);

    if (event.notes) {
      appendTextElement(card, "p", "event-notes", event.notes);
    }

    const footer = document.createElement("div");
    footer.className = "event-card-footer";
    appendTextElement(
      footer,
      "span",
      "event-scope",
      `scope: ${(event.scope ?? []).join(", ")} · ${event.confidence}`,
    );

    if (event.url) {
      const link = document.createElement("a");
      link.href = event.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = "Open source ↗";
      footer.appendChild(link);
    }

    card.appendChild(footer);
    list.appendChild(card);
  }
}

async function loadEventContext() {
  const response = await fetch(EVENT_DATA_URL, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`dashboard_data.json: HTTP ${response.status}`);
  }
  const data = await response.json();
  if (!data.event_context || !Array.isArray(data.events)) {
    return;
  }
  renderEventSummary(data);
  renderEventTrack(data);
  renderEventList(data);
}

loadEventContext().catch((error) => {
  console.warn("Event context unavailable", error);
  const summary = document.querySelector("#event-summary");
  if (summary) {
    summary.textContent = "Event context unavailable";
  }
});
