import type {
  VisualizationConfig,
  LinePoint,
  BarDatum,
  ScatterPoint,
  MapPoint,
  HeatmapCell,
} from "@/components/VisualizationRenderer";

function toTitleCase(input: string): string {
  return input
    .trim()
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .toLowerCase()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function pickFirst<T>(arr: T[], n: number): T[] {
  return arr.slice(0, Math.max(0, n));
}

function tryParseDate(value: unknown): Date | null {
  if (value instanceof Date) return value;
  if (typeof value === "string" || typeof value === "number") {
    const d = new Date(value);
    return isNaN(d.getTime()) ? null : d;
  }
  return null;
}

function hasKeys(obj: Record<string, unknown>, keys: string[]): boolean {
  return keys.every((k) => k in obj);
}

function chooseTypeFromQuery(query: string | undefined):
  | "line"
  | "bar"
  | "scatter"
  | "map"
  | "heatmap"
  | null {
  if (!query) return null;
  const q = query.toLowerCase();
  if (/map|geo|location|lat|lng|longitude|latitude/.test(q)) return "map";
  if (/heatmap|matrix|grid/.test(q)) return "heatmap";
  if (/trend|over time|time series|forecast|timeline/.test(q)) return "line";
  if (/scatter|correlation|relationship/.test(q)) return "scatter";
  if (/bar|compare|top|rank|distribution|hist/.test(q)) return "bar";
  return null;
}

function chooseTypeFromData(data: unknown[]):
  | "line"
  | "bar"
  | "scatter"
  | "map"
  | "heatmap"
  | null {
  if (data.length === 0) return null;
  const sample = pickFirst(data, 20).filter(isRecord) as Record<string, unknown>[];
  if (sample.length === 0) return null;

  // Geo points
  if (sample.some((d) => hasKeys(d, ["lat", "lng"]) || hasKeys(d, ["latitude", "longitude"]))) {
    return "map";
  }

  // Heatmap cells
  if (sample.some((d) => hasKeys(d, ["row", "col", "value"]))) {
    return "heatmap";
  }

  // XY points
  if (sample.some((d) => hasKeys(d, ["x", "y"]) || hasKeys(d, ["time", "value"]) || hasKeys(d, ["date", "value"])) ) {
    // Prefer line when x looks like a date/time or index
    const hasTemporalX = sample.some((d) => {
      const rec = d as Record<string, unknown>;
      const xCandidate: unknown = rec["x"] ?? rec["time"] ?? rec["date"];
      return tryParseDate(xCandidate) !== null;
    });
    return hasTemporalX ? "line" : "scatter";
  }

  // Category/value pairs
  if (sample.some((d) => hasKeys(d, ["category", "value"]) || hasKeys(d, ["label", "value"]) )) {
    return "bar";
  }

  // Arrays of numbers -> line over index
  if (sample.every((d) => typeof d === "number")) {
    return "line";
  }

  // Fallback
  return null;
}

function extractNumericValues(obj: Record<string, unknown>): number[] {
  return Object.values(obj).filter((v) => typeof v === "number") as number[];
}

function summarize(values: number[]): { min: number; max: number; mean: number } | null {
  if (!values.length) return null;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  return { min, max, mean };
}

function inferLine(data: unknown[]): { data: LinePoint[]; insights: string[]; title: string } {
  const points: LinePoint[] = [];
  const insights: string[] = [];

  if (data.length && typeof data[0] === "number") {
    const nums = data as number[];
    nums.forEach((y, index) => points.push({ x: index, y }));
    const stats = summarize(nums);
    if (stats) insights.push(`Min ${stats.min}, Max ${stats.max}, Mean ${stats.mean.toFixed(2)}`);
    return { data: points, insights, title: "Time Series (Index)" };
  }

  const sample = pickFirst(data, 100).filter(isRecord) as Record<string, unknown>[];
  const candidateXKeys = ["x", "time", "date", "timestamp"];
  const candidateYKeys = ["y", "value", "count", "amount", "metric"];

  let xKey: string | null = null;
  let yKey: string | null = null;

  // Pick first present keys
  for (const key of candidateXKeys) {
    if (sample.some((d) => key in d)) { xKey = key; break; }
  }
  for (const key of candidateYKeys) {
    if (sample.some((d) => key in d)) { yKey = key; break; }
  }

  if (xKey && yKey) {
    for (const d of sample) {
      const xRaw = d[xKey];
      const x = tryParseDate(xRaw) ?? (typeof xRaw === "number" ? xRaw : null);
      const y = typeof d[yKey] === "number" ? (d[yKey] as number) : null;
      if (x !== null && y !== null) {
        points.push({ x, y });
      }
    }
  } else {
    // Fallback: index for x, first numeric value for y
    sample.forEach((d, i) => {
      const nums = extractNumericValues(d);
      if (nums[0] !== undefined) points.push({ x: i, y: nums[0] });
    });
  }

  const stats = summarize(points.map((p) => p.y));
  if (stats) insights.push(`Min ${stats.min}, Max ${stats.max}, Mean ${stats.mean.toFixed(2)}`);

  const title = xKey && yKey ? `${toTitleCase(yKey)} over ${toTitleCase(xKey)}` : "Line Chart";
  return { data: points, insights, title };
}

function inferBar(data: unknown[]): { data: BarDatum[]; insights: string[]; title: string } {
  const rows: BarDatum[] = [];
  const insights: string[] = [];

  const sample = pickFirst(data, 500);

  if (sample.length && typeof sample[0] === "number") {
    const counts = new Map<number, number>();
    (sample as number[]).forEach((n) => counts.set(n, (counts.get(n) ?? 0) + 1));
    counts.forEach((value, category) => rows.push({ category: String(category), value }));
  } else if (sample.length && typeof sample[0] === "string") {
    const counts = new Map<string, number>();
    (sample as string[]).forEach((s) => counts.set(s, (counts.get(s) ?? 0) + 1));
    counts.forEach((value, category) => rows.push({ category, value }));
  } else {
    const recs = sample.filter(isRecord) as Record<string, unknown>[];
    // Prefer explicit category/value fields
    const catKey = ["category", "label", "name", "group"].find((k) => recs.some((r) => k in r));
    const valKey = ["value", "count", "total", "amount"].find((k) => recs.some((r) => k in r));

    if (catKey && valKey) {
      recs.forEach((r) => {
        const category = String(r[catKey] ?? "");
        const value = typeof r[valKey] === "number" ? (r[valKey] as number) : NaN;
        if (!Number.isNaN(value)) rows.push({ category, value });
      });
    } else if (recs.length) {
      // Fallback: pick first string key as category and first numeric as value
      const stringKey = Object.keys(recs[0]).find((k) => typeof recs[0][k as keyof typeof recs[0]] === "string");
      const numericKey = Object.keys(recs[0]).find((k) => typeof recs[0][k as keyof typeof recs[0]] === "number");
      if (stringKey && numericKey) {
        recs.forEach((r) => rows.push({ category: String(r[stringKey]), value: Number(r[numericKey]) }));
      }
    }
  }

  if (rows.length) {
    const maxBar = rows.reduce((a, b) => (a.value > b.value ? a : b));
    insights.push(`Top category: ${maxBar.category} (${maxBar.value})`);
  }

  return { data: rows, insights, title: "Bar Chart" };
}

function inferScatter(data: unknown[]): { data: ScatterPoint[]; insights: string[]; title: string } {
  const points: ScatterPoint[] = [];
  const recs = pickFirst(data, 1000).filter(isRecord) as Record<string, unknown>[];

  const numericKeys = Array.from(
    new Set(
      recs.flatMap((r) => Object.keys(r).filter((k) => typeof r[k] === "number"))
    )
  );

  const [xKey, yKey] = numericKeys.length >= 2 ? numericKeys.slice(0, 2) : [null, null];

  if (xKey && yKey) {
    recs.forEach((r) => points.push({ x: Number(r[xKey]), y: Number(r[yKey]) }));
  }

  // Simple correlation sign (pearson-ish)
  let insight = "";
  if (points.length) {
    const xs = points.map((p) => p.x);
    const ys = points.map((p) => p.y);
    const meanX = xs.reduce((a, b) => a + b, 0) / xs.length;
    const meanY = ys.reduce((a, b) => a + b, 0) / ys.length;
    const num = points.reduce((sum, p) => sum + (p.x - meanX) * (p.y - meanY), 0);
    const denX = Math.sqrt(points.reduce((s, p) => s + Math.pow(p.x - meanX, 2), 0));
    const denY = Math.sqrt(points.reduce((s, p) => s + Math.pow(p.y - meanY, 2), 0));
    const r = denX && denY ? num / (denX * denY) : 0;
    insight = `Correlation ~ ${r.toFixed(2)}`;
  }

  return { data: points, insights: insight ? [insight] : [], title: "Scatter Plot" };
}

function inferMap(data: unknown[]): { data: MapPoint[]; insights: string[]; title: string } {
  const points: MapPoint[] = [];
  const recs = pickFirst(data, 1000).filter(isRecord) as Record<string, unknown>[];

  for (const r of recs) {
    const lat = typeof (r as Record<string, unknown>)["lat"] === "number"
      ? (r as Record<string, number>)["lat"]
      : typeof (r as Record<string, unknown>)["latitude"] === "number"
      ? (r as Record<string, number>)["latitude"]
      : null;
    const lng = typeof (r as Record<string, unknown>)["lng"] === "number"
      ? (r as Record<string, number>)["lng"]
      : typeof (r as Record<string, unknown>)["longitude"] === "number"
      ? (r as Record<string, number>)["longitude"]
      : null;
    if (lat !== null && lng !== null) {
      const value = typeof (r as Record<string, unknown>)["value"] === "number"
        ? (r as Record<string, number>)["value"]
        : undefined;
      const label = (r as Record<string, unknown>)["label"] !== undefined
        ? String((r as Record<string, unknown>)["label"])
        : undefined;
      points.push({ lat, lng, value, label });
    }
  }

  const insights = points.length ? [`Locations: ${points.length}`] : [];
  return { data: points, insights, title: "Geospatial Map" };
}

function inferHeatmap(data: unknown[]): { data: HeatmapCell[]; insights: string[]; title: string } {
  const cells: HeatmapCell[] = [];
  const recs = pickFirst(data, 500).filter(isRecord) as Record<string, unknown>[];

  for (const r of recs) {
    const rr = r as Record<string, unknown>;
    if (typeof rr["row"] === "number" && typeof rr["col"] === "number" && typeof rr["value"] === "number") {
      cells.push({ row: rr["row"] as number, col: rr["col"] as number, value: rr["value"] as number });
    }
  }

  const insights = cells.length ? [`Cells: ${cells.length}`] : [];
  return { data: cells, insights, title: "Heatmap" };
}

export function generateVisualizationConfig(inputData: unknown, query: string | undefined): VisualizationConfig {
  const dataArray: unknown[] = Array.isArray(inputData)
    ? inputData
    : isRecord(inputData)
    ? [inputData]
    : [];

  const preferredType = chooseTypeFromQuery(query);
  const dataInferredType = chooseTypeFromData(dataArray);
  const chosen = preferredType ?? dataInferredType ?? "bar";

  const options = { width: undefined, height: undefined };

  if (chosen === "map") {
    const { data, insights, title } = inferMap(dataArray);
    return { type: "map", data, options, metadata: { title, description: query ?? "", insights } };
  }
  if (chosen === "heatmap") {
    const { data, insights, title } = inferHeatmap(dataArray);
    return { type: "heatmap", data, options, metadata: { title, description: query ?? "", insights } };
  }
  if (chosen === "scatter") {
    const { data, insights, title } = inferScatter(dataArray);
    return { type: "scatter", data, options, metadata: { title, description: query ?? "", insights } };
  }
  if (chosen === "line") {
    const { data, insights, title } = inferLine(dataArray);
    return { type: "line", data, options, metadata: { title, description: query ?? "", insights } };
  }

  // Default to bar
  const { data, insights, title } = inferBar(dataArray);
  return { type: "bar", data, options, metadata: { title, description: query ?? "", insights } };
}
