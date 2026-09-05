const EVENT_DATA_URL = "./data/dashboard_data.json";

const eventDateFormat = new Intl.DateTimeFormat("it-IT", {
  day: "2-digit",
  month: "short",
  year: "numeric",
});
const eventShortDateFormat = new Intl.DateTimeFormat("it-IT", {
  day: "2-digit",
  month: "short",
});

let selectedEventDay = null;
let eventTimelineIndex = new Map();

function eventAsDate(value) {
  return new Date(`${value}T12:00:00Z`);
}

function formatEventDate(value) {
  return eventDateFormat.format(eventAsDate(value));
}

function formatEventShortDate(value) {
  return eventShortDateFormat.format(eventAsDate(value));
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

function syncEventSelection(day) {
  const activeDay = selectedEventDay === day ? null : day;
  selectedEventDay = activeDay;

  document.querySelectorAll("[data-event-day]").forEach((element) => {
    const selected = activeDay !== null && element.dataset.eventDay === activeDay;
    element.classList.toggle("selected", selected);
    if (element.matches("button")) {
      element.setAttribute("aria-pressed", selected ? "true" : "false");
    }
  });

  document.querySelectorAll(".event-card").forEach((card) => {
    card.classList.toggle("selected", activeDay !== null && card.dataset.eventDay === activeDay);
  });

  const index = activeDay === null ? null : eventTimelineIndex.get(activeDay);
  if (typeof window.setOrbitfabricEventGuide === "function") {
    window.setOrbitfabricEventGuide(Number.isInteger(index) ? index : null);
  }

  const selection = document.querySelector("#event-selection");
  if (selection) {
    selection.textContent = activeDay
      ? `${formatEventDate(activeDay)} selected on traffic charts`
      : "Tap an in-window marker to inspect that day on both charts.";
  }
}

function scrollToEvent(eventId) {
  document.querySelector(`#event-${CSS.escape(eventId)}`)?.scrollIntoView({
    behavior: "smooth",
    block: "center",
  });
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
    marker.dataset.eventDay = day;
    marker.setAttribute("aria-pressed", "false");
    const position = ((eventAsDate(day).getTime() - start) / span) * 100;
    marker.style.left = `${Math.min(100, Math.max(0, position))}%`;
    marker.setAttribute(
      "aria-label",
      `${formatEventDate(day)}: ${events.map((event) => event.label).join("; ")}`,
    );
    marker.title = events.map((event) => event.label).join("\n");
    marker.textContent = events.length > 1 ? String(events.length) : "";
    marker.addEventListener("click", () => {
      syncEventSelection(day);
      scrollToEvent(events[0].id);
    });
    line.appendChild(marker);
  }

  const range = document.createElement("div");
  range.className = "event-track-range";
  appendTextElement(range, "span", "", formatEventDate(context.timeline_start));
  appendTextElement(range, "span", "", formatEventDate(context.timeline_end));
  track.appendChild(range);

  const selection = document.createElement("div");
  selection.id = "event-selection";
  selection.className = "event-selection";
  selection.textContent = "Tap an in-window marker to inspect that day on both charts.";
  track.appendChild(selection);

  const pending = (data.events ?? []).filter(
    (event) => eventStatus(event, context) === "pending",
  );
  if (pending.length) {
    const pendingStrip = document.createElement("div");
    pendingStrip.className = "event-pending-strip";
    appendTextElement(pendingStrip, "span", "event-pending-label", "Awaiting traffic");

    for (const event of pending) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "event-pending-item";
      button.textContent = `${formatEventShortDate(event.date)} · ${event.label}`;
      button.addEventListener("click", () => scrollToEvent(event.id));
      pendingStrip.appendChild(button);
    }
    track.appendChild(pendingStrip);
  }
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
    card.dataset.eventDay = event.date;

    const meta = document.createElement("div");
    meta.className = "event-card-meta";
    appendTextElement(meta, "span", "event-date", formatEventDate(event.date));
    appendTextElement(meta, "span", "event-badge", event.type);
    appendTextElement(meta, "span", "event-badge", event.channel);
    appendTextElement(
      meta,
      "span",
      `event-status ${status}`,
      status === "pending"
        ? "awaiting traffic"
        : status === "before"
          ? "before retained window"
          : "in traffic window",
    );
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

    const actions = document.createElement("div");
    actions.className = "event-card-actions";

    if (status === "in-window") {
      const locate = document.createElement("button");
      locate.type = "button";
      locate.className = "event-locate";
      locate.dataset.eventDay = event.date;
      locate.setAttribute("aria-pressed", "false");
      locate.textContent = "Show on charts";
      locate.addEventListener("click", () => syncEventSelection(event.date));
      actions.appendChild(locate);
    }

    if (event.url) {
      const link = document.createElement("a");
      link.href = event.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = "Open source ↗";
      actions.appendChild(link);
    }

    footer.appendChild(actions);
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

  eventTimelineIndex = new Map(
    (data.timeline ?? []).map((point, index) => [point.date, index]),
  );

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
