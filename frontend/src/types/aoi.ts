export interface AOI {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  radius_km: number;
  description: string;
  active: boolean;
  monitoring_interval: string;
  last_checked: string | null;
  created_at: string;
}