export type MapLayer =
  | "satellite"
  | "change"
  | "segmentation"
  | "dynamicworld"
  | "objects";

export interface MapLayerOption {
  id: MapLayer;
  label: string;
}