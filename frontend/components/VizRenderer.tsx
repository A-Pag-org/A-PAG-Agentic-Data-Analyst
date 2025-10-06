"use client";
import React from "react";
import { Box } from "@chakra-ui/react";
import { VisualizationRenderer, VisualizationConfig } from "./VisualizationRenderer";

export const VizRenderer: React.FC<{ config: VisualizationConfig }> = ({ config }) => {
  return (
    <Box w="full">
      <VisualizationRenderer config={config} />
    </Box>
  );
};
