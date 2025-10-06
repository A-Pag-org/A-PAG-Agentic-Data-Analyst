"use client";
import React from "react";
import { Box, Card, CardBody } from "@chakra-ui/react";
import { VisualizationRenderer, VisualizationConfig } from "./VisualizationRenderer";

export const VizRenderer: React.FC<{ config: VisualizationConfig }> = ({ config }) => {
  return (
    <Card className="scale-in" w="full" mb={6}>
      <CardBody p={{ base: 4, md: 6 }}>
        <Box w="full">
          <VisualizationRenderer config={config} />
        </Box>
      </CardBody>
    </Card>
  );
};
