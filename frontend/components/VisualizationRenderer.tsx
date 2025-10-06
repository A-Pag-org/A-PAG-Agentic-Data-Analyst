import React from "react";

export type ChartOptions = {
  width?: number;
  height?: number;
  colors?: string[];
  [key: string]: unknown;
};

export interface VisualizationConfig {
  type: "line" | "bar" | "scatter" | "map" | "heatmap";
  data: unknown[];
  options: ChartOptions;
  metadata: {
    title: string;
    description: string;
    insights: string[];
  };
}

interface ChartProps {
  data: unknown[];
  options: ChartOptions;
}

const LineChart: React.FC<ChartProps> = ({ data, options }) => {
  return (
    <div role="img" aria-label="Line chart">
      <strong>Line Chart</strong>
      <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify({ data, options }, null, 2)}</pre>
    </div>
  );
};

const BarChart: React.FC<ChartProps> = ({ data, options }) => {
  return (
    <div role="img" aria-label="Bar chart">
      <strong>Bar Chart</strong>
      <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify({ data, options }, null, 2)}</pre>
    </div>
  );
};

const ScatterPlot: React.FC<ChartProps> = ({ data, options }) => {
  return (
    <div role="img" aria-label="Scatter plot">
      <strong>Scatter Plot</strong>
      <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify({ data, options }, null, 2)}</pre>
    </div>
  );
};

const LeafletMap: React.FC<ChartProps> = ({ data, options }) => {
  return (
    <div role="img" aria-label="Map visualization">
      <strong>Map</strong>
      <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify({ data, options }, null, 2)}</pre>
    </div>
  );
};

const HeatmapChart: React.FC<ChartProps> = ({ data, options }) => {
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
      return null;
  }
};
