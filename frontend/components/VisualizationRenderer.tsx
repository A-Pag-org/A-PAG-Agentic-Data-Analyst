import React from "react";

export type ChartOptions = {
  width?: number;
  height?: number;
  colors?: string[];
  [key: string]: unknown;
};

// Strongly typed data shapes for each visualization
export type LinePoint = { x: number | Date; y: number; series?: string };
export type BarDatum = { category: string; value: number };
export type ScatterPoint = { x: number; y: number; label?: string };
export type MapPoint = { lat: number; lng: number; value?: number; label?: string };
export type HeatmapCell = { row: number; col: number; value: number };

export type VisualizationMetadata = {
  title: string;
  description: string;
  insights: string[];
};

type BaseVisualizationConfig<TType extends string, TDatum> = {
  type: TType;
  data: TDatum[];
  options: ChartOptions;
  metadata: VisualizationMetadata;
};

export type VisualizationConfig =
  | BaseVisualizationConfig<"line", LinePoint>
  | BaseVisualizationConfig<"bar", BarDatum>
  | BaseVisualizationConfig<"scatter", ScatterPoint>
  | BaseVisualizationConfig<"map", MapPoint>
  | BaseVisualizationConfig<"heatmap", HeatmapCell>;

// Strongly typed chart props per visualization type
type LineChartProps = { data: LinePoint[]; options: ChartOptions };
type BarChartProps = { data: BarDatum[]; options: ChartOptions };
type ScatterPlotProps = { data: ScatterPoint[]; options: ChartOptions };
type LeafletMapProps = { data: MapPoint[]; options: ChartOptions };
type HeatmapChartProps = { data: HeatmapCell[]; options: ChartOptions };

const LineChart: React.FC<LineChartProps> = ({ data, options }) => {
  return (
    <div role="img" aria-label="Line chart">
      <strong>Line Chart</strong>
      <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify({ data, options }, null, 2)}</pre>
    </div>
  );
};

const BarChart: React.FC<BarChartProps> = ({ data, options }) => {
  return (
    <div role="img" aria-label="Bar chart">
      <strong>Bar Chart</strong>
      <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify({ data, options }, null, 2)}</pre>
    </div>
  );
};

const ScatterPlot: React.FC<ScatterPlotProps> = ({ data, options }) => {
  return (
    <div role="img" aria-label="Scatter plot">
      <strong>Scatter Plot</strong>
      <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify({ data, options }, null, 2)}</pre>
    </div>
  );
};

const LeafletMap: React.FC<LeafletMapProps> = ({ data, options }) => {
  return (
    <div role="img" aria-label="Map visualization">
      <strong>Map</strong>
      <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify({ data, options }, null, 2)}</pre>
    </div>
  );
};

const HeatmapChart: React.FC<HeatmapChartProps> = ({ data, options }) => {
  return (
    <div role="img" aria-label="Heatmap visualization">
      <strong>Heatmap</strong>
      <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify({ data, options }, null, 2)}</pre>
    </div>
  );
};

export const VisualizationRenderer: React.FC<{ config: VisualizationConfig }> = ({ config }) => {
  switch (config.type) {
    case "line":
      return <LineChart data={config.data} options={config.options} />;
    case "bar":
      return <BarChart data={config.data} options={config.options} />;
    case "scatter":
      return <ScatterPlot data={config.data} options={config.options} />;
    case "map":
      return <LeafletMap data={config.data} options={config.options} />;
    case "heatmap":
      return <HeatmapChart data={config.data} options={config.options} />;
    default:
      // Exhaustive check to catch unhandled types during development
      const _exhaustiveCheck: never = config;
      return null;
  }
};
