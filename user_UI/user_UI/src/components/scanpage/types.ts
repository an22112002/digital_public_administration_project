export interface DocumentItem {
  srID: string;
  serviceID: number;
  code: string;
  title: string;
  description: string;
  required: boolean;
  ocr_enabled: boolean;
  color: string | null;
  files: string[] | null;
}

export interface ScanFile {
  url: string;
  link: string;
}

export interface SendFile {
  srID: string;
  files: string[];
}
