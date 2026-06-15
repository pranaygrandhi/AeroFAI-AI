export type Balloon = {
  balloon_number: number;
  sheet: number;
  zone: string;
  characteristic_type: string;
};

export type DimensionCharacteristic = {
  type: string;
  nominal: number;
  plus_tolerance: number;
  minus_tolerance: number;
};

export type GdtCharacteristic = {
  type: string;
  tolerance: number;
  modifier?: string;
  datums: string[];
};
