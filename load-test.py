#!/usr/bin/env python3
"""
Quiz App Load Tester (Playwright)

- Launches N concurrent browser contexts (>=200).
- Workflow per client:
  1) Open http://localhost:8000/play
  2) Fill game key (default "620306"), submit
  3) Wait for name field, enter "client-<id>", click "Abschicken"
  4) Wait for game start (#progress-circle or answer grid)
  5) Repeatedly click a random answer button; wait for next question (buttons enabled again)
- Measures:
  * Page load time for /play (goto -> networkidle/domcontentloaded)
  * All REST calls (resource_type in {'xhr','fetch'}) with durations (request -> finished)
- Outputs summary tables (page loads + REST endpoints) at the end.

Usage examples:
    python load_quiz.py --clients 250 --key 620306 --rounds 20
    python load_quiz.py --duration 120  # run answers for ~120s per client
    python load_quiz.py --csv metrics.csv --json metrics.json

Tips:
- If your "Submit"/"Abschicken" button texts differ, adjust selectors below.
- For heavy loads, consider --ramp-up 20 to spread start times.
"""

import asyncio
import argparse
import json
import math
import os
import random
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, Page, Request

# ---------- Config defaults ----------
DEFAULT_BASE = "http://localhost:8000"
DEFAULT_PATH = "/play"

# ---------- Data structures ----------


@dataclass
class RequestMetric:
  client_id: int
  method: str
  url: str
  path: str
  status: Optional[int]
  resource_type: str
  start_ms: float
  end_ms: float
  duration_ms: float
  ok: bool
  phase: str = "rest"  # "rest" or "page_load"


@dataclass
class Aggregator:
  # all metrics
  metrics: List[RequestMetric] = field(default_factory=list)

  def add(self, m: RequestMetric) -> None:
    self.metrics.append(m)

  # --- Stats helpers ---
  @staticmethod
  def _percentile(values: List[float], pct: float) -> float:
    if not values:
      return float("nan")
    values_sorted = sorted(values)
    # Nearest-rank method
    k = max(1, math.ceil(pct * len(values_sorted))) - 1
    return values_sorted[k]

  @staticmethod
  def _fmt_ms(x: float) -> str:
    if math.isnan(x):
      return "nan"
    return f"{x:.1f}"

  def summarize(self) -> Tuple[str, str]:
    """
    Returns (page_load_table_str, rest_table_str)
    """
    # Group page loads by path
    page_loads = [m for m in self.metrics if m.phase == "page_load"]
    rest_calls = [m for m in self.metrics if m.phase == "rest" and m.resource_type in {"xhr", "fetch"}]

    def group_by(items: List[RequestMetric], key_fn):
      g: Dict[str, List[RequestMetric]] = {}
      for it in items:
        g.setdefault(key_fn(it), []).append(it)
      return g

    # PAGE LOADS
    by_page = group_by(page_loads, lambda m: m.path or urlparse(m.url).path)
    page_lines = []
    header = ["Page", "Count", "Avg ms", "p50", "p90", "p99", "Min", "Max", "Errors"]
    page_lines.append(" | ".join(header))
    page_lines.append("-" * (len(" | ".join(header)) + 4))
    for path, items in sorted(by_page.items(), key=lambda kv: kv[0]):
      durs = [m.duration_ms for m in items if not math.isnan(m.duration_ms)]
      errs = sum(1 for m in items if not m.ok)
      avg = sum(durs) / len(durs) if durs else float("nan")
      p50 = self._percentile(durs, 0.50)
      p90 = self._percentile(durs, 0.90)
      p99 = self._percentile(durs, 0.99)
      mn = min(durs) if durs else float("nan")
      mx = max(durs) if durs else float("nan")
      page_lines.append(
          " | ".join(
              [
                  path or "(unknown)",
                  str(len(items)),
                  self._fmt_ms(avg),
                  self._fmt_ms(p50),
                  self._fmt_ms(p90),
                  self._fmt_ms(p99),
                  self._fmt_ms(mn),
                  self._fmt_ms(mx),
                  f"{errs}"
              ]
          )
      )
    page_table = "\n".join(page_lines) if len(page_lines) > 2 else "No page load metrics captured."

    # REST CALLS
    by_endpoint = group_by(rest_calls, lambda m: f"{m.method} {m.path or urlparse(m.url).path}")
    rest_lines = []
    header_r = ["Endpoint (method path)", "Count", "Avg ms", "p50", "p90", "p99", "Min", "Max", "Err%"]
    rest_lines.append(" | ".join(header_r))
    rest_lines.append("-" * (len(" | ".join(header_r)) + 4))
    for ep, items in sorted(by_endpoint.items(), key=lambda kv: kv[0]):
      durs = [m.duration_ms for m in items if not math.isnan(m.duration_ms)]
      errs = sum(1 for m in items if not m.ok)
      avg = sum(durs) / len(durs) if durs else float("nan")
      p50 = self._percentile(durs, 0.50)
      p90 = self._percentile(durs, 0.90)
      p99 = self._percentile(durs, 0.99)
      mn = min(durs) if durs else float("nan")
      mx = max(durs) if durs else float("nan")
      err_pct = (errs / len(items) * 100.0) if items else 0.0
      rest_lines.append(
          " | ".join(
              [
                  ep,
                  str(len(items)),
                  self._fmt_ms(avg),
                  self._fmt_ms(p50),
                  self._fmt_ms(p90),
                  self._fmt_ms(p99),
                  self._fmt_ms(mn),
                  self._fmt_ms(mx),
                  f"{err_pct:.1f}%"
              ]
          )
      )
    rest_table = "\n".join(rest_lines) if len(rest_lines) > 2 else "No REST (xhr/fetch) metrics captured."

    return page_table, rest_table

# ---------- Client logic ----------


async def wait_for_game_ui(page: Page, timeout_ms: int) -> None:
  """
  Wait until the game screen appears: either #progress-circle
  or the answer grid with buttons.
  """
  try:
    await page.wait_for_selector("#progress-circle", state="visible", timeout=timeout_ms)
    return
  except Exception:
    pass
  # Answer grid fallback
  await page.wait_for_selector("div.grid button", state="visible", timeout=timeout_ms)


async def click_random_answer(page: Page, timeout_ms: int) -> None:
  """
  Click a random enabled answer button, then wait for the next question
  by waiting for buttons to be disabled then re-enabled.
  """
  # Ensure buttons are visible
  await page.wait_for_selector("div.grid button", state="visible", timeout=timeout_ms)
  # Pick among currently enabled buttons
  enabled_locator = page.locator("div.grid button:not([disabled])")
  count = await enabled_locator.count()
  # If none enabled (edge), wait briefly and retry once
  if count == 0:
    await page.wait_for_timeout(200)
    count = await enabled_locator.count()
  if count == 0:
    # As a last resort click first button if present
    any_btns = page.locator("div.grid button")
    if await any_btns.count() > 0:
      await any_btns.nth(0).click()
    return
  idx = random.randrange(count)
  await enabled_locator.nth(idx).click()

  # Wait for transient disabled state (server evaluating question)
  # Then wait for next set to become enabled again
  try:
    await page.wait_for_selector("div.grid button[disabled]", state="attached", timeout=timeout_ms)
  except Exception:
    # Sometimes they never disable; just proceed
    pass
  # Now wait until enabled buttons appear again (next question)
  try:
    await page.wait_for_selector("div.grid button:not([disabled])", state="visible", timeout=timeout_ms)
  except Exception:
    # If not re-enabled, at least ensure buttons are visible again
    await page.wait_for_selector("div.grid button", state="visible", timeout=timeout_ms)


def just_path(url: str) -> str:
  try:
    return urlparse(url).path or "/"
  except Exception:
    return url


async def run_client(
    client_id: int,
    browser: Browser,
    agg: Aggregator,
    base_url: str,
    start_path: str,
    key_value: str,
    rounds: int,
    duration_s: Optional[int],
    think_time_ms: Tuple[int, int],
    timeouts: Dict[str, int],
    headful_name: Optional[str] = None,
) -> None:
  context = await browser.new_context(
      viewport={"width": 1280, "height": 800},
      user_agent=f"QuizLoadTester/1.0 Client/{client_id}",
      java_script_enabled=True,
      ignore_https_errors=True,
      bypass_csp=True,
  )
  page = await context.new_page()

  # ---- Network timing hooks ----
  req_start: Dict[Request, float] = {}

  def on_request(req: Request):
    req_start[req] = time.perf_counter() * 1000.0  # ms

  async def finalize_metric(req: Request, ok: bool):
    start_ms = req_start.pop(req, time.perf_counter() * 1000.0)
    end_ms = time.perf_counter() * 1000.0
    dur = max(0.0, end_ms - start_ms)
    resp = await req.response() if ok else None
    status = resp.status if resp else None
    agg.add(
        RequestMetric(
            client_id=client_id,
            method=req.method,
            url=req.url,
            path=just_path(req.url),
            status=status,
            resource_type=req.resource_type,
            start_ms=start_ms,
            end_ms=end_ms,
            duration_ms=dur,
            ok=(ok and (status is not None) and (status < 400)),
            phase="rest" if req.resource_type in {"xhr", "fetch"} else "other",
        )
    )

  page.on("request", on_request)
  page.on(
      "requestfinished",
      lambda req: asyncio.create_task(finalize_metric(req, True))
  )
  page.on(
      "requestfailed",
      lambda req: asyncio.create_task(finalize_metric(req, False))
  )

  # ---- Flow ----
  url = f"{base_url.rstrip('/')}{start_path}"
  # Measure initial page load
  t0 = time.perf_counter() * 1000.0
  try:
    # Try networkidle first, fallback to domcontentloaded
    try:
      await page.goto(url, wait_until="networkidle", timeout=timeouts["goto"])
    except Exception:
      await page.goto(url, wait_until="domcontentloaded", timeout=timeouts["goto"])
    t1 = time.perf_counter() * 1000.0
    agg.add(
        RequestMetric(
            client_id=client_id,
            method="GET",
            url=url,
            path=start_path,
            status=200,
            resource_type="document",
            start_ms=t0,
            end_ms=t1,
            duration_ms=max(0.0, t1 - t0),
            ok=True,
            phase="page_load",
        )
    )
  except Exception:
    t1 = time.perf_counter() * 1000.0
    agg.add(
        RequestMetric(
            client_id=client_id,
            method="GET",
            url=url,
            path=start_path,
            status=None,
            resource_type="document",
            start_ms=t0,
            end_ms=t1,
            duration_ms=max(0.0, t1 - t0),
            ok=False,
            phase="page_load",
        )
    )
    await context.close()
    return

  # Step 2: Enter key and submit
  try:
    # Fill any visible text input (assumed "key")
    await page.wait_for_selector('input[type="text"]:visible', timeout=timeouts["ui"])
    key_input = page.locator('input[type="text"]:visible').first
    await key_input.fill(key_value)
    # Prefer clicking a button with "Submit", else press Enter
    submit_btn = page.locator('button:has-text("Submit")')
    if await submit_btn.count() > 0:
      await submit_btn.first.click()
    else:
      await key_input.press("Enter")
  except Exception:
    # If this fails, client can't proceed
    await context.close()
    return

  # Step 3: Wait for name field and click "Abschicken"
  try:
    await page.wait_for_selector('button:has-text("Abschicken")', state="visible", timeout=timeouts["ui"])
    name_btn = page.locator('button:has-text("Abschicken")').first
    # Fill the visible text input again (assumed "name")
    await page.wait_for_selector('input[type="text"]:visible', timeout=timeouts["ui"])
    name_input = page.locator('input[type="text"]:visible').first
    await name_input.fill(f"client-{client_id}")
    await name_btn.click()
  except Exception:
    # If localized differently, try pressing Enter as fallback
    try:
      await page.keyboard.press("Enter")
    except Exception:
      await context.close()
      return

  # Step 4: Wait for game start
  try:
    await wait_for_game_ui(page, timeout_ms=timeouts["game"])
  except Exception:
    await context.close()
    return

  # Step 5: Answer loop
  start_play = time.perf_counter()
  q_count = 0
  try:
    while True:
      # Optional stopping conditions
      if rounds > 0 and q_count >= rounds:
        break
      if duration_s is not None and (time.perf_counter() - start_play) >= duration_s:
        break

      # "Think" a bit to avoid synchronized clicks
      await page.wait_for_timeout(random.randint(*think_time_ms))
      await click_random_answer(page, timeout_ms=timeouts["question"])
      q_count += 1
  finally:
    await context.close()

# ---------- Main / CLI ----------


def parse_args() -> argparse.Namespace:
  p = argparse.ArgumentParser(description="Load test for Quiz app with real browsers (Playwright).")
  p.add_argument("--base", default=DEFAULT_BASE, help="Base URL, default http://localhost:8000")
  p.add_argument("--path", default=DEFAULT_PATH, help="Start path, default /play")
  p.add_argument("--key", required=True, help="Quiz key to enter at first input")
  p.add_argument("--clients", type=int, default=200, help="Number of concurrent clients (default 200)")
  p.add_argument("--rounds", type=int, default=15, help="Max questions to answer per client (0 = unlimited)")
  p.add_argument("--duration", type=int, default=None,
                 help="Max answering time per client in seconds (overrides rounds if provided)")
  p.add_argument("--headful", action="store_true", help="Run headed (useful for debugging small client counts)")
  p.add_argument("--ramp-up", type=float, default=10.0, help="Seconds to spread client starts over (default 10s)")
  p.add_argument("--min-think", type=int, default=200, help="Min think time between answers in ms (default 200)")
  p.add_argument("--max-think", type=int, default=1000, help="Max think time between answers in ms (default 1200)")
  p.add_argument("--goto-timeout", type=int, default=30000, help="Timeout for page.goto in ms (default 15000)")
  p.add_argument("--ui-timeout", type=int, default=30000, help="Timeout for waiting UI elements in ms (default 15000)")
  p.add_argument("--game-timeout", type=int, default=30000, help="Timeout for waiting game UI in ms (default 30000)")
  p.add_argument("--question-timeout", type=int, default=20000,
                 help="Timeout around a question cycle in ms (default 20000)")
  p.add_argument("--csv", default=None, help="Write raw metrics to CSV file")
  p.add_argument("--json", default=None, help="Write raw metrics to JSON file")
  return p.parse_args()


def write_outputs(agg: Aggregator, csv_path: Optional[str], json_path: Optional[str]) -> None:
  if json_path:
    with open(json_path, "w", encoding="utf-8") as f:
      json.dump([m.__dict__ for m in agg.metrics], f, indent=2)
    print(f"\nWrote JSON metrics to: {json_path}")

  if csv_path:
    import csv
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
      w = csv.writer(f)
      w.writerow(["client_id", "phase", "method", "url", "path", "status",
                 "resource_type", "start_ms", "end_ms", "duration_ms", "ok"])
      for m in agg.metrics:
        w.writerow([m.client_id, m.phase, m.method, m.url, m.path, m.status if m.status is not None else "",
                   m.resource_type, f"{m.start_ms:.3f}", f"{m.end_ms:.3f}", f"{m.duration_ms:.3f}", int(m.ok)])
    print(f"Wrote CSV metrics to: {csv_path}")


async def main_async():
  args = parse_args()
  agg = Aggregator()

  async with async_playwright() as pw:
    browser = await pw.chromium.launch(
        headless=not args.headful,
        args=[
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ],
    )

    # Schedule all clients with ramp-up
    tasks = []
    for i in range(args.clients):
      delay = (args.ramp_up * (i / max(1, args.clients - 1))) if args.ramp_up > 0 else 0.0

      async def starter(idx=i, dly=delay):
        if dly > 0:
          await asyncio.sleep(dly)
        return await run_client(
            client_id=idx + 1,
            browser=browser,
            agg=agg,
            base_url=args.base,
            start_path=args.path,
            key_value=args.key,
            rounds=args.rounds if args.duration is None else 0,
            duration_s=args.duration,
            think_time_ms=(args.min_think, args.max_think),
            timeouts={
                "goto": args.goto_timeout,
                "ui": args.ui_timeout,
                "game": args.game_timeout,
                "question": args.question_timeout,
            },
        )
      tasks.append(asyncio.create_task(starter()))
    await asyncio.gather(*tasks, return_exceptions=True)

    await browser.close()

  # ----- Output -----
  page_table, rest_table = agg.summarize()
  print("\n=== Page Loads ===")
  print(page_table)
  print("\n=== REST (XHR/Fetch) ===")
  print(rest_table)

  write_outputs(agg, args.csv, args.json)


def main():
  try:
    asyncio.run(main_async())
  except KeyboardInterrupt:
    print("\nInterrupted.", file=sys.stderr)


if __name__ == "__main__":
  main()
